from django.contrib import admin
from .models import Veiculo


@admin.register(Veiculo)
class VeiculoAdmin(admin.ModelAdmin):
    list_display = ("placa", "modelo", "cor", "ano", "categoria", "cliente", "created_at")
    list_filter = ("categoria", "ano")
    search_fields = ("placa", "modelo", "cliente__nome", "cliente__telefone")
    autocomplete_fields = ("cliente",)
