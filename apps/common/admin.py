import json
from django.contrib import admin
from django.utils.html import format_html
from django.urls import path, reverse
from django.db.models import Count, Sum, Q
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.shortcuts import redirect, render
from django.utils.timezone import now
from django import forms
from django.db import models
from django.utils.translation import gettext_lazy as _

from rest_framework_api_key.admin import APIKeyModelAdmin
from unfold.admin import ModelAdmin, TabularInline, StackedInline
from unfold.forms import AdminPasswordChangeForm, UserChangeForm, UserCreationForm
from unfold.decorators import action, display
from unfold.contrib.filters.admin import (
    TextFilter,
    RangeDateFilter,
    RangeDateTimeFilter,
    RangeNumericFilter,
    ChoicesDropdownFilter,
)
from django.contrib.admin import SimpleListFilter, BooleanFieldListFilter
import datetime
from unfold.sections import TableSection, TemplateSection
from unfold.components import BaseComponent, register_component
from unfold.enums import ActionVariant
from unfold.contrib.forms.widgets import WysiwygWidget

from apps.common.models import (
    User,
    Team,
    TeamMember,
    BlogPost,
    TodoItem,
    UserAPIKey,
    TeamAPIKey,
    Address,
    City,
    Country,
    Currency,
    Document,
    Email,
    SMS,
    Image,
    Note,
    Payment,
    Subscription,
    Upload,
)

# Define which models should be shown in the main admin navigation
MAIN_NAV_MODELS = ["User", "Team", "BlogPost", "TodoItem"]

# Categories for model organization
ADMIN_CATEGORIES = {
    "People": ["User", "Team", "TeamMember"],
    "Content": ["BlogPost", "Note", "Document", "Image", "Upload"],
    "Tasks": ["TodoItem"],
    "Locations": ["Address", "City", "Country"],
    "Finance": ["Payment", "Subscription", "Currency"],
    "Communications": ["Email", "SMS"],
    "Security": ["UserAPIKey", "TeamAPIKey"],
}


# Custom Filters for Admin
class BooleanFilter(SimpleListFilter):
    """Custom boolean filter for non-boolean fields."""

    title = "Filter Title"
    parameter_name = "param"
    filter_function = None

    def __init__(self, request, params, model, model_admin):
        super().__init__(request, params, model, model_admin)
        self.filter_function = (
            self.lookup_choices[2] if len(self.lookup_choices) > 2 else None
        )

    def lookups(self, request, model_admin):
        return (
            ("1", _("Yes")),
            ("0", _("No")),
        )

    def queryset(self, request, queryset):
        if self.value() is None:
            return queryset

        if self.filter_function:
            return self.filter_function(queryset, self.value() == "1")

        return queryset


class HasDescriptionFilter(BooleanFilter):
    """Filter that shows todos with or without descriptions."""

    title = _("Has Description")
    parameter_name = "has_description"

    def queryset(self, request, queryset):
        if self.value() is None:
            return queryset

        if self.value() == "1":
            return queryset.exclude(description="")
        else:
            return queryset.filter(description="")


class IsOverdueFilter(BooleanFilter):
    """Filter that shows overdue todos."""

    title = _("Is Overdue")
    parameter_name = "is_overdue"

    def queryset(self, request, queryset):
        if self.value() is None:
            return queryset

        now_date = datetime.datetime.now()

        if self.value() == "1":
            return queryset.filter(
                due_at__lt=now_date, status__in=["TODO", "IN_PROGRESS", "BLOCKED"]
            )
        else:
            return queryset.filter(
                Q(due_at__gte=now_date) | Q(due_at__isnull=True) | Q(status="DONE")
            )


class DueInFilter(SimpleListFilter):
    """Filter that shows todos due within a certain timeframe."""

    title = _("Due In")
    parameter_name = "due_in"

    def lookups(self, request, model_admin):
        return (
            ("today", _("Due Today")),
            ("tomorrow", _("Due Tomorrow")),
            ("week", _("Due This Week")),
            ("overdue", _("Overdue")),
            ("month", _("Due This Month")),
        )

    def queryset(self, request, queryset):
        today = datetime.datetime.now().date()
        tomorrow = today + datetime.timedelta(days=1)
        week_end = today + datetime.timedelta(days=7)
        month_end = today + datetime.timedelta(days=30)

        if self.value() == "today":
            return queryset.filter(
                due_at__date=today, status__in=["TODO", "IN_PROGRESS", "BLOCKED"]
            )
        elif self.value() == "tomorrow":
            return queryset.filter(
                due_at__date=tomorrow, status__in=["TODO", "IN_PROGRESS", "BLOCKED"]
            )
        elif self.value() == "week":
            return queryset.filter(
                due_at__date__range=[today, week_end],
                status__in=["TODO", "IN_PROGRESS", "BLOCKED"],
            )
        elif self.value() == "month":
            return queryset.filter(
                due_at__date__range=[today, month_end],
                status__in=["TODO", "IN_PROGRESS", "BLOCKED"],
            )
        elif self.value() == "overdue":
            return queryset.filter(
                due_at__lt=datetime.datetime.now(),
                status__in=["TODO", "IN_PROGRESS", "BLOCKED"],
            )
        return queryset


