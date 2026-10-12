from django.contrib import admin
from .models import MovimentoFidelidade


@admin.register(MovimentoFidelidade)
class MovimentoFidelidadeAdmin(admin.ModelAdmin):
    list_display = ("cliente", "pontos", "tipo", "descricao", "ordem_servico", "created_at")
    list_filter = ("tipo", "created_at")
    search_fields = ("cliente__nome", "cliente__telefone", "descricao")
    autocomplete_fields = ("cliente",)
