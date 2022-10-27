from datetime import timedelta
from typing import Tuple
from django.contrib.admin.utils import flatten


class HistoryTableAdminMixin:
    """
    Mixin supposed to use with django.contrib.admin.ModelAdmin to show HistoryTable
    """
    class Media:
        """画面表示のカスタマイズ"""
        # Foreign keyのadd, change, delete, viewアイコンを非表示にする
        css = {"all": ("cmm/css/cmm.css",)}

    def is_changeable(self, obj=None):
        """レコードの編集可不可を決める、過去レコードは編集不可とする"""
        if obj and getattr(obj, 'valid_through', obj.get_reference_date() + timedelta(days=1)) \
            <= obj.get_reference_date():
            return False
        else:
            return True

    def get_readonly_fields(self, request, obj=None) -> Tuple[str]:
        """valid_throughを読取専用とする"""
        if not obj:
            # 新規作成の場合は最初の設定(おおもとはreadonly_fields=())に従う
            return (*super().get_readonly_fields(request, obj), 'valid_through')

        # 既存レコード編集時、有効終了日が過去のものは全項目編集不可とする
        if getattr(obj, 'valid_through', obj.get_reference_date() + timedelta(days=1)) <= obj.get_reference_date():
            # 過去レコードは全項目編集不可にする
            return tuple(flatten(self.get_fields(request, obj)))

        # 有効終了日を変更不可にする
        return (*super().get_readonly_fields(request, obj), 'valid_through')

    def has_delete_permission(self, request, obj=None):
        """override of the ModelAdmin"""
        return self.is_changeable(obj) and super().has_delete_permission(request, obj)

    def has_change_permission(self, request, obj=None):
        """override of the ModelAdmin"""
        return self.is_changeable(obj) and super().has_delete_permission(request, obj)

    def render_change_form(self, request, context, add=False, change=False, form_url='', obj=None):
        """Hide "save and add another" and "save and continue" button"""
        # pylint: disable=too-many-arguments
        context.update({
            "show_save": True,
            "show_save_and_add_another": False,
            "show_save_and_continue": False,
            "show_delete": True
        })
        return super().render_change_form(request, context, add, change, form_url, obj)

    def delete_queryset(self, request, queryset):
        """querysetのdeleteメソッドをOverrideしてmodelの削除処理を実行するようにする"""
        # pylint: disable = unused-argument
        for obj in queryset:
            obj.delete()
