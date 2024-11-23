from django.contrib import admin
from .models import DataSummary, SummaryComparison


@admin.register(DataSummary)
class DataSummaryAdmin(admin.ModelAdmin):
    list_display = ("label", "created_at", "updated_at")
    search_fields = ("label",)


@admin.register(SummaryComparison)
class SummaryComparisonAdmin(admin.ModelAdmin):
    list_display = ("summary_1", "summary_2", "comparison_type", "created_at")
    list_filter = ("comparison_type",)
    search_fields = ("summary_1__label", "summary_2__label")
