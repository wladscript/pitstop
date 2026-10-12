from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render
from apps.ordens.models import OrdemServico
from .services import gerar_dados_pix_os


@login_required
def pix_os_view(request, ordem_id):
    if request.user.is_admin:
        ordem = get_object_or_404(OrdemServico.objects.select_related("veiculo", "unidade"), pk=ordem_id)
    else:
        ordem = get_object_or_404(OrdemServico.objects.select_related("veiculo", "unidade"), pk=ordem_id, cliente=request.user)

    dados_pix = gerar_dados_pix_os(ordem)
    return render(
        request,
        "pagamentos/pix.html",
        {
            "ordem": ordem,
            "pix": dados_pix,
        },
    )
