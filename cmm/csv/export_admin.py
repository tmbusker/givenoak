import logging
from typing import Any, Dict, Tuple
from cmm.const import EXPORT_CSV, EXCEL_FILE_EXT, EXPORT_EXCEL, UTF8, CSV_FILE_EXT


_logger = logging.getLogger(__name__)

class ExportAdminMixin:
    """Export処理のベースクラス"""

    csv_export = True
    csv_encoding = UTF8
    csv_file_extension = CSV_FILE_EXT
    
    excel_export = True
    excel_file_extension = EXCEL_FILE_EXT
    
    def get_export_titles(self) -> Tuple[str]:
        """CSVファイルのタイトル行（第一行）を出力する"""
        if hasattr(self, 'get_csv_columns'):
            return self.get_csv_columns()
        return ()

    def model2csv(self, model: Dict[str, Any]) -> Dict[str, Any]:
        """デフォルトでは同名項目を転送"""
        return {k:v for (k,v) in model.items() if k in self.get_csv_columns()}

    def get_actions(self, request):
        """Django admin list viewのアクションリストを取得する（アクションのプルダウンリスト）"""
        actions = super().get_actions(request)
        # pylint: disable = protected-access
        opts = self.model._meta
        if not request.user.has_perm(f'{opts.app_label}.{EXPORT_CSV}_{opts.model_name}'):
            for action in [EXPORT_CSV, EXPORT_EXCEL]:
                if action in actions:
                    del actions[action]
        else:
            if not self.csv_export and EXPORT_CSV in actions:
                del actions[EXPORT_CSV]
            elif not self.excel_export and EXPORT_EXCEL in actions:
                del actions[EXPORT_EXCEL]

        return actions
