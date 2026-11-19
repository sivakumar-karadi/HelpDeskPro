
from django.urls import path
from django.contrib.auth.views import LoginView

from . import views


urlpatterns = [
    path("", views.home, name="home"),

    # Authentication
    path(
        "register/",
        views.register,
        name="register",
    ),

    path(
        "login/",
        LoginView.as_view(
            template_name="registration/login.html"
        ),
        name="login",
    ),

    path(
        "logout/",
        views.logout_user,
        name="logout",
    ),

    # User Profile
    path(
        "profile/",
        views.profile,
        name="profile",
    ),

    # Ticket management
    path(
        "create-ticket/",
        views.create_ticket,
        name="create_ticket",
    ),

    path(
        "ticket/<int:ticket_id>/",
        views.ticket_detail,
        name="ticket_detail",
    ),

    path(
        "ticket/<int:ticket_id>/edit/",
        views.edit_ticket,
        name="edit_ticket",
    ),

    path(
        "update-ticket/<int:ticket_id>/",
        views.update_ticket_status,
        name="update_ticket_status",
    ),

    path(
        "delete-ticket/<int:ticket_id>/",
        views.delete_ticket,
        name="delete_ticket",
    ),
]
