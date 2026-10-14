import json
from decimal import Decimal, InvalidOperation
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Count, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from apps.accounts.models import User
from apps.catalogo.models import Servico
from apps.ordens.models import OrdemServico
from apps.ordens.services import (
    marcar_pagamento_ordem,
    mudar_status_ordem,
    override_preco_ordem,
)
from apps.unidades.models import Unidade
from .decorators import admin_required


@admin_required
def kanban_view(request):
    unidades = Unidade.objects.all()
    unidade_id = request.GET.get("unidade")

    ordens_qs = (
        OrdemServico.objects.select_related("cliente", "veiculo", "unidade")
        .prefetch_related("itens")
        .order_by("-updated_at")
    )

    unidade_selecionada = None
    if unidade_id:
        try:
            uid = int(unidade_id)
            ordens_qs = ordens_qs.filter(unidade_id=uid)
            unidade_selecionada = next((u for u in unidades if u.id == uid), None)
        except (ValueError, TypeError):
            pass

    colunas = [
        {"id": "nafila", "nome": OrdemServico.STATUS_NA_FILA, "badge_class": "badge-nafila", "cards": []},
        {"id": "execucao", "nome": OrdemServico.STATUS_EXECUCAO, "badge_class": "badge-execucao", "cards": []},
        {"id": "pronto", "nome": OrdemServico.STATUS_PRONTO, "badge_class": "badge-pronto", "cards": []},
    ]

    col_map = {col["nome"]: col["cards"] for col in colunas}
    for os in ordens_qs:
        if os.status in col_map:
            col_map[os.status].append(os)

    return render(
        request,
        "painel/kanban.html",
        {
            "colunas": colunas,
            "unidades": unidades,
            "unidade_selecionada": unidade_selecionada,
            "total_ordens": ordens_qs.count(),
        },
    )


