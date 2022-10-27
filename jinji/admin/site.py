from django.utils.translation import gettext_lazy as _
from django.shortcuts import render
from cmm.utils.adminsite import SuperUserAdminSite


class JinjiAdminSite(SuperUserAdminSite):
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

        return render(request, 'cmm/site_index.html', context=context)

# override default admin site
jinji = JinjiAdminSite(name='jinji')
