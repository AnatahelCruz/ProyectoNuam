from django import forms
from .models import CalificacionTributaria

class CalificacionForm(forms.ModelForm):
    class Meta:
        model = CalificacionTributaria
        fields = [
            'codigo_emisor', 'nombre_emisor', 'tipo_instrumento',
            'monto_bruto', 'monto_neto', 'retencion_impuesto',
            'fecha_emision', 'año_tributario', 'estado_calificacion',
            'observaciones'
        ]
        widgets = {
            'codigo_emisor': forms.TextInput(attrs={'class': 'form-control'}),
            'nombre_emisor': forms.TextInput(attrs={'class': 'form-control'}),
            'tipo_instrumento': forms.TextInput(attrs={'class': 'form-control'}),
            'monto_bruto': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'monto_neto': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'retencion_impuesto': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'fecha_emision': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'año_tributario': forms.NumberInput(attrs={'class': 'form-control'}),
            'estado_calificacion': forms.Select(attrs={'class': 'form-select'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

