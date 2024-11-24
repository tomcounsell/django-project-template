# apps/insights/admin.py
from django.contrib import admin
from django.urls import path
from django.shortcuts import render, redirect
from .forms import RunComparisonForm
from .models.comparison import Comparison


class ComparisonAdmin(admin.ModelAdmin):
    list_display = ("start_date", "end_date", "comparison_summary")
    search_fields = ("start_date", "end_date")

    # Add custom URLs for the start-comparison page
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

    # Custom view for running a comparison
    def start_comparison_view(self, request):
        if request.method == "POST":
            form = RunComparisonForm(request.POST)
            if form.is_valid():
                start_date = form.cleaned_data["start_date"]
                # Trigger your comparison pipeline or tasks here
                self.message_user(
                    request, f"Comparison pipeline started for {start_date}"
                )
                # Redirect to Django Q2's successful tasks page
                return redirect("/admin/django_q/success/")
        else:
            form = RunComparisonForm()
        return render(
            request,
            "admin/insights/start_comparison.html",  # Match the template's location
            {"form": form, "title": "Run Week-over-Week Comparison"},
        )

    # Add a link to the changelist view for "Run Comparison"
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context["start_comparison_url"] = "start-comparison/"
        return super().changelist_view(request, extra_context=extra_context)


admin.site.register(Comparison, ComparisonAdmin)
