from django import forms
from .models import Veiculo, format_placa


class VeiculoForm(forms.ModelForm):
    class Meta:
        model = Veiculo
        fields = ("placa", "modelo", "cor", "ano", "categoria")
        widgets = {
            "placa": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "ABC1D23",
                    "style": "text-transform: uppercase; letter-spacing: 0.1em; font-weight: 700;",
                    "maxlength": 8,
                }
            ),
            "modelo": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Ex: Honda Civic, Fiat Pulse"}
            ),
            "cor": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Ex: Preto, Prata, Branco"}
            ),
            "ano": forms.NumberInput(
                attrs={"class": "form-control", "placeholder": "Ex: 2022", "min": 1980, "max": 2030}
            ),
            "categoria": forms.Select(
                attrs={"class": "form-select"}
            ),
        }

    def clean_placa(self):
        placa = format_placa(self.cleaned_data.get("placa"))
        if len(placa) < 7:
            raise forms.ValidationError("Informe uma placa válida com 7 caracteres.")
        return placa
