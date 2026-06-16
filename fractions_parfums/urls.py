from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap

# ✅ SITEMAP
from fractions_parfums.sitemaps import StaticSitemap

# ✅ ROBOTS
from django.http import HttpResponse
from django.views.decorators.http import require_GET


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

    # ✅ 👇 SUPER IMPORTANTE (ANTES DE TUDO)
    path("robots.txt", robots_txt),

    # ✅ ADMIN
    path('admin/', admin.site.urls),

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

    # ✅ LOGIN GOOGLE
    path('accounts/', include('allauth.urls')),
]


# ✅ MEDIA
urlpatterns += static(
    settings.MEDIA_URL,
    document_root=settings.MEDIA_ROOT
)