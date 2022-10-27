from django.db import models
from django.utils.translation import gettext_lazy as _
from cmm.models import SimpleTable, Code, Organization
from mst.models.ido import IdoSyumoku


class Dkido(SimpleTable, models.Model):
    """異動情報"""
    ido_syumoku = models.ForeignKey(IdoSyumoku, on_delete=models.DO_NOTHING,
                                     blank=True, null=True, verbose_name=_('異動種目'))
    cshainno = models.CharField(max_length=32, blank=False, verbose_name=_('職員番号'))
    dhtreingb_dte = models.DateField(blank=True, null=True, verbose_name=_('発令年月日'))
    nnmn_ido_cde = models.CharField(max_length=80, blank=True, null=True)
    nnmn_ido_nme = models.CharField(max_length=80, blank=True, null=True)
    znsyk_kojin_cde = models.CharField(max_length=8, blank=True, null=True, verbose_name=_('前職指定個人番号'))
    # kyyo_syri_cde = models.CharField(max_length=2, blank=True, null=True)
    # kyyo_syri_nme = models.CharField(max_length=40, blank=True, null=True)
    cnamekna = models.CharField(max_length=40, blank=True, null=True, verbose_name=_('カナ氏名'))
    cnameknj = models.CharField(max_length=40, blank=True, null=True, verbose_name=_('漢字氏名'))
    seibetu_kbn = models.ForeignKey(Code, on_delete=models.DO_NOTHING, related_name='seibetu', blank=True, null=True,
                                  limit_choices_to={'category__category': '047'}, verbose_name=_('性別'))
    seibetu_nme = models.CharField(max_length=2, blank=True, null=True)
    # birth_dte = models.CharField(max_length=7, blank=True, null=True)
    dbirth_dte = models.DateField(blank=True, null=True, verbose_name=_('生年月日'))
    # age = models.DecimalField(max_digits=4, decimal_places=2, blank=True, null=True)
    # ndm_age = models.DecimalField(max_digits=4, decimal_places=2, blank=True, null=True)
    # saiyo_dte = models.CharField(max_length=7, blank=True, null=True)
    dsaiyo_dte = models.DateField(blank=True, null=True, verbose_name=_('採用年月日'))
    kkn_cde = models.ForeignKey(Code, on_delete=models.DO_NOTHING, related_name='kikan', blank=True, null=True,
                                  limit_choices_to={'category__category': '003'}, verbose_name=_('機関'))
    kkn_nme = models.CharField(max_length=80, blank=True, null=True)
    szk_cde = models.ForeignKey(Organization, on_delete=models.DO_NOTHING, related_name='shozoku', blank=True, null=True,
                                  verbose_name=_('所属'))
    szk_nme = models.CharField(max_length=80, blank=True, null=True)
    # bkyk_cde = models.CharField(max_length=80, blank=True, null=True)
    # bkyk_nme = models.CharField(max_length=80, blank=True, null=True)
    # sort_jyn = models.IntegerField(blank=True, null=True)
    kei_cde = models.ForeignKey(Code, on_delete=models.DO_NOTHING, related_name='kei', blank=True, null=True,
                                  limit_choices_to={'category__category': '005'}, verbose_name=_('系'))
    # kei_nme = models.CharField(max_length=80, blank=True, null=True)
    # kkrkoza_cde = models.CharField(max_length=6, blank=True, null=True)
    # kkrkoza_nme = models.CharField(max_length=80, blank=True, null=True)
    yosan_cde = models.ForeignKey(Code, on_delete=models.DO_NOTHING, related_name='yosanko', blank=True, null=True,
                                  limit_choices_to={'category__category': '007'}, verbose_name=_('予算項'))
    yosan_nme = models.CharField(max_length=80, blank=True, null=True)
    knmei_cde = models.ForeignKey(Code, on_delete=models.DO_NOTHING, related_name='kanmei', blank=True, null=True,
                                  limit_choices_to={'category__category': '008'}, verbose_name=_('官名'))
    knmei_nme = models.CharField(max_length=40, blank=True, null=True)
    syksy_cde = models.ForeignKey(Code, on_delete=models.DO_NOTHING, related_name='syokusyu', blank=True, null=True,
                                  limit_choices_to={'category__category': '052'}, verbose_name=_('職種'))
    syksy_nme = models.CharField(max_length=80, blank=True, null=True)
    kinmsaki_cde = models.ForeignKey(Code, on_delete=models.DO_NOTHING, related_name='kinmusaki', blank=True, null=True,
                                  limit_choices_to={'category__category': '012'}, verbose_name=_('採用直前の勤務先'))
    kinmsaki_nme = models.CharField(max_length=80, blank=True, null=True)
    nnki_cde = models.ForeignKey(Code, on_delete=models.DO_NOTHING, related_name='ninki', blank=True, null=True,
                                  limit_choices_to={'category__category': '116'}, verbose_name=_('任期区分'))
    nnki_nme = models.CharField(max_length=80, blank=True, null=True)
    nnki_mr_dte = models.DateField(blank=True, null=True)
    dnnki_mr_dte = models.CharField(max_length=7, blank=True, null=True, verbose_name=_('任期満了年月日'))
    tsykgo_cde = models.ForeignKey(Code, on_delete=models.DO_NOTHING, related_name='syusyokusaki', blank=True, null=True,
                                  limit_choices_to={'category__category': '052'}, verbose_name=_('退職等後の就職先等コード'))
    tsykgo_nme = models.CharField(max_length=80, blank=True, null=True)
    hkyh_cde = models.ForeignKey(Code, on_delete=models.DO_NOTHING, related_name='hokyuhyo', blank=True, null=True,
                                  limit_choices_to={'category__category': '053'}, verbose_name=_('俸給表'))
    hkyh_nme = models.CharField(max_length=40, blank=True, null=True)
    kyu = models.IntegerField(blank=True, null=True)
    kyu_ido_cde = models.ForeignKey(Code, on_delete=models.DO_NOTHING, related_name='kyu_ido', blank=True, null=True,
                                  limit_choices_to={'category__category': '016'}, verbose_name=_('級異動種目'))
    kyu_ido_nme = models.CharField(max_length=80, blank=True, null=True)
    goho = models.IntegerField(blank=True, null=True)
    goho_ido_cde = models.ForeignKey(Code, on_delete=models.DO_NOTHING, related_name='goho_ido', blank=True, null=True,
                                  limit_choices_to={'category__category': '017'}, verbose_name=_('号俸異動種目'))
    goho_ido_nme = models.CharField(max_length=80, blank=True, null=True)
    nxt_syky_dte = models.CharField(max_length=5, blank=True, null=True, verbose_name=_('次期昇給期'))

    class Meta:
        managed = True
        db_table = 'dkido'
