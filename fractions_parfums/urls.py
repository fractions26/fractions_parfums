from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap
from fractions_parfums.sitemaps import StaticSitemap

sitemaps = {
    'static': StaticSitemap,
}


urlpatterns = [

    path('admin/', admin.site.urls),
        
    # ✅ PESQUISA SITEMAP GOOGLE)
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}),

    # ✅ PÁGINAS (home está aqui dentro)
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

    # ✅ FRETE (CORRIGIDO)
    path('entrega/', include('apps.entrega.urls')),

    # ✅ LOGIN GOOGLE)
    path('accounts/', include('allauth.urls')),

]


# ✅ MEDIA
urlpatterns += static(
    settings.MEDIA_URL,
    document_root=settings.MEDIA_ROOT
)