from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProductoViewSet, CompraViewSet, ProveedorViewSet, RegisterView, LoginView
from .views import OrderViewSet, OrderItemViewSet
from .views import UserOrdersView, CartValidationView
from .views import UserMeView
from .views import VentasTotalesView, ProductoMasVendidoView, VentasPorUsuarioView
from .views import producto_mas_vendido_grafico
from .views import ComprasPorUsuarioView
from .views import ventas_por_usuario_grafico

router = DefaultRouter()
router.register(r'productos', ProductoViewSet)
router.register(r'compras', CompraViewSet)
router.register(r'proveedores', ProveedorViewSet)
router.register(r'orders', OrderViewSet)
router.register(r'order-items', OrderItemViewSet)



urlpatterns = [
    path('', include(router.urls)),
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),  
    path('my-orders/', UserOrdersView.as_view(), name='my_orders'),
    path('cart/validate/', CartValidationView.as_view(), name='validate_cart'),
    path('users/me/', UserMeView.as_view(), name='user_me'),
    path('compras/usuario/', ComprasPorUsuarioView.as_view(), name='compras_por_usuario'),
    path('reportes/ventas_totales/', VentasTotalesView.as_view(), name='ventas_totales'),
    path('reportes/producto_mas_vendido/', ProductoMasVendidoView.as_view(), name='producto_mas_vendido'),
    path('reportes/ventas_por_usuario/<int:usuario_id>/', VentasPorUsuarioView.as_view(), name='ventas_por_usuario'),
    path('reportes/producto_mas_vendido_grafico/', producto_mas_vendido_grafico, name='producto_mas_vendido_grafico'),
    path('reportes/ventas_por_usuario_grafico/', ventas_por_usuario_grafico, name='ventas_por_usuario_grafico'),
   
    
]