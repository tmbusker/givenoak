from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.shortcuts import render
from django.contrib.auth.admin import GroupAdmin, UserAdmin
from cmm.const import EXPORT_CSV, EXPORT_EXCEL
from cmm.csv.export import export_excel, export_csv
from cmm.models.base import AuthUser, AuthGroup
from cmm.csv import ExportAdminMixin, CsvImportAdminMixin
from cmm.utils.adminsite import ActiveUserAdminSite


# class cmmAdminSite(admin.AdminSite):
class CmmAdminSite(ActiveUserAdminSite):
    """ AdminSiteのカスタマイズ"""
    site_title = _('cmm')
    site_header = _('cmm')
    # site_url = None

    index_title = _('cmm')

    def index(self, request, extra_context=None):
        """サイトの初期表示画面"""
        context = {
            **self.each_context(request),
            'title': _('cmm'),
            'app_list': self.get_app_list(request),
        }

        return render(request, 'cmm/site_index.html', context=context)

# override default admin site
cmmSite = CmmAdminSite(name='cmmSite')
cmmSite.add_action(export_csv, EXPORT_CSV)
cmmSite.add_action(export_excel, EXPORT_EXCEL)

@admin.register(AuthUser, site=cmmSite)
class AuthUserAdmin(ExportAdminMixin, CsvImportAdminMixin, UserAdmin):
    """AdminSiteでの表示をカスタマイズする"""
    # inlines = (EmployeeInline,)

@admin.register(AuthGroup, site=cmmSite)
class AuthGroupAdmin(ExportAdminMixin, CsvImportAdminMixin, GroupAdmin):
    """AdminSiteでの表示をカスタマイズする"""
