from django import forms

from admin_commands.models import ManagementCommand


class ExecuteCommandForm(forms.Form):
    # command = forms.ModelChoiceField(ManagementCommand.objects.all())
    args = forms.CharField(required=False)
