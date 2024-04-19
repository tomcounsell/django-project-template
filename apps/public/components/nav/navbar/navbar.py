from django_components import component


@component.register("navbar")
class Navbar(component.Component):
    template_name = "nav/navbar/navbar.html"

    def get_context_data(self, active_thing_id=None):
        return {}

    class Media:
        # css = "nav/navbar/navbar.css"
        js = "nav/navbar/navbar.js"
