from django.utils.translation import ugettext_lazy as _
from django import forms
from django.contrib.auth.models import User

class UserChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.get_display_name()

class ImportResultsForm(forms.Form):
    project = forms.IntegerField(required=False, widget=forms.HiddenInput())
    user = UserChoiceField(required=True, queryset=User.objects.all(), label=_('user'), widget=forms.Select(attrs={'style': 'width: 100%;'}), help_text=_('select a user'))
    file = forms.FileField(required=True, label=_('select a file'), widget=forms.FileInput(attrs={'class': 'filestyle', 'data-buttonText':_("choose file"), 'data-icon':'false'}))
