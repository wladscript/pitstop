from django.urls import path
from . import views

app_name = "ordens"

urlpatterns = [
    path("", views.lista_ordens, name="lista"),
    path("nova/", views.nova_ordem, name="nova"),
    path("<int:pk>/", views.detalhe_ordem, name="detalhe"),
    path("api/<int:pk>/status/", views.status_ordem_api, name="status_api"),
]
