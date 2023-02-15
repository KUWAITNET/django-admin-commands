from django import forms

from django.utils.translation import gettext_lazy as _


class ExecuteCommandForm(forms.Form):
    # command = forms.ModelChoiceField(ManagementCommand.objects.filter(deleted=False), label=_('Command'))
    args = forms.CharField(required=False, label=_('Arguments to send to command'))
