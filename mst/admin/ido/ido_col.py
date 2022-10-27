from typing import Tuple
from django.contrib import admin
from cmm.admin.base import CommonBaseTableAminMixin


class IdoColAdmin(CommonBaseTableAminMixin, admin.ModelAdmin):
    """AdminSiteでの表示をカスタマイズする"""

    fields = [('teiin_hijokin', 'table_id'), ('col_id', 'col_name'), ('col_no', 'valid_flag')]
    list_display = ('teiin_hijokin', 'table_id', 'col_id', 'col_name', 'col_no')

    list_display_links = ['col_name']
    list_per_page = 100
    search_fields = ['table_id', 'col_id', 'col_name', 'col_no']
    ordering = ['teiin_hijokin', 'col_no']
    list_filter = ('teiin_hijokin', 'table_id')
    readonly_field = ('teiin_hijokin', 'table_id', 'col_id', 'col_name', 'col_no')
    
    def get_csv_columns(self) -> Tuple[str]:
        return ('teiin_hijokin', 'table_id', 'col_id', 'col_name', 'col_no')
