# apps/insights/admin.py
from django.contrib import admin
from .models import DataSummary
from .forms.admin import DataSummaryAdminForm


@admin.register(DataSummary)
class DataSummaryAdmin(admin.ModelAdmin):
    form = DataSummaryAdminForm
    list_display = ("label",)
    search_fields = ("label",)
