from django.urls import path

from . import views
from .forms import CustomLoginForm

app_name = "users"


urlpatterns = [
    path(
        "profile/",
        views.UserHomeView.as_view(extra_context={"active": "profile"}),
        name="user_profile",
    ),
    path(
        "details/",
        views.UserUpdateView.as_view(extra_context={"active": "profile"}),
        name="account_update",
    ),
    path("logout/", views.CustomLogoutView.as_view(), name="logout"),
    path(
        "login/",
        views.CustomLoginView.as_view(extra_context={"active": "login"}),
        name="login",
    ),
    path("register/", views.RegisterView.as_view(extra_context={"active": "register"}), name="register"),
]
