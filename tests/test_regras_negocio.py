from decimal import Decimal
import pytest
from django.core.exceptions import ValidationError
from apps.accounts.models import User
from apps.catalogo.models import Servico
from apps.fidelidade.models import MovimentoFidelidade
from apps.garagem.models import Veiculo
from apps.garagem.services import consultar_placa
from apps.ordens.models import OrdemServico
from apps.ordens.services import (
    criar_ordem_servico,
    marcar_pagamento_ordem,
    mudar_status_ordem,
    override_preco_ordem,
)
from apps.pagamentos.services import _crc16, gerar_brcode_pix, gerar_dados_pix_os
from apps.unidades.models import Unidade


@pytest.fixture
def cliente_teste(db):
    return User.objects.create_user(
        telefone="11988881111",
        nome="Cliente Teste",
        password="senha",
    )


@pytest.fixture
def unidades_teste(db):
    u_ativa = Unidade.objects.create(
        nome="Unidade Ativa",
        endereco="Rua Teste, 100",
        is_ativa=True,
        aceitando_pedidos=True,
    )
    u_lotada = Unidade.objects.create(
        nome="Unidade Lotada",
        endereco="Rua Cheia, 200",
        is_ativa=True,
        aceitando_pedidos=False,
    )
    return u_ativa, u_lotada


@pytest.fixture
def servicos_teste(db):
    s1 = Servico.objects.create(
        nome="Lavagem Simples",
        preco_base=Decimal("50.00"),
        is_ativo=True,
    )
    s2 = Servico.objects.create(
        nome="Enceramento",
        preco_base=Decimal("100.00"),
        is_ativo=True,
    )
    return s1, s2


