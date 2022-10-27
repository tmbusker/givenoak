from django.contrib import admin
from cmm.admin.base import CommonBaseTableAminMixin
from jinji.admin import jinji
from jinji.models.ido import Dkido


@admin.register(Dkido, site=jinji)
class DkidoAdmin(CommonBaseTableAminMixin, admin.ModelAdmin):
    """AdminSiteでの表示をカスタマイズする"""

    fields = ['ido_syumoku', ('cshainno', 'cnamekna', 'cnameknj'),]
    list_display = ('ido_syumoku', 'cshainno', 'cnameknj',)

    list_display_links = ['ido_syumoku']
    list_per_page = 100
