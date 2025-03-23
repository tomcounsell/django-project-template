"""
Navigation bar component definition.
"""
from django_components import component


@component.register("nav-navbar")
class Navbar(component.Component):
    """
    Main navigation bar component shown at the top of all pages.
    Displays the site logo, navigation menu, and account options.
    """
    template_name = "nav/navbar.html"

    def get_context_data(self, active_thing_id=None):
        """Return context for the navbar."""
        return {}

    # Media class will be added back when implementing Tailwind
