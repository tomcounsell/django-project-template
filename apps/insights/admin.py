# apps/insights/admin.py
from django.contrib import admin
from django.urls import path
from django.shortcuts import render, redirect
from .forms import RunComparisonForm
from .models.comparison import Comparison, KeyMetricComparison
from .models.summary import Summary, KeyMetric


class KeyMetricInline(admin.TabularInline):
    """
    Inline admin to display all KeyMetric entries for a Summary.
    """

    model = KeyMetric
    extra = 0  # Do not display extra blank rows
    readonly_fields = ("name", "formatted_value")
    can_delete = False

    def formatted_value(self, obj):
        """Display the value rounded to the nearest whole number."""
        return f"{round(obj.value):,}" if obj.value is not None else "N/A"

    formatted_value.short_description = "Value (Rounded)"


class KeyMetricComparisonInline(admin.TabularInline):
    """
    Inline admin to display all KeyMetricComparison entries for a Comparison.
    """

    model = KeyMetricComparison
    extra = 0  # Do not display extra blank rows
    readonly_fields = (
        "name",
        "rounded_value1",
        "rounded_value2",
        "description",
        "formatted_percentage_difference",
    )
    can_delete = False

    def rounded_value1(self, obj):
        """Round value1 to the nearest whole number."""
        return f"{round(obj.value1):,}" if obj.value1 is not None else "N/A"

    def rounded_value2(self, obj):
        """Round value2 to the nearest whole number."""
        return f"{round(obj.value2):,}" if obj.value2 is not None else "N/A"

    def formatted_percentage_difference(self, obj):
        """Display percentage difference to 1 decimal place."""
        return (
            f"{obj.percentage_difference:.1f}%"
            if obj.percentage_difference is not None
            else "N/A"
        )

    rounded_value1.short_description = "Week 1 Value (Rounded)"
    rounded_value2.short_description = "Week 2 Value (Rounded)"
    formatted_percentage_difference.short_description = "Percentage Difference"


class ComparisonAdmin(admin.ModelAdmin):
    list_display = (
        "start_date",
        "end_date",
        "comparison_summary",
        "display_summary1",
        "display_summary2",
    )
    search_fields = ("start_date", "end_date")
    inlines = [KeyMetricComparisonInline]  # Add the inline view for KeyMetricComparison

    def display_summary1(self, obj):
        """Display Summary1 details."""
        return f"Summary from {obj.summary1.start_date} to {obj.summary1.end_date}"

    def display_summary2(self, obj):
        """Display Summary2 details."""
        return f"Summary from {obj.summary2.start_date} to {obj.summary2.end_date}"

    display_summary1.short_description = "Summary 1"
    display_summary2.short_description = "Summary 2"


class SummaryAdmin(admin.ModelAdmin):
    """
    Admin view for the Summary model.
    """

    list_display = ("start_date", "end_date", "dataset_summary")
    search_fields = ("start_date", "end_date")
    readonly_fields = (
        "start_date",
        "end_date",
        "dataset_summary",
    )  # Make fields read-only
    inlines = [KeyMetricInline]  # Add inline view for KeyMetric


admin.site.register(Summary, SummaryAdmin)  # Register the Summary model
admin.site.register(Comparison, ComparisonAdmin)  # Register the Comparison model
