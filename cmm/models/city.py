from django.db import models
from django.utils.translation import gettext_lazy as _
from cmm.const import EXPORT_CSV, IMPORT_CSV
from cmm.models.base import HistoryTable, SimpleTable


class City(HistoryTable, SimpleTable, models.Model):
    """市区町村コードテスト専用"""
    code = models.CharField(max_length=6, blank=False, verbose_name=_('city code'))
    name = models.CharField(max_length=32, blank=True, verbose_name=_('city'))
    name_kana = models.CharField(max_length=32, blank=True, verbose_name=_('city kana'))
    pref_name = models.CharField(max_length=32, blank=False, verbose_name=_('todofuken'))
    pref_name_kana = models.CharField(max_length=32, blank=False, verbose_name=_('todofuken kana'))

    class Meta:
        db_table = 'cmm_tst_city'
        verbose_name = _('shikuchoson')
        verbose_name_plural = _('shikuchosons')
        permissions = [(EXPORT_CSV + '_cmm_tst_city', 'Can export shikuchoson csv'),
                       (IMPORT_CSV + '_cmm_tst_city', 'Can import shikuchoson csv'),
                      ]

        constraints = [
            models.UniqueConstraint(name = db_table + '_unique', fields = ['code', 'valid_from']),
        ]
        ordering = ['code', ]

    def __str__(self) -> str:
        return ' '.join([self.pref_name, self.name])

    def has_same_contents(self, obj) -> bool:
        return self.code == obj.code and self.name == obj.name
