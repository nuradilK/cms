from django import forms

from .models import Submission


class SubmitForm(forms.ModelForm):

    class Meta:
        model = Submission
        fields = ('problem', 'language', 'source')
