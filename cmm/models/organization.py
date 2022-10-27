from django.db import models
from django.utils.translation import gettext_lazy as _
from cmm.const import EXPORT_CSV, IMPORT_CSV, ORG_RANK
from cmm.models.base import CommonBaseTable
from cmm.models import Code


class Organization(CommonBaseTable):
    """組織マスタ"""
    code = models.CharField(max_length=64, blank=False, verbose_name=_('organization code'))
    name = models.CharField(max_length=128, blank=False, verbose_name=_('organization'))
    abbr = models.CharField(max_length=128, blank=True, null=True, verbose_name=_('abbreviation'))
    rank = models.ForeignKey(Code, on_delete=models.DO_NOTHING, blank=True, null=True,
                             limit_choices_to={'category__category': ORG_RANK},
                             verbose_name=_('organization hierarchy'))
    relation = models.ManyToManyField('self', blank=True
                        ,through='OrganizationRel', verbose_name=_('parent organization'))

    class Meta:
        db_table = 'cmm_organization'
        verbose_name = _('organization')
        verbose_name_plural = _('organizations')
        permissions = [(EXPORT_CSV + '_' + db_table, 'Can export ' + db_table),
                       (IMPORT_CSV + '_' + db_table, 'Can import ' + db_table),
                      ]

        constraints = [
            models.UniqueConstraint(name = db_table + '_unique', fields = ['code']),
        ]
 
    def __str__(self):
        return self.name

def get_all_upper_organizations():
    """上位組織リスト"""
    orgs = Organization.objects.raw("""
        select main.id
              ,main.code
              ,main.abbr
              ,main.rank_id
          from cmm_organization main
          left join cmm_code c
            on c.id = main.rank_id
         where c.code between '0' and '4'
           and exists (select 1
                         from cmm_organization_rel rel
                        where rel.parent_id = main.id)
         order by main.code nulls first
        """)
    return list(orgs)
