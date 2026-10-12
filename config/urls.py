from django.contrib import admin
from django.shortcuts import redirect
from django.urls import include, path


def root_redirect(request):
    if request.user.is_authenticated:
        if request.user.is_admin:
            return redirect("painel:kanban")
        return redirect("garagem:lista")
    return redirect("accounts:login")


urlpatterns = [
    path("", root_redirect, name="root"),
    path("admin/", admin.site.urls),
    path("auth/", include("apps.accounts.urls")),
    path("garagem/", include("apps.garagem.urls")),
    path("ordens/", include("apps.ordens.urls")),
    path("fidelidade/", include("apps.fidelidade.urls")),
    path("pagamentos/", include("apps.pagamentos.urls")),
    path("painel/", include("apps.painel.urls")),
]
