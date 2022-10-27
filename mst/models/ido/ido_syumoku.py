from django.db import models
from django.utils.translation import gettext_lazy as _
from cmm.models import EXPORT_CSV, IMPORT_CSV, CommonBaseTable
from mst.models.ido import IdoType
from mst.models.ido.common import get_teiin_hijokin


class IdoSyumoku(CommonBaseTable, models.Model):
    """異動種目"""
    # code = DCIDOSMK_ORG.GRP_SEQ(2) + BUTTON_SEQ(2) + BUNKI1_SEQ(2) + BUNKI2_SEQ(2)
    code = models.CharField(max_length=8, blank=False, verbose_name=_('code'))
    name = models.CharField(max_length=128, blank=False, verbose_name=_('異動種目'))
    ido_type = models.ForeignKey(IdoType, on_delete=models.DO_NOTHING, blank=False, verbose_name=_('異動分類'))
    abbr = models.CharField(max_length=128, blank=True, null=True, verbose_name=_('abbreviation'))
    display_ctl = models.CharField(max_length=512, blank=True, null=True, verbose_name=_('画面制御'))
    display_order = models.IntegerField(blank=True, null=True, verbose_name=_('display order'))
    comment = models.CharField(max_length=128, blank=True, null=True, verbose_name=_('comment'))
    # deprecated
    nnmn_ido_cde = models.CharField(max_length=128, blank=True, null=True, verbose_name=_('任免異動種目区分'))
     
    class Meta:
        db_table = 'mst_ido_syumoku'
        verbose_name = _('異動種目')
        verbose_name_plural = _('異動種目')
        permissions = [(EXPORT_CSV + '_' + db_table, 'Can export ' + db_table),
                       (IMPORT_CSV + '_' + db_table, 'Can import ' + db_table),
        ]

        constraints = [
            models.UniqueConstraint(name = db_table + '_unique', fields = ['ido_type', 'code']),
        ]
        ordering = ['ido_type__display_order', 'code', 'display_order']

    def __str__(self):
        return self.name

    def teiin_hijokin(self):
        """定員・非常勤区分を取得する"""
        return get_teiin_hijokin(self.ido_type.code)

    teiin_hijokin.short_description = _('定員・非常勤')
