# apps/insights/forms.py
from django import forms
from django.core.exceptions import ValidationError


class RunComparisonForm(forms.Form):
    start_date = forms.DateField(
        widget=forms.widgets.DateInput(attrs={"type": "date"}),
        label="Start Date",
        help_text="Select the start date of the week to compare.",
        required=True,  # Ensures the field is required
    )

    def clean_start_date(self):
        """
        Ensure the start_date is provided and valid.
        """
        start_date = self.cleaned_data.get("start_date")
        if not start_date:
            raise ValidationError("Start date is required.")
        return start_date
