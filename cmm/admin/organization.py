from typing import Any, Dict, Tuple
from django.contrib import admin
from django.http.request import HttpRequest
from django.db.models.query import QuerySet, F
from django.urls import reverse
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from cmm.admin.base import CommonBaseTableAminMixin, ValidFilter
from cmm.forms import SimpleModelForm
from cmm.models import Organization, Code, get_all_upper_organizations
from cmm.models.organization_rel import OrganizationRel
from mst.admin import mstSite


class ChildOrgForm(SimpleModelForm):
    """所属組織をインラインで表示する"""
    html_readonly_fields = ('org', )

class ChildOrganizationInline(admin.TabularInline):
    """所属組織をインラインで表示する"""
    model = OrganizationRel
    form = ChildOrgForm
    fk_name = 'parent'
    extra = 0
    # max_num = 0
    # can_delete = False

    fields = ['code_link', 'org', 'rank_name']
    readonly_fields = ('rank_name', 'code_link')
    autocomplete_fields = ['org']

    def get_queryset(self, request):
        """所属に絞る"""
        organization_id = request.resolver_match.kwargs.get('object_id')
        return OrganizationRel.objects.filter(parent_id=organization_id, valid_flag=True)

    @admin.display(description=_('organization code'))
    def code_link(self, instance):
        """所属組織へのリンク"""
        site = self.admin_site.name
        opts = instance.org.__class__._meta
        app, model = opts.app_label, opts.model_name
        url = reverse(f'{site}:{app}_{model}_change', args=(instance.org.id,))
        return format_html('<a href="{}">{}</a>', url, instance.org.code)
    
    @admin.display(description=_('rank'))
    def rank_name(self, instance):
        """name of as rank"""
        return instance.org.rank.name

class ParentOrganizationListFilter(admin.SimpleListFilter):
    """組織一覧画面の上位組織フィルター、上位組織一覧を階層的に表示する"""
    title = _('parent organization')

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'parent_org_id'

    def lookups(self, request, model_admin):
        """上位組織リスト"""
        upper_organizations = get_all_upper_organizations()
        return [(org.id, '|' + '-'*int(org.rank.code) + org.abbr) for org in upper_organizations]

    def queryset(self, request, queryset):
        """指定した上位組織で絞る"""
        if self.value() is None:
            return queryset

        return queryset.filter(child__parent_id=self.value())

@admin.register(Organization, site=mstSite)
class OrganizationAdmin(CommonBaseTableAminMixin, admin.ModelAdmin):
    """AdminSiteでの表示をカスタマイズする"""
    fields = [('name', 'code', 'abbr'), ('rank', 'valid_flag')]
    list_display = ( 'abbr', 'code', 'rank', 'valid_flag')

    list_display_links = ['code', 'abbr']
    list_per_page = 100
    search_fields = ['abbr', 'code']
    list_filter = (ParentOrganizationListFilter, ValidFilter)

    header_row_number = 1
    csv_skip_limit = 1000

    inlines = (ChildOrganizationInline,)
    
    def get_readonly_fields(self, request, obj=None) -> Tuple[str]:
        return (*super().get_readonly_fields(request, obj), 'code' if obj is not None else None)

    def get_queryset(self, request: HttpRequest) -> QuerySet[Any]:
        # return super().get_queryset(request).order_by(F('relation__parent__code').asc(nulls_first=True), 'code')
        return super().get_queryset(request).order_by(F('child__parent__code').asc(nulls_first=True), 'code')

    def get_csv_columns(self) -> Tuple[str]:
        return ('code', 'abbr', 'parent_code', 'name', 'rank')

    def get_model_fields(self) -> Tuple[str]:
        return ('code', 'abbr', 'name', 'rank')

    def csv2model(self, csv_dict: Dict[str, Any], *args, **kwargs) -> Dict[str, Any]:
        model_dict = super().csv2model(csv_dict, *args, **kwargs)

        model_dict['rank'] = Code.objects.filter(category__category='org_rank', code=csv_dict.get('rank')).first()
        return model_dict

class OrganizationRelListFilter(ParentOrganizationListFilter):
    """組織階層一覧画面の上位組織フィルター、上位組織一覧を階層的に表示する"""
    def queryset(self, request, queryset):
        """指定した上位組織で絞る"""
        if self.value() is None:
            return queryset

        return queryset.filter(parent_id=self.value())

@admin.register(OrganizationRel, site=mstSite)
class OrganizationRelAdmin(CommonBaseTableAminMixin, admin.ModelAdmin):
    """AdminSiteでの表示をカスタマイズする"""
    fields = [('parent', 'org', 'valid_flag')]
    list_display = ('parent', 'org', 'valid_flag')
    list_filter = (OrganizationRelListFilter, ValidFilter)
    list_display_links = None

    def get_csv_columns(self) -> Tuple[str]:
        return ('code', 'abbr', 'parent_code', 'name', 'rank')

    def get_model_fields(self) -> Tuple[str]:
        return ('parent', 'org')

    def csv2model(self, csv_dict: Dict[str, Any], *args, **kwargs) -> Dict[str, Any]:
        model_dict = super().csv2model(csv_dict, *args, **kwargs)

        parent, org = csv_dict['parent_code'], csv_dict['code']
        model_dict['parent'] = Organization.objects.filter(code=parent).first()
        model_dict['org'] = Organization.objects.filter(code=org).first()
        return model_dict
