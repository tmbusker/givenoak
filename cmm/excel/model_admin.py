import logging
from cmm.csv import ImportAdminMixin


_logger = logging.getLogger(__name__)

class ExcelImportAdminMixin(ImportAdminMixin):
    """Excelファイル読み込み"""
