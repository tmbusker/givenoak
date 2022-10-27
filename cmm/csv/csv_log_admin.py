from django.contrib import admin

from cmm.admin import cmmSite
from cmm.csv import CsvLog
from cmm.csv import ExportAdminMixin



@admin.register(CsvLog, site=cmmSite)
class CsvLogModelAdmin(ExportAdminMixin, admin.ModelAdmin):
    """CSV import, exportのログをAdminSiteに表示する"""
    list_display = ('creator', 'create_time', 'log_type', 'log_level', 'file_name',
                    'row_no', 'row_content', 'message')

    list_display_links = None       # remove the link to the model's edit view
    list_per_page = 20
    search_fields = ['creator', 'create_time', 'log_type', 'log_level', 'file_name']
    list_filter = ('file_name', 'creator', 'create_time', 'log_type', 'log_level')

    def has_add_permission(self, request, obj=None):
        '''hide the add button'''
        # pylint: disable = unused-argument
        return False
