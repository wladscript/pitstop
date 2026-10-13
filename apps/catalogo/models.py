from decimal import Decimal, ROUND_HALF_UP
from django.db import models
from django.db.models import Q

CATEGORIA_MULTIPLIERS = {
    "Pequeno": Decimal("1.00"),
    "Médio": Decimal("1.30"),
    "Grande": Decimal("1.60"),
}


class ServicoQuerySet(models.QuerySet):
    def disponiveis_na_unidade(self, unidade):
        """
        Serviços oferecidos na unidade informada.
        Serviço sem nenhuma unidade vinculada = disponível em todas as unidades.
        """
        unidade_id = getattr(unidade, "pk", unidade)
        return self.filter(Q(unidades__isnull=True) | Q(unidades__pk=unidade_id)).distinct()


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
    unidades = models.ManyToManyField(
        "unidades.Unidade",
        verbose_name="Unidades onde é oferecido",
        related_name="servicos",
        blank=True,
        help_text="Deixe vazio para disponibilizar o serviço em todas as unidades.",
    )
    is_ativo = models.BooleanField("Ativo para contratação", default=True)
    ordem_exibicao = models.PositiveSmallIntegerField("Ordem de exibição", default=0)
    created_at = models.DateTimeField("Criado em", auto_now_add=True)
    updated_at = models.DateTimeField("Atualizado em", auto_now=True)

    class Meta:
        verbose_name = "Serviço"
        verbose_name_plural = "Serviços"
        ordering = ["ordem_exibicao", "nome"]

    objects = ServicoQuerySet.as_manager()

    def __str__(self):
        return f"{self.nome} - R$ {self.preco_base}"

    @property
    def todas_unidades(self) -> bool:
        return len(self.unidades.all()) == 0

    def disponivel_na_unidade(self, unidade) -> bool:
        unidade_id = getattr(unidade, "pk", unidade)
        ids = [u.pk for u in self.unidades.all()]
        return not ids or unidade_id in ids

    def preco_para_categoria(self, categoria: str) -> Decimal:
        """Calcula o valor do serviço de acordo com a categoria do veículo."""
        mult = CATEGORIA_MULTIPLIERS.get(categoria, Decimal("1.00"))
        valor = (self.preco_base * mult).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        return valor

    @property
    def preco_medio(self) -> Decimal:
        return self.preco_para_categoria("Médio")

    @property
    def preco_grande(self) -> Decimal:
        return self.preco_para_categoria("Grande")