class UserAssignedFilter(SimpleListFilter):
    """Filter that shows todos assigned to the current user."""

    title = _("Assignment")
    parameter_name = "assigned"

    def lookups(self, request, model_admin):
        return (
            ("me", _("Assigned to me")),
            ("unassigned", _("Unassigned")),
            ("others", _("Assigned to others")),
        )

    def queryset(self, request, queryset):
        if self.value() == "me":
            return queryset.filter(assignee=request.user)
        elif self.value() == "unassigned":
            return queryset.filter(assignee__isnull=True)
        elif self.value() == "others":
            return queryset.exclude(assignee=request.user).exclude(
                assignee__isnull=True
            )
        return queryset


class CompletedWithinFilter(SimpleListFilter):
    """Filter that shows todos completed within a certain timeframe."""

    title = _("Completed Within")
    parameter_name = "completed_within"

    def lookups(self, request, model_admin):
        return (
            ("today", _("Today")),
            ("yesterday", _("Yesterday")),
            ("week", _("This Week")),
            ("month", _("This Month")),
        )

    def queryset(self, request, queryset):
        today = datetime.datetime.now().date()
        yesterday = today - datetime.timedelta(days=1)
        week_start = today - datetime.timedelta(days=today.weekday())
        month_start = today.replace(day=1)

        if self.value() == "today":
            return queryset.filter(completed_at__date=today, status="DONE")
        elif self.value() == "yesterday":
            return queryset.filter(completed_at__date=yesterday, status="DONE")
        elif self.value() == "week":
            return queryset.filter(completed_at__date__gte=week_start, status="DONE")
        elif self.value() == "month":
            return queryset.filter(completed_at__date__gte=month_start, status="DONE")
        return queryset


@admin.register(User)
class UserAdmin(ModelAdmin):
    form = UserChangeForm
    add_form = UserCreationForm
    change_password_form = AdminPasswordChangeForm
    compressed_fields = True
    warn_unsaved_form = True

    list_display = [
        "display_header",
        "email",
        "status_badge",
        "display_staff",
        "display_superuser",
        "display_created",
    ]
    search_fields = ("username", "email", "first_name", "last_name")
    list_filter = [
        "is_staff",
        "is_active",
        "is_superuser",
        ("date_joined", RangeDateTimeFilter),
    ]
    list_filter_submit = True

    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (
            "Personal info",
            {
                "fields": (("first_name", "last_name"), "email", "biography"),
                "classes": ["tab"],
            },
        ),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
                "classes": ["tab"],
            },
        ),
        (
            "Important dates",
            {
                "fields": ("last_login", "date_joined"),
                "classes": ["tab"],
            },
        ),
    )
    readonly_fields = ["last_login", "date_joined"]

    # Add actions to the admin interface
    actions_detail = [
        "reset_user_password",
        "deactivate_user",
        {"title": _("More Actions"), "items": ["activate_user", "toggle_superuser"]},
    ]

    # Custom helper displays with the @display decorator
    @display(description=_("User"), header=True)
    def display_header(self, instance):
        # Return a list for a nicer user display with name,
        # initials and potential avatar
        return [
            instance.username,
            None,
            (
                f"{instance.first_name[:1]}{instance.last_name[:1]}".upper()
                if instance.first_name and instance.last_name
                else ""
            ),
        ]

    @display(description=_("Staff"), boolean=True)
    def display_staff(self, instance):
        return instance.is_staff

    @display(description=_("Superuser"), boolean=True)
    def display_superuser(self, instance):
        return instance.is_superuser

    @display(description=_("Created"))
    def display_created(self, instance):
        return instance.date_joined

    def status_badge(self, obj):
        if obj.is_active:
            return format_html(
                '<span class="unfold-badge bg-green-500 text-white">Active</span>'
            )
        return format_html(
            '<span class="unfold-badge bg-red-500 text-white">Inactive</span>'
        )

    status_badge.short_description = "Status"

    # Custom actions
    @action(description=_("Reset Password"))
    def reset_user_password(self, request, object_id):
        # Action to send a password reset email to the user
        user = User.objects.get(pk=object_id)
        # Logic to send password reset would go here
        messages.success(request, f"Password reset email sent to {user.email}")
        return redirect("admin:common_user_change", object_id)

    @action(description=_("Deactivate User"))
    def deactivate_user(self, request, object_id):
        user = User.objects.get(pk=object_id)
        user.is_active = False
        user.save()
        messages.success(request, f"User {user.username} has been deactivated")
        return redirect("admin:common_user_change", object_id)

    @action(description=_("Activate User"))
    def activate_user(self, request, object_id):
        user = User.objects.get(pk=object_id)
        user.is_active = True
        user.save()
        messages.success(request, f"User {user.username} has been activated")
        return redirect("admin:common_user_change", object_id)

    @action(description=_("Toggle Superuser Status"))
    def toggle_superuser(self, request, object_id):
        user = User.objects.get(pk=object_id)
        user.is_superuser = not user.is_superuser
        user.save()
        messages.success(request, f"Superuser status toggled for {user.username}")
        return redirect("admin:common_user_change", object_id)


class TeamMemberInline(TabularInline):
    model = TeamMember
    extra = 1
    autocomplete_fields = ["user"]
    ordering_field = "weight"  # Allow ordering of members
    show_change_link = True
    tab = True  # Show in a tab interface


# Create a Table Section for team members
class TeamMemberTableSection(TableSection):
    verbose_name = _("Team Members")
    related_name = "teammember_set"
    model_name = "teammember"
    fields = ["user", "role_display", "joined_at"]
    height = 380  # Fixed height

    def role_display(self, instance):
        colors = {
            "owner": "bg-purple-500",
            "admin": "bg-red-500",
            "member": "bg-blue-500",
            "guest": "bg-gray-500",
        }
        color = colors.get(instance.role, "bg-gray-500")

        return format_html(
            '<span class="unfold-badge {} text-white">{}</span>',
            color,
            instance.get_role_display(),
        )

    role_display.short_description = _("Role")


