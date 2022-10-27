from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from cmm.forms import SimpleModelForm
from cmm.admin.base import CommonBaseTableAminMixin
from mst.admin.ido import IdoSyumokuScreenColAdmin
from mst.models.ido import IdoSyumokuScreen


class IdoSyumokuScreenForm(SimpleModelForm):
    """異動種目で異動項目をインライン表示"""
    html_readonly_fields = ('ido_syumoku', 'ido_screen', )

class IdoSyumokuScreenInline(admin.TabularInline):
    """所属組織をインラインで表示する"""
    model = IdoSyumokuScreen
    form = IdoSyumokuScreenForm
    extra = 0
    # max_num = 0
    # can_delete = False

    fields = ['ido_screen_link', 'ido_syumoku', 'ido_screen']
    readonly_fields = ('ido_screen_link', )

    def get_queryset(self, request):
        """所属に絞る"""
        object_id = request.resolver_match.kwargs.get('object_id')
        return IdoSyumokuScreen.objects.filter(ido_syumoku_id=object_id, valid_flag=True)

    @admin.display(description=_('異動入力画面'))
    def ido_screen_link(self, instance):
        """異動項目へのリンク"""
        site = self.admin_site.name
        opts = instance._meta
        app, model = opts.app_label, opts.model_name
        url = reverse(f'{site}:{app}_{model}_change', args=(instance.id,))
        return format_html('<a href="{}">{}</a>', url, instance.ido_screen.screen_code)

class IdoSyumokuScreenAdmin(CommonBaseTableAminMixin, admin.ModelAdmin):
    """異動種目ごとの入力画面"""
    form = IdoSyumokuScreenForm
    fields = ['ido_syumoku', 'ido_screen']

    inlines = [IdoSyumokuScreenColAdmin]

    def render_change_form(self, request, context, add=False, change=False, form_url='', obj=None):
        """Hide "save" button"""
        # pylint: disable=too-many-arguments
        context['show_save'] = False

        return super().render_change_form(request, context, add, change, form_url, obj)
