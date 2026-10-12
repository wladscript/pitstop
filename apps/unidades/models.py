from django.db import models


class Unidade(models.Model):
    nome = models.CharField("Nome da Unidade", max_length=120)
    endereco = models.CharField("Endereço Completo", max_length=255)
    is_ativa = models.BooleanField(
        "Ativa no Sistema",
        default=True,
        help_text="Se desativada, a unidade não aparece para novos agendamentos.",
    )
    aceitando_pedidos = models.BooleanField(
        "Aceitando Pedidos (Capacidade)",
        default=True,
        help_text="Kill-switch de lotação: quando falso, exibe aviso de capacidade máxima atingida.",
    )
    created_at = models.DateTimeField("Criado em", auto_now_add=True)
    updated_at = models.DateTimeField("Atualizado em", auto_now=True)

    class Meta:
        verbose_name = "Unidade"
        verbose_name_plural = "Unidades"
        ordering = ["nome"]

    def __str__(self):
        status = "Disponível" if self.disponivel else "Lotada / Fechada"
        return f"{self.nome} ({status})"

    @property
    def disponivel(self) -> bool:
        return self.is_ativa and self.aceitando_pedidos