# Register a custom component for team stats
@register_component
class TeamStatsComponent(BaseComponent):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Count active vs inactive teams
        team_count = Team.objects.count()
        active_teams = Team.objects.filter(is_active=True).count()
        inactive_teams = team_count - active_teams

        # Get teams with most members
        teams_with_members = Team.objects.annotate(member_count=Count("members"))
        top_teams = teams_with_members.order_by("-member_count")[:5]

        context.update(
            {
                "team_count": team_count,
                "active_teams": active_teams,
                "inactive_teams": inactive_teams,
                "top_teams": top_teams,
            }
        )

        return context


@admin.register(Team)
class TeamAdmin(ModelAdmin):
    list_display = [
        "display_header",
        "slug",
        "member_count",
        "status_badge",
        "created_at",
    ]
    list_filter = [
        ("is_active", ChoicesDropdownFilter),
        ("created_at", RangeDateFilter),
    ]
    list_filter_submit = True
    search_fields = ("name", "slug", "description")
    prepopulated_fields = {"slug": ("name",)}
    inlines = [TeamMemberInline]
    list_sections = [TeamMemberTableSection]
    compressed_fields = True
    warn_unsaved_form = True

    # Add tabs to the detail view
    fieldsets = (
        (None, {"fields": ("name", "slug", "description", "is_active")}),
        (
            "Metadata",
            {
                "fields": ("meta_data",),
                "classes": ["tab"],
            },
        ),
        (
            "Timestamps",
            {
                "fields": ("created_at", "modified_at"),
                "classes": ["tab"],
            },
        ),
    )
    readonly_fields = ["created_at", "modified_at"]

    # Add actions to the admin interface
    actions_list = [
        "export_teams",
        {
            "title": _("Bulk Actions"),
            "variant": ActionVariant.PRIMARY,
            "items": ["activate_teams", "deactivate_teams"],
        },
    ]

    actions_detail = ["manage_members", "activate_team", "deactivate_team"]

    # Custom displays
    @display(description=_("Team"), header=True)
    def display_header(self, instance):
        return [
            instance.name,
            (
                instance.description[:30] + "..."
                if instance.description and len(instance.description) > 30
                else instance.description
            ),
        ]

    def member_count(self, obj):
        """Return the number of members in the team."""
        count = obj.members.count()
        return format_html(
            '<span class="unfold-badge bg-blue-500 text-white">{}</span>', count
        )

    def status_badge(self, obj):
        if obj.is_active:
            return format_html(
                '<span class="unfold-badge bg-green-500 text-white">Active</span>'
            )
        return format_html(
            '<span class="unfold-badge bg-red-500 text-white">Inactive</span>'
        )

    member_count.short_description = "Members"
    status_badge.short_description = "Status"

    # Custom actions
    @action(description=_("Export Teams"), icon="download")
    def export_teams(self, request):
        # Logic to export teams to CSV/Excel would go here
        messages.success(
            request, "Teams export initiated. You will receive an email when complete."
        )
        return redirect("admin:common_team_changelist")

    @action(description=_("Activate Teams"), icon="check_circle")
    def activate_teams(self, request):
        # Bulk activate teams
        queryset = self.get_queryset(request).filter(is_active=False)
        count = queryset.count()
        queryset.update(is_active=True)
        messages.success(request, f"{count} teams have been activated")
        return redirect("admin:common_team_changelist")

    @action(description=_("Deactivate Teams"), icon="block")
    def deactivate_teams(self, request):
        # Bulk deactivate teams
        queryset = self.get_queryset(request).filter(is_active=True)
        count = queryset.count()
        queryset.update(is_active=False)
        messages.success(request, f"{count} teams have been deactivated")
        return redirect("admin:common_team_changelist")

    @action(description=_("Manage Members"), url_path="manage-members")
    def manage_members(self, request, object_id):
        # This could redirect to a custom view or just to the inline
        team = Team.objects.get(pk=object_id)
        messages.info(request, f"Managing members for team: {team.name}")
        return redirect("admin:common_team_change", object_id)

    @action(description=_("Activate Team"))
    def activate_team(self, request, object_id):
        team = Team.objects.get(pk=object_id)
        team.is_active = True
        team.save()
        messages.success(request, f"Team {team.name} has been activated")
        return redirect("admin:common_team_change", object_id)

    @action(description=_("Deactivate Team"))
    def deactivate_team(self, request, object_id):
        team = Team.objects.get(pk=object_id)
        team.is_active = False
        team.save()
        messages.success(request, f"Team {team.name} has been deactivated")
        return redirect("admin:common_team_change", object_id)


@admin.register(TeamMember)
class TeamMemberAdmin(ModelAdmin):
    list_display = ("user", "team", "role_badge")
    list_filter = ("role", "team")
    search_fields = ("user__username", "user__email", "team__name")
    autocomplete_fields = ["user", "team"]

    def role_badge(self, obj):
        colors = {
            "owner": "bg-purple-500",
            "admin": "bg-red-500",
            "member": "bg-blue-500",
            "guest": "bg-gray-500",
        }
        color = colors.get(obj.role, "bg-gray-500")

        return format_html(
            '<span class="unfold-badge {} text-white">{}</span>',
            color,
            obj.get_role_display(),
        )

    role_badge.short_description = "Role"


