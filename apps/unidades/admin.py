from django.contrib import admin
from .models import Unidade


@admin.register(Unidade)
class UnidadeAdmin(admin.ModelAdmin):
    list_display = ("nome", "endereco", "is_ativa", "aceitando_pedidos", "created_at")
    list_filter = ("is_ativa", "aceitando_pedidos")
    search_fields = ("nome", "endereco")
