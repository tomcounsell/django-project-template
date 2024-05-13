from django.contrib.auth import views as auth_views
from django.urls import path

from .views import account

app_name = "public"

urlpatterns = []

# Brand, Category, and Item
urlpatterns += (
    [
        path(
            "",
            account.HomeView.as_view(),
            name="home",
        ),
    ]
)

# Auth and Accounts
urlpatterns += [
    path(
        "account/login",
        account.LoginView.as_view(),
        name="account-login",
    ),
    path(
        "account/logout",
        auth_views.LogoutView.as_view(next_page="/"),
        name="account-logout",
    ),
    path(
        "account/settings",
        account.SettingsView.as_view(),
        name="account-settings",
    ),
    # path(
    #     "account/create",
    #     account.AccountCreateView.as_view(),
    #     name="account-create",
    # ),
]
