import pytest
from django.urls import reverse
from django.test import Client

from apps.common.tests.factories import UserFactory


class TestWishFormStyling:
    """Test the styling of the wish form."""

    @pytest.fixture
    def client(self):
        """Set up a client with a logged-in staff user."""
        client = Client()
        user = UserFactory(is_staff=True)
        client.force_login(user)
        return client

    def test_wish_form_input_styling(self, client):
        """Test that wish form inputs have consistent styling."""
        response = client.get(reverse("staff:wish-create"))
        assert response.status_code == 200

        # Check for input styling classes
        # Focus states: focus:outline-hidden focus:ring-2 focus:ring-blue-500 focus:border-blue-500
        # General styling: rounded-xs border-gray-300 bg-white text-sm
        content = response.content.decode()

        # Common style classes that should be in all inputs
        style_classes = [
            "rounded-xs",
            "border-gray-300",
            "bg-white",
            "focus:outline-hidden",
            "focus:ring-2",
            "focus:ring-blue-500",
            "focus:border-blue-500",
            "text-sm",
        ]

        # Check text inputs
        for field_name in ["title", "tags"]:
            for style_class in style_classes:
                assert 'class="w-full px-3 py-2 border' in content
                assert (
                    style_class in content
                ), f"Style class '{style_class}' missing in {field_name} input"

        # Check selects (status, priority, effort, value)
        for field_name in ["status", "priority", "effort", "value"]:
            for style_class in style_classes:
                assert (
                    style_class in content
                ), f"Style class '{style_class}' missing in {field_name} select"

        # Check textarea (description)
        for style_class in style_classes:
            assert (
                style_class in content
            ), f"Style class '{style_class}' missing in description textarea"

        # Check number input (cost_estimate)
        for style_class in style_classes:
            assert (
                style_class in content
            ), f"Style class '{style_class}' missing in cost_estimate input"

    def test_wish_create_modal_styling(self, client):
        """Test the styling of the wish create modal."""
        response = client.get(
            reverse("staff:wish-create-modal"), HTTP_HX_REQUEST="true"
        )
        assert response.status_code == 200

        content = response.content.decode()

        # Common style classes for inputs in the modal
        style_classes = [
            "rounded-xs",
            "focus:outline-hidden",
            "focus:ring",
            "focus:ring-slate-200",
            "focus:ring-opacity-50",
            "focus:border-slate-500",
            "border-slate-300",
            "shadow-xs",
            "text-sm",
        ]

        # Check that all input fields exist and have proper styling
        field_types = {
            "title": "input",
            "description": "textarea",
            "status": "select",
            "priority": "select",
            "effort": "select",
            "value": "select",
            "cost_estimate": "input",
            "tags": "input",
            "due_at": "input",
        }

        for field, input_type in field_types.items():
            assert (
                f'id="id_{field}"' in content
            ), f"Field {field} not found in modal form"

            # Verification depends on modal form implementation
            if (
                input_type == "input"
                or input_type == "textarea"
                or input_type == "select"
            ):
                for style_class in style_classes:
                    assert (
                        style_class in content
                    ), f"Style class '{style_class}' missing in {field} {input_type}"
