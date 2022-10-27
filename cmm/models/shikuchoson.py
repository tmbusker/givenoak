from django.db import models
from django.utils.translation import gettext_lazy as _
from cmm.models import CommonBaseTable
from cmm.const import EXPORT_CSV, IMPORT_CSV


class Shikuchoson(CommonBaseTable, models.Model):
    """市区町村コード"""
    code = models.CharField(max_length=6, blank=False, verbose_name=_('shikuchoson code'))
    name = models.CharField(max_length=32, blank=True, verbose_name=_('shikuchoson'))
    name_kana = models.CharField(max_length=32, blank=True, verbose_name=_('shikuchoson kana'))
    pref_name = models.CharField(max_length=32, blank=False, verbose_name=_('todofuken'))
    pref_name_kana = models.CharField(max_length=32, blank=False, verbose_name=_('todofuken kana'))

    class Meta:
        db_table = 'cmm_city'
        verbose_name = _('shikuchoson')
        verbose_name_plural = _('shikuchosons')
        permissions = [(EXPORT_CSV + '_shikuchoson', 'Can export shikuchoson csv'),
                       (IMPORT_CSV + '_shikuchoson', 'Can import shikuchoson csv'),
                      ]

        constraints = [
            models.UniqueConstraint(name = db_table + '_unique', fields = ['code']),
        ]
        ordering = ['code', ]

    def __str__(self) -> str:
        return ' '.join([self.pref_name, self.name])
