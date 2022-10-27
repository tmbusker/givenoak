from django.db import models
from django.utils.translation import gettext_lazy as _
from cmm.const import EXPORT_CSV, IMPORT_CSV
from cmm.models.base import CommonBaseTable
from cmm.models import Shikuchoson, Code, ZipCode


class Person(CommonBaseTable, models.Model):
    """個人情報"""
    first_name = models.CharField(max_length=128, blank=False, verbose_name=_('first name'))                        # 名
    middle_name = models.CharField(max_length=128, blank=True, null=True, verbose_name=_('middle name'))
    last_name = models.CharField(max_length=128, blank=False, verbose_name=_('last name'))                          # 姓
    first_name_kana = models.CharField(max_length=128, blank=True, null=True, verbose_name=_('名（カナ）'))         # 名カナ
    last_name_kana = models.CharField(max_length=128, blank=True, null=True, verbose_name=_('姓（カナ）'))          # 姓カナ
    birthday = models.DateField(blank = True, null=True, verbose_name = _('birth day'))
    sex = models.ForeignKey(Code, on_delete=models.DO_NOTHING, blank=True, null=True,
                             limit_choices_to={'category__category': 'sex'}, verbose_name=_('sex'))
    email = models.EmailField(max_length=256, blank=True, null=True, verbose_name=_('email'))
    phone_number = models.CharField(max_length=32, blank=True, null=True, verbose_name=_('phone number'))
    mobile = models.CharField(max_length=32, blank=True, null=True, verbose_name=_('mobile phone'))
    zipcode = models.ForeignKey(ZipCode, on_delete=models.DO_NOTHING, blank=True, null=True, verbose_name=_('zipcode'))
    shikuchoson = models.ForeignKey(Shikuchoson, on_delete=models.DO_NOTHING, blank=True, null=True,
                                    verbose_name=_('shikuchoson'))
    address = models.CharField(max_length=128, blank=True, null=True, verbose_name=_('address'))
    my_number = models.CharField(max_length=32, blank=True, null=True, verbose_name=_('my number'))

    class Meta:
        db_table = 'cmm_person'
        verbose_name = _('person')
        verbose_name_plural = _('persons')
        permissions = [(EXPORT_CSV + '_address', 'Can export address'),
                       (IMPORT_CSV + '_address', 'Can import address'),
                      ]

        constraints = [
            models.UniqueConstraint(name = db_table + '_unique',
                                    fields = ['first_name', 'last_name', 'birthday', 'zipcode']),
        ]
