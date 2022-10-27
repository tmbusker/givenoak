from django.utils import timezone
from cmm.csv import CsvImportAdminMixin, ExportAdminMixin
from cmm.admin.base import SimpleTableAminMixin


class CommonBaseTableAminMixin(SimpleTableAminMixin, ExportAdminMixin, CsvImportAdminMixin):
    """Csv export, import可能なHistoryTableのAdminMixin"""
    prev_url = None

    def pre_import_processing(self, *args, **kwargs):
        # pylint: disable = protected-access
        # 初回取込時のデフォルト基準日を指定
        self.model._history_date = timezone.now()
