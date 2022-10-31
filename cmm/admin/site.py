from django.utils.translation import gettext_lazy as _
from django.contrib.auth.admin import GroupAdmin, UserAdmin
from django.shortcuts import render
from cmm.const import EXPORT_CSV, EXPORT_EXCEL
from cmm.csv.export import export_excel, export_csv
from cmm.models.base import AuthUser, AuthGroup
from cmm.csv import ExportAdminMixin, CsvImportAdminMixin
from cmm.models import (Category, Code, Organization, OrganizationRel,
                        Person, Shikuchoson, ZipCode, Employee)
from cmm.utils.adminsite import ActiveUserAdminSite
from cmm.admin import (CategoryModelAdmin, CodeModelAdmin,
                       OrganizationAdmin, OrganizationRelAdmin,
                       PersonAdmin, ShikuchosonModelAdmin,
                       ZipCodeModelAdmin, EmployeeAdmin)


class AuthUserAdmin(ExportAdminMixin, CsvImportAdminMixin, UserAdmin):
    """AdminSiteでの表示をカスタマイズする"""
    # inlines = (EmployeeInline,)

class AuthGroupAdmin(ExportAdminMixin, CsvImportAdminMixin, GroupAdmin):
    """AdminSiteでの表示をカスタマイズする"""

# class cmmAdminSite(admin.AdminSite):
class CmmAdminSite(ActiveUserAdminSite):
    """ AdminSiteのカスタマイズ"""
    site_title = _('cmmSite')
    site_header = _('cmHeader')
    # site_url = None
    index_title = _('cmmIndexTitle')

    def index(self, request, extra_context=None):
        context = {
            **self.each_context(request),
            'title': _('cmmTitle'),
            'app_list': self.get_app_list(request),
        }

        return render(request, 'admin/index.html', context=context)

# override default admin site
cmmSite = CmmAdminSite(name='cmmSite')

cmmSite.add_action(export_csv, EXPORT_CSV)
cmmSite.add_action(export_excel, EXPORT_EXCEL)

cmmSite.register(AuthUser, AuthUserAdmin)
cmmSite.register(AuthGroup, AuthGroupAdmin)
cmmSite.register(Category, CategoryModelAdmin)
cmmSite.register(Code, CodeModelAdmin)
cmmSite.register(Employee, EmployeeAdmin)
cmmSite.register(Organization, OrganizationAdmin)
cmmSite.register(OrganizationRel, OrganizationRelAdmin)
cmmSite.register(Person, PersonAdmin)
cmmSite.register(Shikuchoson, ShikuchosonModelAdmin)
cmmSite.register(ZipCode, ZipCodeModelAdmin)
