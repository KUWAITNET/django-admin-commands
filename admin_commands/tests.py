from django.test import TestCase, override_settings
from .models import ManagementCommand

class Tests(TestCase):

    @override_settings(ADMIN_COMMANDS_CONFIG={'allowed_commands': ['createsuperuser']})
    def test_sync_commands(self):
        from .utils import sync_commands
        sync_commands()
        qs = ManagementCommand.objects.all()
        self.assertEqual(qs.count(), 1)
        self.assertEqual(qs[0].name, 'createsuperuser')
        self.assertEqual(qs[0].app_label, 'django.contrib.auth')
        self.assertFalse(qs[0].deleted)

        @override_settings(ADMIN_COMMANDS_CONFIG={'allowed_commands': []})
        def test_remove_command():
            from .utils import sync_commands
            sync_commands()
            command = ManagementCommand.objects.get(name='createsuperuser')
            self.assertTrue(command.deleted)

        test_remove_command()



