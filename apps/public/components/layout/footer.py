from django_components import component


@component.register("footer")
class Footer(component.Component):
    template_name = "footer/footer.html"

    def get_context_data(self):
        return {}

    class Media:
        pass
        # css = "footer/footer.css"
        # js = "footer/footer.js"
