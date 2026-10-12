import re
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models


def clean_phone(phone: str) -> str:
    """Extrai apenas os dígitos do telefone informado."""
    if not phone:
        return ""
    return re.sub(r"\D", "", phone)


class UserManager(BaseUserManager):
    def create_user(self, telefone, nome, password=None, **extra_fields):
        if not telefone:
            raise ValueError("O número de telefone é obrigatório")
        if not nome:
            raise ValueError("O nome é obrigatório")

        telefone = clean_phone(telefone)
        user = self.model(telefone=telefone, nome=nome.strip(), **extra_fields)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()

        # Se for admin, garante is_staff
        if user.role == "admin":
            user.is_staff = True

        user.save(using=self._db)
        return user

    def create_superuser(self, telefone, nome, password=None, **extra_fields):
        extra_fields.setdefault("role", "admin")
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superusuário deve ter is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superusuário deve ter is_superuser=True.")

        return self.create_user(telefone, nome, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = (
        ("cliente", "Cliente"),
        ("admin", "Administrador"),
    )

    nome = models.CharField("Nome completo", max_length=150)
    telefone = models.CharField(
        "Telefone / WhatsApp",
        max_length=20,
        unique=True,
        db_index=True,
        help_text="Somente números ou formato (DD) 99999-9999",
    )
    role = models.CharField("Perfil de acesso", max_length=10, choices=ROLE_CHOICES, default="cliente")
    pontos_fidelidade = models.PositiveIntegerField("Pontos de fidelidade", default=0)

    is_active = models.BooleanField("Ativo", default=True)
    is_staff = models.BooleanField("Acesso à equipe", default=False)
    created_at = models.DateTimeField("Data de cadastro", auto_now_add=True)
    updated_at = models.DateTimeField("Última atualização", auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = "telefone"
    REQUIRED_FIELDS = ["nome"]

    class Meta:
        verbose_name = "Usuário"
        verbose_name_plural = "Usuários"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.nome} ({self.formatted_telefone})"

    def clean(self):
        super().clean()
        self.telefone = clean_phone(self.telefone)

    def save(self, *args, **kwargs):
        self.telefone = clean_phone(self.telefone)
        if self.role == "admin":
            self.is_staff = True
        super().save(*args, **kwargs)

    @property
    def is_admin(self) -> bool:
        return self.role == "admin" or self.is_superuser

    @property
    def formatted_telefone(self) -> str:
        """Formata o telefone para exibição: (XX) XXXXX-XXXX ou (XX) XXXX-XXXX."""
        t = self.telefone
        if len(t) == 11:
            return f"({t[:2]}) {t[2:7]}-{t[7:]}"
        elif len(t) == 10:
            return f"({t[:2]}) {t[2:6]}-{t[6:]}"
        return t
