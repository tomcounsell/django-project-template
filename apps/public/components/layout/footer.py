from django_components import component


@component.register("layout-footer")
class Footer(component.Component):
    template_name = "layout/footer.html"

    def get_context_data(self):
        return {}

    # Media class removed - will add back when implementing Tailwind
