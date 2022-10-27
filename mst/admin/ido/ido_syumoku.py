from typing import Any, Dict, Tuple

from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.utils.html import format_html

from cmm.admin.base import CommonBaseTableAminMixin, ValidFilter
from cmm.forms import SimpleModelForm
from mst.models import IdoSyumoku, IdoType, get_ido_type_code
from mst.admin.ido import (IdoSyumokuIdoCategoryFilter, 
                           IdoSyumokuScreenInline, IdoSyumokuTeiinHijokinFilter, IdoTypeFilter)


class IdoSyumokuAdmin(CommonBaseTableAminMixin, admin.ModelAdmin):
    """AdminSiteでの表示をカスタマイズする"""
    fields = [('ido_type', 'code', 'nnmn_ido_cde'), ('name', 'display_order', 'valid_flag')]
    list_display = ('teiin_hijokin', 'ido_type', 'name', 'code', 'nnmn_ido_cde', 'display_order', 'valid_flag')

    readonly_fields = ('ido_type', 'code')
    list_display_links = ['name']
    list_per_page = 100
    search_fields = ['name', 'nnmn_ido_cde']
    list_filter = (IdoSyumokuTeiinHijokinFilter, IdoSyumokuIdoCategoryFilter, IdoTypeFilter, ValidFilter)
    
    inlines = [IdoSyumokuScreenInline]

    def render_change_form(self, request, context, add=False, change=False, form_url='', obj=None):
        """Hide "save" button"""
        # pylint: disable=too-many-arguments
        context['show_save'] = False

        return super().render_change_form(request, context, add, change, form_url, obj)

    def get_csv_columns(self) -> Tuple[str]:
        return ('CTEIHIJKB', 'CBUNRUICD', 'CBUNRUINM', 'GRP_SEQ', 'BUTTON_SEQ', 'BUNKI1_SEQ', 'BUNKI2_SEQ'
                ,'name', 'display_order', 'nnmn_ido_cde', 'display_ctl')

    def get_model_fields(self) -> Tuple[str]:
        return ('ido_type', 'name', 'code', 'display_order', 'nnmn_ido_cde', 'display_ctl')

    def csv2model(self, csv_dict: Dict[str, str], *args, **kwargs) -> Dict[str, Any]:
        model_dict = super().csv2model(csv_dict, *args, **kwargs)

        model_dict['ido_type'] = IdoType.objects.filter(code=get_ido_type_code(csv_dict)).first()
        model_dict['code'] = csv_dict.get('GRP_SEQ') + csv_dict.get('BUTTON_SEQ') \
                            + csv_dict.get('BUNKI1_SEQ') + csv_dict.get('BUNKI2_SEQ')

        return model_dict

class IdoSyumokuForm(SimpleModelForm):
    """ModeFormの設定"""
    html_readonly_fields = ('code', 'name', 'nnmn_ido_cde', 'ido_type')

class IdoSyumokuInline(admin.TabularInline):
    """移動種目をインラインで表示する"""
    model = IdoSyumoku
    form = IdoSyumokuForm
    extra = 0
    can_delete = False
    show_change_link = True

    fields = ['code_link', 'code', 'name', 'nnmn_ido_cde', 'ido_type', 'display_order', 'valid_flag']
    readonly_fields = ('code_link',)

    def get_readonly_fields(self, request, obj=None) -> Tuple[str]:
        if obj is None:
            self.extra = 1

        return super().get_readonly_fields(request, obj)

    @admin.display(description=_('異動種目'))
    def code_link(self, instance):
        """所属組織へのリンク"""
        if instance.id is None:
            return ''
        
        site = self.admin_site.name
        opts = instance._meta
        app, model = opts.app_label, opts.model_name
        url = reverse(f'{site}:{app}_{model}_change', args=(instance.id,))
        return format_html('<a href="{}">{}</a>', url, '編集')
