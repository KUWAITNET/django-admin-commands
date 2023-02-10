from io import StringIO

from django.contrib.auth import get_user_model
from django.core.management import load_command_class, call_command
from django.db import models
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _

User = get_user_model()


# Create your models here.
class ManagementCommand(models.Model):
    name = models.CharField(max_length=255, unique=True)
    app_label = models.CharField(max_length=255)
    help = models.TextField(default='')
    default_args = models.TextField(default='')
    deleted = models.BooleanField(default=False)

    class Meta:
        verbose_name = _('Management Command')
        verbose_name_plural = _('Management Commands')
        default_permissions = []
        permissions = [
            ('execute_command', _('Can execute command')),
        ]

    def __str__(self):
        return self.name

    def get_command(self):
        return load_command_class(self.app_label, self.name)

    def print_help(self):
        from io import StringIO

        command = self.get_command()

        out = StringIO()
        parser = command.create_parser(self.app_label, self.name)
        # parser.print_help(out)
        parser.print_usage(out)
        return out.getvalue()

    def execute(self, user, sys_args):
        log = CallCommandLog.objects.create(
            user=user,
            command=self,
            args=sys_args
        )
        out = StringIO()
        err = StringIO()
        args = [self.name]
        if sys_args:
            args.append(sys_args)
        try:
            call_command(*args, stdout=out, stderr=err)
        except Exception as e:
            err.write(str(e))

        log.output = out.getvalue()
        log.error = err.getvalue()
        log.finished = now()
        log.save()
        return


class CallCommandLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    command = models.ForeignKey(ManagementCommand, on_delete=models.CASCADE)
    started = models.DateTimeField(auto_now_add=True)
    finished = models.DateTimeField(null=True)
    args = models.TextField()
    output = models.TextField(default='')
    error = models.TextField(default='')

    class Meta:
        default_permissions = []
        permissions = [
            ('view_other_users_log', _('View other users log')),
        ]

    def __str__(self):
        return f'{self.command.name} - {self.started} -> {self.finished}'


