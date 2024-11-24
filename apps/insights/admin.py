# apps/insights/admin.py
from django.contrib import admin
from .models.summary import Summary, KeyMetric


# Define an Inline Admin for KeyMetric
class KeyMetricInline(admin.TabularInline):
    model = KeyMetric
    extra = 0  # Number of empty rows to display for adding new KeyMetrics
    readonly_fields = (
        "name",
        "value",
    )  # Make fields readonly if they're auto-generated
    can_delete = False  # Disable deletion if KeyMetrics shouldn't be deleted manually


# Extend the Summary Admin to include the inline KeyMetrics
class SummaryAdmin(admin.ModelAdmin):
    list_display = (
        "start_date",
        "end_date",
        "dataset_summary",
    )  # Fields to display in the list view
    search_fields = ("start_date", "end_date")  # Fields to search on
    list_filter = ("start_date", "end_date")  # Add filters for date ranges
    inlines = [KeyMetricInline]

    # Control fields displayed on the detail/edit form
    fields = ("start_date", "end_date", "dataset_summary")

    # Alternatively, exclude fields you don't want
    # exclude = ("data_source",)


# Register the Summary model with the custom admin
admin.site.register(Summary, SummaryAdmin)
