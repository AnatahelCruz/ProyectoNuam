from django import forms
from .models import CalificacionTributaria, Instrumento

class CalificacionForm(forms.ModelForm):
    nuevo_instrumento = forms.CharField(
        required=True,
        label="Instrumento",
        widget=forms.TextInput(attrs={'placeholder': 'Ingresar instrumento'})
    )

    class Meta:
        model = CalificacionTributaria
        fields = [
            'mercado',
            'nuevo_instrumento',
            'descripcion',
            'fecha_pago',
            'secuencia_evento',
            'dividendo',
            'valor_historico',
            'factor_actualizacion',
            'anio',
            'isfut'
        ]
        widgets = {
            'fecha_pago': forms.DateInput(attrs={'type': 'date'}),
            'descripcion': forms.Textarea(attrs={'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.instrumento:
            self.fields["nuevo_instrumento"].initial = self.instance.instrumento.nombre

    def save(self, commit=True):
        instrumento_nombre = self.cleaned_data.get("nuevo_instrumento").strip()

        instrumento, _ = Instrumento.objects.get_or_create(nombre=instrumento_nombre)
        self.instance.instrumento = instrumento

        return super().save(commit)
