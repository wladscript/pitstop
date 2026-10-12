from decimal import Decimal
from typing import List, Optional
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import transaction
from apps.catalogo.models import Servico
from apps.fidelidade.services import creditar_pontos_os
from apps.garagem.models import Veiculo
from apps.unidades.models import Unidade
from .models import OrdemServico, OrdemServicoItem

STATUS_FLOW = [
    OrdemServico.STATUS_NA_FILA,
    OrdemServico.STATUS_PREPARACAO,
    OrdemServico.STATUS_EXECUCAO,
    OrdemServico.STATUS_PRONTO,
    OrdemServico.STATUS_FINALIZADO,
]


def criar_ordem_servico(
    cliente,
    veiculo: Veiculo,
    unidade: Unidade,
    servico_ids: List[int],
    logistica_entrada: str = "Entrega no local",
    logistica_saida: str = "Retirada no local",
    enderecos: str = "",
    observacoes: str = "",
) -> OrdemServico:
    """
    Cria uma nova ordem de serviço com validações completas:
    - Valida permissão do veículo (pertence ao cliente);
    - Valida kill-switch de capacidade da unidade;
    - Impede OS vazia sem serviços;
    - Congela os preços unitários calculados para a categoria do veículo.
    """
    if veiculo.cliente_id != cliente.id and not cliente.is_admin:
        raise PermissionDenied("O veículo selecionado não pertence a este usuário.")

    if not unidade.disponivel:
        raise ValidationError("A unidade selecionada está operando na capacidade máxima no momento.")

    if not servico_ids:
        raise ValidationError("Selecione pelo menos um serviço para abrir o pedido.")

    servicos = list(Servico.objects.filter(id__in=servico_ids, is_ativo=True))
    if not servicos:
        raise ValidationError("Nenhum serviço válido foi selecionado.")

    with transaction.atomic():
        ordem = OrdemServico.objects.create(
            cliente=cliente,
            veiculo=veiculo,
            unidade=unidade,
            status=OrdemServico.STATUS_NA_FILA,
            status_pagamento=OrdemServico.PAGAMENTO_PENDENTE,
            logistica_entrada=logistica_entrada or "Entrega no local",
            logistica_saida=logistica_saida or "Retirada no local",
            enderecos=enderecos or "",
            observacoes=observacoes or "",
            valor_total=Decimal("0.00"),
        )

        total = Decimal("0.00")
        for servico in servicos:
            preco_item = servico.preco_para_categoria(veiculo.categoria)
            OrdemServicoItem.objects.create(
                ordem_servico=ordem,
                servico=servico,
                nome_servico=servico.nome,
                preco_aplicado=preco_item,
            )
            total += preco_item

        ordem.valor_total = total
        ordem.save(update_fields=["valor_total"])

        return ordem


def mudar_status_ordem(ordem: OrdemServico, novo_status: str, usuario=None) -> OrdemServico:
    """
    Altera o status da OS com validação de regras de transição e bloqueio de saída.
    """
    if novo_status not in STATUS_FLOW:
        raise ValidationError(f"Status '{novo_status}' inválido.")

    # Regra 3: Bloqueio na saída - Não pode Finalizado sem estar Pago
    if novo_status == OrdemServico.STATUS_FINALIZADO and not ordem.pode_finalizar:
        raise ValidationError("Não é possível liberar o veículo: o pagamento ainda está pendente.")

    antigo_status = ordem.status
    ordem.status = novo_status
    ordem.save(update_fields=["status", "updated_at"])

    # Dispara crédito de pontos de fidelidade na primeira vez que finaliza
    if novo_status == OrdemServico.STATUS_FINALIZADO and antigo_status != OrdemServico.STATUS_FINALIZADO:
        creditar_pontos_os(ordem)

    return ordem


def override_preco_ordem(ordem: OrdemServico, novo_valor: Decimal, usuario=None) -> OrdemServico:
    """
    Permite override manual de preço pelo admin, desde que a OS ainda não esteja paga.
    """
    if ordem.status_pagamento == OrdemServico.PAGAMENTO_PAGO:
        raise ValidationError("Não é possível alterar o valor de uma ordem de serviço já paga.")

    if novo_valor < Decimal("0.00"):
        raise ValidationError("O valor total não pode ser negativo.")

    ordem.valor_total = novo_valor
    ordem.override_preco = True
    ordem.save(update_fields=["valor_total", "override_preco", "updated_at"])
    return ordem


def marcar_pagamento_ordem(ordem: OrdemServico, novo_status: str, usuario=None) -> OrdemServico:
    """
    Atualiza o status de pagamento (Pendente ou Pago).
    """
    if novo_status not in [OrdemServico.PAGAMENTO_PENDENTE, OrdemServico.PAGAMENTO_PAGO]:
        raise ValidationError("Status de pagamento inválido.")

    ordem.status_pagamento = novo_status
    ordem.save(update_fields=["status_pagamento", "updated_at"])
    return ordem