@admin.register(BlogPost)
class BlogPostAdmin(ModelAdmin):
    list_display = (
        "title",
        "author_display",
        "location_display",
        "publishing_status",
        "expiration_status",
    )
    list_filter = ("published_at", "expired_at")
    search_fields = ("title", "subtitle", "content", "tags")
    date_hierarchy = "created_at"
    readonly_fields = ("created_at", "modified_at", "authored_at")

    fieldsets = (
        (
            "Content",
            {
                "fields": (
                    "title",
                    "subtitle",
                    "content",
                    "featured_image",
                    "reading_time_minutes",
                    "tags",
                )
            },
        ),
        (
            "Author Information",
            {"fields": ("author", "is_author_anonymous", "authored_at")},
        ),
        (
            "Publication Status",
            {"fields": ("published_at", "edited_at", "unpublished_at")},
        ),
        ("Expiration", {"fields": ("valid_at", "expired_at")}),
        ("Location", {"fields": ("address", "latitude", "longitude")}),
        ("Permalink", {"fields": ("slug",)}),
        ("Timestamps", {"fields": ("created_at", "modified_at")}),
    )

    def author_display(self, obj):
        return obj.author_display_name

    def location_display(self, obj):
        if obj.address:
            return format_html(
                '<span class="unfold-badge bg-blue-500 text-white">{}</span>',
                str(obj.address)[:30],
            )
        return "-"

    def publishing_status(self, obj):
        if obj.is_published:
            return format_html(
                '<span class="unfold-badge bg-green-500 text-white">Published</span>'
            )
        return format_html(
            '<span class="unfold-badge bg-gray-500 text-white">Draft</span>'
        )

    def expiration_status(self, obj):
        if obj.is_expired:
            return format_html(
                '<span class="unfold-badge bg-red-500 text-white">Expired</span>'
            )
        return format_html(
            '<span class="unfold-badge bg-green-500 text-white">Active</span>'
        )

    author_display.short_description = "Author"
    location_display.short_description = "Location"
    publishing_status.short_description = "Status"
    expiration_status.short_description = "Expiration"


class TodoItemTemplateSection(TemplateSection):
    template_name = "admin/dashboard/todo_stats.html"
    model_name = "todoitem"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        todo_stats = {
            "TODO": TodoItem.objects.filter(status="TODO").count(),
            "IN_PROGRESS": TodoItem.objects.filter(status="IN_PROGRESS").count(),
            "BLOCKED": TodoItem.objects.filter(status="BLOCKED").count(),
            "DONE": TodoItem.objects.filter(status="DONE").count(),
        }
        context["todo_stats"] = todo_stats
        context["total"] = sum(todo_stats.values())
        return context


