from django.urls import path
from . import views

app_name = "garagem"

urlpatterns = [
    path("", views.lista_veiculos, name="lista"),
    path("novo/", views.novo_veiculo, name="novo"),
    path("<int:pk>/editar/", views.editar_veiculo, name="editar"),
    path("<int:pk>/excluir/", views.excluir_veiculo, name="excluir"),
    path("api/placa/<str:placa>/", views.consulta_placa_api, name="consulta_placa_api"),
]
