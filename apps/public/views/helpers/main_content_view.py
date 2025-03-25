import inspect
import logging
import os
import re
from typing import Dict, Optional

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render as django_render
from django.views import View


class MainContentView(View):
    """
    Base view class for general views in the project.
    """

    url: str = ""
    template_name: Optional[str] = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Initialize base context with URL
        self.context = {
            "is_oob": False,  # templates need to check this
        }

    def dispatch(self, request, *args, **kwargs):
        # Update context with default URL and base template choice
        if not self.context.get("url", None):
            self.context["url"] = self.url
        if not self.context.get("base_template", None):
            self.context["base_template"] = "_base.html"

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
        context: Optional[dict] = None,
    ) -> HttpResponse:
        """
        Render the template with the provided or default context.
        """
        request = request or self.request
        template_name = template_name or self.template_name
        combined_context = {**self.context, **(context or {})}

        return django_render(request, template_name, combined_context)