@admin.register(TodoItem)
class TodoItemAdmin(ModelAdmin):
    list_display = [
        "display_header",
        "priority_badge",
        "category_badge",
        "status_badge",
        "assignee_display",
        "due_date_display",
    ]
    list_filter = [
        # Custom filters
        DueInFilter,
        UserAssignedFilter,
        CompletedWithinFilter,
        HasDescriptionFilter,
        IsOverdueFilter,
        # Default filters
        ("priority", ChoicesDropdownFilter),
        ("category", ChoicesDropdownFilter),
        ("status", ChoicesDropdownFilter),
        ("assignee", ChoicesDropdownFilter),
        ("due_at", RangeDateFilter),
        ("created_at", RangeDateTimeFilter),
    ]
    list_filter_submit = True
    list_sections = [TodoItemTemplateSection]
    search_fields = ("title", "description")
    date_hierarchy = "created_at"
    readonly_fields = ("created_at", "modified_at", "completed_at")
    autocomplete_fields = ["assignee"]
    warn_unsaved_form = True
    compressed_fields = True

    fieldsets = (
        (
            "Task Information",
            {"fields": ("title", "description", "priority", "category", "status")},
        ),
        (
            "Assignment",
            {
                "fields": ("assignee", "due_at"),
                "classes": ["tab"],
            },
        ),
        (
            "Completion",
            {
                "fields": ("completed_at",),
                "classes": ["tab"],
            },
        ),
        (
            "Timestamps",
            {
                "fields": ("created_at", "modified_at"),
                "classes": ["tab"],
            },
        ),
    )

    # Custom actions for TodoItem
    actions_list = [
        "mark_as_done",
        {
            "title": _("Bulk Status Update"),
            "items": ["mark_as_in_progress", "mark_as_blocked", "mark_as_todo"],
        },
        {
            "title": _("Priority Actions"),
            "variant": ActionVariant.PRIMARY,
            "items": ["set_high_priority", "set_medium_priority", "set_low_priority"],
        },
        {"title": _("Date Actions"), "items": ["clear_due_date"]},
    ]

    actions_detail = ["mark_todo_done", "mark_todo_in_progress", "copy_todo"]

    # Display header with rich context
    @display(description=_("Task"), header=True)
    def display_header(self, instance):
        # Return rich header with title and description preview
        return [
            instance.title,
            (
                instance.description[:50] + "..."
                if instance.description and len(instance.description) > 50
                else instance.description
            ),
        ]

    def priority_badge(self, obj):
        colors = {"HIGH": "bg-red-500", "MEDIUM": "bg-yellow-500", "LOW": "bg-blue-500"}
        return format_html(
            '<span class="unfold-badge {} text-white">{}</span>',
            colors.get(obj.priority, "bg-gray-500"),
            obj.get_priority_display(),
        )

    def category_badge(self, obj):
        colors = {
            "FRONTEND": "bg-purple-500",
            "BACKEND": "bg-blue-500",
            "API": "bg-green-500",
            "DATABASE": "bg-yellow-500",
            "PERFORMANCE": "bg-orange-500",
            "SECURITY": "bg-red-500",
            "DOCUMENTATION": "bg-gray-500",
            "TESTING": "bg-teal-500",
            "GENERAL": "bg-gray-500",
        }
        return format_html(
            '<span class="unfold-badge {} text-white">{}</span>',
            colors.get(obj.category, "bg-gray-500"),
            obj.get_category_display(),
        )

    def status_badge(self, obj):
        colors = {
            "TODO": "bg-blue-500",
            "IN_PROGRESS": "bg-yellow-500",
            "BLOCKED": "bg-red-500",
            "DONE": "bg-green-500",
        }
        return format_html(
            '<span class="unfold-badge {} text-white">{}</span>',
            colors.get(obj.status, "bg-gray-500"),
            obj.get_status_display(),
        )

    def assignee_display(self, obj):
        if obj.assignee:
            return f"{obj.assignee.first_name} {obj.assignee.last_name}"
        return "-"

    def due_date_display(self, obj):
        if not obj.due_at:
            return "-"

        if obj.is_overdue:
            return format_html(
                '<span class="unfold-badge bg-red-500 text-white">{}</span>',
                obj.time_remaining_display,
            )
        return format_html(
            '<span class="unfold-badge bg-blue-500 text-white">{}</span>',
            obj.time_remaining_display,
        )

    priority_badge.short_description = "Priority"
    category_badge.short_description = "Category"
    status_badge.short_description = "Status"
    assignee_display.short_description = "Assignee"
    due_date_display.short_description = "Due Date"

    # Custom actions
    @action(description=_("Mark as Done"), icon="done")
    def mark_as_done(self, request):
        # Bulk action to mark selected todos as done
        selected = request.POST.getlist("_selected_action")
        updated = TodoItem.objects.filter(id__in=selected).update(
            status="DONE", completed_at=now()
        )
        messages.success(request, f"Successfully marked {updated} items as done")
        return redirect("admin:common_todoitem_changelist")

    @action(description=_("Mark as In Progress"), icon="pending")
    def mark_as_in_progress(self, request):
        selected = request.POST.getlist("_selected_action")
        updated = TodoItem.objects.filter(id__in=selected).update(status="IN_PROGRESS")
        messages.success(request, f"Successfully marked {updated} items as in progress")
        return redirect("admin:common_todoitem_changelist")

    @action(description=_("Mark as Blocked"), icon="block")
    def mark_as_blocked(self, request):
        selected = request.POST.getlist("_selected_action")
        updated = TodoItem.objects.filter(id__in=selected).update(status="BLOCKED")
        messages.success(request, f"Successfully marked {updated} items as blocked")
        return redirect("admin:common_todoitem_changelist")

    @action(description=_("Reset to Todo"), icon="refresh")
    def mark_as_todo(self, request):
        selected = request.POST.getlist("_selected_action")
        updated = TodoItem.objects.filter(id__in=selected).update(
            status="TODO", completed_at=None
        )
        messages.success(request, f"Successfully reset {updated} items to todo status")
        return redirect("admin:common_todoitem_changelist")

    @action(description=_("Set High Priority"), icon="priority_high")
    def set_high_priority(self, request):
        selected = request.POST.getlist("_selected_action")
        updated = TodoItem.objects.filter(id__in=selected).update(priority="HIGH")
        messages.success(request, f"Successfully set {updated} items to high priority")
        return redirect("admin:common_todoitem_changelist")

    @action(description=_("Set Medium Priority"), icon="low_priority")
    def set_medium_priority(self, request):
        selected = request.POST.getlist("_selected_action")
        updated = TodoItem.objects.filter(id__in=selected).update(priority="MEDIUM")
        messages.success(
            request, f"Successfully set {updated} items to medium priority"
        )
        return redirect("admin:common_todoitem_changelist")

    @action(description=_("Set Low Priority"), icon="low_priority")
    def set_low_priority(self, request):
        selected = request.POST.getlist("_selected_action")
        updated = TodoItem.objects.filter(id__in=selected).update(priority="LOW")
        messages.success(request, f"Successfully set {updated} items to low priority")
        return redirect("admin:common_todoitem_changelist")

    @action(description=_("Clear Due Date"), icon="event_busy")
    def clear_due_date(self, request):
        selected = request.POST.getlist("_selected_action")
        updated = TodoItem.objects.filter(id__in=selected).update(due_at=None)
        messages.success(request, f"Successfully cleared due date for {updated} items")
        return redirect("admin:common_todoitem_changelist")

    # Detail actions
    @action(description=_("Mark as Done"))
    def mark_todo_done(self, request, object_id):
        todo = TodoItem.objects.get(pk=object_id)
        todo.status = "DONE"
        todo.completed_at = now()
        todo.save()
        messages.success(request, f'Todo "{todo.title}" marked as done')
        return redirect("admin:common_todoitem_change", object_id)

    @action(description=_("Mark as In Progress"))
    def mark_todo_in_progress(self, request, object_id):
        todo = TodoItem.objects.get(pk=object_id)
        todo.status = "IN_PROGRESS"
        todo.save()
        messages.success(request, f'Todo "{todo.title}" marked as in progress')
        return redirect("admin:common_todoitem_change", object_id)

    @action(description=_("Create Copy"))
    def copy_todo(self, request, object_id):
        todo = TodoItem.objects.get(pk=object_id)
        new_todo = TodoItem.objects.create(
            title=f"Copy of {todo.title}",
            description=todo.description,
            priority=todo.priority,
            category=todo.category,
            status="TODO",
            assignee=todo.assignee,
            due_at=todo.due_at,
        )
        messages.success(request, f'Created copy of "{todo.title}"')
        return redirect("admin:common_todoitem_change", new_todo.id)


