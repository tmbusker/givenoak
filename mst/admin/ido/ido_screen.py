from django.contrib import admin

from cmm.admin.base import CommonBaseTableAminMixin
from mst.models.ido import IdoScreen
from mst.admin import mstSite


@admin.register(IdoScreen, site=mstSite)
class IdoScreenAdmin(CommonBaseTableAminMixin, admin.ModelAdmin):
    """異動入力画面"""
    fields = ['screen_code', 'screen_name']
    search_fields = ['screen_code', 'screen_name']
    list_display = ['screen_code', 'screen_name']
