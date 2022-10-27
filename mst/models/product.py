from django.db import models
from django.utils.translation import gettext_lazy as _
from cmm.models.base import CommonBaseTable
from cmm.const import EXPORT_CSV, IMPORT_CSV


class Product(CommonBaseTable, models.Model):
    """製品"""
    SYSTEM = 'system'
    OPTION = 'option'
    
    PRODUCT_CHOICES = [
        (SYSTEM, _('製品')),
        (OPTION, _('オプション')),
    ]
    code = models.CharField(max_length=64, blank=False, verbose_name=_('product code'))
    name = models.CharField(max_length=128, blank=False, verbose_name=_('product'))
    abbr = models.CharField(max_length=128, blank=True, null=True, verbose_name=_('abbreviation'))
    summary = models.CharField(max_length=512, blank=True, null=True, verbose_name=_('summary'))
    product_ver = models.CharField(max_length=16, blank=True, null=True, verbose_name=_('version'))
    display_order = models.IntegerField(blank=True, null=True, verbose_name=_('display order'))
    parent = models.ForeignKey('product', blank=True, null=True, on_delete=models.DO_NOTHING,
                                   verbose_name=_('parent product'))
    product_type = models.CharField(max_length=32, choices=PRODUCT_CHOICES, blank=True, null=True,
                                    verbose_name=_('product type'))
    comment = models.CharField(max_length=128, blank=True, null=True, verbose_name=_('comment'))

    class Meta:
        db_table = 'mst_product'
        verbose_name = _('product')
        verbose_name_plural = _('products')
        permissions = [(EXPORT_CSV + '_product', 'Can export product csv'),
                       (IMPORT_CSV + '_product', 'Can import product csv'),
                      ]

        constraints = [
            models.UniqueConstraint(name = db_table + '_unique', fields = ['code']),
        ]
        ordering = ['code', ]

    def __str__(self) -> str:
        if self.parent is not None:
            return self.parent.name + ' ' + self.name

        return self.name
