from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from cmm.models.base import UniqueConstraintMixin


class VersionedTable(UniqueConstraintMixin, models.Model):
    """楽観的排他用のversionカラムを持つテーブル"""
    version = models.IntegerField(blank=True, null=True, verbose_name=_("version"))

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        current_db_record = self.retrieve_by_unique_key()
        if current_db_record and current_db_record.version and self.version:
            # current_db_record.refresh_from_db()
            if self.version == current_db_record.version:
                self.version += 1
                super().save(*args, **kwargs)
            else:
                raise ValidationError(
                    _('Race condition was detected. Confirm the content and try again later.'),
                    code='race_condition',
                    params = None
                )
        else:
            self.version = 1
            super().save(*args, **kwargs)
