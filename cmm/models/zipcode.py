from django.db import models
from django.utils.translation import gettext_lazy as _
from cmm.models import CommonBaseTable, Shikuchoson
from cmm.const import EXPORT_CSV, IMPORT_CSV


class ZipCode(CommonBaseTable, models.Model):
    """郵便番号と市区町村＆町域名と一対一にならないので、このマスタは入力補助用にしか使えない"""
    zipcode = models.CharField(max_length=7, blank=True, null=True, verbose_name=_('zipcode'))
    shikuchoson = models.ForeignKey(Shikuchoson, blank=False, on_delete=models.DO_NOTHING,
                                    verbose_name=_('shikuchoson'))
    machiikimei = models.CharField(max_length=128, blank=True, null=True, verbose_name=_('町域名'))
    machiikimei_kana = models.CharField(max_length=128, blank=True, null=True, verbose_name=_('町域名（カナ）'))

    class Meta:
        db_table = 'cmm_zipcode'
        verbose_name = _('zipcode')
        verbose_name_plural = _('zipcode')
        permissions = [(EXPORT_CSV + '_zipcode', 'Can export zipcode'),
                       (IMPORT_CSV + '_zipcode', 'Can import zipcode'),
                      ]

        constraints = [
            models.UniqueConstraint(name = db_table + '_unique', 
                                    fields = ['zipcode', 'shikuchoson', 'machiikimei']),
        ]
        ordering = ['zipcode', 'shikuchoson', 'machiikimei', ]

    def __str__(self) -> str:
        # pylint: disable = invalid-str-returned
        return self.zipcode
