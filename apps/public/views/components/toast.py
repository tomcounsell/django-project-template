"""
Toast notifications component definition.
"""
from django_components import component


@component.register("messages-toast")
class Toast(component.Component):
    """
    Toast notification component for displaying messages to the user.
    Renders different styled notifications based on message type
    (success, info, warning, error).
    """
    template_name = "messages/toast.html"

    def get_context_data(self):
        """Return context for the toast notifications."""
        return {}

    # Media class will be added back when implementing Tailwind