@admin.register(UserAPIKey)
class UserAPIKeyAdmin(APIKeyModelAdmin):
    list_display = ("name", "user", "prefix", "created_at", "revoked")
    list_filter = ("revoked",)
    search_fields = ("name", "prefix", "user__username", "user__email")
    autocomplete_fields = ["user"]
    readonly_fields = ("created_at", "modified_at")


@admin.register(TeamAPIKey)
class TeamAPIKeyAdmin(APIKeyModelAdmin):
    list_display = ("name", "team", "prefix", "created_at", "revoked")
    list_filter = ("revoked",)
    search_fields = ("name", "prefix", "team__name")
    autocomplete_fields = ["team"]
    readonly_fields = ("created_at", "modified_at")


@admin.register(Address)
class AddressAdmin(ModelAdmin):
    list_display = ("line_1", "city", "region", "postal_code", "country", "map_link")
    list_filter = ("country",)
    search_fields = ("line_1", "line_2", "city", "region", "postal_code")
    readonly_fields = ("created_at", "modified_at")
    autocomplete_fields = ["country"]

    fieldsets = (
        (
            "Address Information",
            {
                "fields": (
                    "line_1",
                    "line_2",
                    "line_3",
                    "city",
                    "region",
                    "postal_code",
                    "country",
                )
            },
        ),
        ("Google Maps", {"fields": ("google_map_link",)}),
        ("Timestamps", {"fields": ("created_at", "modified_at")}),
    )

    def map_link(self, obj):
        if obj.google_map_link:
            return format_html(
                '<a href="{}" target="_blank" class="unfold-badge bg-blue-500 text-white">View Map</a>',
                obj.google_map_url,
            )
        return "-"

    map_link.short_description = "Map"


@admin.register(City)
class CityAdmin(ModelAdmin):
    list_display = ("name", "code", "country", "currency_display")
    list_filter = ("country",)
    search_fields = ("name", "code", "country__name")
    autocomplete_fields = ["country"]

    def currency_display(self, obj):
        if obj.currency:
            return format_html(
                '<span class="unfold-badge bg-green-500 text-white">{}</span>',
                obj.currency,
            )
        return "-"

    currency_display.short_description = "Currency"


@admin.register(Country)
class CountryAdmin(ModelAdmin):
    list_display = ("name", "code", "calling_code_display", "currency")
    list_filter = ("currency",)
    search_fields = ("name", "code")
    autocomplete_fields = ["currency"]

    def calling_code_display(self, obj):
        if obj.calling_code:
            return format_html(
                '<span class="unfold-badge bg-blue-500 text-white">+{}</span>',
                obj.calling_code,
            )
        return "-"

    calling_code_display.short_description = "Calling Code"


@admin.register(Currency)
class CurrencyAdmin(ModelAdmin):
    list_display = ("name", "code_upper", "created_at")
    search_fields = ("name", "code")
    readonly_fields = ("created_at", "modified_at")

    def code_upper(self, obj):
        return format_html(
            '<span class="unfold-badge bg-green-500 text-white">{}</span>',
            obj.code.upper(),
        )

    code_upper.short_description = "Code"


@admin.register(Note)
class NoteAdmin(ModelAdmin):
    list_display = ("id", "text_preview", "author", "created_at")
    search_fields = ("text", "author__username", "author__email")
    readonly_fields = ("created_at", "modified_at")
    autocomplete_fields = ["author"]

    def text_preview(self, obj):
        if obj.text:
            return obj.text[:50] + "..." if len(obj.text) > 50 else obj.text
        return "-"

    text_preview.short_description = "Text"


@admin.register(Email)
class EmailAdmin(ModelAdmin):
    list_display = (
        "subject",
        "to_address",
        "from_address",
        "email_type",
        "sent_status",
        "read_status",
    )
    list_filter = ("type", "sent_at", "read_at")
    search_fields = ("to_address", "from_address", "subject", "body")
    readonly_fields = ("created_at", "modified_at", "sent_at", "read_at")

    fieldsets = (
        (
            "Email Details",
            {"fields": ("to_address", "from_address", "subject", "body", "type")},
        ),
        ("Attachments", {"fields": ("attachments",)}),
        ("Status", {"fields": ("sent_at", "read_at")}),
        ("Timestamps", {"fields": ("created_at", "modified_at")}),
    )

    def email_type(self, obj):
        type_colors = {
            0: "bg-blue-500",  # NOTIFICATION
            1: "bg-green-500",  # CONFIRMATION
            2: "bg-purple-500",  # PASSWORD
        }
        return format_html(
            '<span class="unfold-badge {} text-white">{}</span>',
            type_colors.get(obj.type, "bg-gray-500"),
            obj.get_type_display(),
        )

    def sent_status(self, obj):
        if obj.sent_at:
            return format_html(
                '<span class="unfold-badge bg-green-500 text-white">Sent</span>'
            )
        return format_html(
            '<span class="unfold-badge bg-yellow-500 text-white">Pending</span>'
        )

    def read_status(self, obj):
        if obj.read_at:
            return format_html(
                '<span class="unfold-badge bg-green-500 text-white">Read</span>'
            )
        return format_html(
            '<span class="unfold-badge bg-gray-500 text-white">Unread</span>'
        )

    email_type.short_description = "Type"
    sent_status.short_description = "Sent"
    read_status.short_description = "Read"


