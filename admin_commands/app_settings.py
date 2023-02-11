from django.conf import settings
from django.utils.functional import lazy

ADMIN_COMMANDS_CONFIG_DEFAULTS = {
    'allowed_commands': [],
    'use_django_rq': False,
}

def get_admin_commands_settings():
    ADMIN_COMMANDS_CONFIG = getattr(settings, 'ADMIN_COMMANDS_CONFIG', ADMIN_COMMANDS_CONFIG_DEFAULTS.copy())
    ADMIN_COMMANDS_CONFIG.update(ADMIN_COMMANDS_CONFIG)
    return ADMIN_COMMANDS_CONFIG


ADMIN_COMMANDS_CONFIG = lazy(get_admin_commands_settings, dict)()



