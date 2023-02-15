from django.apps import AppConfig
from django.db import OperationalError, ProgrammingError
from django.utils.translation import gettext_lazy as _


class AdminCommandsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'admin_commands'
    verbose_name = _('Admin Commands')

    def ready(self):
        super().ready()
        from .utils import sync_commands
        try:
            sync_commands()
        except (OperationalError, ProgrammingError):  # pragma: no cover Before first migrations
            pass
