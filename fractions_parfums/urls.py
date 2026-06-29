from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap
from django.contrib.auth import views as auth_views
from django.contrib import admin
from django.urls import path, include
from two_factor.urls import urlpatterns as tf_patterns

# ✅ SITEMAP
from fractions_parfums.sitemaps import StaticSitemap

# ✅ ROBOTS
from django.http import HttpResponse
from django.views.decorators.http import require_GET

# ✅ FAVICON
from django.views.generic import RedirectView
from django.templatetags.static import static as static_url


# ✅ FUNÇÃO ROBOTS.TXT
@require_GET
def robots_txt(request):
    lines = [
        "User-agent: *",
        "Allow: /",
        "",
        "User-agent: facebookexternalhit",
        "Allow: /",
        "",
        "User-agent: WhatsApp",
        "Allow: /",
        "",
        "User-agent: Twitterbot",
        "Allow: /",
        "",
        "Sitemap: https://fractionsparfums.com.br/sitemap.xml",
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain")


# ✅ SITEMAPS REGISTRADOS
sitemaps = {
    'static': StaticSitemap,
}


urlpatterns = [

    # ✅ FAVICON
    path(
        "favicon.ico",
        RedirectView.as_view(
            url=static_url("images/favicon.png"),
            permanent=True
        ),
    ),

    # ✅ ROBOTS.TXT
    path("robots.txt", robots_txt),
    
    
    # ✅ TWO FACTOR AUTH
    path(
    '',
    include(
        (tf_patterns[0], 'two_factor'),
        namespace='two_factor'
    )
),


    # ✅ ADMIN
    path('painel-interno-fractions/', admin.site.urls),

    # ✅ SITEMAP
    path(
        'sitemap.xml',
        sitemap,
        {'sitemaps': sitemaps},
        name='sitemap'
    ),

    # ✅ PÁGINAS
    path('', include('apps.paginas.urls')),

    # ✅ PRODUTOS
    path('produtos/', include('apps.produtos.urls')),

    # ✅ CARRINHO
    path('carrinho/', include('apps.carrinho.urls')),

    # ✅ CHECKOUT / PEDIDOS
    path('checkout/', include('apps.pedidos.urls')),
    path('pedido/', include('apps.pedidos.urls')),

    # ✅ PAGAMENTO
    path('pagamento/', include('apps.pagamentos.urls')),

    # ✅ USUÁRIO
    path('usuario/', include('apps.usuarios.urls')),

    # ✅ FRETE
    path('entrega/', include('apps.entrega.urls')),
    
    # ✅ CUPONS
    path('cupons/', include('apps.cupons.urls')),
    
# ✅ RECUPERAR SENHA

    path(
        'senha/reset/',
        auth_views.PasswordResetView.as_view(
            template_name='usuarios/password_reset.html',
            email_template_name='usuarios/password_reset_email.html',
            subject_template_name='usuarios/password_reset_subject.txt'
        ),
        name='password_reset'
    ),

    path(
        'senha/reset/enviado/',
        auth_views.PasswordResetDoneView.as_view(
            template_name='usuarios/password_reset_done.html'
        ),
        name='password_reset_done'
    ),

    path(
        'senha/reset/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(
            template_name='usuarios/password_reset_confirm.html'
        ),
        name='password_reset_confirm'
    ),

    path(
        'senha/reset/concluido/',
        auth_views.PasswordResetCompleteView.as_view(
            template_name='usuarios/password_reset_complete.html'
        ),
        name='password_reset_complete'
    ),

    # ✅ LOGIN GOOGLE
    path('accounts/', include('allauth.urls')),
]

# ✅ MEDIA
urlpatterns += static(
    settings.MEDIA_URL,
    document_root=settings.MEDIA_ROOT
)