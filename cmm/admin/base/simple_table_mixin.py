from typing import Tuple
from django.contrib import messages
from django import forms
from django.http import HttpResponseRedirect
from django.utils import timezone
from django.conf import settings


class SimpleTableAminMixin():
    """Csv export, import可能なHistoryTableのAdminMixin"""
    save_as = False
    save_as_continue = True

    class Media:
        """画面表示のカスタマイズ"""
        # Foreign keyのadd, change, delete, viewアイコンを非表示にする
        css = {"all": ("cmm/css/cmm.css",)}

    def get_readonly_fields(self, request, obj=None) -> Tuple[str]:
        """削除フラグを読み取り専用とする"""
        readonly_fields = ('creator', 'create_time', 'updater', 'update_time')
        return super().get_readonly_fields(request, obj) + readonly_fields

    def render_change_form(self, request, context, add=False, change=False, form_url='', obj=None):
        """Hide "save and add another" and "save and continue" button"""
        # pylint: disable=too-many-arguments
        if context.get('show_save_and_continue') is None:
            context['show_save_and_continue'] = True
        if context.get('show_save_and_add_another') is None:
            context['show_save_and_add_another'] = False

        return super().render_change_form(request, context, add, change, form_url, obj)

    def change_view(self, request, object_id, form_url='', extra_context=None):
        """Override ModelAdmin's same method"""
        try:
            return super().change_view(request, object_id, form_url, extra_context)
        except forms.ValidationError as error:
            self.message_user(request, '.'.join(error.messages), level=messages.ERROR)
            return HttpResponseRedirect(request.path)

    def delete_queryset(self, request, queryset):
        """querysetのdeleteメソッドをOverrideしてmodelの削除処理を実行するようにする"""
        # pylint: disable = unused-argument
        for obj in queryset:
            obj.delete()

    def save_model(self, request, obj, form, change):
        """Override ModelAdmin's same method"""
        if obj is not None:
            obj.updater = request.user.username
            obj.update_time = timezone.now()
        super().save_model(request, obj, form, change)

    def save_formset(self, request, form, formset, change):
        """Override ModelAdmin's same method"""
        for inline_form in formset:
            inline_form.instance.updater = form.instance.updater
            inline_form.instance.update_time = timezone.now()
            # 有効フラグはいったん親と連動しない
            # inline_form.instance.valid_flag = form.instance.valid_flag
            
        super().save_formset(request, form, formset, change)
