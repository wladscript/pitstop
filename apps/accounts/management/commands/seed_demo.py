from decimal import Decimal
from django.conf import settings
from django.core.management.base import BaseCommand
from apps.accounts.models import User
from apps.catalogo.models import Servico
from apps.garagem.models import Veiculo
from apps.ordens.models import OrdemServico, OrdemServicoItem
from apps.ordens.services import criar_ordem_servico, mudar_status_ordem, marcar_pagamento_ordem
from apps.unidades.models import Unidade


class Command(BaseCommand):
    help = "Popula o banco de dados com dados iniciais e de demonstração (Admin, Cliente, Veículos, Unidades, Serviços e OSs)"

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Iniciando seed de dados do Pit Stop..."))

        # 1. Usuário Administrador
        admin_tel = settings.ADMIN_PHONE
        admin_user = User.objects.filter(role="admin").first()
        if not admin_user:
            admin_user = User.objects.create_superuser(
                telefone=admin_tel,
                nome=getattr(settings, "ADMIN_NAME", "Administrador Pit Stop"),
                password=settings.ADMIN_PASSWORD,
            )
            self.stdout.write(self.style.SUCCESS(f"✔ Admin criado: {admin_user.telefone} / {settings.ADMIN_PASSWORD}"))
        else:
            admin_user.telefone = admin_tel
            admin_user.nome = getattr(settings, "ADMIN_NAME", "Administrador Pit Stop")
            admin_user.set_password(settings.ADMIN_PASSWORD)
            admin_user.save()
            self.stdout.write(f"ℹ Admin atualizado: {admin_user.telefone}")

        # 2. Cliente Demo
        demo_tel = settings.DEMO_PHONE
        demo_user = User.objects.filter(role="cliente").first()
        if not demo_user:
            demo_user = User.objects.create_user(
                telefone=demo_tel,
                nome=getattr(settings, "DEMO_NAME", "Cliente Demonstração"),
                password=settings.DEMO_PASSWORD,
                role="cliente",
                pontos_fidelidade=120,
            )
            self.stdout.write(self.style.SUCCESS(f"✔ Cliente Demo criado: {demo_user.telefone} / {settings.DEMO_PASSWORD}"))
        else:
            demo_user.telefone = demo_tel
            demo_user.nome = getattr(settings, "DEMO_NAME", "Cliente Demonstração")
            demo_user.set_password(settings.DEMO_PASSWORD)
            demo_user.save()
            self.stdout.write(f"ℹ Cliente Demo atualizado: {demo_user.telefone}")

        # 3. Veículos do Cliente Demo
        v1, _ = Veiculo.objects.get_or_create(
            cliente=demo_user,
            placa="ABC1D23",
            defaults={"modelo": "Honda Civic", "cor": "Preto", "ano": 2022, "categoria": "Médio"},
        )
        v2, _ = Veiculo.objects.get_or_create(
            cliente=demo_user,
            placa="XYZ4E56",
            defaults={"modelo": "Jeep Compass", "cor": "Prata", "ano": 2021, "categoria": "Grande"},
        )
        self.stdout.write(self.style.SUCCESS("✔ Veículos de demonstração cadastrados (Honda Civic, Jeep Compass)"))

        # 4. Unidades
        u1, _ = Unidade.objects.get_or_create(
            nome="Pit Stop • Eldorado",
            defaults={
                "endereco": "Rua Felisberta Francisca de Carvalho, 494 - Eldorado - Contagem - MG",
                "is_ativa": True,
                "aceitando_pedidos": True,
            },
        )
        u2, _ = Unidade.objects.get_or_create(
            nome="Pit Stop • Alvorada",
            defaults={
                "endereco": "Av. José Luís da Cunha, 79 - Alvorada - Contagem - MG",
                "is_ativa": True,
                "aceitando_pedidos": True,
            },
        )
        self.stdout.write(self.style.SUCCESS("✔ Unidades cadastradas (Eldorado e Alvorada)"))

        # 5. Serviços do Catálogo
        servicos_data = [
            ("Lavagem Simples", "Lavagem externa com cera rápida e secagem técnica", Decimal("40.00"), 45, 1),
            ("Lavagem Completa", "Externa + interna detalhada + aspiração e painel", Decimal("80.00"), 75, 2),
            ("Enceramento Premium", "Descontaminação da pintura + cera nobre de carnaúba", Decimal("180.00"), 120, 3),
            ("Detalhamento Completo", "Estética automotiva full detail: motor, chassi e verniz", Decimal("350.00"), 240, 4),
        ]
        servicos_criados = []
        for nome, desc, preco, duracao, ordem in servicos_data:
            serv, _ = Servico.objects.get_or_create(
                nome=nome,
                defaults={
                    "descricao": desc,
                    "preco_base": preco,
                    "duracao_estimada_minutos": duracao,
                    "ordem_exibicao": ordem,
                    "is_ativo": True,
                },
            )
            servicos_criados.append(serv)

        # Serviço exclusivo de unidade: Lanternagem só existe na Alvorada
        lanternagem, _ = Servico.objects.get_or_create(
            nome="Lanternagem",
            defaults={
                "descricao": "Reparo de amassados, desempeno e recuperação de lataria",
                "preco_base": Decimal("250.00"),
                "duracao_estimada_minutos": 480,
                "ordem_exibicao": 5,
                "is_ativo": True,
            },
        )
        lanternagem.unidades.set([u2])
        servicos_criados.append(lanternagem)
        self.stdout.write(self.style.SUCCESS(f"✔ {len(servicos_criados)} Serviços cadastrados no catálogo"))

        # 6. Ordens de Serviço demonstrativas para o Kanban (se o banco estiver vazio de OSs)
        if not OrdemServico.objects.exists():
            # OS 1: Na Fila
            criar_ordem_servico(
                cliente=demo_user,
                veiculo=v1,
                unidade=u1,
                servico_ids=[servicos_criados[1].id],  # Lavagem Completa
                logistica_entrada="Entrega no local",
                logistica_saida="Retirada no local",
                observacoes="Atenção especial às rodas aro 18.",
            )

            # OS 2: Em Execução
            os2 = criar_ordem_servico(
                cliente=demo_user,
                veiculo=v2,
                unidade=u2,
                servico_ids=[servicos_criados[2].id],  # Enceramento Premium
                logistica_entrada="Leva e Traz",
                logistica_saida="Leva e Traz",
                enderecos="Av. Faria Lima, 3500",
                observacoes="Cliente aguarda finalização até às 17h.",
            )
            mudar_status_ordem(os2, OrdemServico.STATUS_EXECUCAO)

            # OS 3: Pronto (Pago)
            os3 = criar_ordem_servico(
                cliente=demo_user,
                veiculo=v1,
                unidade=u1,
                servico_ids=[servicos_criados[0].id],  # Lavagem Simples
            )
            mudar_status_ordem(os3, OrdemServico.STATUS_EXECUCAO)
            mudar_status_ordem(os3, OrdemServico.STATUS_PRONTO)
            marcar_pagamento_ordem(os3, OrdemServico.PAGAMENTO_PAGO)

            self.stdout.write(self.style.SUCCESS("✔ 3 Ordens de Serviço criadas para preencher o Kanban inicial"))

        self.stdout.write(self.style.SUCCESS("\n🎉 Seed concluído com sucesso!"))
        self.stdout.write(f"👉 Acesso Admin: Telefone: {admin_tel} | Senha: {settings.ADMIN_PASSWORD}")
        self.stdout.write(f"👉 Acesso Demo:  Telefone: {demo_tel} | Senha: {settings.DEMO_PASSWORD}\n")
