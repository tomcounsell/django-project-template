import datetime

from django import forms
from django.contrib import admin, messages
from django.db.models import Count, Q
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import path, reverse
from django.utils.html import format_html
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _
from unfold.admin import ModelAdmin
from unfold.contrib.filters.admin import (
    ChoicesDropdownFilter,
    RangeDateFilter,
    RangeDateTimeFilter,
)
from unfold.decorators import action, display
from unfold.enums import ActionVariant
from unfold.sections import TemplateSection

from apps.staff.models import Wish


# Custom Filters for Admin
class HasDescriptionFilter(admin.SimpleListFilter):
    """Filter that shows wishes with or without descriptions."""

    title = _("Has Description")
    parameter_name = "has_description"

    def lookups(self, request, model_admin):
        return (
            ("1", _("Yes")),
            ("0", _("No")),
        )

    def queryset(self, request, queryset):
        if self.value() is None:
            return queryset

        if self.value() == "1":
            return queryset.exclude(description="")
        else:
            return queryset.filter(description="")


class IsOverdueFilter(admin.SimpleListFilter):
    """Filter that shows overdue wishes."""

    title = _("Is Overdue")
    parameter_name = "is_overdue"

    def lookups(self, request, model_admin):
        return (
            ("1", _("Yes")),
            ("0", _("No")),
        )

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


class DueInFilter(admin.SimpleListFilter):
    """Filter that shows wishes due within a certain timeframe."""

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


class UserAssignedFilter(admin.SimpleListFilter):
    """Filter that shows wishes assigned to the current user."""

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


class CompletedWithinFilter(admin.SimpleListFilter):
    """Filter that shows wishes completed within a certain timeframe."""

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


class WishTemplateSection(TemplateSection):
    template_name = "admin/dashboard/todo_stats.html"  # Reusing the same template
    model_name = "wish"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        wish_stats = {
            "TODO": Wish.objects.filter(status="TODO").count(),
            "IN_PROGRESS": Wish.objects.filter(status="IN_PROGRESS").count(),
            "BLOCKED": Wish.objects.filter(status="BLOCKED").count(),
            "DONE": Wish.objects.filter(status="DONE").count(),
        }
        context["todo_stats"] = wish_stats  # Reusing the same context variable name
        context["total"] = sum(wish_stats.values())
        return context


@admin.register(Wish)
class WishAdmin(ModelAdmin):
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
    list_sections = [WishTemplateSection]
    search_fields = ("title", "description")
    date_hierarchy = "created_at"
    readonly_fields = ("created_at", "modified_at", "completed_at")
    autocomplete_fields = ["assignee"]
    warn_unsaved_form = True
    compressed_fields = True

    fieldsets = (
        (
            "Wish Information",
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

    # Custom actions for Wish
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

    actions_detail = ["mark_wish_done", "mark_wish_in_progress", "copy_wish"]

    # Display header with rich context
    @display(description=_("Wish"), header=True)
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
        # Bulk action to mark selected wishes as done
        selected = request.POST.getlist("_selected_action")
        updated = Wish.objects.filter(id__in=selected).update(
            status="DONE", completed_at=now()
        )
        messages.success(request, f"Successfully marked {updated} wishes as done")
        return redirect("admin:staff_wish_changelist")

    @action(description=_("Mark as In Progress"), icon="pending")
    def mark_as_in_progress(self, request):
        selected = request.POST.getlist("_selected_action")
        updated = Wish.objects.filter(id__in=selected).update(status="IN_PROGRESS")
        messages.success(request, f"Successfully marked {updated} wishes as in progress")
        return redirect("admin:staff_wish_changelist")

    @action(description=_("Mark as Blocked"), icon="block")
    def mark_as_blocked(self, request):
        selected = request.POST.getlist("_selected_action")
        updated = Wish.objects.filter(id__in=selected).update(status="BLOCKED")
        messages.success(request, f"Successfully marked {updated} wishes as blocked")
        return redirect("admin:staff_wish_changelist")

    @action(description=_("Reset to Todo"), icon="refresh")
    def mark_as_todo(self, request):
        selected = request.POST.getlist("_selected_action")
        updated = Wish.objects.filter(id__in=selected).update(
            status="TODO", completed_at=None
        )
        messages.success(request, f"Successfully reset {updated} wishes to todo status")
        return redirect("admin:staff_wish_changelist")

    @action(description=_("Set High Priority"), icon="priority_high")
    def set_high_priority(self, request):
        selected = request.POST.getlist("_selected_action")
        updated = Wish.objects.filter(id__in=selected).update(priority="HIGH")
        messages.success(request, f"Successfully set {updated} wishes to high priority")
        return redirect("admin:staff_wish_changelist")

    @action(description=_("Set Medium Priority"), icon="low_priority")
    def set_medium_priority(self, request):
        selected = request.POST.getlist("_selected_action")
        updated = Wish.objects.filter(id__in=selected).update(priority="MEDIUM")
        messages.success(
            request, f"Successfully set {updated} wishes to medium priority"
        )
        return redirect("admin:staff_wish_changelist")

    @action(description=_("Set Low Priority"), icon="low_priority")
    def set_low_priority(self, request):
        selected = request.POST.getlist("_selected_action")
        updated = Wish.objects.filter(id__in=selected).update(priority="LOW")
        messages.success(request, f"Successfully set {updated} wishes to low priority")
        return redirect("admin:staff_wish_changelist")

    @action(description=_("Clear Due Date"), icon="event_busy")
    def clear_due_date(self, request):
        selected = request.POST.getlist("_selected_action")
        updated = Wish.objects.filter(id__in=selected).update(due_at=None)
        messages.success(request, f"Successfully cleared due date for {updated} wishes")
        return redirect("admin:staff_wish_changelist")

    # Detail actions
    @action(description=_("Mark as Done"))
    def mark_wish_done(self, request, object_id):
        wish = Wish.objects.get(pk=object_id)
        wish.status = "DONE"
        wish.completed_at = now()
        wish.save()
        messages.success(request, f'Wish "{wish.title}" marked as done')
        return redirect("admin:staff_wish_change", object_id)

    @action(description=_("Mark as In Progress"))
    def mark_wish_in_progress(self, request, object_id):
        wish = Wish.objects.get(pk=object_id)
        wish.status = "IN_PROGRESS"
        wish.save()
        messages.success(request, f'Wish "{wish.title}" marked as in progress')
        return redirect("admin:staff_wish_change", object_id)

    @action(description=_("Create Copy"))
    def copy_wish(self, request, object_id):
        wish = Wish.objects.get(pk=object_id)
        new_wish = Wish.objects.create(
            title=f"Copy of {wish.title}",
            description=wish.description,
            priority=wish.priority,
            category=wish.category,
            status="TODO",
            assignee=wish.assignee,
            due_at=wish.due_at,
        )
        messages.success(request, f'Created copy of "{wish.title}"')
        return redirect("admin:staff_wish_change", new_wish.id)