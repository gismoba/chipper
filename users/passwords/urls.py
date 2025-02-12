from django.contrib.auth import views
from django.urls import path

urlpatterns = [
    path(
        "password_change/",
        views.PasswordChangeView.as_view(extra_context={"active": "profile"}),
        name="password_change",
    ),
    path(
        "password_change/done/",
        views.PasswordChangeDoneView.as_view(extra_context={"active": "profile"}),
        name="password_change_done",
    ),
    path(
        "password_reset/",
        views.PasswordResetView.as_view(extra_context={"active": "profile"}),
        name="password_reset",
    ),
    path(
        "password_reset/done/",
        views.PasswordResetDoneView.as_view(extra_context={"active": "profile"}),
        name="password_reset_done",
    ),
    path(
        "reset/<uidb64>/<token>/",
        views.PasswordResetConfirmView.as_view(extra_context={"active": "profile"}),
        name="password_reset_confirm",
    ),
    path(
        "reset/done/",
        views.PasswordResetCompleteView.as_view(extra_context={"active": "profile"}),
        name="password_reset_complete",
    ),
]
