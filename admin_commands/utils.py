from django.core.management import get_commands, load_command_class

from .app_settings import ADMIN_COMMANDS_CONFIG


def sync_commands():
    from .models import ManagementCommand
    commands_dict = get_commands()
    allowed_commands = ADMIN_COMMANDS_CONFIG['allowed_commands']
    commands_in_db = list(ManagementCommand.objects.all().values_list('name', flat=True))
    default_args = ''
    if allowed_commands == 'all':
        commands = commands_dict.keys()
    else:
        commands = list(allowed_commands)

    for command in commands:
        if type(command) is tuple:
            command, default_args = command

        app_label = commands_dict.get(command, None)

        if not app_label:
            raise ValueError(f'Command {command} not found in management commands')
        else:
            command_class = load_command_class(app_label, command)
            c, created = ManagementCommand.objects.get_or_create(name=command, app_label=app_label)
            c.help = command_class.help
            c.default_args = default_args
            c.deleted = False
            c.save()
            if not created:
                commands_in_db.remove(command)
    ManagementCommand.objects.filter(name__in=commands_in_db).update(deleted=True)










