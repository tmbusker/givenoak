from django.contrib import admin
from cmm.admin.base import CommonBaseTableAminMixin, ValidFilter
from mst.models import ProjectProduct, Project
from mst.admin import mstSite


class ProjectProductInline(admin.TabularInline):
    """プロジェクト関連製品をインラインで表示する"""
    model = ProjectProduct
    extra = 1

    fields = ['project', 'product', 'comment']
    search_fields = ['product']

    # ※参考 検索フィールド＋Select Box
    autocomplete_fields = ['product']

# @admin.register(Project, site=mstSite)
class ProjectAdmin(CommonBaseTableAminMixin, admin.ModelAdmin):
    """AdminSiteでの表示をカスタマイズする"""
    fields = [('name', 'code'), 'customer', 'valid_flag']
    list_display = ('name', 'code', 'customer', 'valid_flag')
    list_display_links = ['code', 'name']
    list_filter = ('customer', ValidFilter)
    search_fields = ['name', 'code', 'customer']

    inlines = (ProjectProductInline,)
