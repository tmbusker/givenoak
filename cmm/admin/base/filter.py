from datetime import date
from django.contrib import admin
from django.utils.translation import get_language, gettext_lazy as _

from cmm.const import LANGUAGES


class CommonFilter(admin.SimpleListFilter):
    """Abstract class, only to override choices"""
    def choices(self, changelist):
        # yield {
        #     "selected": self.value() is None,
        #     "query_string": changelist.get_query_string(remove=[self.parameter_name]),
        #     "display": _("All"),
        # }
        for lookup, title in self.lookup_choices:
            yield {
                "selected": self.value() == str(lookup),
                "query_string": changelist.get_query_string(
                    {self.parameter_name: lookup}
                ),
                "display": title,
            }

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
    
    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """

class ValidFilter(CommonFilter):
    """有効フラグのフィルター"""
    title = _('valid flag')
    parameter_name = 'valid_flag'

    def lookups(self, request, model_admin):
        return [('valid', _("Valid")),
                ('invalid', _("Invalid")),
                ('all', _("All")),
        ]

    def queryset(self, request, queryset):
        if self.value() == 'all':
            return queryset

        if self.value() == 'invalid':
            return queryset.filter(valid_flag=False)
        
        return queryset.filter(valid_flag=True)

class LanguageFilter(CommonFilter):
    """言語フィルター"""
    title = _('language')
    parameter_name = 'lang'

    def lookups(self, request, model_admin):
        return LANGUAGES + [('all', _("All"))]

    def queryset(self, request, queryset):
        lang = get_language()
        if self.value() is not None:
            lang = self.value()
            
        if lang == 'all':
            return queryset

        return queryset.filter(lang=lang)

class ValidAtFilter(CommonFilter):
    """有効期間のフィルタ"""
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = _('valid at')

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'reference_date'

    def lookups(self, request, model_admin):
        return [('all', _("All")),
                ('valid', _("Valid")),
                ('expired', _("Expired")),
                ('future', _("Valid in the future")),
               ]

    def queryset(self, request, queryset):
        if self.value() == 'all':
            return queryset

        ref_date = date.today()
        if self.value() == 'valid':
            return queryset.filter(valid_from__lte=ref_date, valid_through__gte=ref_date)

        ref_date = date.today()
        if self.value() == 'expired':
            return queryset.filter(valid_through__lt=ref_date)
        
        if self.value() == 'future':
            return queryset.filter(valid_from__gt=ref_date)

        return queryset.filter(valid_through__gte=ref_date)
