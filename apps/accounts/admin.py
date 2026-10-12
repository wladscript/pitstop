from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ("nome", "telefone", "role", "pontos_fidelidade", "is_staff", "is_active", "created_at")
    list_filter = ("role", "is_staff", "is_active")
    search_fields = ("nome", "telefone")
    ordering = ("-created_at",)

    fieldsets = (
        (None, {"fields": ("telefone", "password")}),
        ("Informações Pessoais", {"fields": ("nome",)}),
        ("Permissões e Perfil", {"fields": ("role", "pontos_fidelidade", "is_active", "is_staff", "is_superuser")}),
        ("Datas", {"fields": ("created_at", "updated_at")}),
    )
    readonly_fields = ("created_at", "updated_at")

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("telefone", "nome", "role", "password"),
            },
        ),
    )
