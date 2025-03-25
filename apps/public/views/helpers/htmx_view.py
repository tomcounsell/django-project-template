from typing import Any, Dict, Optional

from django.contrib import messages
from django.http import HttpRequest, HttpResponse
from django.template.loader import render_to_string
from django_htmx import http as htmx

from apps.public.views.helpers.main_content_view import MainContentView


class HTMXView(MainContentView):
    """
    Base view class for handling HTMX requests with additional features for
    out-of-band (OOB) responses, URL updates, custom events, and multiple component rendering.
    """

    template_name: Optional[str] = None
    oob_templates: Optional[Dict[str, str]] = None
    push_url: Optional[str] = None

    def dispatch(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        # Ensure this view only handles HTMX requests
        if not getattr(request, "htmx", False):
            raise NotImplementedError("This view is only accessible via HTMX requests.")

        return super().dispatch(request, *args, **kwargs)

    def render(
        self,
        request: HttpRequest = None,
        template_name: Optional[str] = None,
        context: Optional[dict] = None,
        oob_templates: Optional[Dict[str, str]] = None,
        push_url: Optional[str] = None,
    ) -> HttpResponse:
        """
        Render a main template with optional OOB templates in a combined response.

        :param request: Django HttpRequest object
        :param template_name: The main template to render (defaults to class attribute)
        :param context: Context data for the template(s)
        :param oob_templates: A dictionary of OOB templates with target IDs as keys (defaults to class attribute)
        :param push_url: URL to push to the history state (defaults to class attribute)
        :return: HttpResponse with combined template output and HTMX-specific modifications
        """
        request = request or self.request
        combined_context = {**self.context, **(context or {})}

        # Use class attributes as defaults if not explicitly provided
        template_name = template_name or self.template_name
        oob_templates = oob_templates or self.oob_templates or {}
        push_url = push_url or self.push_url

        # Render the main template if provided
        main_html = (
            render_to_string(template_name, combined_context, request=request)
            if template_name
            else ""
        )

        # by default, include message toasts in the OOB templates
        if messages.get_messages(request) and "messages" not in oob_templates:
            oob_templates["messages"] = "common/toasts.html"

        if len(oob_templates):
            combined_context["is_oob"] = True

        # Render each OOB template and wrap it in the OOB structure
        oob_html = ""
        for oob_target_id, oob_template in oob_templates.items():
            oob_html += render_to_string(
                oob_template, combined_context, request=request
            )

        # Combine main content and OOB content
        combined_html = main_html + oob_html

        # Create the response with the combined HTML output
        response = HttpResponse(combined_html)

        # Handle URL push for history
        if push_url:
            response = htmx.push_url(response, url=push_url)

        return response


# EXAMPLE USAGE:
"""
class SomeComponentView(TeamSessionMixin, HTMXView):
    template_name = "things/component.html"
    oob_templates = {
        "slide_nav": "deck/slide_nav.html",
        "messages": "common/toasts.html",
    }
    push_url = "/things/this-one"

    def get(self, request, *args, **kwargs):
        # Any additional logic for GET requests
        return self.render(request)

    def post(self, request, *args, **kwargs):
        # Any additional logic for POST requests
        return self.render(request)
"""
