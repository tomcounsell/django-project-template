# apps/insights/admin.py
from django.contrib import admin
from django.urls import path
from django.shortcuts import render
from .forms import RunComparisonForm
from .models.comparison import Comparison


class ComparisonAdmin(admin.ModelAdmin):
    list_display = ("start_date", "end_date", "comparison_summary")
    search_fields = ("start_date", "end_date")

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "start-comparison/",
                self.admin_site.admin_view(self.start_comparison_view),
                name="start_comparison",
            ),
        ]
        return custom_urls + urls

    def start_comparison_view(self, request):
        if request.method == "POST":
            form = RunComparisonForm(request.POST)
            if form.is_valid():
                start_date = form.cleaned_data["start_date"]
                # Trigger your comparison pipeline or tasks here
                self.message_user(
                    request, f"Comparison pipeline started for {start_date}"
                )
        else:
            form = RunComparisonForm()
        return render(
            request,
            "admin/start_comparison.html",
            {"form": form, "title": "Run Comparison"},
        )


admin.site.register(Comparison, ComparisonAdmin)
