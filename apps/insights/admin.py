# apps/insights/admin.py
from django.contrib import admin
from .models import DataSummary


@admin.register(DataSummary)
class DataSummaryAdmin(admin.ModelAdmin):
    list_display = ("label",)
    search_fields = ("label",)