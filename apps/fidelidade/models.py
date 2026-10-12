from django.conf import settings
from django.db import models


class MovimentoFidelidade(models.Model):
    TIPO_CREDITO = "credito"
    TIPO_RESGATE = "resgate"
    TIPO_CHOICES = (
        (TIPO_CREDITO, "Crédito de Pontos"),
        (TIPO_RESGATE, "Resgate de Pontos"),
    )

    cliente = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="movimentos_fidelidade",
        verbose_name="Cliente",
    )
    # Garante vínculo único com a OS: uma OS nunca poderá creditar duas vezes!
    ordem_servico = models.OneToOneField(
        "ordens.OrdemServico",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="movimento_fidelidade",
        verbose_name="Ordem de Serviço de Origem",
    )
    pontos = models.PositiveIntegerField("Quantidade de Pontos")
    tipo = models.CharField("Tipo de Movimentação", max_length=15, choices=TIPO_CHOICES, default=TIPO_CREDITO)
    descricao = models.CharField("Descrição do Lançamento", max_length=255)
    created_at = models.DateTimeField("Data e Hora", auto_now_add=True)

    class Meta:
        verbose_name = "Movimentação de Fidelidade"
        verbose_name_plural = "Extrato de Fidelidade"
        ordering = ["-created_at"]

    def __str__(self):
        sinal = "+" if self.tipo == self.TIPO_CREDITO else "-"
        return f"{self.cliente.nome}: {sinal}{self.pontos} pts ({self.descricao})"
