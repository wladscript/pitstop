import json
from decimal import Decimal
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from apps.catalogo.models import Servico
from apps.garagem.models import Veiculo
from apps.unidades.models import Unidade
from .models import OrdemServico
from .services import criar_ordem_servico


@login_required
def lista_ordens(request):
    ordens = OrdemServico.objects.filter(cliente=request.user).select_related("veiculo", "unidade")
    return render(request, "ordens/lista.html", {"ordens": ordens})


@login_required
def nova_ordem(request):
    veiculos = list(Veiculo.objects.filter(cliente=request.user))
    if not veiculos:
        messages.info(request, "Cadastre um veículo primeiro para abrir uma solicitação.")
        return redirect("garagem:novo")

    unidades = list(Unidade.objects.filter(is_ativa=True))
    servicos = list(Servico.objects.filter(is_ativo=True).prefetch_related("unidades"))

    # Pré-seleção do veículo via query param se houver
    veiculo_id_param = request.GET.get("veiculo")
    veiculo_selecionado = None
    if veiculo_id_param:
        try:
            veiculo_selecionado = next((v for v in veiculos if v.id == int(veiculo_id_param)), None)
        except ValueError:
            pass

    if request.method == "POST":
        try:
            veiculo_id = int(request.POST.get("veiculo_id", 0))
            unidade_id = int(request.POST.get("unidade_id", 0))
            servico_ids = [int(s) for s in request.POST.getlist("servico_ids")]
            logistica_entrada = request.POST.get("logistica_entrada", "Entrega no local")
            logistica_saida = request.POST.get("logistica_saida", "Retirada no local")
            enderecos = request.POST.get("enderecos", "")
            observacoes = request.POST.get("observacoes", "")

            veiculo = get_object_or_404(Veiculo, id=veiculo_id, cliente=request.user)
            unidade = get_object_or_404(Unidade, id=unidade_id)

            ordem = criar_ordem_servico(
                cliente=request.user,
                veiculo=veiculo,
                unidade=unidade,
                servico_ids=servico_ids,
                logistica_entrada=logistica_entrada,
                logistica_saida=logistica_saida,
                enderecos=enderecos,
                observacoes=observacoes,
            )

            messages.success(request, f"Ordem de Serviço #{ordem.id:04d} aberta com sucesso!")
            return redirect("pagamentos:pix_os", ordem_id=ordem.id)
        except ValidationError as e:
            messages.error(request, e.message if hasattr(e, "message") else str(e))
        except Exception as e:
            messages.error(request, f"Erro ao criar pedido: {e}")

    # Monta mapa JSON de serviços com preços para o frontend calcular em tempo real no wizard
    servicos_json = [
        {
            "id": s.id,
            "nome": s.nome,
            "descricao": s.descricao,
            "preco_base": float(s.preco_base),
            "duracao": s.duracao_estimada_minutos,
            # Lista vazia = disponível em todas as unidades
            "unidades": [u.id for u in s.unidades.all()],
        }
        for s in servicos
    ]

    veiculos_json = [
        {
            "id": v.id,
            "modelo": v.modelo,
            "placa": v.placa_display,
            "categoria": v.categoria,
        }
        for v in veiculos
    ]

    return render(
        request,
        "ordens/nova.html",
        {
            "veiculos": veiculos,
            "veiculo_selecionado": veiculo_selecionado,
            "unidades": unidades,
            "servicos": servicos,
            "servicos_json": json.dumps(servicos_json),
            "veiculos_json": json.dumps(veiculos_json),
        },
    )


@login_required
def detalhe_ordem(request, pk):
    # Clientes só acessam suas próprias ordens; Admin acessa todas
    if request.user.is_admin:
        ordem = get_object_or_404(OrdemServico.objects.select_related("cliente", "veiculo", "unidade"), pk=pk)
    else:
        ordem = get_object_or_404(OrdemServico.objects.select_related("cliente", "veiculo", "unidade"), pk=pk, cliente=request.user)

    itens = ordem.itens.all()
    return render(
        request,
        "ordens/detalhe.html",
        {
            "ordem": ordem,
            "itens": itens,
            "flow": [
                OrdemServico.STATUS_NA_FILA,
                OrdemServico.STATUS_EXECUCAO,
                OrdemServico.STATUS_PRONTO,
            ],
        },
    )


@login_required
def status_ordem_api(request, pk):
    """
    API leve para polling em tempo real na tela de detalhe da OS.
    """
    if request.user.is_admin:
        ordem = get_object_or_404(OrdemServico, pk=pk)
    else:
        ordem = get_object_or_404(OrdemServico, pk=pk, cliente=request.user)

    return JsonResponse(
        {
            "id": ordem.id,
            "status": ordem.status,
            "status_pagamento": ordem.status_pagamento,
            "valor_total": float(ordem.valor_total),
            "updated_at": ordem.updated_at.isoformat(),
        }
    )
