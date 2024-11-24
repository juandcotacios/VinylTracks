from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProductoViewSet, CompraViewSet, ProveedorViewSet, RegisterView, LoginView
from .views import OrderViewSet, OrderItemViewSet
from .views import UserOrdersView

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
]
urlpatterns += [
    path('my-orders/', UserOrdersView.as_view(), name='my_orders'),
]
