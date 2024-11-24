
from django.urls import path

from .views import viewsweb, login_view, register_view, user_dashboard, logout_view, profile_view,add_to_cart, view_cart, checkout


urlpatterns = [
    path("", viewsweb, name="mainweb"),
    path("login/", login_view, name="login"),
    path("register/", register_view, name="register"), 
    path("dashboard/", user_dashboard, name="user_dashboard"), 
    path("logout/", logout_view, name="logout"),
    path("profile/", profile_view, name="profile"),
    path("cart/", view_cart, name="cart"),
    path("add-to-cart/<int:product_id>/", add_to_cart, name="add_to_cart"),  # Añadir al carrito
    path("checkout/", checkout, name="checkout"),  # Procesar el pedido
]
