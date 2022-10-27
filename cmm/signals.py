from django.dispatch import receiver
from django_auth_ldap.backend import populate_user, LDAPBackend

from cmm.models import Employee


@receiver(populate_user, sender=LDAPBackend)
def ldap_auth_handler(user, ldap_user, **kwargs):
    """LDAP連携情報に基づいて職員情報を更新する"""
    name = ldap_user.attrs._data.get('name')[0]
    employee, created = Employee.objects.get_or_create(name = name)
    if created:
        employee.auth_user = user
        employee.name = name
