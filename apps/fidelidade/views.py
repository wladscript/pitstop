from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import MovimentoFidelidade


@login_required
def extrato_fidelidade_view(request):
    cliente = request.user
    movimentos = MovimentoFidelidade.objects.filter(cliente=cliente).select_related("ordem_servico")

    # Regra de Níveis de Fidelidade
    pts = cliente.pontos_fidelidade
    if pts >= 300:
        nivel = "Ouro"
        proximo_nivel = None
        pts_faltantes = 0
        porcentagem = 100
    elif pts >= 100:
        nivel = "Prata"
        proximo_nivel = "Ouro"
        pts_faltantes = 300 - pts
        porcentagem = int((pts / 300) * 100)
    else:
        nivel = "Bronze"
        proximo_nivel = "Prata"
        pts_faltantes = 100 - pts
        porcentagem = int((pts / 100) * 100)

    return render(
        request,
        "fidelidade/extrato.html",
        {
            "movimentos": movimentos,
            "nivel": nivel,
            "proximo_nivel": proximo_nivel,
            "pts_faltantes": pts_faltantes,
            "porcentagem": porcentagem,
        },
    )
