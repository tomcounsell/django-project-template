from django_components import component


@component.register("messages")
class Messages(component.Component):
    template_name = "messages/messages.html"

    def get_context_data(self):
        return {}

    class Media:
        pass
        # css = "messages/messages.css"
        # js = "messages/messages.js"
