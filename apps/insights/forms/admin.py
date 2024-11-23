# app/insights/forms/admin.py
from django import forms


class DataSummaryAdminForm(forms.ModelForm):
    start_date = forms.DateField(
        widget=forms.widgets.DateInput(attrs={"type": "date"}),
        required=False,
        help_text="Select a start date for the analysis.",
    )
