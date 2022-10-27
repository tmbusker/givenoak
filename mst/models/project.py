from django.db import models
from django.utils.translation import gettext_lazy as _
from cmm.models import EXPORT_CSV, IMPORT_CSV, CommonBaseTable
from mst.models import Product, Customer


class Project(CommonBaseTable, models.Model):
    """プロジェクト"""
    NEGOTIATING = 10
    DELIVERING = 20
    DELIVERED = 30
    
    STATUS_CHOICES = [
        (NEGOTIATING, '商談中'),
        (DELIVERING, '導入中'),
        (DELIVERED, '導入済'),
    ]

    code = models.CharField(max_length=64, blank=False, verbose_name=_('project code'))
    name = models.CharField(max_length=128, blank=False, verbose_name=_('project'))
    abbr = models.CharField(max_length=128, blank=True, null=True, verbose_name=_('abbreviation'))
    customer = models.ForeignKey(Customer, on_delete=models.DO_NOTHING, verbose_name=_('customer'))
    products = models.ManyToManyField(Product, through='ProjectProduct', verbose_name=_('project product'))
    status = models.IntegerField(blank=False, choices=STATUS_CHOICES, verbose_name=_('status'))
    comment = models.CharField(max_length=128, blank=True, null=True, verbose_name=_('comment'))
    
    class Meta:
        db_table = 'mst_project'
        verbose_name = _('project')
        verbose_name_plural = _('projects')
        permissions = [(EXPORT_CSV + '_project', 'Can export project csv'),
                       (IMPORT_CSV + '_project', 'Can import project csv'),
                      ]

        constraints = [
            models.UniqueConstraint(name = db_table + '_unique', fields = ['code']),
        ]
        ordering = ['code', ]

class ProjectProduct(CommonBaseTable):
    """プロジェクト関連製品"""
    project = models.ForeignKey(Project, on_delete=models.DO_NOTHING, verbose_name=_('project'))
    product = models.ForeignKey(Product, on_delete=models.DO_NOTHING, verbose_name=_('product'))
    comment = models.CharField(max_length=128, blank=True, null=True, verbose_name=_('comment'))
    
    class Meta:
        db_table = 'mst_project_product'
        verbose_name = _('project product')
        verbose_name_plural = _('project product')
        permissions = [(EXPORT_CSV + '_project_product', 'Can export project products csv'),
                       (IMPORT_CSV + '_project_product', 'Can import project products csv'),
                      ]

        constraints = [
            models.UniqueConstraint(name = db_table + '_unique', fields = ['project', 'product']),
        ]
        ordering = ['project', 'product']

    def __str__(self) -> str:
        return self.name
