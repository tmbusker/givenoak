from typing import Tuple
from django.contrib import admin
from django.core.exceptions import ValidationError
from django.forms.models import BaseInlineFormSet
from django.utils.translation import gettext_lazy as _
from cmm.admin.base import CommonFilter, CommonBaseTableAminMixin, ValidFilter
from cmm.models import OrgMember, Employee, get_all_upper_organizations
from cmm.utils.date import Period, flat_overlap


class AffiliationListFilter(CommonFilter):
    """職員画面の本務組織フィルター"""
    title = _('main duty organization')

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'affiliation_id'

    def lookups(self, request, model_admin):
        """上位組織リスト"""
        upper_organizations = list(get_all_upper_organizations())
        return [(org.id, '|' + '-'*int(org.rank.code) + org.abbr) for org in upper_organizations]

    def queryset(self, request, queryset):
        """指定組織で絞る"""
        if self.value() is None:
            return queryset

        return queryset.filter(orgmember__organization_id=self.value())

class OrgMemberInlineFormSet(BaseInlineFormSet):
    """Customize BaseInlineFormSet"""
    def clean(self):
        """同一期間中に本務を一つに制限するチェックを追加"""
        super().clean()
        if any(self.errors):
            return
        
        # pylint: disable = not-callable
        default_valid_through = self.model().get_default_valid_through()
        periods = []
        for form in self.forms:
            valid_from = form.cleaned_data.get('valid_from')
            valid_through = form.instance.valid_through or default_valid_through
            periods.append(Period(valid_from, valid_through))
        
        for period in flat_overlap(periods):
            main_duty_count = 0
            for form in self.forms:
                valid_from = form.cleaned_data.get('valid_from')
                valid_through = form.instance.valid_through or default_valid_through
                if valid_from <= period.valid_through and valid_through >= period.valid_from:
                    if form.cleaned_data.get('is_main_duty'):
                        main_duty_count += 1

            if main_duty_count == 0:
                raise ValidationError(
                    _('You must specify one and only one main duty organization.'),
                    code='multiple_main_duty',
                    params = {'valid_from': period.valid_from, 'valid_through': period.valid_through}
                )
            
            if main_duty_count > 1:
                raise ValidationError(
                    _('You cannot have multiple main duty simultaneously.'),
                    code='multiple_main_duty',
                    params = {'valid_from': period.valid_from, 'valid_through': period.valid_through}
                )

class OrgMemberInline(admin.TabularInline):
    """職員所属組織をインラインで表示する"""
    model = OrgMember
    formset = OrgMemberInlineFormSet
    extra = 0

    fields = ['employee', 'organization', 'is_main_duty', 'is_manager', 'is_staff']
    # readonly_fields = ['valid_through']
    search_fields = ['organization']

    # ※参考 検索フィールド＋Select Box
    autocomplete_fields = ['organization']

    # ※参考 検索用子画面を開く、ただしidのみを表示
    # raw_id_fields=('organization',)

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        formfield = super().formfield_for_dbfield(db_field, request, **kwargs)
        if db_field.name == 'organization':
            formfield.widget.can_add_related = False
            formfield.widget.can_change_related = False
            formfield.widget.can_delete_related = False
            formfield.widget.can_view_related = False
        return formfield

    def get_queryset(self, request):
        """職員の有効期間のOverlapする所属に絞る"""
        # qs = super().get_queryset(request)
        employee_id = request.resolver_match.kwargs.get('object_id')
        employee = Employee.objects.filter(id=employee_id).first()
        if employee is None:
            return None
        return OrgMember.objects.filter(employee_id=employee_id)

class EmployeeAdmin(CommonBaseTableAminMixin, admin.ModelAdmin):
    """AdminSiteでの表示をカスタマイズする"""
    fields = [('name', 'code'), 'email', 'valid_flag']
    # readonly_fields=( 'valid_through',)
    list_display = ('name', 'code', 'main_duty_organization', 'email', 'valid_flag')
    list_display_links = ['code', 'name']
    list_filter = (AffiliationListFilter, ValidFilter)
    search_fields = ['name', 'code', 'organizations__organization__name']

    inlines = (OrgMemberInline,)

    # ※参考
    # ManyToMany用選択元＆選択済リストを表示する、選択元は検索フィールド付き。ただし、throughの指定がない場合のみ利用可能
    # fields = [('name', 'code'), 'email', 'auth_user', 'organizations', ('valid_from', 'valid_through')]
    # filter_horizontal = ('organizations',)

    def get_readonly_fields(self, request, obj=None) -> Tuple[str]:
        return (*super().get_readonly_fields(request, obj), 'code' if obj is not None else None)

    def render_change_form(self, request, context, *args, **kwargs):
        # if request.user.is_superuser:
        #     context['adminform'].form.fields['auth_user'].queryset = AuthUser.objects.all()
        # else:
        #     context['adminform'].form.fields['auth_user'].queryset = AuthUser.objects.filter(group=request.user.group)

        return super().render_change_form(request, context, *args, **kwargs)
