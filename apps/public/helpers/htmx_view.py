from typing import Dict, Optional

from django.contrib import messages
from django.http import HttpRequest, HttpResponse
from django.template.loader import render_to_string
from django_htmx import http as htmx

from apps.public.helpers.main_content_view import MainContentView


class HTMXView(MainContentView):
    """
    Specialized view for handling HTMX requests with enhanced features.

    This view extends MainContentView with additional functionality for working
    with HTMX, including out-of-band (OOB) updates, URL history management,
    and more efficient partial rendering.

    Attributes:
        template_name (str): Primary template to render
        oob_templates (Dict[str, str]): Mapping of element IDs to templates for OOB updates
        push_url (str): URL to push into browser history
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
        context: Optional[Dict] = None,
        oob_templates: Optional[Dict[str, str]] = None,
        push_url: Optional[str] = None,
    ) -> HttpResponse:
        """
        Render a main template with optional OOB templates in a combined response.

        Args:
            request: Django HttpRequest object
            template_name: The main template to render (defaults to class attribute)
            context: Context data for the template(s)
            oob_templates: A dictionary of OOB templates with target IDs as keys
            push_url: URL to push to the browser history

        Returns:
            HttpResponse with combined template output and HTMX-specific modifications
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

        # Always include message toasts in the OOB templates if there are messages
        if messages.get_messages(request) and "messages" not in oob_templates:
            oob_templates["messages"] = "layout/messages/toast.html"

        # Mark context as OOB if we have OOB templates
        if oob_templates:
            combined_context["is_oob"] = True

        # Render each OOB template and build the OOB HTML
        oob_html = ""
        for oob_target_id, oob_template in oob_templates.items():
            oob_content = render_to_string(
                oob_template, combined_context, request=request
            )
            # For true OOB responses, add hx-swap-oob attribute
            if oob_content.strip():
                # Check if the content already has an OOB attribute
                if 'hx-swap-oob="true"' not in oob_content:
                    # Insert the OOB attribute at the first tag
                    first_tag_end = oob_content.find(">")
                    if first_tag_end > 0:
                        oob_content = (
                            oob_content[:first_tag_end]
                            + f' id="{oob_target_id}" hx-swap-oob="true"'
                            + oob_content[first_tag_end:]
                        )
                oob_html += oob_content

        # Combine main content and OOB content
        combined_html = main_html + oob_html

        # Create the response with the combined HTML output
        response = HttpResponse(combined_html)

        # Handle URL push for history
        if push_url:
            response = htmx.push_url(response, url=push_url)

        return response


# Example usage comment for documentation
"""
Example Usage:

class MyComponentView(TeamSessionMixin, HTMXView):
    template_name = "components/my_component.html"
    oob_templates = {
        "nav_menu": "components/nav_menu.html",
        "messages": "layout/messages/toast.html",
    }
    push_url = "/my/component/url"

    def get(self, request, *args, **kwargs):
        # Any additional logic for GET requests
        return self.render(request)

    def post(self, request, *args, **kwargs):
        # Process form submission or other POST action
        form = MyForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Changes saved successfully!")
            return self.render(request)
        
        # Add form back to context and render with errors
        return self.render(request, context={"form": form})
"""
