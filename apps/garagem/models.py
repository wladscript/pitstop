import re
from django.conf import settings
from django.db import models


def format_placa(placa: str) -> str:
    """Limpa e formata a placa (remove hífens e converte para maiúsculas)."""
    if not placa:
        return ""
    return re.sub(r"[^A-Za-z0-9]", "", placa).upper()


class Veiculo(models.Model):
    CATEGORIA_CHOICES = (
        ("Pequeno", "Pequeno (Hatch / Compacto)"),
        ("Médio", "Médio (Sedan / SUV Compacto)"),
        ("Grande", "Grande (Pickup / SUV Grande / Van)"),
    )

    cliente = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="veiculos",
        verbose_name="Proprietário / Cliente",
    )
    placa = models.CharField(
        "Placa do Veículo",
        max_length=10,
        db_index=True,
        help_text="Padrão Mercosul (ex: ABC1D23) ou antigo (ex: ABC1234)",
    )
    modelo = models.CharField("Modelo", max_length=80, help_text="Ex: Honda Civic, Chevrolet Onix")
    cor = models.CharField("Cor", max_length=40, help_text="Ex: Preto, Prata, Branco")
    ano = models.PositiveSmallIntegerField("Ano de Fabricação")
    categoria = models.CharField(
        "Categoria de Porte",
        max_length=15,
        choices=CATEGORIA_CHOICES,
        default="Médio",
        help_text="Define o multiplicador de preço dos serviços",
    )
    created_at = models.DateTimeField("Cadastrado em", auto_now_add=True)
    updated_at = models.DateTimeField("Atualizado em", auto_now=True)

    class Meta:
        verbose_name = "Veículo"
        verbose_name_plural = "Veículos"
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(fields=["cliente", "placa"], name="unique_veiculo_por_cliente")
        ]

    def __str__(self):
        return f"{self.modelo} ({self.placa_display}) - {self.cor}"

    def clean(self):
        super().clean()
        self.placa = format_placa(self.placa)

    def save(self, *args, **kwargs):
        self.placa = format_placa(self.placa)
        super().save(*args, **kwargs)

    @property
    def placa_display(self) -> str:
        """Formata placa para exibição bonita (ex: ABC-1234 ou ABC1D23)."""
        p = self.placa
        if len(p) == 7 and p[3].isdigit():
            # Formato antigo AAA9999 -> AAA-9999
            return f"{p[:3]}-{p[3:]}"
        return p
