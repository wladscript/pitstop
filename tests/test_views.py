from decimal import Decimal
import pytest
from django.urls import reverse
from apps.accounts.models import User
from apps.catalogo.models import Servico
from apps.garagem.models import Veiculo
from apps.ordens.models import OrdemServico
from apps.unidades.models import Unidade


@pytest.fixture
def cliente(db):
    return User.objects.create_user(
        telefone="11988887777",
        nome="Cliente Demo",
        password="demo123",
        role="cliente",
    )


@pytest.fixture
def admin(db):
    return User.objects.create_superuser(
        telefone="11999999999",
        nome="Admin Pit Stop",
        password="admin123",
    )


@pytest.fixture
def veiculo(db, cliente):
    return Veiculo.objects.create(
        cliente=cliente,
        placa="ABC1D23",
        modelo="Honda Civic",
        cor="Preto",
        ano=2022,
        categoria="Médio",
    )


@pytest.fixture
def unidade(db):
    return Unidade.objects.create(
        nome="Pit Stop Vila Olímpia",
        endereco="Rua Fradique Coutinho, 123",
        is_ativa=True,
        aceitando_pedidos=True,
    )


@pytest.fixture
def servico(db):
    return Servico.objects.create(
        nome="Lavagem Completa",
        descricao="Externa e interna",
        preco_base=Decimal("80.00"),
        is_ativo=True,
    )


@pytest.mark.django_db
class TestViewsFluxoCompleto:
    def test_welcome_page_exibe_dois_botoes(self, client):
        response = client.get(reverse("accounts:login"))
        assert response.status_code == 200
        content = response.content.decode("utf-8")
        assert "Cadastrar agora" in content
        assert "Já tenho cadastro" in content
        assert "Clube Fidelidade Pit Stop" in content

    def test_registro_novo_cliente(self, client):
        response = client.post(reverse("accounts:login"), {
            "action": "register",
            "nome": "Marcos Silva",
            "telefone": "(31) 98765-4321",
            "password": "senhaforte123",
            "password_confirm": "senhaforte123",
        })
        assert response.status_code == 302
        assert response.url == reverse("garagem:novo")

    def test_login_cliente_redireciona_garagem(self, client, cliente):
        response = client.post(reverse("accounts:login"), {
            "telefone": "11988887777",
            "password": "demo123",
        })
        assert response.status_code == 302
        assert response.url == reverse("garagem:lista")

    def test_login_admin_redireciona_kanban(self, client, admin):
        response = client.post(reverse("accounts:login"), {
            "telefone": "11999999999",
            "password": "admin123",
        })
        assert response.status_code == 302
        assert response.url == reverse("painel:kanban")

    def test_garagem_lista_requer_login(self, client):
        response = client.get(reverse("garagem:lista"))
        assert response.status_code == 302
        assert "/auth/login/" in response.url

    def test_cliente_acessa_garagem_e_veiculo(self, client, cliente, veiculo):
        client.force_login(cliente)
        response = client.get(reverse("garagem:lista"))
        assert response.status_code == 200
        assert "Honda Civic" in response.content.decode("utf-8")
        assert "ABC-1D23" in response.content.decode("utf-8")

    def test_cliente_cria_ordem_e_vai_para_pix(self, client, cliente, veiculo, unidade, servico):
        client.force_login(cliente)
        response = client.post(reverse("ordens:nova"), {
            "veiculo_id": veiculo.id,
            "unidade_id": unidade.id,
            "servico_ids": [servico.id],
            "logistica_entrada": "Entrega no local",
            "logistica_saida": "Retirada no local",
        })
        assert response.status_code == 302
        assert "/pagamentos/os/" in response.url
        assert "/pix/" in response.url

        # Acessa tela do Pix
        response_pix = client.get(response.url)
        assert response_pix.status_code == 200
        content = response_pix.content.decode("utf-8")
        assert "<svg" in content
        assert "Copiar Código Pix" in content

    def test_cliente_comum_bloqueado_no_painel_admin(self, client, cliente):
        client.force_login(cliente)
        response = client.get(reverse("painel:kanban"))
        # PermissionDenied -> status 403
        assert response.status_code == 403

    def test_admin_acessa_kanban_e_move_card_api(self, client, admin, cliente, veiculo, unidade, servico):
        # Cria OS
        from apps.ordens.services import criar_ordem_servico
        os = criar_ordem_servico(cliente, veiculo, unidade, [servico.id])

        client.force_login(admin)
        response_kanban = client.get(reverse("painel:kanban"))
        assert response_kanban.status_code == 200
        assert f"OS #{os.id:04d}" in response_kanban.content.decode("utf-8")

        # Mover para Preparação via API
        response_api = client.post(
            reverse("painel:mover_status_api", kwargs={"pk": os.id}),
            data={"status": "Preparação"},
            content_type="application/json",
        )
        assert response_api.status_code == 200
        data = response_api.json()
        assert data["ok"] is True
        assert data["status"] == "Preparação"

        # Tentar mover para Finalizado sem pagar deve falhar (regra 3)
        response_bloqueio = client.post(
            reverse("painel:mover_status_api", kwargs={"pk": os.id}),
            data={"status": "Finalizado"},
            content_type="application/json",
        )
        assert response_bloqueio.status_code == 400
        assert "pagamento ainda está pendente" in response_bloqueio.json()["error"]
