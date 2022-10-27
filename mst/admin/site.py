from django.utils.translation import gettext_lazy as _
from django.shortcuts import render
from cmm.utils.adminsite import SuperUserAdminSite
from cmm.const import EXPORT_CSV, EXPORT_EXCEL
from cmm.csv.export import export_excel, export_csv
from cmm.models.base import AuthUser, AuthGroup
from cmm.models import (Category, Code, Organization, OrganizationRel,
                        Person, Shikuchoson, ZipCode, Employee)
from cmm.admin import (AuthGroupAdmin, AuthUserAdmin,
                       CategoryModelAdmin, CodeModelAdmin,
                       OrganizationAdmin, OrganizationRelAdmin,
                       PersonAdmin, ShikuchosonModelAdmin,
                       ZipCodeModelAdmin, EmployeeAdmin)
from mst.admin.ido import (IdoTypeAdmin, IdoSyumokuAdmin, IdoScreenAdmin, IdoColAdmin,
                           IdoSyumokuScreenAdmin)
from mst.models.ido import (IdoType, IdoSyumoku, IdoScreen, IdoCol,
                           IdoSyumokuScreen)


class MasterDataAdminSite(SuperUserAdminSite):
    """ AdminSiteのカスタマイズ"""
    site_title = _('mstSite')
    site_header = _('mstSite')
    # site_url = None

    index_title = _('mstSite')

    def index(self, request, extra_context=None):
        context = {
            **self.each_context(request),
            'title': _('mstSite'),
            'app_list': self.get_app_list(request),
        }

        return render(request, 'cmm/site_index.html', context=context)

# override default admin site
mstSite = MasterDataAdminSite(name='mstSite')

mstSite.add_action(export_csv, EXPORT_CSV)
mstSite.add_action(export_excel, EXPORT_EXCEL)

mstSite.register(AuthUser, AuthUserAdmin)
mstSite.register(AuthGroup, AuthGroupAdmin)
mstSite.register(Category, CategoryModelAdmin)
mstSite.register(Code, CodeModelAdmin)
mstSite.register(Employee, EmployeeAdmin)
mstSite.register(Organization, OrganizationAdmin)
mstSite.register(OrganizationRel, OrganizationRelAdmin)
mstSite.register(Person, PersonAdmin)
mstSite.register(Shikuchoson, ShikuchosonModelAdmin)
mstSite.register(ZipCode, ZipCodeModelAdmin)

mstSite.register(IdoScreen, IdoScreenAdmin)
mstSite.register(IdoType, IdoTypeAdmin)
mstSite.register(IdoCol, IdoColAdmin)
mstSite.register(IdoSyumoku, IdoSyumokuAdmin)
mstSite.register(IdoSyumokuScreen, IdoSyumokuScreenAdmin)
