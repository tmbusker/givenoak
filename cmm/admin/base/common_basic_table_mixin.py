from django.utils import timezone
from cmm.csv import CsvImportAdminMixin, ExportAdminMixin, CsvImportMixin

from cmm.admin.base import SimpleTableAminMixin


class CommonBaseTableAminMixin(SimpleTableAminMixin, ExportAdminMixin, CsvImportAdminMixin, CsvImportMixin):
    """Csv export, import可能なHistoryTableのAdminMixin"""

    def pre_import_processing(self, *args, **kwargs):
        # pylint: disable = protected-access
        # 初回取込時のデフォルト基準日を指定
        self.model._history_date = timezone.now()
