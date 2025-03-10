from django import forms
from .models import ScannedMail

class ScanMailForm(forms.ModelForm):
    class Meta:
        model = ScannedMail
        fields = ['mail_image']
