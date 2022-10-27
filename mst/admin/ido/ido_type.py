from typing import Any, Dict, Tuple
from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from cmm.admin.base import CommonBaseTableAminMixin, ValidFilter
from mst.admin import mstSite
from mst.admin.ido import IdoCategoryFilter, TeiinHijokinFilter, IdoSyumokuInline
from mst.models.ido import IdoType, get_ido_type_code

@admin.register(IdoType, site=mstSite)
class IdoTypeAdmin(CommonBaseTableAminMixin, admin.ModelAdmin):
    """AdminSiteでの表示をカスタマイズする"""
    fields = [('name', 'code', 'display_order','valid_flag')]
    list_display = ('teiin_hijokin', 'name', 'disp_order', 'valid_flag')

    list_display_links = ['name']
    list_per_page = 100
    search_fields = ['name']
    list_filter = (TeiinHijokinFilter, IdoCategoryFilter, ValidFilter,)
    
    inlines = (IdoSyumokuInline,)
    
    def get_readonly_fields(self, request, obj=None) -> Tuple[str]:
        if obj is None:
            return super().get_readonly_fields(request, obj)
        
        return super().get_readonly_fields(request, obj) + ('code', )

    @admin.display(description=_('display order'))
    def disp_order(self, obj) -> str:
        """show without thousand separator"""
        return str(obj.display_order)
    
    def get_csv_columns(self) -> Tuple[str]:
        return ('CTEIHIJKB', 'CBUNRUICD', 'name', 'GRP_SEQ', 'display_order')
        
    def get_model_fields(self) -> Tuple[str]:
        return ('name', 'code', 'display_order')

    def csv2model(self, csv_dict: Dict[str, str], *args, **kwargs) -> Dict[str, Any]:
        model_dict = super().csv2model(csv_dict, *args, **kwargs)

        model_dict['code'] = get_ido_type_code(csv_dict)
        return model_dict
