import csv
import io
import logging
from typing import Any, Dict, Set, Tuple
from django.utils.translation import gettext_lazy as _
from django.contrib.admin.utils import flatten
from django.forms import modelform_factory
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone
from cmm.const import UTF8
from cmm.utils.modelform import get_modelform_non_unique_error_codes, get_modelform_error_messages
from cmm.models.base import UniqueConstraintMixin, SimpleTable, VersionedTable, HistoryTable
from cmm.csv import CsvLog


_logger = logging.getLogger(__name__)

class TooManyInvalidRowsError(Exception):
    """CSV import処理にて指定した件数以上のエラーまたはスキップが発生した時の例外"""
    def __init__(self, file_name, row_cnt):
        self.file_name = file_name
        self.row_cnt = row_cnt
        self.message = _('There are too many errors to stop importing. [File: %(file_name)s]')%{"file_name": file_name}
        super().__init__()

    def __str__(self):
        return self.message

class CsvImportBaseMixin:
    """CSV import処理にてカスタマイズ可能な共通属性とメソッドをまとめたもの
        # todo: language選択を可能にする
    """
    # encoding = 'cp932'
    encoding = UTF8
    dialect = csv.excel
    date_format = '%Y/%m/%d'
    is_save_log2database = True

    chunk_size = 1000               # 一回の読込行数、chunkごとにDB保存する
    header_row_number = 1           # the number of first rows to skip, if no rows to skip then should be 0.
    csv_error_limit = 100           # エラーとなった行数がこの上限を超えたら処理を中断する。
    csv_skip_limit = 100            # スキップした行数がこの上限を超えたら処理を中断する、読み飛ばし結果を画面表示する場合は必須。

    is_bulk_insert = False          # ユニーク制限がある場合は重複処理が必須となり、重複処理ポリシーに従う。
                                    # ユニーク制限がない場合、重複容認なら重複インポートになり、重複不可なら重複処理ポリシーに従う。
    is_duplicate_available = False  # 重複容認ポリシー、ユニーク制限がある場合は無視される。
                                    # True: 重複行がインポートされる、False: 重複ポリシーに従う
    is_replace_existing = True      # 重複処理ポリシー、True:取込データ優先、False:既存データ優先

    @property
    def is_resolve_duplicate(self):
        """重複チェックの実施有無。"""
        has_unique_restriction = issubclass(self.model, UniqueConstraintMixin)
        if has_unique_restriction or not self.is_duplicate_available:
            return True
        return False             # 重複チェックなし、重複行はそのままインポートされる

    def get_csv_columns(self) -> Tuple[str]:
        """CSVファイルの列名定義"""
        return tuple(flatten(self.fields))

    def get_model_fields(self) -> Tuple[str]:
        """CSVと関連つけられるModelのfields"""
        return self.get_csv_columns()
        
    # pylint: disable = unused-argument
    def csv2model(self, csv_dict: Dict[str, str], *args, **kwargs) -> Dict[str, Any]:
        """デフォルトでは同名項目を転送、必要に応じてOverride"""
        return self.get_default_values() | {k:v for (k,v) in csv_dict.items() if k in self.get_model_fields()}

    def get_skippable_errors(self, modelform, *args, **kwargs) -> Set[str]:
        """ModelForm.Clean()チェックのエラーのなかでスキップできるものを設定する（エラー行ではなくスキップ行としてマークする）"""
        return {}

    def get_default_values(self) -> Dict[str, Any]:
        """CSVファイルからインポートされない項目のデフォルト値を設定する。Overrideするときは親の結果を含むこと"""
        if issubclass(self.model, HistoryTable):
            return {'valid_from': self.model().get_default_valid_from(),
                    'valid_through': self.model().get_default_valid_through(),
                    }
        else:
            return {}

    def pre_import_processing(self, *args, **kwargs):
        """CSV importの前処理"""

    def post_import_processing(self, *args, **kwargs):
        """CSV importの後処理"""

    def read_csv_file(self, csv_file, login_user_name: str, lot_number: str) -> int:
        """CSVファイルの読み込み処理"""
        def get_modelform_cleaned_data(csv_log: CsvLog):
            """CSV行をModelFormに変換する"""
            def get_modelform_class():
                """Dynamically generate ModelForm class"""
                def disable_formfield(db_field, **kwargs):
                    form_field = db_field.formfield(**kwargs)
                    if form_field:
                        form_field.widget.attrs['disabled'] = 'true'
                    return form_field

                form_fields = list(set(self.get_model_fields() + tuple(k for k in self.get_default_values())))
                return modelform_factory(self.model, fields = form_fields, formfield_callback = disable_formfield)

            # Add default values to the csv row.
            modelform = get_modelform_class()(self.csv2model(csv_log.row_content, chunk = chunk))

            if modelform.is_valid():
                csv_log.message = _('Newly imported row.')
                csv_log.modelform = modelform
            else:
                non_unique_error_codes = get_modelform_non_unique_error_codes(modelform)
                if not non_unique_error_codes:      # unique violation
                    if self.is_bulk_insert or not self.is_replace_existing:
                        csv_log.log_level = CsvLog.WARN     # DBと重複したのでスキップする
                        csv_log.message = get_modelform_error_messages(modelform)
                    else:
                        csv_log.message = _("Update existing row.")
                        csv_log.edit_type = CsvLog.UPDATE
                        modelform.cleaned_data = modelform.data
                        csv_log.modelform = modelform
                elif non_unique_error_codes.issubset(self.get_skippable_errors(modelform)):
                    csv_log.log_level = CsvLog.WARN
                    csv_log.message = get_modelform_error_messages(modelform)
                else:
                    csv_log.log_level = CsvLog.ERROR
                    csv_log.message = get_modelform_error_messages(modelform)

        def add2chunk(csv_log: CsvLog):
            """chunkに重複行がなければそのまま追加、あれば入れ替え。"""
            def get_duplicated_in_chunk() -> CsvLog:
                """chunk内での重複行を取得する"""
                if issubclass(self.model, UniqueConstraintMixin):
                    obj = csv_log.modelform.instance
                    for row in chunk:
                        if all(getattr(row.modelform.instance, f, None) == getattr(obj, f, None) \
                                for f in obj.get_unique_key()):
                            return row
                    return None
                
                for row in chunk:
                    if csv_log.row_content == row.row_content:
                        return row

                return None

            if self.is_resolve_duplicate:
                duplicated = get_duplicated_in_chunk()

            if duplicated is None:
                chunk.append(csv_log)
            else:
                if self.is_replace_existing:            # 後発優先の場合、元の行をスキップし、現在行をDB反映候補とする
                    csv_log.edit_type = duplicated.edit_type
                    csv_log.message = duplicated.message
                    duplicated.log_level = CsvLog.INFO
                    
                    duplicated.log_level = CsvLog.WARN
                    duplicated.message = _('Duplicated with another row.[row no: %(row_no)s.]') \
                                            % {"row_no": csv_log.row_no}
                    csv_discard.append(duplicated)
                    chunk.remove(duplicated)
                    chunk.append(csv_log)
                else:                                   # 先発優先：現在行をスキップする
                    csv_log.log_level = CsvLog.WARN
                    csv_log.message = _('Duplicated with another row.[row no: %(row_no)s.]') \
                                            % {"row_no": duplicated.row_no}
                    csv_discard.append(csv_log)

        @transaction.atomic
        def save_to_database() -> None:
            """正常データをインポート先Tableに保存し、CSVログを記録する"""
            def save_records():
                """
                - HistoryTableによる履歴管理が利用できる
                - VersionedTableによる楽観的排他も利用できる
                - SimpleTableのcreator,create_timeも自動設定される
                """
                for row in chunk:
                    if issubclass(self.model, SimpleTable):
                        row.modelform.cleaned_data['updater'] = row.creator
                        row.modelform.cleaned_data['creator'] = row.creator
                        row.modelform.cleaned_data['update_time'] = update_time
                        row.modelform.cleaned_data['create_time'] = update_time

                    try:
                        self.model(**row.modelform.cleaned_data).save()
                    except ValidationError as error:
                        row.log_level = CsvLog.ERROR
                        row.message = str(error)
                        csv_discard.append(row)
                        # pylint: disable = protected-access
                        _logger.error('There is an error when saving %s to database. Error: %s', 
                                        self.model._meta.verbose_name.title(), error)
                    except Exception as exc:
                        _logger.error(row.modelform.cleaned_data)
                        _logger.exception(exc)
                        raise exc

                # remove skipped row from chunk
                for row in csv_discard:
                    if row in chunk:
                        chunk.remove(row)

            def bulk_create_records():
                """Tableのすべての要設定項目はここで設定する必要がある"""
                for row in chunk:
                    if issubclass(self.model, SimpleTable):
                        row.modelform.cleaned_data['updater'] = row.creator
                        row.modelform.cleaned_data['creator'] = row.creator
                        row.modelform.cleaned_data['update_time'] = update_time
                        row.modelform.cleaned_data['create_time'] = update_time
                    if issubclass(self.model, VersionedTable):
                        row.modelform.cleaned_data['version'] = 1

                self.model.objects.bulk_create(self.model(**c.modelform.cleaned_data) for c in chunk)

            update_time = timezone.now()
            if chunk:
                if self.is_bulk_insert or not self.is_resolve_duplicate:
                    bulk_create_records()
                else:
                    # bulk_createはinsertしかできないので、既存データを更新するにはModelのsave()関数を呼び出す
                    save_records()

                if self.is_save_log2database:
                    # 正常取り込みもlogテーブルに記録する
                    CsvLog.objects.bulk_create([csv_log.convert_content2json() for csv_log in chunk])
                # pylint: disable = protected-access
                inserted = sum(1 if c.edit_type == CsvLog.INSERT else 0 for c in chunk)
                _logger.info('We have inserted %s and updated %s rows into %s.', inserted, len(chunk) - inserted,
                             self.model._meta.verbose_name)

            # 一時データをクリアする
            chunk.clear()
            
            if csv_discard:
                save_discard()
            
        # @transaction.atomic
        def save_discard():
            """読み飛ばした行とエラー行の情報をDBに記録する"""
            CsvLog.objects.bulk_create([csv_log.convert_content2json() for csv_log in csv_discard])
            skipped_rows = sum(1 if c.log_level == CsvLog.WARN else 0 for c in csv_discard)
            _logger.warning('We have skipped %s rows when importing csv into %s.',
                                skipped_rows, self.model._meta.verbose_name)
            _logger.error('There were %s error rows when importing csv into %s.',
                                skipped_rows, self.model._meta.verbose_name)
            csv_discard.clear()
            
            
        text_wrapper = io.TextIOWrapper(csv_file, encoding = self.encoding)
        csv_reader = csv.reader(text_wrapper, dialect = self.dialect)

        row_no = 0
        chunk = []              # list[CsvLog]
        csv_discard = []        # list[CsvLog]
        for row in csv_reader:
            row_no += 1

            # ヘッダー行と空行は読み飛ばすだけ、ログ記録は残さない
            if row_no <= self.header_row_number or not row:
                continue

            csv_log = CsvLog(
                file_name = csv_file.name,
                row_no = row_no,
                row_content = dict(zip(self.get_csv_columns(), row)),
                creator = login_user_name,
                lot_number = lot_number,
            )
            # pylint: disable = attribute-defined-outside-init
            get_modelform_cleaned_data(csv_log)

            if csv_log.log_level in (CsvLog.WARN, CsvLog.ERROR) :
                csv_discard.append(csv_log)
            else:
                add2chunk(csv_log)

            if sum(1 if c.log_level == CsvLog.ERROR else 0 for c in csv_discard) >= self.csv_error_limit:
                # エラー情報をCSVログに記録する
                save_discard()
                raise TooManyInvalidRowsError(csv_file.name, row_no)

            if len(chunk) >= self.chunk_size:
                save_to_database()

        if chunk or csv_discard:
            save_to_database()

        return row_no
