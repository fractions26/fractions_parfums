from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [

    path('admin/', admin.site.urls),

    path('', include('apps.paginas.urls')),

    path('produtos/', include('apps.produtos.urls')),

    path('carrinho/', include('apps.carrinho.urls')),

    path('checkout/', include('apps.pedidos.urls')),

    # ✅ PEDIDOS
    path('pedido/', include('apps.pedidos.urls')),

    # ✅ PAGAMENTOS
    path('pagamento/', include('apps.pagamentos.urls')),
    
    # ✅ USUARIOS
    path('usuario/', include('apps.usuarios.urls')),
    
]

# ✅ MEDIA
urlpatterns += static(
    settings.MEDIA_URL,
    document_root=settings.MEDIA_ROOT
)