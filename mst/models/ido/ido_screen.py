from django.db import models
from django.utils.translation import gettext_lazy as _

from cmm.models.base import CommonBaseTable


class IdoScreen(CommonBaseTable, models.Model):
    """異動情報入力画面"""
    screen_code = models.CharField(max_length=40, blank=False, null=False, verbose_name=_('画面コード'))
    screen_name = models.CharField(max_length=40, blank=True, null=True, verbose_name=_('画面名'))

    class Meta:
        # managed = True
        db_table = 'mst_ido_screen'
        verbose_name = _('異動情報入力画面')
        verbose_name_plural = _('異動情報入力画面')

        constraints = [
            models.UniqueConstraint(name = db_table + '_unique', fields = ['screen_code']),
        ]
        ordering = ['screen_code']

    def __str__(self):
        return self.screen_name
