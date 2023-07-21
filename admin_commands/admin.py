from django.contrib import admin
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseNotFound
from django.shortcuts import render
from django.template.defaultfilters import linebreaksbr
from django.urls import reverse
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from .app_settings import ADMIN_COMMANDS_CONFIG
from .forms import ExecuteCommandForm
from .models import ManagementCommand, CallCommandLog


class CommandAdminBase(admin.ModelAdmin):
    list_display = ['name', 'app_label', 'get_help', 'default_args', 'execute_command_link']
    readonly_fields = ['name', 'app_label', 'help']
    fields = ['name', 'app_label', 'help', 'default_args']
    actions = None
    list_filter = ['app_label']
    change_form_template = 'admin_commands/execute_command.html'

    def has_change_permission(self, request, obj=None):
        return request.user.has_perm("admin_commands.execute_command")

    def has_add_permission(self, request):
        return False

    def get_urls(self):
        from django.urls import path
        urls = super().get_urls()
        my_urls = [
            path('<object_id>/execute/', self.admin_site.admin_view(self.execute_command_view),
                 name='admin_commands_execute_command'),
        ]
        return my_urls + urls

    def changeform_view(self, request, object_id=None, form_url='', extra_context=None):
        extra_context = extra_context or {}
        command = self.get_object(request, object_id)
        if command is None:
            return HttpResponseNotFound()

        extra_context['command'] = command
        if request.method == 'GET':
            form = ExecuteCommandForm(initial={'command': command.pk})
            extra_context['form'] = form
        return super().changeform_view(request, object_id, form_url, extra_context)

    def get_help(self, obj):
        if not obj.help:
            return ''
        return format_html(linebreaksbr(obj.help))

    get_help.short_description = _('Help')

    def execute_command_link(self, obj):
        return format_html('<a href="{}">{}</a>', reverse("admin:admin_commands_execute_command", args=[obj.pk]),
                           _('Execute'))

    execute_command_link.short_description = _('Execute command')

    def execute_command_and_return_response(self, request, command, args):

        if ADMIN_COMMANDS_CONFIG['use_django_rq']:
            from django_rq import get_queue
            queue = get_queue('default')
            queue.enqueue(command.execute, request.user, args)
        else:
            command.execute(request.user, args)

        self.message_user(request, _('Command executed'))
        return self.response_post_save_add(request, command)

    def execute_command_view(self, request, object_id):
        command = self.get_object(request, object_id)
        if self.has_change_permission(request, command) is False:
            raise PermissionDenied

        if request.method == 'POST':
            form = ExecuteCommandForm(request.POST)
            if form.is_valid():
                return self.execute_command_and_return_response(request, command, form.cleaned_data['args'])

        else:
            form = ExecuteCommandForm(initial={'command': command.pk})

        opts = self.model._meta
        context = dict(
            self.admin_site.each_context(request),
            module_name=str(opts.verbose_name_plural),
            has_add_permission=self.has_add_permission(request),
            opts=opts,
            command=command,
            actions_on_top=self.actions_on_top,
            actions_on_bottom=self.actions_on_bottom,
            actions_selection_counter=self.actions_selection_counter,
            preserved_filters=self.get_preserved_filters(request),
            form=form,
        )
        return render(request, 'admin_commands/execute_command.html', context)

    def get_queryset(self, request):
        return super().get_queryset(request).filter(deleted=False)


@admin.register(ManagementCommand)
class ManagementCommandAdmin(CommandAdminBase):
    pass


@admin.register(CallCommandLog)
class CallCommandAdmin(admin.ModelAdmin):
    list_display = ['command', 'args', 'user', 'started', 'finished', 'get_output', 'get_error']
    list_filter = ['command', 'user']

    def get_output(self, obj):
        if not obj.output:
            return ''
        return format_html(linebreaksbr(obj.output))

    get_output.short_description = _('Output')

    def get_error(self, obj):
        if not obj.error:
            return ''
        return format_html(mark_safe(linebreaksbr(obj.error)))

    get_error.short_description = _('Error')

    def has_view_permission(self, request, obj=None):
        return request.user.has_perm("admin_commands.execute_command")

    def has_change_permission(self, request, obj=None):
        if obj:
            return False
        return request.user.has_perm("admin_commands.execute_command")

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if not request.user.has_perm("admin_commands.view_other_users_log"):
            qs = qs.filter(user=request.user)
        return qs
