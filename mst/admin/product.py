from typing import Tuple
from django.contrib import admin
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from cmm.admin.base import CommonBaseTableAminMixin, ValidFilter
from mst.models import Product
from mst.admin import mstSite


class ParentListFilter(admin.SimpleListFilter):
    """上位フィルター、上位一覧を階層的に表示する"""
    title = _('parent')

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'parent_id'

    def lookups(self, request, model_admin):
        """上位リスト"""
        return [(parent.id, parent.name) for parent in Product.objects.filter(parent__isnull=True)]

    def queryset(self, request, queryset):
        """指定した上位で絞る"""
        if self.value() is None:
            return queryset

        return queryset.filter(Q(parent__id=self.value())|Q(id=self.value()))

# @admin.register(Product, site=mstSite)
class ProductAdmin(CommonBaseTableAminMixin, admin.ModelAdmin):
    """AdminSiteでの表示をカスタマイズする"""
    fields = [('name', 'code'), ('abbr', 'parent'), ('product_type', 'display_order'),
              'summary', 'product_ver', 'comment', 'valid_flag']
    list_display = ('parent', 'name', 'product_type', 'product_ver', 'summary', 'valid_flag')

    list_display_links = ['name']
    list_per_page = 100
    search_fields = ['name']
    ordering = ['display_order']
    list_filter = (ParentListFilter, 'product_type', ValidFilter)

    def get_readonly_fields(self, request, obj=None) -> Tuple[str]:
        if obj is None:
            return super().get_readonly_fields(request, obj)
        
        return super().get_readonly_fields(request, obj) + ('parent', 'code', 'product_type')

    def get_exclude(self, request, obj=None):
        if obj is not None:
            return super().get_exclude(request, obj) or () + ('code',)
            
        return super().get_exclude(request, obj)
        
    def get_form(self, request, obj=None, change=False, **kwargs):
        """新規画面ではCodeを表示し、更新画面ではCodeを表示したくない
        1. fieldsを変えると実現可能だが、新規・更新画面切替時にF5でrefreshしないと反映されない...
        2. exclude=('code',)やget_exclude()のoverrideは効かない
        結論：実現不能（JavaScriptなら何とかなるかも）
        """
        # if change:
        #     self.exclude = ('code',)
        return super().get_form(request, obj, **kwargs)
        
    def csv2model(self, csv_dict: dict, *args, **kwargs) -> dict:
        parent = Product.objects.filter(code=csv_dict.get('parent')).first()
        model_dict = super().csv2model(csv_dict, *args, **kwargs)
        model_dict['parent'] = parent

        return model_dict
    
    def post_import_processing(self, *args, **kwargs):
        Product.objects.filter(parent__isnull=True).update(product_type=Product.SYSTEM)
        Product.objects.filter(~Q(parent__isnull=True)).update(product_type=Product.OPTION)
