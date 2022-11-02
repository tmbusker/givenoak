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


_logger = logging.getLogger(__name__)

class CsvImportForm(Form):
    """CSVファイルアップロード用Form"""
    import_file = FileField(
        required=True,
        label = _('File to upload')
    )

class CsvImportAdminMixin():
    """CSVインポート処理"""

    # change_list_template = 'cmm/change_list_with_csv_import.html'
    import_template = 'cmm/csv_import.html'

    def has_import_csv_permission(self, request) -> bool:
        """CSV import権限有無のチェック"""
        # pylint: disable = protected-access
        opts = self.model._meta
        if opts.model_name.lower() == 'user' or opts.model_name.lower() == 'group':
            return request.user.has_perm(f'{opts.app_label}.add_{opts.model_name}')

        return request.user.has_perm(f'{opts.app_label}.{IMPORT_CSV}_{opts.model_name}')

    def changelist_view(self, request, extra_context=None):
        """CSV import権限を画面側に渡す"""
        extra_context = extra_context or {}
        extra_context['has_import_csv_permission'] = self.has_import_csv_permission(request)
        return super().changelist_view(request, extra_context=extra_context)
    
    def get_urls(self):
        """CSV importのURLを設定"""
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

        # インポートファイルの選択画面表示
        if request.method == "GET":
            form = CsvImportForm()

        # 画面で選択したインポートファイルの受け取り
        if request.method == "POST":
            form = CsvImportForm(request.POST, request.FILES)
            if form.is_valid():
                csv_file = form.cleaned_data['import_file']     # django.core.files.uploadedfile.InMemoryUploadedFile
                _logger.info('Importing CSV file %s into %s.', csv_file.name, opts.model_name)

                # インポートファイルを読み込む前の処理
                self.pre_import_processing()

                row_cnt = 0
                lot_number = str(hash(csv_file.name + request.user.username + str(timezone.now())))

                # インポートファイルの読み込み処理
                row_cnt = self.read_csv_file(csv_file, request.user.username, lot_number)

                # インポートファイルを読み込みがすべて完了した後の処理
                self.post_import_processing(lot_number=lot_number)

                # ログ情報収集
                queryset = CsvLog.objects.filter(lot_number=lot_number)
                # 読み飛ばしたレコード
                skipped = list(queryset.filter(log_level=CsvLog.WARN).order_by('row_no'))
                # エラーで破棄したレコード
                discarded = list(queryset.filter(log_level=CsvLog.ERROR).order_by('row_no'))
                imported = row_cnt - self.header_row_number - len(skipped) - len(discarded)
                info = _('Import result: imported %(imp)s rows, skipped %(skip)s rows and discardeded: %(dis)s rows.')%{
                         'imp': imported, 'skip': len(skipped), 'dis': len(discarded)}
                _logger.info(info)
                
                if discarded or skipped:
                    context['title'] = _('%(name)s import errors')% {'name': opts.verbose_name}
                    context['field_names'] = self.get_csv_columns()
                    context['csv_logs'] = [csv_log.convert_content2values() for csv_log in discarded] \
                                        + [csv_log.convert_content2values() for csv_log in skipped]
                    context['info'] = info
                    return TemplateResponse(request, 'cmm/csv_import_error.html', context)
                
                return redirect(reverse_lazy(
                    f'{request.resolver_match.namespace}:{opts.app_label}_{opts.model_name}_changelist'))

        context['form'] = form
        return TemplateResponse(request, 'cmm/csv_import.html', context)
