import datetime

from django.contrib import admin, messages
from django.db.models import Q
from django.shortcuts import redirect
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


# User assigned filter removed as assignee field was removed


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
    template_name = "admin/dashboard/wish_stats.html"
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
        "tags_display",
        "status_badge",
        "effort_display",
        "value_display",
        "cost_display",
        "due_date_display",
    ]
    list_filter = [
        # Custom filters
        DueInFilter,
        CompletedWithinFilter,
        HasDescriptionFilter,
        IsOverdueFilter,
        # Default filters
        ("priority", ChoicesDropdownFilter),
        ("status", ChoicesDropdownFilter),
        ("effort", ChoicesDropdownFilter),
        ("value", ChoicesDropdownFilter),
        ("due_at", RangeDateFilter),
        ("created_at", RangeDateTimeFilter),
    ]
    list_filter_submit = True
    list_sections = [WishTemplateSection]
    search_fields = ("title", "description", "tags")
    date_hierarchy = "created_at"
    readonly_fields = ("created_at", "modified_at", "completed_at")
    warn_unsaved_form = True
    compressed_fields = True

    fieldsets = (
        (
            "Wish Information",
            {"fields": ("title", "description", "priority", "status", "tags")},
        ),
        (
            "Estimation",
            {
                "fields": ("effort", "value", "cost_estimate", "due_at"),
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

    def tags_display(self, obj):
        if not obj.tags or not isinstance(obj.tags, list) or len(obj.tags) == 0:
            return "-"
            
        tags_html = []
        for tag in obj.tags[:3]:  # Show first 3 tags
            tags_html.append(
                format_html(
                    '<span class="unfold-badge bg-blue-500 text-white mr-1">{}</span>',
                    tag
                )
            )
            
        if len(obj.tags) > 3:
            tags_html.append(format_html('<span class="text-gray-500">+{} more</span>', len(obj.tags) - 3))
            
        return format_html(''.join([str(tag) for tag in tags_html]))

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
        
    def effort_display(self, obj):
        if not obj.effort:
            return "-"
            
        return format_html(
            '<span class="unfold-badge bg-slate-500 text-white">{}</span>',
            obj.get_effort_display()
        )
        
    def value_display(self, obj):
        if not obj.value:
            return "-"
            
        return obj.value
        
    def cost_display(self, obj):
        if obj.cost_estimate is None:
            return "-"
            
        return format_html(
            '<span class="unfold-badge bg-green-500 text-white">{}</span>',
            obj.formatted_cost
        )

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
    tags_display.short_description = "Tags"
    status_badge.short_description = "Status"
    effort_display.short_description = "Effort"
    value_display.short_description = "Value"
    cost_display.short_description = "Cost"
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
        messages.success(
            request, f"Successfully marked {updated} wishes as in progress"
        )
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
            tags=wish.tags.copy() if isinstance(wish.tags, list) else [],
            status="TODO",
            effort=wish.effort,
            value=wish.value,
            cost_estimate=wish.cost_estimate,
            due_at=wish.due_at,
        )
        messages.success(request, f'Created copy of "{wish.title}"')
        return redirect("admin:staff_wish_change", new_wish.id)
