import logging
from django.db import transaction
from .models import MovimentoFidelidade

logger = logging.getLogger("pitstop.fidelidade")


def creditar_pontos_os(ordem) -> int:
    """
    Credita pontos de fidelidade para o cliente da OS finalizada.
    Regra: 1 ponto para cada R$ 10,00 pagos (mínimo 1 ponto).
    Proteção: se a OS já gerou crédito, não gera novamente.
    """
    with transaction.atomic():
        # Verifica se já existe crédito para esta OS
        if hasattr(ordem, "movimento_fidelidade") and ordem.movimento_fidelidade is not None:
            logger.info("OS #%s já possui crédito de fidelidade gerado anteriormente.", ordem.id)
            return 0

        # Verifica pelo model se já existe
        if MovimentoFidelidade.objects.filter(ordem_servico=ordem).exists():
            logger.info("OS #%s já possui crédito de fidelidade no banco.", ordem.id)
            return 0

        pontos = max(1, int(ordem.valor_total // 10))
        cliente = ordem.cliente

        MovimentoFidelidade.objects.create(
            cliente=cliente,
            ordem_servico=ordem,
            pontos=pontos,
            tipo=MovimentoFidelidade.TIPO_CREDITO,
            descricao=f"Crédito pela conclusão da OS #{ordem.id:04d}",
        )

        cliente.pontos_fidelidade += pontos
        cliente.save(update_fields=["pontos_fidelidade"])

        logger.info("[FIDELIDADE] +%s pontos creditados para %s (OS #%s)", pontos, cliente.nome, ordem.id)
        return pontos
