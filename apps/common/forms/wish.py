from django import forms
from django.utils import timezone

from apps.common.models import User
from apps.staff.models import Wish


class WishForm(forms.ModelForm):
    """Form for creating and updating Wish."""

    assignee = forms.ModelChoiceField(
        queryset=User.objects.filter(is_active=True),
        required=False,
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    due_at = forms.DateTimeField(
        required=False,
        widget=forms.DateTimeInput(
            attrs={"type": "datetime-local", "class": "form-control"}
        ),
    )

    class Meta:
        model = Wish
        fields = [
            "title",
            "description",
            "priority",
            "category",
            "status",
            "assignee",
            "due_at",
        ]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "priority": forms.Select(attrs={"class": "form-select"}),
            "category": forms.Select(attrs={"class": "form-select"}),
            "status": forms.Select(attrs={"class": "form-select"}),
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

    def save(self, commit=True, user=None):
        """Save the form and set the assignee to the current user if not specified."""
        instance = super().save(commit=False)

        # If no assignee is specified and this is a new item, assign to current user
        if not instance.pk and not instance.assignee and user:
            instance.assignee = user

        if commit:
            instance.save()
        return instance