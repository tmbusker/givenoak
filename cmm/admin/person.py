from typing import Tuple
from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.db import connection, transaction
from cmm.admin.base import SimpleTableAminMixin, ValidFilter
from cmm.csv import CsvBulkImportMixin, CsvImportAdminMixin, ExportAdminMixin
from cmm.models import Employee, Code, ZipCode


class EmployeeInline(admin.StackedInline):
    """職員情報をインラインで表示できるように定義する"""
    model = Employee
    can_delete = False
    verbose_name_plural = _('employee')

class PersonAdmin(SimpleTableAminMixin, ExportAdminMixin, CsvImportAdminMixin, CsvBulkImportMixin, admin.ModelAdmin):
    """AdminSiteでの表示をカスタマイズする"""
    fields = ['last_name', 'first_name', 'last_name_kana', 'first_name_kana','birthday','sex','email',
              'phone_number','mobile','zipcode','address','my_number', 'valid_flag']
    list_display = ('last_name', 'first_name','birthday','sex','email', 'valid_flag')
    list_display_links = ['first_name', 'last_name']
    list_filter = (ValidFilter,)

    # is_bulk_insert = True

    def get_csv_columns(self) -> Tuple[str]:
        return ('last_name', 'first_name', 'last_name_kana', 'first_name_kana','年齢','birthday','sex','email',
                'phone_number','mobile','zipcode','address','my_number')

    def get_model_fields(self) -> Tuple[str]:
        return ('last_name', 'first_name', 'last_name_kana', 'first_name_kana', 'birthday', 'sex', 'email',
                'phone_number', 'mobile', 'zipcode', 'address', 'my_number')

    def csv2model(self, csv_dict: dict, *args, **kwargs) -> dict:
        model_dict = super().csv2model(csv_dict, *args, **kwargs)
        # CSVにて性別の略称が設定されている場合の対応
        model_dict['sex'] = Code.objects.filter(category__category='sex', abbr=csv_dict.get('sex')).first()
        # CSVにて郵便番号が設定されている場合の対応
        zipcode = ZipCode.objects.filter(zipcode=csv_dict['zipcode'].replace('-', '')).first()
        model_dict['zipcode'] = zipcode
        if zipcode is not None:
            model_dict['shikuchoson'] = zipcode.shikuchoson
        return model_dict

    @transaction.atomic
    def post_import_processing(self, *args, **kwargs):
        ## call stored procedure
        with connection.cursor() as cur:
            # cur.execute("BEGIN")
            cur.execute('call create_cmm_authusers();', [])
            # cur.execute("COMMIT")
        
        # 実行に時間がかかるので、いったんコメントアウトする
        # for user in AuthUser.objects.filter(password='password'):
        #     user.set_password('password')
        #     user.save()
