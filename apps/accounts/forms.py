from django import forms
from django.contrib.auth import authenticate
from .models import User, clean_phone


class LoginForm(forms.Form):
    telefone = forms.CharField(
        label="Telefone / WhatsApp",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "(11) 99999-9999",
                "autofocus": True,
                "inputmode": "numeric",
            }
        ),
    )
    password = forms.CharField(
        label="Senha de Acesso",
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": "••••••••",
            }
        ),
    )

    def clean(self):
        cleaned_data = super().clean()
        telefone = clean_phone(cleaned_data.get("telefone", ""))
        password = cleaned_data.get("password")

        if telefone and password:
            try:
                user = User.objects.get(telefone=telefone)
                if not user.check_password(password):
                    raise forms.ValidationError("Telefone ou senha inválidos.")
                if not user.is_active:
                    raise forms.ValidationError("Esta conta está desativada.")
                self.user_cache = user
            except User.DoesNotExist:
                raise forms.ValidationError("Telefone ou senha inválidos.")
        return cleaned_data

    def get_user(self):
        return getattr(self, "user_cache", None)


class RegisterForm(forms.ModelForm):
    password = forms.CharField(
        label="Senha",
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": "Mínimo de 6 dígitos",
            }
        ),
        min_length=6,
    )
    password_confirm = forms.CharField(
        label="Confirmar Senha",
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": "Repita sua senha",
            }
        ),
    )

    class Meta:
        model = User
        fields = ("nome", "telefone")
        widgets = {
            "nome": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Ex: João Carlos Silva"}
            ),
            "telefone": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "(11) 99999-9999",
                    "inputmode": "numeric",
                }
            ),
        }

    def clean_telefone(self):
        telefone = clean_phone(self.cleaned_data.get("telefone"))
        if not telefone or len(telefone) < 10:
            raise forms.ValidationError("Informe um telefone válido com DDD (mínimo 10 dígitos).")
        if User.objects.filter(telefone=telefone).exists():
            raise forms.ValidationError("Este número de telefone já está cadastrado.")
        return telefone

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get("password")
        p2 = cleaned_data.get("password_confirm")
        if p1 and p2 and p1 != p2:
            self.add_error("password_confirm", "As senhas informadas não coincidem.")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user
