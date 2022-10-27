from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class CmmConfig(AppConfig):
    """Application configuration"""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'cmm'
    verbose_name = _('cmm')

    # pylint: disable = import-outside-toplevel
    def ready(self):
        # Implicitly connect signal handlers decorated with @receiver.
        from . import signals
        from django_auth_ldap.backend import populate_user
        # Explicitly connect a signal handler.
        populate_user.connect(signals.ldap_auth_handler)
