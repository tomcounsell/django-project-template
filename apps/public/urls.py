from django.contrib.auth import views as auth_views
from django.urls import path

from .views import account
from .views.teams.team_views import (
    TeamListView, TeamCreateView, TeamDetailView, 
    TeamUpdateView, TeamDeleteView
)
from .views.teams.member_views import (
    add_team_member, change_member_role, 
    remove_team_member, leave_team
)

app_name = "public"

urlpatterns = []

# Home page
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

# Team URLs
urlpatterns += [
    path("teams/", TeamListView.as_view(), name="team-list"),
    path("teams/create/", TeamCreateView.as_view(), name="team-create"),
    path("teams/<slug:team_slug>/", TeamDetailView.as_view(), name="team-detail"),
    path("teams/<slug:team_slug>/edit/", TeamUpdateView.as_view(), name="team-edit"),
    path("teams/<slug:team_slug>/delete/", TeamDeleteView.as_view(), name="team-delete"),
    
    # Team membership URLs
    path("teams/<slug:team_slug>/members/add/", add_team_member, name="add-team-member"),
    path(
        "teams/<slug:team_slug>/members/<int:member_id>/change-role/", 
        change_member_role, 
        name="change-member-role"
    ),
    path(
        "teams/<slug:team_slug>/members/<int:member_id>/remove/", 
        remove_team_member, 
        name="remove-team-member"
    ),
    path("teams/<slug:team_slug>/leave/", leave_team, name="leave-team"),
]
