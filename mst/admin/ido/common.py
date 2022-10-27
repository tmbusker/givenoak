from django.utils.translation import gettext_lazy as _
from cmm.admin.base.filter import CommonFilter
from mst.const import IDO_CATEGORIES, TEIIN_HIJOKIN_CHOICES
from mst.models.ido.ido_type import IdoType


class TeiinHijokinFilter(CommonFilter):
    """定員・非常勤フィルター"""
    title = _('定員・非常勤')
    parameter_name = 'teiin_hijokin'

    def lookups(self, request, model_admin):
        return [('all', _('All')), *TEIIN_HIJOKIN_CHOICES]

    def queryset(self, request, queryset):
        if self.value() is not None and self.value() != 'all':
            return queryset.filter(code__startswith=self.value())

        return queryset

class IdoSyumokuTeiinHijokinFilter(TeiinHijokinFilter):
    """異動種目画面の定員・非常勤フィルター"""
    def queryset(self, request, queryset):
        if self.value() is not None and self.value() != 'all':
            return queryset.filter(ido_type__code__startswith=self.value())

        return queryset

class IdoCategoryFilter(CommonFilter):
    """異動カテゴリフィルター"""
    title = _('異動カテゴリ')
    parameter_name = 'ido_category'

    def lookups(self, request, model_admin):
        return [('all', _('All'))] + [(key, key) for key in IDO_CATEGORIES]

    def queryset(self, request, queryset):
        if self.value() is not None and self.value() != 'all':
            return queryset.filter(code__in=IDO_CATEGORIES.get(self.value()))

        return queryset

class IdoTypeFilter(CommonFilter):
    """異動カテゴリフィルター"""
    title = _('異動分類')
    parameter_name = 'ido_type'

    def lookups(self, request, model_admin):
        teiin_hijokin = request.GET.get('teiin_hijokin')
        ido_category = request.GET.get('ido_category')
        ido_type_queryset = IdoType.objects.all()
        if teiin_hijokin is not None:
            ido_type_queryset = ido_type_queryset.filter(code__startswith=teiin_hijokin)
        if ido_category is not None:
            ido_type_queryset = ido_type_queryset.filter(code__in=IDO_CATEGORIES.get(ido_category))
        return [('all', _('All'))] + list(ido_type_queryset.values_list('code', 'name'))

    def queryset(self, request, queryset):
        if self.value() is not None and self.value() != 'all':
            return queryset.filter(ido_type__code=self.value())

        return queryset

class IdoSyumokuIdoCategoryFilter(IdoCategoryFilter):
    """異動種目画面の異動カテゴリフィルター"""
    def queryset(self, request, queryset):
        if self.value() is not None and self.value() != 'all':
            return queryset.filter(ido_type__code__in=IDO_CATEGORIES.get(self.value()))

        return queryset
