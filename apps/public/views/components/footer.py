"""
Footer component definition.
"""
from django_components import component


@component.register("layout-footer")
class Footer(component.Component):
    """
    Site footer component shown at the bottom of all pages.
    Contains copyright information and site attribution.
    """
    template_name = "layout/footer.html"

    def get_context_data(self):
        """Return context for the footer."""
        return {}

    # Media class will be added back when implementing Tailwind
