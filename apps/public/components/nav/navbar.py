from django_components import component


@component.register("nav-navbar")
class Navbar(component.Component):
    template_name = "nav/navbar.html"

    def get_context_data(self, active_thing_id=None):
        return {}

    # Media class removed - will add back when implementing Tailwind
