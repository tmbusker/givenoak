from django.db import models
from django.utils.translation import gettext_lazy as _
from cmm.const import EXPORT_CSV, IMPORT_CSV
from cmm.exception import RecursiveParenthoodError
from cmm.models.base import CommonBaseTable


class OrganizationRel(CommonBaseTable):
    """組織マスタ Adjacency List"""
    org = models.ForeignKey('Organization', blank=False, on_delete=models.DO_NOTHING
                             ,related_name='child', verbose_name=_('organization'))
    parent = models.ForeignKey('Organization', blank=True, null=True, on_delete=models.DO_NOTHING
                                   ,related_name='parent', verbose_name=_('parent organization'))

    class Meta:
        db_table = 'cmm_organization_rel'
        verbose_name = _('organization relation')
        verbose_name_plural = _('organization relation')
        permissions = [(EXPORT_CSV + '_' + db_table, 'Can export ' + db_table),
                       (IMPORT_CSV + '_' + db_table, 'Can import ' + db_table),
                      ]

        constraints = [
            models.UniqueConstraint(name = db_table + '_unique', fields = ['org', 'parent']),
        ]

    def __str__(self):
        return str(self.parent) + ' ' + str(self.org)

    def save(self, *args, **kwargs):
        # check circulated parenthood
        if self.parent:
            descendants = [desc.org.id for desc in get_descendants(self.parent.id)]
            if self.parent.id in descendants:
                raise RecursiveParenthoodError
        super().save(*args, **kwargs)

def get_descendants(org_id):
    """指定組織の全下部組織を取得する(自分自身は含まない)"""
    orgs = OrganizationRel.objects.raw("""
        with RECURSIVE org_rel(id, org_id) as (
            select id
                  ,org_id
              from cmm_organization_rel
             where parent_id = %(org_id)s
             union all
            select c.id
                  ,c.org_id
              from org_rel p
             inner join cmm_organization_rel c
                on p.org_id = c.parent_id
        )
        select id
              ,org_id
          from org_rel rel
    """, {'org_id': org_id})
    
    return list(orgs)
