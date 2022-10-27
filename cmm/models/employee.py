from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from cmm.models.base.admin import AuthUser
from cmm.models import CommonBaseTable, Organization


class Employee(CommonBaseTable):
    """職員マスタ"""
    code = models.CharField(max_length=64, blank=False, verbose_name=_('employee code'))
    name = models.CharField(max_length=128, blank=True, null=True, verbose_name=_('name'))
    name_kana = models.CharField(max_length=128, blank=True, null=True, verbose_name=_('name kana'))
    email = models.EmailField(max_length=254, blank=True, null=True, verbose_name=_('email'))
    employ_date = models.DateField(blank=False, default=timezone.now, verbose_name=_('employ date'))
    resign_date = models.DateField(blank=True, null=True, verbose_name=_('resign date'))
    resign_reason = models.CharField(max_length=128, blank=True, null=True, verbose_name=_('resign reason'))
    auth_user = models.ForeignKey(AuthUser, blank=True, null=True, on_delete=models.DO_NOTHING,
                                  verbose_name=_('authorization user'))
    organizations = models.ManyToManyField('Organization', through='OrgMember', verbose_name=_('organization'))

    class Meta:
        db_table = 'cmm_employee'
        verbose_name = _('employee')
        verbose_name_plural = _('employees')
        # permissions = [(EXPORT_CSV + '_employee', 'Can export employee csv'),
        #                (IMPORT_CSV + '_employee', 'Can import employee csv'),
        #               ]

        constraints = [
            models.UniqueConstraint(name = db_table + '_unique', fields = ['code']),
        ]
        ordering = ['code', ]

    def __str__(self):
        return self.name

    def main_duty_organization(self):
        """admin list viewで表示できる列を定義する"""
        main_duty_org = self.organizations.all().filter(orgmember__is_main_duty=True).first()
        return main_duty_org.name if main_duty_org is not None else None

    # admin list viewの列タイトルを定義する
    main_duty_organization.short_description = _('main duty organization')
    
class OrgMember(CommonBaseTable):
    """組織メンバー"""
    employee = models.ForeignKey(Employee, on_delete=models.DO_NOTHING, verbose_name=_('employee'))
    organization = models.ForeignKey(Organization, on_delete=models.DO_NOTHING, verbose_name=_('organization'))
    is_main_duty = models.BooleanField(blank=False, default=True, verbose_name=_('is main duty'))
    is_manager = models.BooleanField(blank=False, default=False, verbose_name=_('is manager'))  # 管理者
    is_staff = models.BooleanField(blank=False, default=False,verbose_name=_('is staff'))       # 組織内検索権限を持つメンバー

    class Meta:
        db_table = 'cmm_org_member'
        verbose_name = _('membership')
        verbose_name_plural = _('memberships')

        constraints = [
            models.UniqueConstraint(name = db_table + '_unique', fields = ['employee', 'organization']),
        ]

    def __str__(self):
        return self.employee.name + 'の' + ('本務' if self.is_main_duty else '兼務') + '組織'
