from django.utils.translation import gettext_lazy as _
from cmm.utils.adminsite import ActiveUserAdminSite
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


class JinjiAdminSite(ActiveUserAdminSite):
    """ AdminSiteのカスタマイズ"""
    site_title = _('jinji')
    site_header = _('jinji')
    # site_url = None

    index_title = _('jinji')

# override default admin site
jinjiSite = JinjiAdminSite(name='jinji')

jinjiSite.add_action(export_csv, EXPORT_CSV)
jinjiSite.add_action(export_excel, EXPORT_EXCEL)

jinjiSite.register(AuthUser, AuthUserAdmin)
jinjiSite.register(AuthGroup, AuthGroupAdmin)
jinjiSite.register(Category, CategoryModelAdmin)
jinjiSite.register(Code, CodeModelAdmin)
jinjiSite.register(Employee, EmployeeAdmin)
jinjiSite.register(Organization, OrganizationAdmin)
jinjiSite.register(OrganizationRel, OrganizationRelAdmin)
jinjiSite.register(Person, PersonAdmin)
jinjiSite.register(Shikuchoson, ShikuchosonModelAdmin)
jinjiSite.register(ZipCode, ZipCodeModelAdmin)

jinjiSite.register(IdoScreen, IdoScreenAdmin)
jinjiSite.register(IdoType, IdoTypeAdmin)
jinjiSite.register(IdoCol, IdoColAdmin)
jinjiSite.register(IdoSyumoku, IdoSyumokuAdmin)
jinjiSite.register(IdoSyumokuScreen, IdoSyumokuScreenAdmin)
