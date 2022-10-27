import logging
import itertools
from django.utils import timezone
from simple_history.models import HistoricalRecords
from cmm.models.base import SimpleTable, VersionedTable


_logger = logging.getLogger(__name__)

class CommonBaseTable(SimpleTable):
    """共通ベーステーブル"""
    history = HistoricalRecords(inherit=True, )
    __history_date = timezone.now()

    class Meta:
        abstract = True

    def has_same_contents(self, obj) -> bool:
        """作成者、作成日時、更新者、更新日時、バージョン番号など補助項目以外で変更有無を判断する、保存有無の判定に使う"""
        # pylint: disable = no-member
        inherited_fields = list(itertools.chain(SimpleTable._meta.fields,VersionedTable._meta.fields))
        exclude_fields = ['id'] + [f.name for f in inherited_fields]
        # 有効フラグが変更されたら、変更ありとみなす
        exclude_fields.remove('valid_flag')
        return all(getattr(self, f.name, None) == getattr(obj, f.name, None) \
                    for f in self._meta.fields if f.name not in exclude_fields)

    def save(self, *args, **kwargs):
        """CSV import処理より呼び出された場合は、変更有無の判定が必要。ModelAdmin継承画面なら不要。"""
        # self._history_date = timezone.now()
        same_record = self.retrieve_by_unique_key()

        # pylint: disable = attribute-defined-outside-init, invalid-name
        if same_record is not None:
            # 変更がない場合は保存処理をスキップする
            if self.has_same_contents(same_record):
                _logger.debug("Skip to save the contents because no change was detected on %s.", self)
                return
            
            self.id = same_record.id
            self._state.adding = False

        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs) -> None:
        # self._history_date = timezone.now()
        super().delete(*args, **kwargs)

    @property
    def _history_date(self):
        return self.__history_date

    @_history_date.setter
    def _history_date(self, value):
        self.__history_date = value
