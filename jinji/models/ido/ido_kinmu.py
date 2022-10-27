from tabnanny import verbose
from django.db import models
from django.utils.translation import gettext_lazy as _

from cmm.models import Code
from cmm.models.base import CommonBaseTable
from mst.models.ido import Dkido


class IdoKinmu(CommonBaseTable, models.Model):
    """勤務情報"""
    dkido = models.OneToOneField(Dkido, on_delete=models.CASCADE, blank=False, verbose_name=_('異動情報'))
    jikan_cde = models.ForeignKey(Code, on_delete=models.DO_NOTHING, related_name='jikan', blank=True, null=True,
                                  limit_choices_to={'category__category': '611'}, verbose_name=_('勤務時間帯区分'))
    # jikan_nme = models.CharField(max_length=80, blank=True, null=True, verbose_name=_(''))
    kyujitu_cde = models.ForeignKey(Code, on_delete=models.DO_NOTHING, related_name='kyujitu', blank=True, null=True,
                                   limit_choices_to={'category__category': 'J11'}, verbose_name=_('休日区分'))
    # kyujitu_nme = models.CharField(max_length=80, blank=True, null=True, verbose_name=_(''))
    kinmu_keitai = models.IntegerChoices('勤務形態', '標準時間勤務 変形時間勤務 勤務情報は別途作成')
    kinmu_start_hyojun = models.CharField(max_length=5, blank=True, null=True, verbose_name=_('標準勤務開始時刻'))
    kinmu_end_hyojun = models.CharField(max_length=5, blank=True, null=True, verbose_name=_('標準勤務終了時刻'))
    kyukei_start_hyojun = models.CharField(max_length=5, blank=True, null=True, verbose_name=_('標準休憩開始時刻'))
    kyukei_end_hyojun = models.CharField(max_length=5, blank=True, null=True, verbose_name=_('標準休憩終了時刻'))
    num_w_hyojun = models.DecimalField(max_digits=4, decimal_places=2, blank=True, null=True, verbose_name=_('標準勤務時間'))
    yobi1 = models.BooleanField(blank=True, null=True, verbose_name=_('月'))
    kinmu_start1 = models.CharField(max_length=5, blank=True, null=True, verbose_name=_('勤務開始時刻'))
    kinmu_end1 = models.CharField(max_length=5, blank=True, null=True, verbose_name=_('勤務終了時刻'))
    kyukei_start1 = models.CharField(max_length=5, blank=True, null=True, verbose_name=_('休憩開始時刻'))
    kyukei_end1 = models.CharField(max_length=5, blank=True, null=True, verbose_name=_('休憩終了時刻'))
    num_w1 = models.DecimalField(max_digits=4, decimal_places=2, blank=True, null=True, verbose_name=_('勤務時間'))
    yobi2 = models.CharField(max_length=1, blank=True, null=True, verbose_name=_('火'))
    kinmu_start2 = models.CharField(max_length=5, blank=True, null=True, verbose_name=_('勤務開始時刻'))
    kinmu_end2 = models.CharField(max_length=5, blank=True, null=True, verbose_name=_('勤務終了時刻'))
    kyukei_start2 = models.CharField(max_length=5, blank=True, null=True, verbose_name=_('休憩開始時刻'))
    kyukei_end2 = models.CharField(max_length=5, blank=True, null=True, verbose_name=_('休憩終了時刻'))
    num_w2 = models.DecimalField(max_digits=4, decimal_places=2, blank=True, null=True, verbose_name=_('勤務時間'))
    yobi3 = models.CharField(max_length=1, blank=True, null=True, verbose_name=_('水'))
    kinmu_start3 = models.CharField(max_length=5, blank=True, null=True, verbose_name=_('勤務開始時刻'))
    kinmu_end3 = models.CharField(max_length=5, blank=True, null=True, verbose_name=_('勤務終了時刻'))
    kyukei_start3 = models.CharField(max_length=5, blank=True, null=True, verbose_name=_('休憩開始時刻'))
    kyukei_end3 = models.CharField(max_length=5, blank=True, null=True, verbose_name=_('休憩終了時刻'))
    num_w3 = models.DecimalField(max_digits=4, decimal_places=2, blank=True, null=True, verbose_name=_('勤務時間'))
    yobi4 = models.CharField(max_length=1, blank=True, null=True, verbose_name=_('木'))
    kinmu_start4 = models.CharField(max_length=5, blank=True, null=True, verbose_name=_('勤務開始時刻'))
    kinmu_end4 = models.CharField(max_length=5, blank=True, null=True, verbose_name=_('勤務終了時刻'))
    kyukei_start4 = models.CharField(max_length=5, blank=True, null=True, verbose_name=_('休憩開始時刻'))
    kyukei_end4 = models.CharField(max_length=5, blank=True, null=True, verbose_name=_('休憩終了時刻'))
    num_w4 = models.DecimalField(max_digits=4, decimal_places=2, blank=True, null=True, verbose_name=_('勤務時間'))
    yobi5 = models.CharField(max_length=1, blank=True, null=True, verbose_name=_('金'))
    kinmu_start5 = models.CharField(max_length=5, blank=True, null=True, verbose_name=_('勤務開始時刻'))
    kinmu_end5 = models.CharField(max_length=5, blank=True, null=True, verbose_name=_('勤務終了時刻'))
    kyukei_start5 = models.CharField(max_length=5, blank=True, null=True, verbose_name=_('休憩開始時刻'))
    kyukei_end5 = models.CharField(max_length=5, blank=True, null=True, verbose_name=_('休憩終了時刻'))
    num_w5 = models.DecimalField(max_digits=4, decimal_places=2, blank=True, null=True, verbose_name=_('勤務時間'))
    yobi6 = models.CharField(max_length=1, blank=True, null=True, verbose_name=_('土'))
    kinmu_start6 = models.CharField(max_length=5, blank=True, null=True, verbose_name=_('勤務開始時刻'))
    kinmu_end6 = models.CharField(max_length=5, blank=True, null=True, verbose_name=_('勤務終了時刻'))
    kyukei_start6 = models.CharField(max_length=5, blank=True, null=True, verbose_name=_('休憩開始時刻'))
    kyukei_end6 = models.CharField(max_length=5, blank=True, null=True, verbose_name=_('休憩終了時刻'))
    num_w6 = models.DecimalField(max_digits=4, decimal_places=2, blank=True, null=True, verbose_name=_('勤務時間'))
    yobi7 = models.CharField(max_length=1, blank=True, null=True, verbose_name=_('日'))
    kinmu_start7 = models.CharField(max_length=5, blank=True, null=True, verbose_name=_('勤務開始時刻'))
    kinmu_end7 = models.CharField(max_length=5, blank=True, null=True, verbose_name=_('勤務終了時刻'))
    kyukei_start7 = models.CharField(max_length=5, blank=True, null=True, verbose_name=_('休憩開始時刻'))
    kyukei_end7 = models.CharField(max_length=5, blank=True, null=True, verbose_name=_('休憩終了時刻'))
    num_w7 = models.DecimalField(max_digits=4, decimal_places=2, blank=True, null=True, verbose_name=_('勤務時間'))
    num_week = models.DecimalField(max_digits=4, decimal_places=2, blank=True, null=True, verbose_name=_('週勤務時間'))
    days_week = models.BooleanField(blank=True, null=True, verbose_name=_('週勤務日数'))

    class Meta:
        # managed = True
        db_table = 'mst_ido_kinmu'
        verbose_name = _('勤務情報')
        verbose_name_plural = _('勤務情報')

        constraints = [
            models.UniqueConstraint(name = db_table + '_unique', fields = ['dkido']),
        ]
