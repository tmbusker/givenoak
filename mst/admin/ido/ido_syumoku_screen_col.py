
from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from cmm.forms import SimpleModelForm
from mst.models.ido import IdoSyumokuScreenCol


class IdoSyumokuScreenColForm(SimpleModelForm):
    """異動種目で異動項目をインライン表示"""
    html_readonly_fields = ('ido_col', )

class IdoSyumokuScreenColAdmin(admin.TabularInline):
    """所属組織をインラインで表示する"""
    model = IdoSyumokuScreenCol
    form = IdoSyumokuScreenColForm
    extra = 0
    # max_num = 0
    # can_delete = False

    fields = ['ido_col_link', 'ido_col', 'edit_type']
    readonly_fields = ('ido_col_link', )
    autocomplete_fields = ['ido_col']

    def get_queryset(self, request):
        """所属に絞る"""
        object_id = request.resolver_match.kwargs.get('object_id')
        return IdoSyumokuScreenCol.objects.filter(ido_syumoku_screen_id=object_id, valid_flag=True)

    @admin.display(description=_('異動項目コード'))
    def ido_col_link(self, instance):
        """異動項目へのリンク"""
        site = self.admin_site.name
        opts = instance.ido_col.__class__._meta
        app, model = opts.app_label, opts.model_name
        url = reverse(f'{site}:{app}_{model}_change', args=(instance.ido_col.id,))
        return format_html('<a href="{}">{}</a>', url, instance.ido_col.col_id)
