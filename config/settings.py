"""
Django settings for Pit Stop project.
"""

from pathlib import Path
import environ

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Carregar variáveis de ambiente do arquivo .env
env = environ.Env(
    DEBUG=(bool, False),
)
environ.Env.read_env(BASE_DIR / ".env")

SECRET_KEY = env("SECRET_KEY", default="django-insecure-pitstop-dev-change-in-production")
DEBUG = env.bool("DEBUG", default=True)
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=["localhost", "127.0.0.1"])

# Application definition
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "whitenoise.runserver_nostatic",
    "django.contrib.staticfiles",
    # Pit Stop Apps
    "apps.accounts.apps.AccountsConfig",
    "apps.unidades.apps.UnidadesConfig",
    "apps.garagem.apps.GaragemConfig",
    "apps.catalogo.apps.CatalogoConfig",
    "apps.ordens.apps.OrdensConfig",
    "apps.fidelidade.apps.FidelidadeConfig",
    "apps.pagamentos.apps.PagamentosConfig",
    "apps.painel.apps.PainelConfig",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# Database
# Padrão: SQLite local com zero overhead de configuração
DATABASES = {
    "default": env.db("DATABASE_URL", default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}")
}

# Autenticação Customizada por Telefone
AUTH_USER_MODEL = "accounts.User"

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
        "OPTIONS": {"min_length": 6},
    },
]

# Internationalization
LANGUAGE_CODE = "pt-br"
TIME_ZONE = "America/Sao_Paulo"
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

# Redirecionamentos de Login
LOGIN_URL = "accounts:login"
LOGIN_REDIRECT_URL = "garagem:lista"
LOGOUT_REDIRECT_URL = "accounts:login"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Parâmetros Pix (BR Code)
PIX_RECEIVER_NAME = env("PIX_RECEIVER_NAME", default="PIT STOP LAVA RAPIDO")
PIX_RECEIVER_CITY = env("PIX_RECEIVER_CITY", default="SAO PAULO")
PIX_KEY = env("PIX_KEY", default="pitstop@pix.com.br")

# Parâmetros de Seed e Demonstração
ADMIN_NAME = env("ADMIN_NAME", default="Administrador Pit Stop")
ADMIN_PHONE = env("ADMIN_PHONE", default="11999999999")
ADMIN_PASSWORD = env("ADMIN_PASSWORD", default="admin123")

DEMO_NAME = env("DEMO_NAME", default="Cliente Demonstração")
DEMO_PHONE = env("DEMO_PHONE", default="11988887777")
DEMO_PASSWORD = env("DEMO_PASSWORD", default="demo123")
