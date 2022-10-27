from typing import Tuple
from django.contrib import admin
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from cmm.admin.base import CommonBaseTableAminMixin, ValidFilter
from mst.models import Customer


class CustomerValidAtFilter(admin.SimpleListFilter):
    """フィルター条件に廃止を追加"""
    def lookups(self, request, model_admin):
        return [('elimination', _('Elimination'))]

    def queryset(self, request, queryset):
        if self.value() is None or self.value() == 'all':
            return super().queryset(request, queryset)

        if self.value() == 'elimination':
            return super().queryset(request, queryset).filter(valid_flag=True)

        return super().queryset(request, queryset).filter(valid_flag=False)

class CustomerAdmin(CommonBaseTableAminMixin, admin.ModelAdmin):
    """AdminSiteでの表示をカスタマイズする"""
    fields = [('name', 'code'), ('abbr', 'old_name'), 'kigo', 'address', 'comment', 'valid_flag']
    list_display = ('abbr', 'code', 'kigo', 'old_name', 'comment', 'valid_flag')
    list_display_links = ['code', 'abbr']
    list_filter = ('kigo', ValidFilter)
    search_fields = ['name', 'code', 'abbr']

    def get_readonly_fields(self, request, obj=None) -> Tuple[str]:
        return super().get_readonly_fields(request, obj) + ('code',) if obj is not None else ()

    def post_import_processing(self, *args, **kwargs):
        Customer.objects.filter(comment__contains='廃止').update(valid_flag=False)
        Customer.objects.filter(Q(name='文部科学省')|Q(name__contains='文化庁')).update(kigo='D')
        Customer.objects.filter(Q(name='筑波技術大学')).update(kigo='A')
        Customer.objects.filter(Q(name='兵庫県立大学')).update(kigo='G')
