"""
Account menu component definition.
"""
from django_components import component


@component.register("nav-account_menu")
class AccountMenu(component.Component):
    """
    Account dropdown menu component.
    Displays user-specific options such as settings and logout.
    Shows login link for unauthenticated users.
    """
    template_name = "nav/account_menu.html"

    def get_context_data(self):
        """Return context for the account menu."""
        return {}
