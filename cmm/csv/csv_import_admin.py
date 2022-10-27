import logging

from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.forms import FileField, Form
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.urls import path, reverse_lazy
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from cmm.const import IMPORT_CSV

from cmm.csv import CsvLog
from . import CsvImportBaseMixin, TooManyInvalidRowsError


_logger = logging.getLogger(__name__)

class CsvImportForm(Form):
    """CSVファイルアップロード用Form"""
    import_file = FileField(
        required=True,
        label = _('File to upload')
    )

class CsvImportAdminMixin(CsvImportBaseMixin):
    """
    This mixin should be mixed with django.contrib.admin.ModelAdmin.
    When not used with UniqueConstraintMixin, the unique constraint check is skipped.

    Add a "CSV Import" button to AdminSite's List View to import csv file into models.Model.
    CSV error checks reuses ModelForm's check mechanism.
    """

    # change_list_template = 'cmm/change_list_with_csv_import.html'
    import_template = 'cmm/csv_import.html'

    def changelist_view(self, request, extra_context=None):
        """
        override the ModelAdmin's same method
        """
        extra_context = extra_context or {}
        extra_context['has_import_csv_permission'] = self.has_import_csv_permission(request)
        return super().changelist_view(request, extra_context=extra_context)

    def has_import_csv_permission(self, request) -> bool:
        """CSV importの権限有無をチェック"""
        # pylint: disable = protected-access
        opts = self.model._meta
        if opts.model_name.lower() == 'user' or opts.model_name.lower() == 'group':
            return request.user.has_perm(f'{opts.app_label}.add_{opts.model_name}')

        return request.user.has_perm(f'{opts.app_label}.{IMPORT_CSV}_{opts.model_name}')
    
    def get_urls(self):
        """ override the ModelAdmin's same method """
        # pylint: disable = protected-access
        opts = self.model._meta
        import_url = [
            path('csv_import/', self.admin_site.admin_view(self.import_action),
                    name=f'{opts.app_label}_{opts.model_name}_csv_import'),
        ]
        return import_url + super().get_urls()

    @transaction.non_atomic_requests
    def import_action(self, request):
        """CSV import処理"""
        if not self.has_import_csv_permission(request):
            _logger.info('Trying to import CSV file without permission.')
            raise PermissionDenied

        # pylint: disable = protected-access
        opts = self.model._meta
        title = _('Import %(name)s') % {'name': opts.verbose_name}
        context = {
            **self.admin_site.each_context(request),
            'title': title,
            'app_list': self.admin_site.get_app_list(request),
            'opts': opts,
            'has_view_permission': self.has_view_permission(request),
        }

        if request.method == "GET":
            form = CsvImportForm()

        if request.method == "POST":
            form = CsvImportForm(request.POST, request.FILES)
            if form.is_valid():
                csv_file = form.cleaned_data['import_file']     # django.core.files.uploadedfile.InMemoryUploadedFile
                _logger.info('Importing CSV file %s into %s.', csv_file.name, opts.model_name)

                self.pre_import_processing()

                row_cnt = 0
                lot_number = str(hash(csv_file.name + request.user.username + str(timezone.now())))
                try:
                    row_cnt = self.read_csv_file(csv_file, request.user.username, lot_number)

                    self.post_import_processing(lot_number=lot_number)
                except TooManyInvalidRowsError as cte:
                    _logger.error(cte.message)
                    context['too_many_error'] = cte.message
                    row_cnt = cte.row_cnt

                # ログ情報収集
                queryset = CsvLog.objects.filter(lot_number=lot_number)
                skipped = list(queryset.filter(log_level=CsvLog.WARN).order_by('row_no'))
                discard = list(queryset.filter(log_level=CsvLog.ERROR).order_by('row_no'))
                imported = row_cnt - self.header_row_number - len(skipped) - len(discard)
                info = _('Import result: imported %(imp)s rows, skipped %(skip)s rows and discarded: %(dis)s rows.')%{
                         'imp': imported, 'skip': len(skipped), 'dis': len(discard)}
                _logger.info(info)
                if discard or skipped:
                    context['title'] = _('%(name)s import errors')% {'name': opts.verbose_name}
                    context['field_names'] = self.get_csv_columns()
                    context['csv_logs'] = [csv_log.convert_content2values() for csv_log in discard] \
                                        + [csv_log.convert_content2values() for csv_log in skipped]
                    context['info'] = info
                    return TemplateResponse(request, 'cmm/csv_import_error.html', context)
                
                return redirect(reverse_lazy(
                    f'{request.resolver_match.namespace}:{opts.app_label}_{opts.model_name}_changelist'))

        context['form'] = form
        return TemplateResponse(request, 'cmm/csv_import.html', context)
