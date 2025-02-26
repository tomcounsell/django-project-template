from django_components import component


@component.register("messages-toast")
class Toast(component.Component):
    template_name = "messages/toast.html"

    def get_context_data(self):
        return {}

    # Media class removed - will add back when implementing Tailwind
