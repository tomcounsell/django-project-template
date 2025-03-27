from django.contrib.auth import views as auth_views
from django.urls import path
from django.urls import reverse_lazy

from .views import account
from .views.teams.team_views import (
    TeamListView, TeamCreateView, TeamDetailView, 
    TeamUpdateView, TeamDeleteView
)
from .views.teams.member_views import (
    add_team_member, change_member_role, 
    remove_team_member, leave_team
)
from .views.todos import todo_views

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
    
    # Password reset routes
    path(
        "account/password/reset/",
        auth_views.PasswordResetView.as_view(
            template_name='account/password/reset.html',
            email_template_name='account/password/reset_email.html',
            success_url=reverse_lazy('public:password-reset-done')
        ),
        name="password-reset",
    ),
    path(
        "account/password/reset/done/",
        auth_views.PasswordResetDoneView.as_view(
            template_name='account/password/reset_done.html'
        ),
        name="password-reset-done",
    ),
    path(
        "account/password/reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name='account/password/reset_confirm.html',
            success_url=reverse_lazy('public:password-reset-complete')
        ),
        name="password-reset-confirm",
    ),
    path(
        "account/password/reset/complete/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name='account/password/reset_complete.html'
        ),
        name="password-reset-complete",
    ),
    
    # Password change routes (for authenticated users)
    path(
        "account/password/change/",
        auth_views.PasswordChangeView.as_view(
            template_name='account/password/change.html',
            success_url=reverse_lazy('public:password-change-done')
        ),
        name="password-change",
    ),
    path(
        "account/password/change/done/",
        auth_views.PasswordChangeDoneView.as_view(
            template_name='account/password/change_done.html'
        ),
        name="password-change-done",
    ),
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

# Todo URLs
urlpatterns += [
    path("todos/", todo_views.TodoListView.as_view(), name="todo-list"),
    path("todos/create/", todo_views.TodoCreateView.as_view(), name="todo-create"),
    path("todos/<int:pk>/", todo_views.TodoDetailView.as_view(), name="todo-detail"),
    path("todos/<int:pk>/update/", todo_views.TodoUpdateView.as_view(), name="todo-update"),
    path("todos/<int:pk>/delete/", todo_views.TodoDeleteView.as_view(), name="todo-delete"),
    path("todos/<int:pk>/complete/", todo_views.TodoCompleteView.as_view(), name="todo-complete"),
]
