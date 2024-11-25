# apps/insights/admin.py
from django.contrib import admin
from django.urls import path
from django.shortcuts import render
from django.http import HttpResponse
from django.utils.html import format_html
from .forms import RunComparisonForm
from .models.comparison import Comparison, KeyMetricComparison
from .models.summary import Summary, KeyMetric
from .tasks import schedule_summary_tasks

from django.http import HttpResponseRedirect
from django.contrib import messages  # For flashing messages


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
    fields = readonly_fields  # Make all fields explicitly read-only
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

    rounded_value1.short_description = "Current Value"
    rounded_value2.short_description = "Previous Value"
    formatted_percentage_difference.short_description = "Percentage Change"


class ComparisonAdmin(admin.ModelAdmin):

    list_display = (
        "comparison_start_date",
        "comparison_summary",
        "display_summary1",
        "display_summary2",
    )
    search_fields = ("summary1__start_date", "summary2__start_date")
    inlines = [KeyMetricComparisonInline]  # Add the inline view for KeyMetricComparison

    def get_urls(self):
        """
        Extend the admin URLs to include a custom URL for the 'run-comparison' page.
        """
        urls = super().get_urls()
        custom_urls = [
            path(
                "run-comparison/",
                self.admin_site.admin_view(self.run_comparison),
                name="run-comparison",
            ),
        ]
        return custom_urls + urls

    def run_comparison(self, request):
        """
        Handle the custom page for running comparisons with a datepicker.
        """
        if request.method == "POST":
            form = RunComparisonForm(request.POST)
            if form.is_valid():
                start_date = form.cleaned_data["start_date"]
                # Call your function here
                schedule_summary_tasks(start_date)

                # Flash a success message
                messages.success(request, "Comparison task ran successfully!")

                # Redirect to the Django Q success page
                return HttpResponseRedirect("/admin/django_q/success/")
        else:
            form = RunComparisonForm()
        return render(request, "admin/insights/run_comparison.html", {"form": form})

    change_list_template = "admin/insights/comparison_list.html"

    def changelist_view(self, request, extra_context=None):
        """
        Inject a custom link into the changelist page for comparisons.
        """
        if extra_context is None:
            extra_context = {}
        extra_context["custom_link"] = format_html(
            '<a class="button" href="/admin/insights/comparison/run-comparison/">Run Comparison</a>'
        )
        return super().changelist_view(request, extra_context=extra_context)

    def comparison_start_date(self, obj):
        """Use the earliest start_date from summary1 for consistency."""
        return obj.summary1.start_date

    comparison_start_date.short_description = "Start Date"

    def display_summary1(self, obj):
        """Display Summary1 details."""
        return f"Summary from {obj.summary1.start_date}"

    def display_summary2(self, obj):
        """Display Summary2 details."""
        return f"Summary from {obj.summary2.start_date}"

    display_summary1.short_description = "Current Week"
    display_summary2.short_description = "Previous Week"


class SummaryAdmin(admin.ModelAdmin):
    """
    Admin view for the Summary model.
    """

    list_display = ("start_date", "dataset_summary")
    search_fields = ("start_date",)
    readonly_fields = (
        "start_date",
        "dataset_summary",
    )  # Make fields read-only
    inlines = [KeyMetricInline]  # Add inline view for KeyMetric


admin.site.register(Summary, SummaryAdmin)  # Register the Summary model
admin.site.register(Comparison, ComparisonAdmin)  # Register the Comparison model
