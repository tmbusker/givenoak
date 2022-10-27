from typing import Tuple
from django.contrib import admin
from cmm.models import Shikuchoson, ZipCode
from cmm.admin import cmmSite
from cmm.admin.base import CommonBaseTableAminMixin, ValidFilter


@admin.register(ZipCode, site=cmmSite)
class ZipCodeModelAdmin(CommonBaseTableAminMixin, admin.ModelAdmin):
    """郵便番号をAdminSiteに表示する"""
    fields = ['zipcode', 'shikuchoson', 'machiikimei', 'machiikimei_kana', 'valid_flag']
    list_display = ('zipcode', 'shikuchoson', 'machiikimei', 'machiikimei_kana', 'valid_flag')
    list_filter = ('shikuchoson__pref_name', ValidFilter)

    encoding = 'cp932'
    # is_bulk_insert = True
    is_replace_existing = False

    def get_readonly_fields(self, request, obj=None) -> Tuple[str]:
        return (*super().get_readonly_fields(request, obj), 'zipcode' if obj is not None else None)

    def get_csv_columns(self) -> Tuple[str]:
        return ('shikuchoson', 'old_zipcode', 'zipcode', 'pref_name_kana', 'name_kana', 'machiikimei_kana',
                'pref_name', 'name', 'machiikimei')

    def get_model_fields(self) -> Tuple[str]:
        return ('zipcode', 'shikuchoson', 'machiikimei', 'machiikimei_kana')

    def csv2model(self, csv_dict: dict, *args, **kwargs) -> dict:
        model_dict = super().csv2model(csv_dict, *args, **kwargs)

        # コードよりForeign Key取得
        shikuchoson = Shikuchoson.objects.filter(code=csv_dict.get('shikuchoson')).first()
        if shikuchoson is not None:
            model_dict['shikuchoson'] = shikuchoson

        return model_dict
