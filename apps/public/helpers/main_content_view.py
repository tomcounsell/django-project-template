import logging
from typing import Dict, Optional

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render as django_render
from django.views import View
from django_htmx import http as htmx

from apps.common.utilities.logger import ErrorHandlingMixin


class MainContentView(ErrorHandlingMixin, View):
    """
    Base view class for general views in the project.
    
    This class provides a common foundation for all views, handling standard
    context initialization, base template selection, and rendering functionality.
    
    Attributes:
        url (str): URL associated with this view for linking/redirects
        template_name (str): Path to the template to render
    """
    url: str = ""
    template_name: Optional[str] = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Initialize base context with default values
        self.context = {
            "is_oob": False,  # Flag for out-of-band HTMX responses
        }

    def dispatch(self, request, *args, **kwargs):
        # Update context with defaults before dispatching
        if not self.context.get("url", None):
            self.context["url"] = self.url
            
        # Determine base template based on request type (HTMX or regular)
        if not self.context.get("base_template", None):
            if getattr(request, 'htmx', False):
                # For HTMX requests, use partial template by default, unless explicitly requested
                if request.GET.get("hx-get", "") == "page":
                    self.context["base_template"] = "base.html"
                else:
                    self.context["base_template"] = "partial.html"
            else:
                # For regular requests, always use full base template
                self.context["base_template"] = "base.html"
                
        # Add login status to context
        self.context["just_logged_in"] = request.session.get("just_logged_in", False)
        
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        logging.warning("GET method not implemented.")
        if self.template_name:
            logging.warning("Will attempt to render template as-is.")
            return self.render(request)
        raise NotImplementedError("GET method must be implemented in subclass.")

    def post(self, request, *args, **kwargs):
        raise NotImplementedError("POST method must be implemented in subclass.")

    def render(
        self,
        request: HttpRequest = None,
        template_name: Optional[str] = None,
        context: Optional[Dict] = None,
        push_url: Optional[str] = None,
    ) -> HttpResponse:
        """
        Render the template with the provided or default context.
        
        Args:
            request: Django HttpRequest object
            template_name: The template to render (defaults to class attribute)
            context: Context data to pass to the template
            push_url: URL to push to browser history (for HTMX)
            
        Returns:
            HttpResponse with rendered template
        """
        request = request or self.request
        template_name = template_name or self.template_name
        combined_context = {**self.context, **(context or {})}

        response = django_render(request, template_name, combined_context)
        
        # Handle URL pushing for HTMX requests
        if push_url and getattr(request, 'htmx', False):
            response = htmx.push_url(response, url=push_url)
            
        return response