import csv
import io
import logging
import math
from typing import Any, Dict, List, Set, Tuple
from django.utils.translation import gettext_lazy as _
from django.contrib.admin.utils import flatten
from django.forms import modelform_factory
from django.db import transaction
from django.utils import timezone
from cmm.const import UTF8
from cmm.utils.modelform import get_modelform_non_unique_error_codes, get_modelform_error_messages
from cmm.models.base import UniqueConstraintMixin, VersionedTable, HistoryTable
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

class CsvImportMixin:
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
    water_mark = 10                 # エラーとなった割合(%)がこの上限を超えたら処理を中断する。

    is_duplicate_available = False  # 重複容認ポリシー、ユニーク制限がある場合は無視される。
                                    # True: 重複行がインポートされる、False: 重複ポリシーに従う
    is_update_existing = True       # 重複処理ポリシー、True:取込データ優先、False:既存データ優先

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
        
        return {}

    def pre_import_processing(self, *args, **kwargs):
        """CSV importの前処理"""

    def post_import_processing(self, *args, **kwargs):
        """CSV importの後処理"""

    def save_imported_data(self, chunk: List[CsvLog]) -> List[CsvLog]:
        """ modelformのsave"""
        for csv_log in chunk:
            self.model(**csv_log.modelform.cleaned_data).save()

    def __is_resolve_duplicate(self):
        """重複チェックの実施有無。"""
        if self.is_duplicate_available:
            return False
        
        if issubclass(self.model, UniqueConstraintMixin):
            return True
        
        return False             # 重複チェックなし、重複行はそのままインポートされる

    def __get_modelform_class(self):
        """Dynamically generate ModelForm class"""
        def disable_formfield(db_field, **kwargs):
            form_field = db_field.formfield(**kwargs)
            if form_field:
                form_field.widget.attrs['disabled'] = 'true'
            return form_field

        form_fields = list(set(self.get_model_fields() + tuple(k for k in self.get_default_values())))
        return modelform_factory(self.model, fields = form_fields, formfield_callback = disable_formfield)

    def __validate_by_modelform(self, csv_log: CsvLog):
        """ModelFormの入力チェックを実施"""
        modelform = self.__get_modelform_class()(self.csv2model(csv_log.row_content))

        if modelform.is_valid():
            csv_log.log_level = CsvLog.INFO
            csv_log.message = _('Newly imported row.')
            csv_log.modelform = modelform
        else:
            non_unique_error_codes = get_modelform_non_unique_error_codes(modelform)
            if not non_unique_error_codes:      # only unique violation
                if self.is_update_existing:
                    csv_log.message = _("Update existing row.")
                    csv_log.log_level = CsvLog.INFO
                    csv_log.edit_type = CsvLog.UPDATE
                    modelform.cleaned_data = modelform.data
                    csv_log.modelform = modelform
                else:
                    csv_log.log_level = CsvLog.WARN     # DBと重複したのでスキップする
                    csv_log.message = get_modelform_error_messages(modelform)
            elif non_unique_error_codes.issubset(self.get_skippable_errors(modelform)):
                csv_log.log_level = CsvLog.WARN
                csv_log.message = get_modelform_error_messages(modelform)
            else:
                csv_log.log_level = CsvLog.ERROR
                csv_log.message = get_modelform_error_messages(modelform)
        
        return csv_log
        
    def __is_too_many_errors(self, error_cnt: int) -> bool:
        error_limit = math.floor(self.chunk_size * self.water_mark / 100)
        return error_cnt > error_limit

    def __get_duplicated(self, csv_log: CsvLog, chunk: List[CsvLog]) -> CsvLog:
        """chunk内での重複行を取得する"""
        if issubclass(self.model, UniqueConstraintMixin) and hasattr(csv_log, 'model_form'):
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

    def __resolve_duplication(self, csv_log: CsvLog, chunk: List[CsvLog]) -> None:
        """chunkに重複行がなければそのまま追加、あれば入れ替え。"""
        duplicated = self.__get_duplicated(csv_log, chunk)
        if duplicated is None:
            return

        if self.is_replace_existing:            # 後発優先の場合、元の行をスキップし、現在行をDB反映候補とする
            duplicated.log_level = CsvLog.WARN
            duplicated.message = _('Duplicated with another row.[row no: %(row_no)s.]') \
                                    % {"row_no": csv_log.row_no}
        else:                                   # 先発優先：現在行をスキップする
            csv_log.log_level = CsvLog.WARN
            csv_log.message = _('Duplicated with another row.[row no: %(row_no)s.]') \
                                    % {"row_no": duplicated.row_no}

    @transaction.atomic
    def __save(self, chunk) -> None:
        """DB保存処理"""
        imported_data = []

        update_time = timezone.now()
        for csv_log in chunk:
            if csv_log.log_level == CsvLog.INFO:
                csv_log.modelform.cleaned_data['updater'] = csv_log.creator
                csv_log.modelform.cleaned_data['creator'] = csv_log.creator
                csv_log.modelform.cleaned_data['update_time'] = update_time
                csv_log.modelform.cleaned_data['create_time'] = update_time
                if issubclass(self.model, VersionedTable):
                    csv_log.modelform.cleaned_data['version'] = 1
                imported_data.append(csv_log)

        # 正常データをインポート先Tableに保存
        self.save_imported_data(imported_data)
        
        if self.is_save_log2database and imported_data:
            # 正常取り込みもlogテーブルに記録する
            self.__save_csv_logs(imported_data)
            _logger.info('We have imported %s data into %s.', len(imported_data),
                         self.model._meta.verbose_name)

        skipped_data = [csv_log for csv_log in chunk if csv_log.log_level == CsvLog.WARN]
        if skipped_data:
            self.__save_csv_logs(skipped_data)
            _logger.info('We have skipped %s rows when importing csv file.', len(skipped_data))
        
        discarded_data = [csv_log for csv_log in chunk if csv_log.log_level == CsvLog.ERROR]
        if discarded_data:
            self.__save_csv_logs(discarded_data)
            _logger.info('We have discarded %s rows when importing csv file.', len(discarded_data))
        
    def __save_csv_logs(self, chunk: List[CsvLog]) -> None:
        """インポートログ情報をDBに記録する"""
        CsvLog.objects.bulk_create([csv_log.convert_content2json() for csv_log in chunk])
    
    def read_csv_file(self, csv_file, login_user_name: str, lot_number: str) -> int:
        """CSVファイルの読み込み処理
            性能を考慮してchunkごとに読み込んでDBに保存する
        """
        text_wrapper = io.TextIOWrapper(csv_file, encoding = self.encoding)
        csv_reader = csv.reader(text_wrapper, dialect = self.dialect)

        row_no = 0
        chunk = []              # list[CsvLog]
        error_cnt = 0
        for row in csv_reader:
            row_no += 1

            # ヘッダー行と空行は読み飛ばすだけ、ログ記録は残さない
            if row_no <= self.header_row_number or not row:
                continue

            csv_log = CsvLog(file_name = csv_file.name,
                             row_no = row_no,
                             row_content = dict(zip(self.get_csv_columns(), row)),
                             creator = login_user_name,
                             lot_number = lot_number)
            
            self.__validate_by_modelform(csv_log)
            if self.__is_resolve_duplicate():
                self.__resolve_duplication(csv_log, chunk)
            chunk.append(csv_log)

            if csv_log.log_level == CsvLog.ERROR:
                error_cnt += 1
                if self.__is_too_many_errors(error_cnt):
                    self.__save_csv_logs(chunk)
                    break
        
            if len(chunk) >= self.chunk_size:
                self.__save(chunk)
                chunk.clear()
        else:
            if chunk:
                self.__save(chunk)

        return row_no

class CsvBulkImportMixin(CsvImportMixin):
    """DBにbulk insertする、既存DBレコードの上書きは不可"""
    is_update_existing = False
    
    def save_imported_data(self, chunk: List[CsvLog]) -> List[CsvLog]:
        self.model.objects.bulk_create(self.model(**c.modelform.cleaned_data) for c in chunk)
