import csv
import logging
from urllib.parse import quote
from datetime import date
from xlsxwriter.workbook import Workbook

from django.http import HttpResponse
from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from cmm.const import UTF8


_logger = logging.getLogger(__name__)

@admin.display(description=_('export csv'))
def export_csv(modeladmin, request, queryset) -> HttpResponse:
    """CSV export処理"""
    # pylint: disable = unused-argument
    file_encoding = modeladmin.csv_encoding or UTF8
    file_name = modeladmin.model._meta.verbose_name_plural + modeladmin.csv_file_extension
    

    _logger.info('Start to exporting %s', file_name)

    response = HttpResponse(content_type=f'text/csv; charset={file_encoding}')
    # quote()を使わないとファイル名がセットされない
    response['Content-Disposition'] = f'attachment; filename={quote(file_name)}'
    writer = csv.writer(response, modeladmin.dialect)

    if modeladmin.get_export_titles():
        writer.writerow(modeladmin.get_export_titles())

    for row_dict in queryset.values(*modeladmin.get_model_fields()):
        # 日付型の出力フォーマットをセットする
        values = [v.strftime(modeladmin.date_format) if isinstance(v, date) else v \
                    for (k,v) in modeladmin.model2csv(row_dict).items()]
        writer.writerow(values)

    _logger.info('CSV file %s is exported successfully.', file_name)
    return response

@admin.display(description=_('export excel'))
def export_excel(modeladmin, request, queryset):
    """Excel export処理"""
    # pylint: disable = unused-argument
    file_name = modeladmin.model._meta.verbose_name_plural + modeladmin.excel_file_extension
    
    _logger.info('Start to exporting %s', file_name)

    response = HttpResponse(content_type='application/vnd.ms-excel')
    # quote()を使わないと日本語ファイル名がセットされない
    response['Content-Disposition'] = f'attachment; filename={quote(file_name)}'
    
    workbook = Workbook(response, {'in_memory': True})
    worksheet = workbook.add_worksheet(modeladmin.model._meta.model_name)

    row_num = 0

    # ヘッダー行の出力
    if modeladmin.get_export_titles():
        for col_num, value in enumerate(modeladmin.get_export_titles()):
            worksheet.write(row_num, col_num, value)
        row_num += 1

    # 内容出力
    for row in queryset.values_list(*modeladmin.get_model_fields()):
        for col_num, value in enumerate(row):
            worksheet.write(row_num, col_num, value)
        row_num += 1
    
    workbook.close()

    _logger.info('CSV file %s is exported successfully.', file_name)
    return response
