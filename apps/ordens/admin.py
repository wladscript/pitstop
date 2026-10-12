from django.contrib import admin
from .models import OrdemServico, OrdemServicoItem


class OrdemServicoItemInline(admin.TabularInline):
    model = OrdemServicoItem
    extra = 0
    readonly_fields = ("nome_servico", "preco_aplicado")


@admin.register(OrdemServico)
class OrdemServicoAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "cliente",
        "veiculo",
        "unidade",
        "status",
        "status_pagamento",
        "valor_total",
        "override_preco",
        "created_at",
    )
    list_filter = ("status", "status_pagamento", "unidade")
    search_fields = ("id", "cliente__nome", "cliente__telefone", "veiculo__placa", "veiculo__modelo")
    inlines = [OrdemServicoItemInline]
    readonly_fields = ("created_at", "updated_at")
