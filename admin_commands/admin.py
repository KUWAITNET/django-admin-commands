from django.contrib import admin
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseNotFound
from django.shortcuts import render
from django.urls import reverse
from django.utils.encoding import force_text
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from admin_commands.forms import ExecuteCommandForm
from admin_commands.models import ManagementCommand, CallCommandLog


class CommandAdminBase(admin.ModelAdmin):
    list_display = ['name', 'app_label', 'help', 'default_args', 'execute_command_link']
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
            form = ExecuteCommandForm(initial={'args': command.default_args})
            extra_context['form'] = form
        return super().changeform_view(request, object_id, form_url, extra_context)

    def execute_command_link(self, obj):
        return format_html('<a href="{}">{}</a>', reverse("admin:admin_commands_execute_command", args=[obj.pk]),
                           _('Execute'))

    execute_command_link.short_description = _('Execute command')

    def execute_command_and_return_response(self, request, command, args):
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
            form = ExecuteCommandForm(initial={'args': command.default_args})

        opts = self.model._meta
        context = dict(
            self.admin_site.each_context(request),
            module_name=force_text(opts.verbose_name_plural),
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


@admin.register(ManagementCommand)
class ManagementCommandAdmin(CommandAdminBase):
    pass


@admin.register(CallCommandLog)
class CallCommandAdmin(admin.ModelAdmin):
    list_display = ['command', 'args', 'user', 'started', 'finished', 'output', 'error']
    list_filter = ['command', 'user']

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
