from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from .forms import VeiculoForm
from .models import Veiculo
from .services import consultar_placa


@login_required
def lista_veiculos(request):
    veiculos = Veiculo.objects.filter(cliente=request.user)
    return render(request, "garagem/lista.html", {"veiculos": veiculos})


@login_required
def novo_veiculo(request):
    if request.method == "POST":
        form = VeiculoForm(request.POST)
        if form.is_valid():
            veiculo = form.save(commit=False)
            veiculo.cliente = request.user
            veiculo.save()
            messages.success(request, f"Veículo {veiculo.modelo} ({veiculo.placa}) adicionado com sucesso!")
            return redirect("garagem:lista")
    else:
        form = VeiculoForm()

    return render(request, "garagem/form.html", {"form": form, "titulo": "Novo Veículo", "is_edit": False})


@login_required
def editar_veiculo(request, pk):
    veiculo = get_object_or_404(Veiculo, pk=pk, cliente=request.user)
    if request.method == "POST":
        form = VeiculoForm(request.POST, instance=veiculo)
        if form.is_valid():
            form.save()
            messages.success(request, f"Veículo {veiculo.modelo} atualizado com sucesso!")
            return redirect("garagem:lista")
    else:
        form = VeiculoForm(instance=veiculo)

    return render(request, "garagem/form.html", {"form": form, "titulo": "Editar Veículo", "is_edit": True, "veiculo": veiculo})


@login_required
def excluir_veiculo(request, pk):
    veiculo = get_object_or_404(Veiculo, pk=pk, cliente=request.user)
    if request.method == "POST":
        modelo = veiculo.modelo
        # Proteção caso tenha ordens associadas
        if veiculo.ordens_servico.exists():
            messages.error(request, f"Não é possível excluir o veículo {modelo} pois ele possui histórico de ordens de serviço.")
            return redirect("garagem:lista")
        veiculo.delete()
        messages.success(request, f"Veículo {modelo} excluído com sucesso.")
    return redirect("garagem:lista")


@login_required
def consulta_placa_api(request, placa):
    """
    API JSON segura (autenticada) para consulta de dados de veículo por placa.
    """
    try:
        dados = consultar_placa(placa)
        return JsonResponse(dados)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)