@admin.register(SMS)
class SMSAdmin(ModelAdmin):
    list_display = (
        "to_number",
        "from_number",
        "body_preview",
        "delivery_status",
        "sent_status",
    )
    list_filter = ("status", "sent_at", "read_at")
    search_fields = ("to_number", "from_number", "body", "external_id")
    readonly_fields = ("created_at", "modified_at", "sent_at", "read_at", "external_id")

    fieldsets = (
        ("SMS Details", {"fields": ("to_number", "from_number", "body")}),
        (
            "Twilio Information",
            {"fields": ("external_id", "status", "error_code", "error_message")},
        ),
        ("Status", {"fields": ("sent_at", "read_at")}),
        ("Timestamps", {"fields": ("created_at", "modified_at")}),
    )

    def body_preview(self, obj):
        if obj.body:
            return obj.body[:30] + "..." if len(obj.body) > 30 else obj.body
        return "-"

    def delivery_status(self, obj):
        status_colors = {
            "queued": "bg-blue-500",
            "sent": "bg-yellow-500",
            "delivered": "bg-green-500",
            "failed": "bg-red-500",
            "undelivered": "bg-orange-500",
        }
        if obj.status:
            return format_html(
                '<span class="unfold-badge {} text-white">{}</span>',
                status_colors.get(obj.status.lower(), "bg-gray-500"),
                obj.status,
            )
        return "-"

    def sent_status(self, obj):
        if obj.sent_at:
            return format_html(
                '<span class="unfold-badge bg-green-500 text-white">Sent</span>'
            )
        return format_html(
            '<span class="unfold-badge bg-yellow-500 text-white">Pending</span>'
        )

    body_preview.short_description = "Message"
    delivery_status.short_description = "Status"
    sent_status.short_description = "Sent"


@admin.register(Upload)
class UploadAdmin(ModelAdmin):
    list_display = (
        "name_display",
        "file_type_display",
        "size_display",
        "status_badge",
        "created_at",
    )
    list_filter = ("status", "content_type")
    search_fields = ("name", "original", "s3_key")
    readonly_fields = (
        "created_at",
        "modified_at",
        "size",
        "dimensions_display",
        "preview",
    )

    fieldsets = (
        ("Upload Information", {"fields": ("name", "original", "thumbnail")}),
        (
            "File Information",
            {"fields": ("content_type", "size", "dimensions_display", "preview")},
        ),
        ("S3 Storage", {"fields": ("s3_bucket", "s3_key")}),
        ("Status", {"fields": ("status", "error")}),
        ("Metadata", {"fields": ("meta_data",)}),
        ("Timestamps", {"fields": ("created_at", "modified_at")}),
    )

    def name_display(self, obj):
        return obj.name or f"Upload {obj.id}"

    def file_type_display(self, obj):
        if obj.file_type:
            return format_html(
                '<span class="unfold-badge bg-blue-500 text-white">{}</span>',
                obj.file_type,
            )
        return "-"

    def size_display(self, obj):
        if obj.size:
            # Convert bytes to KB or MB
            if obj.size < 1024:
                return f"{obj.size} B"
            elif obj.size < 1024 * 1024:
                return f"{obj.size/1024:.1f} KB"
            else:
                return f"{obj.size/(1024*1024):.1f} MB"
        return "-"

    def status_badge(self, obj):
        status_colors = {
            "pending": "bg-blue-500",
            "processing": "bg-yellow-500",
            "complete": "bg-green-500",
            "error": "bg-red-500",
        }
        return format_html(
            '<span class="unfold-badge {} text-white">{}</span>',
            status_colors.get(obj.status, "bg-gray-500"),
            obj.status.capitalize(),
        )

    def dimensions_display(self, obj):
        """Display image dimensions if available"""
        if obj.dimensions and all(obj.dimensions):
            return f"{obj.dimensions[0]} x {obj.dimensions[1]}"
        return "-"

    def preview(self, obj):
        """Display a preview of the file if possible"""
        if obj.is_image and obj.original:
            return format_html(
                '<img src="{}" style="max-width: 300px; max-height: 200px;" />',
                obj.original,
            )
        if obj.is_pdf and obj.original:
            return format_html(
                '<a href="{}" target="_blank" class="unfold-badge bg-red-500 text-white">View PDF</a>',
                obj.original,
            )
        return "-"

    name_display.short_description = "Name"
    file_type_display.short_description = "Type"
    size_display.short_description = "Size"
    status_badge.short_description = "Status"
    dimensions_display.short_description = "Dimensions"
    preview.short_description = "Preview"


@admin.register(Image)
class ImageAdmin(ModelAdmin):
    list_display = ("name_display", "dimensions_display", "preview", "created_at")
    search_fields = ("name", "original")
    readonly_fields = ("created_at", "modified_at", "dimensions_display", "preview")

    fieldsets = (
        ("Image Information", {"fields": ("name", "original", "thumbnail_url")}),
        ("File Information", {"fields": ("dimensions_display", "preview")}),
        ("S3 Storage", {"fields": ("s3_bucket", "s3_key")}),
        ("Metadata", {"fields": ("meta_data",)}),
        ("Timestamps", {"fields": ("created_at", "modified_at")}),
    )

    def name_display(self, obj):
        return obj.name or f"Image {obj.id}"

    def dimensions_display(self, obj):
        """Display image dimensions if available"""
        if obj.width and obj.height:
            return f"{obj.width} x {obj.height}"
        return "-"

    def preview(self, obj):
        """Display a preview of the image"""
        if obj.original:
            return format_html(
                '<img src="{}" style="max-width: 300px; max-height: 200px;" />',
                obj.original,
            )
        return "-"

    name_display.short_description = "Name"
    dimensions_display.short_description = "Dimensions"
    preview.short_description = "Preview"


