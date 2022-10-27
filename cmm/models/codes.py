import logging
from django.db import models
from django.utils.translation import gettext_lazy as _
from cmm.models.base import CommonBaseTable

_logger = logging.getLogger(__name__)

class Category(CommonBaseTable):
    """コードのカテゴリ"""
    category = models.CharField(max_length=32, blank=False, verbose_name=_('category'))
    name = models.CharField(max_length=128, blank=True, null=True, verbose_name=_('category name'))

    class Meta:
        db_table = 'cmm_category'
        verbose_name = _('category')
        verbose_name_plural = _('categories')

        constraints = [
            models.UniqueConstraint(name = db_table + '_unique', fields = ['category']),
        ]
        ordering = ['category']

    def __str__(self) -> str:
        # pylint: disable = invalid-str-returned
        return self.name or self.category

class Code(CommonBaseTable):
    """コードマスタ"""
    category = models.ForeignKey(Category, blank=False, on_delete=models.CASCADE, verbose_name=_('category'))
    code = models.CharField(max_length=32, blank=False, verbose_name=_('code'))
    name = models.CharField(max_length=128, blank=True, null=True, verbose_name=_('code name'))
    abbr = models.CharField(max_length=128, blank=True, null=True, verbose_name=_('abbreviation'))
    display_order = models.IntegerField(blank=True, null=True, verbose_name=_('display order'))

    class Meta:
        db_table = 'cmm_code'
        verbose_name = _('code')
        verbose_name_plural = _('codes')

        constraints = [
            models.UniqueConstraint(name = db_table + '_unique', fields = ['category', 'code']),
        ]
        ordering = ['category', 'display_order']

    def __str__(self) -> str:
        return self.name or self.code
