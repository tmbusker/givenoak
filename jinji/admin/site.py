from django.utils.translation import gettext_lazy as _
from django.shortcuts import render
from cmm.utils.adminsite import ActiveUserAdminSite
from cmm.const import EXPORT_CSV, EXPORT_EXCEL
from cmm.csv.export import export_excel, export_csv
from cmm.models.base import AuthUser, AuthGroup
from cmm.models import (Category, Code, Organization, OrganizationRel, Employee)
from cmm.admin import (AuthGroupAdmin, AuthUserAdmin,
                       CategoryModelAdmin, CodeModelAdmin,
                       OrganizationAdmin, OrganizationRelAdmin, EmployeeAdmin)
from mst.admin.ido import (IdoTypeAdmin, IdoSyumokuAdmin, IdoScreenAdmin, IdoColAdmin,
                           IdoSyumokuScreenAdmin)
from mst.models.ido import (IdoType, IdoSyumoku, IdoScreen, IdoCol, IdoSyumokuScreen)
from jinji.models import Dkido
from jinji.admin.ido.dkido import DkidoAdmin


class JinjiAdminSite(ActiveUserAdminSite):
    """ AdminSiteのカスタマイズ"""
    site_title = _('jinji')
    site_header = _('jinji')
    # site_url = None

    index_title = _('jinji')

    def index(self, request, extra_context=None):
        context = {
            **self.each_context(request),
            'title': _('jinji'),
            'app_list': self.get_app_list(request),
        }

        return render(request, 'admin/index.html', context=context)

# override default admin site
jinjiSite = JinjiAdminSite(name='jinji')

jinjiSite.add_action(export_csv, EXPORT_CSV)
jinjiSite.add_action(export_excel, EXPORT_EXCEL)

# cmm
jinjiSite.register(AuthUser, AuthUserAdmin)
jinjiSite.register(AuthGroup, AuthGroupAdmin)
jinjiSite.register(Category, CategoryModelAdmin)
jinjiSite.register(Code, CodeModelAdmin)
jinjiSite.register(Employee, EmployeeAdmin)
jinjiSite.register(Organization, OrganizationAdmin)
jinjiSite.register(OrganizationRel, OrganizationRelAdmin)

# mst
jinjiSite.register(IdoScreen, IdoScreenAdmin)
jinjiSite.register(IdoType, IdoTypeAdmin)
jinjiSite.register(IdoCol, IdoColAdmin)
jinjiSite.register(IdoSyumoku, IdoSyumokuAdmin)
jinjiSite.register(IdoSyumokuScreen, IdoSyumokuScreenAdmin)

# jinji
jinjiSite.register(Dkido, DkidoAdmin)