@admin.register(Payment)
class PaymentAdmin(ModelAdmin):
    list_display = (
        "amount_display",
        "status_badge",
        "user",
        "payment_method_display",
        "subscription",
        "paid_at",
    )
    list_filter = ("status", "payment_method", "paid_at")
    search_fields = (
        "user__username",
        "user__email",
        "stripe_payment_intent_id",
        "description",
    )
    readonly_fields = ("created_at", "modified_at")
    autocomplete_fields = ["user", "subscription"]

    fieldsets = (
        (
            "Payment Information",
            {"fields": ("user", "amount", "payment_method", "last4", "description")},
        ),
        ("Status", {"fields": ("status", "paid_at", "refunded_at")}),
        ("Subscription", {"fields": ("subscription",)}),
        ("Stripe", {"fields": ("stripe_payment_intent_id", "receipt_url")}),
        ("Timestamps", {"fields": ("created_at", "modified_at")}),
    )

    def status_badge(self, obj):
        status_colors = {
            "pending": "bg-blue-500",
            "succeeded": "bg-green-500",
            "failed": "bg-red-500",
            "refunded": "bg-purple-500",
            "canceled": "bg-gray-500",
        }
        return format_html(
            '<span class="unfold-badge {} text-white">{}</span>',
            status_colors.get(obj.status, "bg-gray-500"),
            obj.status.capitalize(),
        )

    def payment_method_display(self, obj):
        if obj.payment_method:
            label = obj.payment_method
            if obj.last4:
                label += f" (*{obj.last4})"
            return format_html(
                '<span class="unfold-badge bg-blue-500 text-white">{}</span>', label
            )
        return "-"

    status_badge.short_description = "Status"
    payment_method_display.short_description = "Method"


@admin.register(Subscription)
class SubscriptionAdmin(ModelAdmin):
    list_display = (
        "user",
        "plan_name",
        "price_display",
        "status_badge",
        "renewal_info",
        "trial_badge",
    )
    list_filter = ("status", "interval", "cancel_at_period_end")
    search_fields = (
        "user__username",
        "user__email",
        "plan_name",
        "stripe_subscription_id",
    )
    readonly_fields = ("created_at", "modified_at")
    autocomplete_fields = ["user"]

    fieldsets = (
        (
            "Subscription Information",
            {"fields": ("user", "plan_name", "price", "interval")},
        ),
        ("Status", {"fields": ("status", "start_date", "end_date", "canceled_at")}),
        (
            "Billing Period",
            {
                "fields": (
                    "current_period_start",
                    "current_period_end",
                    "cancel_at_period_end",
                )
            },
        ),
        ("Trial", {"fields": ("trial_end",)}),
        ("Stripe", {"fields": ("stripe_subscription_id",)}),
        ("Timestamps", {"fields": ("created_at", "modified_at")}),
    )

    def status_badge(self, obj):
        status_colors = {
            "active": "bg-green-500",
            "canceled": "bg-red-500",
            "past_due": "bg-orange-500",
            "trialing": "bg-blue-500",
            "unpaid": "bg-yellow-500",
            "incomplete": "bg-gray-500",
            "incomplete_expired": "bg-gray-500",
        }
        return format_html(
            '<span class="unfold-badge {} text-white">{}</span>',
            status_colors.get(obj.status, "bg-gray-500"),
            obj.status.capitalize(),
        )

    def renewal_info(self, obj):
        if obj.current_period_end:
            if obj.cancel_at_period_end:
                return format_html(
                    '<span class="unfold-badge bg-red-500 text-white">Cancels on {}</span>',
                    obj.current_period_end.strftime("%Y-%m-%d"),
                )
            else:
                return format_html(
                    '<span class="unfold-badge bg-blue-500 text-white">Renews on {}</span>',
                    obj.current_period_end.strftime("%Y-%m-%d"),
                )
        return "-"

    def trial_badge(self, obj):
        if obj.is_trial:
            if obj.trial_end:
                return format_html(
                    '<span class="unfold-badge bg-purple-500 text-white">Trial ends {}</span>',
                    obj.trial_end.strftime("%Y-%m-%d"),
                )
            return format_html(
                '<span class="unfold-badge bg-purple-500 text-white">Trial</span>'
            )
        return "-"

    status_badge.short_description = "Status"
    renewal_info.short_description = "Renewal"
    trial_badge.short_description = "Trial"


@admin.register(Document)
class DocumentAdmin(ModelAdmin):
    list_display = ("id", "name_display", "file_type_display", "created_at")
    search_fields = ("name", "original")
    readonly_fields = ("created_at", "modified_at")

    def name_display(self, obj):
        return obj.name or f"Document {obj.id}"

    def file_type_display(self, obj):
        if obj.file_type:
            return format_html(
                '<span class="unfold-badge bg-blue-500 text-white">{}</span>',
                obj.file_type,
            )
        return "-"

    name_display.short_description = "Name"
    file_type_display.short_description = "Type"
