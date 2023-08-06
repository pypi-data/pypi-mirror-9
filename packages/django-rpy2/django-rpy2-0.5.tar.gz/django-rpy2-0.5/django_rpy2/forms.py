from django.contrib.admin import *
from django.forms import ModelForm, ChoiceField

from .models import *

class LateChoiceField(ChoiceField):
    def _get_choices(self):
        return self._choices

    def _set_choices(self, value):
        self._choices = self.widget.choices = value

    choices = property(_get_choices, _set_choices)

class LibraryForm(ModelForm):
    name = LateChoiceField(choices=AvailableLibrary.PACKAGES)

