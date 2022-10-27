from django.db import models
from django.utils.translation import gettext_lazy as _
from cmm.models import EXPORT_CSV, IMPORT_CSV, CommonBaseTable


class Customer(CommonBaseTable, models.Model):
    """顧客"""
    # pylint: disable = non-ascii-name
    国立大学法人 = 'A'
    国立短期大学 = 'B'
    国立高等専門学校機構 = 'C'
    政府機関 = 'D'
    国立研究機関 = 'E'
    独立行政法人 = 'F'
    公立大学 = 'G'
    私立大学 = 'H'
    地方自治体 = 'I'
    警察 = 'J'

    KIGO_CHOICES = [
        (国立大学法人, '国立大学法人'),
        (国立短期大学, '国立短期大学'),
        (国立高等専門学校機構, '国立高等専門学校機構'),
        (政府機関, '政府機関'),
        (国立研究機関, '国立研究機関'),
        (独立行政法人, '独立行政法人'),
        (公立大学, '公立大学'),
        (私立大学, '私立大学'),
        (地方自治体, '地方自治体'),
        (警察, '警察'),
    ]
    code = models.CharField(max_length=64, blank=False, verbose_name=_('customer code'))
    name = models.CharField(max_length=128, blank=False, verbose_name=_('customer'))
    abbr = models.CharField(max_length=128, blank=True, null=True, verbose_name=_('abbreviation'))
    kigo = models.CharField(max_length=2, choices=KIGO_CHOICES, blank=True, null=True, verbose_name=_('kigo'))
    old_name = models.CharField(max_length=128, blank=True, null=True, verbose_name=_('old name'))
    address = models.CharField(max_length=128, blank=True, null=True, verbose_name=_('address'))
    comment = models.CharField(max_length=128, blank=True, null=True, verbose_name=_('comment'))
    
    class Meta:
        db_table = 'mst_customer'
        verbose_name = _('customer')
        verbose_name_plural = _('customers')
        permissions = [(EXPORT_CSV + '_customer', 'Can export customer csv'),
                       (IMPORT_CSV + '_customer', 'Can import customer csv'),
                      ]

        constraints = [
            models.UniqueConstraint(name = db_table + '_unique', fields = ['code']),
        ]
        ordering = ['code', ]

    def __str__(self) -> str:
        return self.name
