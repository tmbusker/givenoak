from django.contrib import admin

from cmm.admin.base import CommonBaseTableAminMixin


class IdoScreenAdmin(CommonBaseTableAminMixin, admin.ModelAdmin):
    """異動入力画面"""
    fields = ['screen_code', 'screen_name']
    search_fields = ['screen_code', 'screen_name']
    list_display = ['screen_code', 'screen_name']
