from django.utils.translation import gettext_lazy as _
from django.shortcuts import render
from cmm.utils.adminsite import SuperUserAdminSite


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
