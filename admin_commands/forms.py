from django import forms

from django.utils.translation import gettext_lazy as _


class ExecuteCommandForm(forms.Form):
    # command = forms.ModelChoiceField(ManagementCommand.objects.all())
    args = forms.CharField(required=False, label=_('Arguments'), help_text=_('Arguments for command'))
