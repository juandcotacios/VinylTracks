
from django.urls import path

from .views import viewsweb, login_view, register_view, user_dashboard, logout_view, profile_view


urlpatterns = [
    path("", viewsweb, name="mainweb"),
    path("login/", login_view, name="login"),
    path("register/", register_view, name="register"), 
    path("dashboard/", user_dashboard, name="user_dashboard"), 
    path("logout/", logout_view, name="logout"),
    path("profile/", profile_view, name="profile"),
]
