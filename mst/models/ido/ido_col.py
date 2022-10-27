from django.db import models
from django.utils.translation import gettext_lazy as _
from cmm.models import EXPORT_CSV, IMPORT_CSV, CommonBaseTable
from mst.const import TEIIN_HIJOKIN_CHOICES


class IdoCol(CommonBaseTable, models.Model):
    """異動入力項目 deprecated"""
    teiin_hijokin = models.CharField(max_length=5, choices=TEIIN_HIJOKIN_CHOICES, blank=False,
                                        verbose_name=_('定員・非常勤'))
    col_no = models.IntegerField(blank=True, null=True, verbose_name=_('項目番号'))
    table_id = models.CharField(max_length=40, blank=True, null=True, verbose_name=_('table id'))
    col_id = models.CharField(max_length=40, blank=True, null=True, verbose_name=_('項目ID'))
    col_name = models.CharField(max_length=40, blank=True, null=True, verbose_name=_('項目名'))
     
    class Meta:
        db_table = 'mst_ido_col'
        verbose_name = _('異動入力項目')
        verbose_name_plural = _('異動入力項目')
        permissions = [(EXPORT_CSV + '_' + db_table, 'Can export ' + db_table),
                       (IMPORT_CSV + '_' + db_table, 'Can import ' + db_table),
                      ]

        constraints = [
            models.UniqueConstraint(name = db_table + '_unique', fields = ['teiin_hijokin', 'col_no']),
        ]
        ordering = ['teiin_hijokin', 'col_no']

    def __str__(self):
        return self.col_name
