import logging
from django.utils import timezone
from django.db import models
from django.utils.translation import gettext_lazy as _

from cmm.models.base import VersionedTable


_logger = logging.getLogger(__name__)

class SimpleTable(VersionedTable, models.Model):
    """作成日付、作成者、更新日時と更新者をもつテーブルのベースクラス"""
    create_time = models.DateTimeField(blank = True, null=True, editable=False, verbose_name = _('create time'))
    creator = models.CharField(max_length = 120, blank = True, editable=False, null=True, verbose_name = _('creator'))
    update_time = models.DateTimeField(blank = True, null=True, editable=False, verbose_name = _('update time'))
    updater = models.CharField(max_length = 120, blank = True, editable=False, null=True, verbose_name = _('updater'))
    valid_flag = models.BooleanField(blank=False, null=False, default=True, verbose_name=_('valid'))

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if self.update_time is None:
            self.update_time = timezone.now()
        if not self.creator:
            self.creator = self.updater
        if self.create_time is None:
            self.create_time = self.update_time

        super().save(*args, **kwargs)
