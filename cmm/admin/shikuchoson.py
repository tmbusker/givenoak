from typing import Tuple
from django.contrib import admin
from cmm.const import SJIS, EXCEL_FILE_EXT
from cmm.models import Shikuchoson
from cmm.admin.base import CommonBaseTableAminMixin, ValidFilter
from cmm.admin import cmmSite

@admin.register(Shikuchoson, site=cmmSite)
class ShikuchosonModelAdmin(CommonBaseTableAminMixin, admin.ModelAdmin):
    """市区町村をAdminSiteに表示する"""
    fields = ['code', ('pref_name', 'pref_name_kana'), ('name', 'name_kana'), 'valid_flag']
    list_display = ('code', 'pref_name', 'pref_name_kana', 'name', 'name_kana', 'valid_flag')
    list_display_links = ['code', 'name']
    list_per_page = 100
    search_fields = ['pref_name', 'name']
    list_filter = ('pref_name', ValidFilter)

    # is_bulk_insert = True
    is_replace_existing = False

    def get_readonly_fields(self, request, obj=None) -> Tuple[str]:
        return (*super().get_readonly_fields(request, obj), 'code' if obj is not None else None)

    def get_csv_columns(self) -> Tuple[str]:
        return ('code', 'pref_name', 'name', 'pref_name_kana', 'name_kana')

    def csv2model(self, csv_dict: dict, *args, **kwargs) -> dict:
        # 市区町村コードは5桁となる（CSVファイルは６桁、最後の桁は確認用）
        csv_dict['code'] = csv_dict['code'][0:5]
        model_dict = super().csv2model(csv_dict, *args, **kwargs)

        return model_dict
