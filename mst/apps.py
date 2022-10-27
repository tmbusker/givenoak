from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class MstConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'mst'
    verbose_name = _('mst')
