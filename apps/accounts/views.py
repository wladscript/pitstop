from django.contrib import messages
from django.contrib.auth import login, logout
from django.shortcuts import redirect, render
from .forms import LoginForm, RegisterForm


def login_view(request):
    if request.user.is_authenticated:
        if request.user.is_admin:
            return redirect("painel:kanban")
        return redirect("garagem:lista")

    initial_mode = request.GET.get("mode", "welcome")
    login_form = LoginForm()
    register_form = RegisterForm()

    if request.method == "POST":
        action = request.POST.get("action", "login")
        if action == "register":
            register_form = RegisterForm(request.POST)
            if register_form.is_valid():
                user = register_form.save()
                login(request, user)
                messages.success(request, "Conta criada com sucesso! Cadastre seu primeiro veículo para começar.")
                return redirect("garagem:novo")
            initial_mode = "register"
        else:
            login_form = LoginForm(request.POST)
            if login_form.is_valid():
                user = login_form.get_user()
                login(request, user)
                messages.success(request, f"Bem-vindo de volta, {user.nome.split()[0]}!")

                next_url = request.GET.get("next")
                if next_url:
                    return redirect(next_url)
                if user.is_admin:
                    return redirect("painel:kanban")
                return redirect("garagem:lista")
            initial_mode = "login"

    return render(
        request,
        "accounts/login.html",
        {
            "login_form": login_form,
            "register_form": register_form,
            "form": login_form,
            "initial_mode": initial_mode,
        },
    )


def register_view(request):
    if request.user.is_authenticated:
        return redirect("garagem:lista")

    if request.method == "POST":
        register_form = RegisterForm(request.POST)
        if register_form.is_valid():
            user = register_form.save()
            login(request, user)
            messages.success(request, "Conta criada com sucesso! Cadastre seu primeiro veículo para começar.")
            return redirect("garagem:novo")
        login_form = LoginForm()
        return render(
            request,
            "accounts/login.html",
            {
                "login_form": login_form,
                "register_form": register_form,
                "form": login_form,
                "initial_mode": "register",
            },
        )

    return redirect("/auth/login/?mode=register")


def logout_view(request):
    logout(request)
    messages.info(request, "Você encerrou sua sessão com segurança.")
    return redirect("accounts:login")