@pytest.mark.django_db
class TestRegrasNegocio:
    def test_regra_1_multiplicador_categoria(self, cliente_teste, unidades_teste, servicos_teste):
        u_ativa, _ = unidades_teste
        s1, s2 = servicos_teste

        # Pequeno (1.0x) -> 50.00 + 100.00 = 150.00
        v_pequeno = Veiculo.objects.create(
            cliente=cliente_teste, placa="AAA1A11", modelo="Ka", cor="Branco", ano=2020, categoria="Pequeno"
        )
        os_peq = criar_ordem_servico(cliente_teste, v_pequeno, u_ativa, [s1.id, s2.id])
        assert os_peq.valor_total == Decimal("150.00")

        # Médio (1.3x) -> 50 * 1.3 (65.00) + 100 * 1.3 (130.00) = 195.00
        v_medio = Veiculo.objects.create(
            cliente=cliente_teste, placa="BBB2B22", modelo="Civic", cor="Preto", ano=2021, categoria="Médio"
        )
        os_med = criar_ordem_servico(cliente_teste, v_medio, u_ativa, [s1.id, s2.id])
        assert os_med.valor_total == Decimal("195.00")

        # Grande (1.6x) -> 50 * 1.6 (80.00) + 100 * 1.6 (160.00) = 240.00
        v_grande = Veiculo.objects.create(
            cliente=cliente_teste, placa="CCC3C33", modelo="Hilux", cor="Prata", ano=2022, categoria="Grande"
        )
        os_gra = criar_ordem_servico(cliente_teste, v_grande, u_ativa, [s1.id, s2.id])
        assert os_gra.valor_total == Decimal("240.00")

    def test_regra_2_bloqueio_criacao_capacidade_maxima(self, cliente_teste, unidades_teste, servicos_teste):
        _, u_lotada = unidades_teste
        s1, _ = servicos_teste
        v = Veiculo.objects.create(
            cliente=cliente_teste, placa="DDD4D44", modelo="Onix", cor="Azul", ano=2019, categoria="Pequeno"
        )

        with pytest.raises(ValidationError, match="capacidade máxima"):
            criar_ordem_servico(cliente_teste, v, u_lotada, [s1.id])

    def test_regra_bloqueio_os_sem_servicos(self, cliente_teste, unidades_teste):
        u_ativa, _ = unidades_teste
        v = Veiculo.objects.create(
            cliente=cliente_teste, placa="EEE5E55", modelo="Polo", cor="Cinza", ano=2020, categoria="Pequeno"
        )

        with pytest.raises(ValidationError, match="pelo menos um serviço"):
            criar_ordem_servico(cliente_teste, v, u_ativa, [])

    def test_regra_3_bloqueio_saida_sem_pagamento(self, cliente_teste, unidades_teste, servicos_teste):
        u_ativa, _ = unidades_teste
        s1, _ = servicos_teste
        v = Veiculo.objects.create(
            cliente=cliente_teste, placa="FFF6F66", modelo="Compass", cor="Preto", ano=2022, categoria="Médio"
        )
        os = criar_ordem_servico(cliente_teste, v, u_ativa, [s1.id])
        assert os.status_pagamento == OrdemServico.PAGAMENTO_PENDENTE

        # Avança até Pronto
        mudar_status_ordem(os, OrdemServico.STATUS_PREPARACAO)
        mudar_status_ordem(os, OrdemServico.STATUS_EXECUCAO)
        mudar_status_ordem(os, OrdemServico.STATUS_PRONTO)

        # Tentar Finalizar sem pagar deve falhar!
        with pytest.raises(ValidationError, match="pagamento ainda está pendente"):
            mudar_status_ordem(os, OrdemServico.STATUS_FINALIZADO)

        # Marca como Pago e agora sim pode Finalizar
        marcar_pagamento_ordem(os, OrdemServico.PAGAMENTO_PAGO)
        os_finalizada = mudar_status_ordem(os, OrdemServico.STATUS_FINALIZADO)
        assert os_finalizada.status == OrdemServico.STATUS_FINALIZADO

    def test_regra_4_fidelidade_sem_duplicidade(self, cliente_teste, unidades_teste, servicos_teste):
        u_ativa, _ = unidades_teste
        s1, s2 = servicos_teste
        v = Veiculo.objects.create(
            cliente=cliente_teste, placa="GGG7G77", modelo="Corolla", cor="Branco", ano=2021, categoria="Pequeno"
        )
        # Valor 150.00 -> 15 pontos
        os = criar_ordem_servico(cliente_teste, v, u_ativa, [s1.id, s2.id])
        marcar_pagamento_ordem(os, OrdemServico.PAGAMENTO_PAGO)

        saldo_inicial = cliente_teste.pontos_fidelidade
        mudar_status_ordem(os, OrdemServico.STATUS_FINALIZADO)

        cliente_teste.refresh_from_db()
        assert cliente_teste.pontos_fidelidade == saldo_inicial + 15
        assert MovimentoFidelidade.objects.filter(ordem_servico=os).count() == 1

        # Tenta disparar finalização novamente (ou status alternado)
        mudar_status_ordem(os, OrdemServico.STATUS_FINALIZADO)
        cliente_teste.refresh_from_db()
        # Não pode ter creditado mais 15 pontos!
        assert cliente_teste.pontos_fidelidade == saldo_inicial + 15
        assert MovimentoFidelidade.objects.filter(ordem_servico=os).count() == 1

    def test_regra_5_override_preco_bloqueado_apos_pagamento(self, cliente_teste, unidades_teste, servicos_teste):
        u_ativa, _ = unidades_teste
        s1, _ = servicos_teste
        v = Veiculo.objects.create(
            cliente=cliente_teste, placa="HHH8H88", modelo="Gol", cor="Prata", ano=2018, categoria="Pequeno"
        )
        os = criar_ordem_servico(cliente_teste, v, u_ativa, [s1.id])

        # Permite override enquanto pendente
        override_preco_ordem(os, Decimal("45.00"))
        os.refresh_from_db()
        assert os.valor_total == Decimal("45.00")
        assert os.override_preco is True

        # Marca como pago
        marcar_pagamento_ordem(os, OrdemServico.PAGAMENTO_PAGO)

        # Bloqueia override após pago
        with pytest.raises(ValidationError, match="já paga"):
            override_preco_ordem(os, Decimal("30.00"))

    def test_regra_6_consulta_placa_mock(self):
        dados = consultar_placa("abc-1234")
        assert dados["placa"] == "ABC1234"
        assert dados["categoria"] in ["Pequeno", "Médio", "Grande"]
        assert dados["fonte"] == "mock"

    def test_regra_7_pix_brcode_e_svg(self, cliente_teste, unidades_teste, servicos_teste):
        u_ativa, _ = unidades_teste
        s1, _ = servicos_teste
        v = Veiculo.objects.create(
            cliente=cliente_teste, placa="III9I99", modelo="Uno", cor="Vermelho", ano=2015, categoria="Pequeno"
        )
        os = criar_ordem_servico(cliente_teste, v, u_ativa, [s1.id])
        dados_pix = gerar_dados_pix_os(os)

        copia_cola = dados_pix["copia_e_cola"]
        assert copia_cola.startswith("000201")
        assert "br.gov.bcb.pix" in copia_cola

        # Valida cálculo de CRC16
        payload_sem_crc = copia_cola[:-4]
        crc_esperado = _crc16(payload_sem_crc)
        assert copia_cola[-4:] == crc_esperado

        # Valida que gerou SVG inline do QR Code
        svg = dados_pix["qrcode_svg"]
        assert "<svg" in svg
        assert "</svg>" in svg
