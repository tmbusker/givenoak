from typing import Any, Dict, Tuple
from django.contrib.admin import register, ModelAdmin, TabularInline
from django.http.request import HttpRequest
from django.utils.translation import gettext_lazy as _
from cmm.admin.base import CommonBaseTableAminMixin, ValidFilter, CommonFilter
from cmm.forms import SimpleModelForm
from cmm.models import Category, Code


class CodeForm(SimpleModelForm):
    """ModeFormの設定"""
    html_readonly_fields = ['code']

class CodeInline(TabularInline):
    """コードをインラインで表示する"""
    model = Code
    form = CodeForm
    extra = 0

    fields = ['code', 'name', 'abbr', 'display_order', 'valid_flag']
    ordering = ['display_order']

    def get_readonly_fields(self, request, obj=None) -> Tuple[str]:
        read_only = ()
        if obj is None:
            self.extra = 1
        return super().get_readonly_fields(request, obj) + read_only

    def get_queryset(self, request):
        """コード種別で絞る"""
        object_id = request.resolver_match.kwargs.get('object_id')
        category = Category.objects.filter(id=object_id).first()
        if category is None:
            return super().get_queryset(request)
        
        return Code.objects.filter(category=category)

class CategoryFilter(CommonFilter):
    """Category一覧画面のCategoryコードフィルター"""
    title = _('category')
    parameter_name = 'category'

    def lookups(self, request, model_admin):
        return [('all', _('All'))] + list(Category.objects.order_by('category').distinct('category') \
                    .values_list('category', 'name'))

    def queryset(self, request, queryset):
        if self.value() is None or self.value() == 'all':
            return queryset

        return queryset.filter(category=self.value())

class CategoryForm(SimpleModelForm):
    """ModeFormの設定"""
    html_readonly_fields = ('category',)


class CategoryModelAdmin(CommonBaseTableAminMixin, ModelAdmin):
    """CategoryをadminSiteに表示する"""
    form = CategoryForm
    
    fields = [('category', 'name'), 'valid_flag']
    list_display = ('category', 'name', 'valid_flag')
    search_fields = ['category', 'name']
    list_filter = (CategoryFilter, ValidFilter)
    ordering = ['category']

    inlines = (CodeInline,)

    def get_csv_columns(self) -> Tuple[str]:
        """CSVファイルの列名定義"""
        return ('category', 'name', 'valid_flag')

class CodeCategoryFilter(CategoryFilter):
    """Code一覧画面のCategoryコードフィルター"""
    def queryset(self, request, queryset):
        if self.value() is None or self.value() == 'all':
            return queryset

        return queryset.filter(category__category=self.value())

class CodeModelAdmin(CommonBaseTableAminMixin, ModelAdmin):
    """CodeをadminSiteに表示する"""
    fields = ['category', ('code', 'name', 'abbr', 'display_order'), 'valid_flag']
    list_display = ('category', 'code', 'name', 'abbr', 'display_order', 'valid_flag')
    search_fields = ['category', 'name', 'abbr']
    list_display_links = None
    list_filter = (CodeCategoryFilter, ValidFilter)
    ordering = ['category', 'display_order']

    def get_readonly_fields(self, request, obj=None) -> Tuple[str]:
        read_only = ('category', 'code')
        return super().get_readonly_fields(request, obj) + read_only if obj is not None else ()

    def has_add_permission(self, request: HttpRequest) -> bool:
        return False

    def get_csv_columns(self) -> Tuple[str]:
        """CSVファイルの列名定義"""
        return ('category__category', 'code', 'name', 'abbr', 'display_order', 'valid_flag')

    def get_model_fields(self) -> Tuple[str]:
        return ('category', 'code', 'name', 'abbr', 'display_order', 'valid_flag')

    def csv2model(self, csv_dict: Dict[str, str], *args, **kwargs) -> Dict[str, Any]:
        model_dict = super().csv2model(csv_dict, *args, **kwargs)
        model_dict['category'] = Category.objects.filter(category=csv_dict['category__category']).first()
        return model_dict

    # def has_delete_permission(self, request: HttpRequest, obj=None) -> bool:
    #     """InlineでCodeを表示しても削除時にはここで権限有無を確認する"""
    #     return False
