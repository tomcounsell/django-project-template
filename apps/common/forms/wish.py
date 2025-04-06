from django import forms
from django.utils import timezone

from apps.staff.models import Wish


class WishForm(forms.ModelForm):
    """Form for creating and updating Wish."""

    tags = forms.CharField(
        required=False,
        help_text="Enter tags separated by commas",
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "e.g. frontend, api, bug"}),
    )

    due_at = forms.DateTimeField(
        required=False,
        widget=forms.DateTimeInput(
            attrs={"type": "datetime-local", "class": "form-control"}
        ),
    )

    cost_estimate = forms.IntegerField(
        required=False,
        min_value=0,
        help_text="Estimated cost in dollars (whole numbers only)",
        widget=forms.NumberInput(attrs={"class": "form-control", "placeholder": "e.g. 500"}),
    )
    
    class Meta:
        model = Wish
        fields = [
            "title",
            "description",
            "priority",
            "status",
            "effort",
            "value",
            "cost_estimate",
            "tags",
            "due_at",
        ]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "priority": forms.Select(attrs={"class": "form-select"}),
            "status": forms.Select(attrs={"class": "form-select"}),
            "effort": forms.Select(attrs={"class": "form-select"}),
            "value": forms.Select(attrs={"class": "form-select"}),
        }

    def clean_status(self):
        """Update completed_at when status is changed to DONE."""
        status = self.cleaned_data.get("status")
        if (
            status == Wish.STATUS_DONE
            and self.instance.pk
            and self.instance.status != Wish.STATUS_DONE
        ):
            # Mark as completed now
            self.instance.completed_at = timezone.now()
        elif (
            status != Wish.STATUS_DONE
            and self.instance.pk
            and self.instance.status == Wish.STATUS_DONE
        ):
            # Clear completed timestamp if reopening
            self.instance.completed_at = None
        return status
        
    def clean_tags(self):
        """Convert comma-separated tags string to list."""
        tags_input = self.cleaned_data.get("tags", "")
        if not tags_input:
            return []
            
        # Split by comma, strip whitespace, convert to lowercase, and filter out empty strings
        tags = [tag.strip().lower() for tag in tags_input.split(",") if tag.strip()]
        
        # Remove duplicates by converting to set and back to list
        return list(dict.fromkeys(tags))

    def __init__(self, *args, **kwargs):
        """Initialize the form and convert tags list to string."""
        instance = kwargs.get("instance")
        if instance and hasattr(instance, "tags") and isinstance(instance.tags, list):
            # Create initial data if not provided
            if "initial" not in kwargs:
                kwargs["initial"] = {}
            # Convert tags list to comma-separated string
            kwargs["initial"]["tags"] = ", ".join(instance.tags)
            
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        """Save the form and process tags."""
        instance = super().save(commit=False)
        
        # Process tags from form data
        if "tags" in self.cleaned_data:
            instance.tags = self.cleaned_data["tags"]

        if commit:
            instance.save()
        return instance
