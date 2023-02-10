from django.contrib.auth.models import User
from django.test import TestCase, override_settings
from .models import ManagementCommand


class Tests(TestCase):


    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.user1 = User.objects.create_superuser('superuser', password='password')
        cls.user1 = User.objects.create_user('user_w_permission', password='password')
        cls.user1 = User.objects.create_user('user_wo_permission', password='password')

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

    def test_permissions(self):
        pass

    def test_logs(self):
        pass