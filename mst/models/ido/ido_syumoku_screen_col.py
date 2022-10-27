from django.db import models
from django.utils.translation import gettext_lazy as _
from cmm.models import EXPORT_CSV, IMPORT_CSV, CommonBaseTable
from mst.models.ido import IdoSyumokuScreen, IdoCol


class IdoSyumokuScreenCol(CommonBaseTable, models.Model):
    """異動種目と異動項目の紐付け"""
    TYPE_K = 'K'
    TYPE_0 = '0'
    TYPE_1 = '1'
    TYPE_3 = '3'
    TYPE_9 = '9'
    TYPE_X = 'X'
 
    TYPE_CHOICES = [
        (TYPE_K, _('必須(固定)')),
        (TYPE_0, _('必須')),
        (TYPE_1, _('任意')),
        (TYPE_3, _('表示のみ')),
        (TYPE_9, _('非表示')),
        (TYPE_X, _('非表示(固定)')),
    ]
 
    ido_syumoku_screen = models.ForeignKey(IdoSyumokuScreen, on_delete=models.DO_NOTHING, verbose_name=_('異動項目'))
    ido_col = models.ForeignKey(IdoCol, on_delete=models.DO_NOTHING, verbose_name=_('異動項目'))
    edit_type = models.CharField(max_length=8, choices=TYPE_CHOICES, blank=False,default=TYPE_X,
                                 verbose_name=_('制御タイプ'))

    class Meta:
        db_table = 'mst_ido_syumoku_screen_col'
        verbose_name = _('異動種目の画面ごと入力項目')
        verbose_name_plural = _('異動種目の画面ごと入力項目')
        permissions = [(EXPORT_CSV + '_' + db_table, 'Can export ' + db_table),
                       (IMPORT_CSV + '_' + db_table, 'Can import ' + db_table),
                      ]

        constraints = [
            models.UniqueConstraint(name = db_table + '_unique', fields = ['ido_syumoku_screen', 'ido_col']),
        ]
        ordering = ['ido_syumoku_screen', 'ido_col']

    def __str__(self):
        return str(self.ido_syumoku_screen) + ' ' + str(self.ido_col)
