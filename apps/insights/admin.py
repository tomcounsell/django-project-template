# apps/insights/admin.py
from django.contrib import admin

# from .models.summary import Summary, KeyMetric
# from .models.comparison import Comparison, KeyMetricComparison


# @admin.register(Summary)
# class SummaryAdmin(admin.ModelAdmin):
#     """
#     Admin configuration for the Summary model.
#     """

#     list_display = (
#         "summary_type",
#         "start_date",
#         "end_date",
#         "created_at",
#         "updated_at",
#     )
#     search_fields = ("summary_type", "dataset_summary", "data_source")
#     list_filter = ("summary_type", "start_date", "end_date")


# @admin.register(KeyMetric)
# class KeyMetricAdmin(admin.ModelAdmin):
#     """
#     Admin configuration for the KeyMetric model.
#     """

#     list_display = ("summary", "name", "value", "created_at", "updated_at")
#     search_fields = ("name",)
#     list_filter = ("summary",)


# @admin.register(Comparison)
# class ComparisonAdmin(admin.ModelAdmin):
#     """
#     Admin configuration for the Comparison model.
#     """

#     list_display = ("summary1", "summary2", "created_at", "updated_at")
#     search_fields = ("comparison_summary",)
#     list_filter = ("summary1", "summary2")


# @admin.register(KeyMetricComparison)
# class KeyMetricComparisonAdmin(admin.ModelAdmin):
#     """
#     Admin configuration for the KeyMetricComparison model.
#     """

#     list_display = (
#         "comparison",
#         "name",
#         "value1",
#         "value2",
#         "percentage_difference",
#         "created_at",
#         "updated_at",
#     )
#     search_fields = ("name", "description")
#     list_filter = ("comparison",)
