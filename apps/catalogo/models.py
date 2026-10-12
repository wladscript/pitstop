from decimal import Decimal, ROUND_HALF_UP
from django.db import models

CATEGORIA_MULTIPLIERS = {
    "Pequeno": Decimal("1.00"),
    "Médio": Decimal("1.30"),
    "Grande": Decimal("1.60"),
}


class Servico(models.Model):
    nome = models.CharField("Nome do Serviço", max_length=120)
    descricao = models.TextField("Descrição detalhada", blank=True)
    preco_base = models.DecimalField(
        "Preço Base (R$)",
        max_digits=10,
        decimal_places=2,
        help_text="Valor base para veículos de porte Pequeno",
    )
    duracao_estimada_minutos = models.PositiveIntegerField(
        "Duração estimada (minutos)",
        default=60,
    )
    is_ativo = models.BooleanField("Ativo para contratação", default=True)
    ordem_exibicao = models.PositiveSmallIntegerField("Ordem de exibição", default=0)
    created_at = models.DateTimeField("Criado em", auto_now_add=True)
    updated_at = models.DateTimeField("Atualizado em", auto_now=True)

    class Meta:
        verbose_name = "Serviço"
        verbose_name_plural = "Serviços"
        ordering = ["ordem_exibicao", "nome"]

    def __str__(self):
        return f"{self.nome} - R$ {self.preco_base}"

    def preco_para_categoria(self, categoria: str) -> Decimal:
        """Calcula o valor do serviço de acordo com a categoria do veículo."""
        mult = CATEGORIA_MULTIPLIERS.get(categoria, Decimal("1.00"))
        valor = (self.preco_base * mult).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        return valor
