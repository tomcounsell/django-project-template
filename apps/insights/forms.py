# apps/insights/forms.py
from django import forms


class RunComparisonForm(forms.Form):
    start_date = forms.DateField(
        widget=forms.widgets.DateInput(attrs={"type": "date"}),
        label="Start Date",
        help_text="Select the start date for the comparison.",
    )
