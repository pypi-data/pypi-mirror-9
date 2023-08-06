from django import forms
from .widgets import PopupGhostdownInput


class VersionAdminForm(forms.ModelForm):
    class Meta:
        widgets = {'release_notes': PopupGhostdownInput(value_path='raw')}
