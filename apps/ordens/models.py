from decimal import Decimal
from django.conf import settings
from django.db import models
from apps.catalogo.models import Servico
from apps.garagem.models import Veiculo
from apps.unidades.models import Unidade


class OrdemServico(models.Model):
    STATUS_NA_FILA = "Na Fila"
    STATUS_EXECUCAO = "Execução"
    STATUS_PRONTO = "Pronto"

    # Constantes legadas para compatibilidade
    STATUS_PREPARACAO = "Preparação"
    STATUS_FINALIZADO = "Finalizado"

    STATUS_CHOICES = (
        (STATUS_NA_FILA, "Na Fila"),
        (STATUS_EXECUCAO, "Execução"),
        (STATUS_PRONTO, "Pronto"),
    )

    PAGAMENTO_PENDENTE = "Pendente"
    PAGAMENTO_PAGO = "Pago"

    PAGAMENTO_CHOICES = (
        (PAGAMENTO_PENDENTE, "Pendente"),
        (PAGAMENTO_PAGO, "Pago"),
    )

    cliente = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="ordens_servico",
        verbose_name="Cliente",
    )
    veiculo = models.ForeignKey(
        Veiculo,
        on_delete=models.PROTECT,
        related_name="ordens_servico",
        verbose_name="Veículo",
    )
    unidade = models.ForeignKey(
        Unidade,
        on_delete=models.PROTECT,
        related_name="ordens_servico",
        verbose_name="Unidade Executora",
    )
    status = models.CharField(
        "Status Operacional",
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_NA_FILA,
        db_index=True,
    )
    status_pagamento = models.CharField(
        "Status do Pagamento",
        max_length=15,
        choices=PAGAMENTO_CHOICES,
        default=PAGAMENTO_PENDENTE,
        db_index=True,
    )
    logistica_entrada = models.CharField(
        "Logística de Entrada",
        max_length=80,
        default="Entrega no local",
    )
    logistica_saida = models.CharField(
        "Logística de Saída",
        max_length=80,
        default="Retirada no local",
    )
    enderecos = models.CharField(
        "Endereço para Leva e Traz (se aplicável)",
        max_length=255,
        blank=True,
        default="",
    )
    valor_total = models.DecimalField(
        "Valor Total (R$)",
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
    )
    override_preco = models.BooleanField(
        "Preço Alterado Manualmente pelo Admin",
        default=False,
    )
    observacoes = models.TextField("Observações do Pedido", blank=True, default="")
    created_at = models.DateTimeField("Data de Abertura", auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField("Última Atualização", auto_now=True)

    class Meta:
        verbose_name = "Ordem de Serviço"
        verbose_name_plural = "Ordens de Serviço"
        ordering = ["-created_at"]

    def __str__(self):
        return f"OS #{self.id:04d} - {self.veiculo.modelo} ({self.status})"

    @property
    def codigo_formatado(self) -> str:
        return f"OS #{self.id:04d}"

    @property
    def pode_finalizar(self) -> bool:
        """Só pode finalizar se o pagamento estiver confirmado como Pago."""
        return self.status_pagamento == self.PAGAMENTO_PAGO


class OrdemServicoItem(models.Model):
    ordem_servico = models.ForeignKey(
        OrdemServico,
        on_delete=models.CASCADE,
        related_name="itens",
        verbose_name="Ordem de Serviço",
    )
    servico = models.ForeignKey(
        Servico,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="itens_os",
        verbose_name="Serviço Contratado",
    )
    nome_servico = models.CharField("Nome do Serviço (Snapshot)", max_length=120)
    preco_aplicado = models.DecimalField(
        "Preço Cobrado (R$)",
        max_digits=10,
        decimal_places=2,
    )

    class Meta:
        verbose_name = "Item da Ordem de Serviço"
        verbose_name_plural = "Itens da Ordem de Serviço"

    def __str__(self):
        return f"{self.nome_servico} (R$ {self.preco_aplicado})"
