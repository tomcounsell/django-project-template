from django_components import component


@component.register("nav-account_menu")
class AccountMenu(component.Component):
    template_name = "nav/account_menu.html"

    def get_context_data(self):
        return {}
