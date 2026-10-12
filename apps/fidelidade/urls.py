from django.urls import path
from . import views

app_name = "fidelidade"

urlpatterns = [
    path("", views.extrato_fidelidade_view, name="extrato"),
]