@admin_required
def mover_status_api(request, pk):
    """
    API JSON para movimentação de cards no Kanban via Drag & Drop ou Botão.
    Valida regra de pagamento antes de finalizar!
    """
    if request.method != "POST":
        return JsonResponse({"error": "Método não permitido"}, status=405)

    try:
        data = json.loads(request.body.decode("utf-8")) if request.body else {}
        novo_status = data.get("status")
        if not novo_status:
            return JsonResponse({"error": "Status não fornecido"}, status=400)

        ordem = get_object_or_404(OrdemServico, pk=pk)
        mudar_status_ordem(ordem, novo_status, usuario=request.user)

        return JsonResponse(
            {
                "ok": True,
                "id": ordem.id,
                "status": ordem.status,
                "status_pagamento": ordem.status_pagamento,
            }
        )
    except ValidationError as e:
        return JsonResponse({"error": e.message if hasattr(e, "message") else str(e)}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@admin_required
def os_detalhe_admin(request, pk):
    ordem = get_object_or_404(
        OrdemServico.objects.select_related("cliente", "veiculo", "unidade").prefetch_related("itens"),
        pk=pk,
    )
    return render(
        request,
        "painel/os_detalhe.html",
        {
            "ordem": ordem,
            "itens": ordem.itens.all(),
            "status_choices": [s[0] for s in OrdemServico.STATUS_CHOICES],
        },
    )


@admin_required
def os_atualizar_status_admin(request, pk):
    if request.method == "POST":
        ordem = get_object_or_404(OrdemServico, pk=pk)
        novo_status = request.POST.get("status")
        try:
            mudar_status_ordem(ordem, novo_status, usuario=request.user)
            messages.success(request, f"Status da OS #{ordem.id:04d} atualizado para '{novo_status}'.")
        except ValidationError as e:
            messages.error(request, e.message if hasattr(e, "message") else str(e))
    return redirect("painel:os_detalhe", pk=pk)


@admin_required
def os_override_preco_admin(request, pk):
    if request.method == "POST":
        ordem = get_object_or_404(OrdemServico, pk=pk)
        try:
            novo_valor_str = request.POST.get("valor_total", "").replace(",", ".")
            novo_valor = Decimal(novo_valor_str)
            override_preco_ordem(ordem, novo_valor, usuario=request.user)
            messages.success(request, f"Valor da OS #{ordem.id:04d} alterado para R$ {novo_valor:.2f}.")
        except ValidationError as e:
            messages.error(request, e.message if hasattr(e, "message") else str(e))
        except Exception:
            messages.error(request, "Valor informado é inválido.")
    return redirect("painel:os_detalhe", pk=pk)


@admin_required
def os_pagamento_admin(request, pk):
    if request.method == "POST":
        ordem = get_object_or_404(OrdemServico, pk=pk)
        status_pagamento = request.POST.get("status_pagamento")
        try:
            marcar_pagamento_ordem(ordem, status_pagamento, usuario=request.user)
            messages.success(request, f"Status de pagamento da OS #{ordem.id:04d} alterado para '{status_pagamento}'.")
        except ValidationError as e:
            messages.error(request, e.message if hasattr(e, "message") else str(e))
    return redirect("painel:os_detalhe", pk=pk)


@admin_required
def unidades_admin(request):
    unidades = Unidade.objects.annotate(
        ordens_ativas_count=Count(
            "ordens_servico",
            filter=Q(ordens_servico__status__in=[
                OrdemServico.STATUS_NA_FILA,
                OrdemServico.STATUS_EXECUCAO,
            ]),
        )
    )
    return render(request, "painel/unidades.html", {"unidades": unidades})


@admin_required
def unidade_toggle_capacidade(request, pk):
    if request.method == "POST":
        unidade = get_object_or_404(Unidade, pk=pk)
        unidade.aceitando_pedidos = not unidade.aceitando_pedidos
        unidade.save()
        status_str = "Aberta para pedidos" if unidade.aceitando_pedidos else "Bloqueada (Capacidade Máxima)"
        messages.success(request, f"Unidade '{unidade.nome}': {status_str}.")
    return redirect("painel:unidades")


@admin_required
def unidade_editar(request, pk):
    if request.method == "POST":
        unidade = get_object_or_404(Unidade, pk=pk)
        nome = request.POST.get("nome", "").strip()
        endereco = request.POST.get("endereco", "").strip()
        if nome and endereco:
            unidade.nome = nome
            unidade.endereco = endereco
            unidade.save()
            messages.success(request, f"Unidade '{unidade.nome}' atualizada com sucesso!")
        else:
            messages.error(request, "Nome e endereço são obrigatórios.")
    return redirect("painel:unidades")


@admin_required
def servicos_admin(request):
    servicos = Servico.objects.prefetch_related("unidades").order_by("ordem_exibicao", "nome")
    servicos_principais = [s for s in servicos if s.tipo == Servico.TIPO_PRINCIPAL]
    servicos_complementos = [s for s in servicos if s.tipo == Servico.TIPO_COMPLEMENTO]
    unidades = Unidade.objects.all()
    return render(
        request,
        "painel/servicos.html",
        {
            "servicos": servicos,
            "servicos_principais": servicos_principais,
            "servicos_complementos": servicos_complementos,
            "unidades": unidades,
        },
    )


def _parse_servico_form(post):
    """Valida os dados do formulário de serviço. Retorna (dados, erros)."""
    erros = []
    nome = post.get("nome", "").strip()
    descricao = post.get("descricao", "").strip()
    tipo = post.get("tipo", Servico.TIPO_PRINCIPAL).strip()
    if tipo not in [Servico.TIPO_PRINCIPAL, Servico.TIPO_COMPLEMENTO]:
        tipo = Servico.TIPO_PRINCIPAL

    if not nome:
        erros.append("O nome do serviço é obrigatório.")

    preco_base = None
    try:
        preco_base = Decimal(post.get("preco_base", "").replace(",", ".").strip())
        if preco_base < 0:
            raise InvalidOperation
        preco_base = preco_base.quantize(Decimal("0.01"))
    except (InvalidOperation, ValueError):
        erros.append("Preço base inválido.")

    duracao = None
    try:
        duracao = int(post.get("duracao_estimada_minutos", ""))
        if duracao <= 0:
            raise ValueError
    except ValueError:
        erros.append("Duração estimada deve ser um número de minutos maior que zero.")

    todas = post.get("todas_unidades") == "on"
    unidade_ids = []
    if not todas:
        unidade_ids = [int(u) for u in post.getlist("unidades") if u.isdigit()]
        if not unidade_ids:
            erros.append("Selecione ao menos uma unidade ou marque 'Todas as unidades'.")

    dados = {
        "nome": nome,
        "tipo": tipo,
        "descricao": descricao,
        "preco_base": preco_base,
        "duracao_estimada_minutos": duracao,
        "unidade_ids": unidade_ids,
    }
    return dados, erros


def _salvar_servico(request, servico=None):
    dados, erros = _parse_servico_form(request.POST)
    if erros:
        for e in erros:
            messages.error(request, e)
        return False

    unidade_ids = dados.pop("unidade_ids")
    with transaction.atomic():
        if servico is None:
            ultima_ordem = Servico.objects.order_by("-ordem_exibicao").values_list("ordem_exibicao", flat=True).first() or 0
            servico = Servico(ordem_exibicao=ultima_ordem + 1)
        for campo, valor in dados.items():
            setattr(servico, campo, valor)
        servico.save()
        # Lista vazia = disponível em todas as unidades
        servico.unidades.set(Unidade.objects.filter(id__in=unidade_ids))
    return servico


@admin_required
def servico_criar(request):
    if request.method == "POST":
        servico = _salvar_servico(request)
        if servico:
            messages.success(request, f"Serviço '{servico.nome}' adicionado ao catálogo!")
    return redirect("painel:servicos")


@admin_required
def servico_editar(request, pk):
    if request.method == "POST":
        servico = get_object_or_404(Servico, pk=pk)
        if _salvar_servico(request, servico):
            messages.success(request, f"Serviço '{servico.nome}' atualizado com sucesso!")
    return redirect("painel:servicos")


@admin_required
def servico_toggle_ativo(request, pk):
    if request.method == "POST":
        servico = get_object_or_404(Servico, pk=pk)
        servico.is_ativo = not servico.is_ativo
        servico.save()
        status_str = "Ativado" if servico.is_ativo else "Desativado"
        messages.success(request, f"Serviço '{servico.nome}': {status_str}.")
    return redirect("painel:servicos")


@admin_required
def servico_excluir(request, pk):
    if request.method == "POST":
        servico = get_object_or_404(Servico, pk=pk)
        nome = servico.nome
        servico.delete()
        messages.success(request, f"Serviço '{nome}' excluído com sucesso do catálogo.")
    return redirect("painel:servicos")


@admin_required
def clientes_admin(request):
    q = request.GET.get("q", "").strip()
    clientes = User.objects.filter(role="cliente").prefetch_related("veiculos")
    if q:
        clientes = clientes.filter(Q(nome__icontains=q) | Q(telefone__icontains=q))
    return render(request, "painel/clientes.html", {"clientes": clientes, "q": q})
