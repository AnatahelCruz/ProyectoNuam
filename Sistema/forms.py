from django import forms
from .models import CalificacionTributaria

class CalificacionForm(forms.ModelForm):
    class Meta:
        model = CalificacionTributaria
        fields = ['contribuyente', 'monto']
