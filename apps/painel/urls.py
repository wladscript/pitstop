from django.urls import path
from . import views

app_name = "painel"

urlpatterns = [
    path("", views.kanban_view, name="kanban"),
    path("api/os/<int:pk>/status/", views.mover_status_api, name="mover_status_api"),
    path("os/<int:pk>/", views.os_detalhe_admin, name="os_detalhe"),
    path("os/<int:pk>/status/", views.os_atualizar_status_admin, name="os_atualizar_status"),
    path("os/<int:pk>/preco/", views.os_override_preco_admin, name="os_override_preco"),
    path("os/<int:pk>/pagamento/", views.os_pagamento_admin, name="os_pagamento"),
    path("unidades/", views.unidades_admin, name="unidades"),
    path("unidades/<int:pk>/toggle-capacidade/", views.unidade_toggle_capacidade, name="unidade_toggle_capacidade"),
    path("unidades/<int:pk>/editar/", views.unidade_editar, name="unidade_editar"),
    path("servicos/", views.servicos_admin, name="servicos"),
    path("servicos/novo/", views.servico_criar, name="servico_criar"),
    path("servicos/<int:pk>/editar/", views.servico_editar, name="servico_editar"),
    path("servicos/<int:pk>/toggle-ativo/", views.servico_toggle_ativo, name="servico_toggle_ativo"),
    path("servicos/<int:pk>/excluir/", views.servico_excluir, name="servico_excluir"),
    path("clientes/", views.clientes_admin, name="clientes"),
]
