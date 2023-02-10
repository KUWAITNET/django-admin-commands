from django.contrib.auth.models import User, Permission
from django.test import TestCase, override_settings
from django.urls import reverse

from .models import ManagementCommand
from .utils import sync_commands


class Tests(TestCase):

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.user1 = User.objects.create_superuser('superuser', password='password')
        cls.user_w_permission = User.objects.create_user('user_w_permission', password='password', is_staff=True)
        cls.user_wo_permission = User.objects.create_user('user_wo_permission', password='password', is_staff=True)
        # add permissions to users
        cls.user_w_permission.user_permissions.add(Permission.objects.get(codename='execute_command'))
        cls.user_w_permission.user_permissions.add(Permission.objects.get(codename='view_other_users_log'))

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

    def check_pages(self, user, status_code):
        command_1 = ManagementCommand.objects.first()
        self.client.login(username=user, password='password')
        response = self.client.get(reverse('admin:admin_commands_managementcommand_changelist'))
        self.assertEqual(response.status_code, status_code)

        response = self.client.get(reverse('admin:admin_commands_managementcommand_change', args=(command_1.pk,)))
        self.assertEqual(response.status_code, status_code)
        response = self.client.get(reverse('admin:admin_commands_callcommandlog_changelist'))
        self.assertEqual(response.status_code, status_code)
        response = self.client.get(reverse('admin:admin_commands_execute_command', args=(command_1.pk,)))
        self.assertEqual(response.status_code, status_code)
        response = self.client.post(reverse('admin:admin_commands_execute_command', args=(command_1.pk,)))
        self.assertEqual(response.status_code, 302 if status_code == 200 else 403)
        self.client.logout()

    def test_permissions(self):
        sync_commands()
        command_1 = ManagementCommand.objects.first()
        command_1.execute(None, '')
        log = command_1.callcommandlog_set.first()

        self.check_pages('superuser', 200)
        self.check_pages('user_w_permission', 200)
        self.check_pages('user_wo_permission', 403)

        self.client.login(username='user_w_permission', password='password')
        response = self.client.get(reverse('admin:admin_commands_managementcommand_change', args=(0,)))
        self.assertEqual(response.status_code, 404)

        response = self.client.get(reverse('admin:admin_commands_callcommandlog_change', args=(log.pk,)))
        self.assertEqual(response.status_code, 200)
        response = self.client.post(reverse('admin:admin_commands_callcommandlog_change', args=(log.pk,)))
        self.assertEqual(response.status_code, 403)

    @override_settings(ADMIN_COMMANDS_CONFIG={'allowed_commands': ['ping_google']})
    def test_execute_command(self):
        # ping_google command would raise an error because the sitemap is mandatory
        # we test that the error is logged
        sync_commands()
        command_1 = ManagementCommand.objects.first()
        self.client.login(username='superuser', password='password')
        response = self.client.post(reverse('admin:admin_commands_execute_command', args=(command_1.pk,)))
        self.assertEqual(response.status_code, 302)
        log = command_1.callcommandlog_set.last()
        self.assertIn('sitemap_url', log.error)

    def test_wrong_settings(self):
        with self.assertRaises(ValueError):
            with override_settings(ADMIN_COMMANDS_CONFIG={'allowed_commands': 'wrong'}):
                sync_commands()

    def test_all_commands(self):
        with override_settings(ADMIN_COMMANDS_CONFIG={'allowed_commands': 'all'}):
            sync_commands()

        commands = list(ManagementCommand.objects.all().values_list('name', flat=True))
        self.assertIn('createsuperuser', commands)
        self.assertIn('ping_google', commands)
        self.assertIn('runserver', commands)
