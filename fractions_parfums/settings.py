from pathlib import Path
from decouple import config
import os

BASE_DIR = Path(__file__).resolve().parent.parent

# =========================
# ✅ SEGURANÇA
# =========================

SECRET_KEY = config('SECRET_KEY')

DEBUG = config('DEBUG', default=False, cast=bool)

ALLOWED_HOSTS = config(
    'ALLOWED_HOSTS',
    default='127.0.0.1,localhost'
).split(',')

# ✅ HTTPS ATRÁS DO RENDER
SECURE_PROXY_SSL_HEADER = (
    'HTTP_X_FORWARDED_PROTO',
    'https'
)

# ✅ REDIRECIONA HTTP → HTTPS
SECURE_SSL_REDIRECT = not DEBUG

# ✅ COOKIES SEGUROS
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG

# ✅ PROTEÇÃO CLICKJACKING
X_FRAME_OPTIONS = 'DENY'

CSRF_TRUSTED_ORIGINS = config(
    'CSRF_TRUSTED_ORIGINS',
    default=''
).split(',')

# ✅ HSTS
SECURE_HSTS_SECONDS = 31536000 if not DEBUG else 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = not DEBUG
SECURE_HSTS_PRELOAD = not DEBUG

# ✅ MIME SNIFFING
SECURE_CONTENT_TYPE_NOSNIFF = True

# ✅ REFERRER POLICY
SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'

# =========================
# ✅ RECAPTCHA
# =========================

RECAPTCHA_SITE_KEY = config(
    'RECAPTCHA_SITE_KEY',
    default=''
)

RECAPTCHA_SECRET_KEY = config(
    'RECAPTCHA_SECRET_KEY',
    default=''
)

# =========================
# ✅ APPS
# =========================

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.postgres',

    'apps.produtos.apps.ProdutosConfig',
    'apps.carrinho.apps.CarrinhoConfig',
    'apps.entrega',
    'apps.pedidos.apps.PedidosConfig',
    'apps.pagamentos.apps.PagamentosConfig',
    'apps.paginas.apps.PaginasConfig',

    'mathfilters',

]

# =========================
# ✅ MIDDLEWARE
# =========================

MIDDLEWARE = [

    'django.middleware.security.SecurityMiddleware',

    # ✅ BLOQUEIA URLS MALFORMADAS
    'fractions_parfums.middleware.InvalidPathMiddleware',

    # ✅ STATIC FILES
    'whitenoise.middleware.WhiteNoiseMiddleware',

    'django.contrib.sessions.middleware.SessionMiddleware',

    'django.middleware.common.CommonMiddleware',

    'django.middleware.csrf.CsrfViewMiddleware',

    'django.contrib.auth.middleware.AuthenticationMiddleware',

    'django.contrib.messages.middleware.MessageMiddleware',

    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'fractions_parfums.urls'

# =========================
# ✅ TEMPLATES
# =========================

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',

        'DIRS': [BASE_DIR / 'templates'],

        'APP_DIRS': True,

        'OPTIONS': {
            'context_processors': [

                'django.template.context_processors.debug',

                'django.template.context_processors.request',

                'django.contrib.auth.context_processors.auth',

                'django.contrib.messages.context_processors.messages',

                'apps.carrinho.context_processors.carrinho_quantidade',

                'apps.carrinho.context_processors.marcas_menu',
            ],
        },
    },
]

WSGI_APPLICATION = 'fractions_parfums.wsgi.application'

# =========================
# ✅ DATABASE
# =========================

DATABASES = {
    'default': {

        'ENGINE': 'django.db.backends.postgresql',

        'NAME': config('DB_NAME', default=''),

        'USER': config('DB_USER', default=''),

        'PASSWORD': config('DB_PASSWORD', default=''),

        'HOST': config('DB_HOST', default='localhost'),

        'PORT': config('DB_PORT', default='5432'),

        'OPTIONS': {

            'client_encoding': 'UTF8',

            'sslmode': (
                'require'
                if config('DB_HOST') != 'localhost'
                else 'disable'
            ),
        },
    }
}

# =========================
# ✅ STATIC FILES
# =========================

STATIC_URL = '/static/'

STATICFILES_DIRS = [
    BASE_DIR / 'static'
]

STATIC_ROOT = BASE_DIR / 'staticfiles'

STATICFILES_STORAGE = (
    'whitenoise.storage.CompressedStaticFilesStorage'
)

# =========================
# ✅ MEDIA
# =========================

MEDIA_URL = '/media/'

MEDIA_ROOT = BASE_DIR / 'media'

# =========================
# ✅ DEFAULT PK
# =========================

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# =========================
# ✅ EMAIL
# =========================

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

EMAIL_HOST = config(
    'EMAIL_HOST',
    default='smtp.hostinger.com'
)

EMAIL_PORT = config(
    'EMAIL_PORT',
    default=587,
    cast=int
)

EMAIL_USE_TLS = config(
    'EMAIL_USE_TLS',
    default=True,
    cast=bool
)

EMAIL_HOST_USER = config(
    'EMAIL_HOST_USER',
    default='contato@fractions.com.br'
)

EMAIL_HOST_PASSWORD = config(
    'EMAIL_HOST_PASSWORD',
    default=''
)

DEFAULT_FROM_EMAIL = 'contato@fractions.com.br'