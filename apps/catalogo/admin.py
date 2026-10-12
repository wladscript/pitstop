from django.contrib import admin
from .models import Servico


@admin.register(Servico)
class ServicoAdmin(admin.ModelAdmin):
    list_display = ("nome", "preco_base", "duracao_estimada_minutos", "is_ativo", "ordem_exibicao")
    list_filter = ("is_ativo",)
    search_fields = ("nome", "descricao")
    list_editable = ("is_ativo", "ordem_exibicao")
