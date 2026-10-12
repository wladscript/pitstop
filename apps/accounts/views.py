from django.contrib import messages
from django.contrib.auth import login, logout
from django.shortcuts import redirect, render
from .forms import LoginForm, RegisterForm


def login_view(request):
    if request.user.is_authenticated:
        if request.user.is_admin:
            return redirect("painel:kanban")
        return redirect("garagem:lista")

    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Bem-vindo de volta, {user.nome.split()[0]}!")

            next_url = request.GET.get("next")
            if next_url:
                return redirect(next_url)
            if user.is_admin:
                return redirect("painel:kanban")
            return redirect("garagem:lista")
    else:
        form = LoginForm()

    return render(request, "accounts/login.html", {"form": form})


def register_view(request):
    if request.user.is_authenticated:
        return redirect("garagem:lista")

    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Conta criada com sucesso! Cadastre seu primeiro veículo para começar.")
            return redirect("garagem:novo")
    else:
        form = RegisterForm()

    return render(request, "accounts/register.html", {"form": form})


def logout_view(request):
    logout(request)
    messages.info(request, "Você encerrou sua sessão com segurança.")
    return redirect("accounts:login")
