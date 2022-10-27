from django.db import models
from django.utils.translation import gettext_lazy as _
from cmm.models import EXPORT_CSV, IMPORT_CSV, CommonBaseTable
from mst.models.ido.common import get_teiin_hijokin


class IdoType(CommonBaseTable, models.Model):
    """異動分類"""
    # code = DCIDOGRP.CTEIHIJKB(1) + CBUNRUICD(2) + GRP_SEQ(2)
    code = models.CharField(max_length=5, blank=False, verbose_name=_('code'))
    name = models.CharField(max_length=128, blank=False, verbose_name=_('異動分類'))
    abbr = models.CharField(max_length=128, blank=True, null=True, verbose_name=_('abbreviation'))
    display_order = models.IntegerField(blank=True, null=True, verbose_name=_('display order'))
    comment = models.CharField(max_length=128, blank=True, null=True, verbose_name=_('comment'))
    
    class Meta:
        db_table = 'mst_ido_type'
        verbose_name = _('異動分類')
        verbose_name_plural = _('異動分類')
        permissions = [(EXPORT_CSV + '_' + db_table, 'Can export ' + db_table),
                       (IMPORT_CSV + '_' + db_table, 'Can import ' + db_table),
        ]

        constraints = [
            models.UniqueConstraint(name = db_table + '_unique', fields = ['code']),
        ]
        ordering = ['code', 'display_order']

    def __str__(self):
        return self.name

    def teiin_hijokin(self):
        """定員・非常勤区分を取得する"""
        return get_teiin_hijokin(self.code)

    teiin_hijokin.short_description = _('定員・非常勤')
