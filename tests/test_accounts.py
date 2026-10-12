import pytest
from django.contrib.auth import authenticate
from apps.accounts.models import User, clean_phone


@pytest.mark.django_db
class TestAccounts:
    def test_clean_phone(self):
        assert clean_phone("(11) 99999-8888") == "11999998888"
        assert clean_phone("11-99999-8888") == "11999998888"
        assert clean_phone(" 11 99999 8888 ") == "11999998888"

    def test_create_user(self):
        user = User.objects.create_user(
            telefone="(11) 91234-5678",
            nome="Carlos Silva",
            password="minhasenha123",
        )
        assert user.telefone == "11912345678"
        assert user.check_password("minhasenha123")
        assert not user.is_staff
        assert not user.is_admin
        assert user.pontos_fidelidade == 0
        assert user.formatted_telefone == "(11) 91234-5678"

    def test_create_superuser(self):
        admin = User.objects.create_superuser(
            telefone="11999990000",
            nome="Super Admin",
            password="adminpassword",
        )
        assert admin.is_staff
        assert admin.is_superuser
        assert admin.is_admin
        assert admin.role == "admin"
