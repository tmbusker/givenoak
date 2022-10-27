from django.db import models
from django.utils.translation import gettext_lazy as _

from cmm.models.base import CommonBaseTable
from mst.models.ido import IdoSyumoku, IdoScreen


class IdoSyumokuScreen(CommonBaseTable, models.Model):
    """異動種目ごとの入力画面"""
    ido_syumoku = models.ForeignKey(IdoSyumoku, on_delete=models.CASCADE, verbose_name=_('異動種目'))
    ido_screen = models.ForeignKey(IdoScreen, on_delete=models.CASCADE, verbose_name=_('異動入力画面'))

    class Meta:
        # managed = True
        db_table = 'mst_ido_syumoku_screen'
        verbose_name = _('異動種目の入力画面')
        verbose_name_plural = _('異動種目の入力画面')

        constraints = [
            models.UniqueConstraint(name = db_table + '_unique', fields = ['ido_syumoku', 'ido_screen']),
        ]

    def __str__(self):
        return str(self.ido_syumoku) + ' ' + str(self.ido_screen)
