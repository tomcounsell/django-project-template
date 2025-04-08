import json

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.template.loader import render_to_string
from django.urls import reverse
from django.views.decorators.http import require_POST

from apps.common.forms.wish import WishForm
from apps.public.views.helpers.main_content_view import MainContentView
from apps.public.views.helpers.htmx_view import HTMXView
from apps.staff.models import Wish


class StaffRequiredMixin(LoginRequiredMixin):
    """Mixin to require staff privileges for access to views."""

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)


class WishListView(StaffRequiredMixin, MainContentView):
    """View for listing all wish items (staff only)."""

    template_name = "staff/wishes/wish_list.html"
    partial_template_name = "staff/wishes/partials/wish_list_content.html"
    tabs_template_name = "staff/wishes/partials/wish_tabs.html"
    
    # Wish status constants
    STATUS_ALL = "ALL"
    STATUS_DRAFT = "DRAFT"
    STATUS_TODO = "TODO"
    STATUS_IN_PROGRESS = "IN_PROGRESS"
    STATUS_BLOCKED = "BLOCKED"
    STATUS_DONE = "DONE"

    def get(self, request, *args, **kwargs):
        """Get all wishes with filtering options."""
        queryset = Wish.objects.all()

        # Get multi-select filter values
        status_list = request.GET.getlist("status")
        priority_list = request.GET.getlist("priority")
        effort_list = request.GET.getlist("effort")
        value_list = request.GET.getlist("value")
        
        # Determine active tab
        active_tab = None
        if not status_list:
            active_tab = "all"
        elif len(status_list) == 1:
            active_tab = status_list[0].lower()
        
        # Filter by status if provided
        if status_list:
            queryset = queryset.filter(status__in=status_list)

        # Filter by priority if provided
        if priority_list:
            queryset = queryset.filter(priority__in=priority_list)
            
        # Filter by tag if provided
        tag = request.GET.get("tag")
        if tag:
            # JSONField lookup to find wishes where the tag exists in the tags list
            queryset = queryset.filter(tags__contains=[tag.lower()])
            
        # Filter by effort if provided
        if effort_list:
            queryset = queryset.filter(effort__in=effort_list)
            
        # Filter by value if provided
        if value_list:
            queryset = queryset.filter(value__in=value_list)
            
        # Filter by cost range if provided
        cost_min = request.GET.get("cost_min")
        cost_max = request.GET.get("cost_max")
        
        if cost_min:
            try:
                cost_min = int(cost_min)
                queryset = queryset.filter(cost_estimate__gte=cost_min)
            except (ValueError, TypeError):
                pass
                
        if cost_max:
            try:
                cost_max = int(cost_max)
                queryset = queryset.filter(cost_estimate__lte=cost_max)
            except (ValueError, TypeError):
                pass

        # Check if any filters are active
        has_active_filters = (
            status_list 
            or priority_list 
            or tag 
            or effort_list 
            or value_list 
            or cost_min 
            or cost_max
        )
        
        # Set the context
        self.context["wishes"] = queryset
        self.context["status_choices"] = Wish.STATUS_CHOICES
        self.context["priority_choices"] = Wish.PRIORITY_CHOICES
        self.context["effort_choices"] = Wish.EFFORT_CHOICES
        self.context["value_choices"] = Wish.VALUE_CHOICES
        
        # This helps with making tab selection logic simpler in the template
        status_filter = status_list[0] if status_list and len(status_list) == 1 else status_list
        
        self.context["current_filters"] = {
            "status_list": status_filter,
            "priority_list": priority_list,
            "tag": tag,
            "effort_list": effort_list,
            "value_list": value_list,
            "cost_min": cost_min,
            "cost_max": cost_max,
            "has_active_filters": has_active_filters,
            "active_tab": active_tab,  # Add explicit active tab tracking
        }

        # Handle HTMX requests
        if getattr(request, "htmx", False):
            if request.htmx.target == "wish-content-container":
                # For HTMX requests targeting the content container
                return self.render(request, template_name=self.partial_template_name)
            elif request.htmx.target == "wish-tabs":
                # For HTMX requests targeting the tabs
                return self.render(request, template_name=self.tabs_template_name)
            else:
                # For HTMX requests to update both content and tabs
                # Use OOB to update both parts
                content_html = render_to_string(
                    self.partial_template_name, 
                    self.context,
                    request=request
                )
                tabs_html = render_to_string(
                    self.tabs_template_name,
                    self.context,
                    request=request
                )
                response = HttpResponse(content_html)
                response["HX-Trigger"] = json.dumps({"updateTabs": tabs_html})
                return response
        
        # For regular requests, render the full page
        return self.render(request)


class WishDetailView(StaffRequiredMixin, MainContentView):
    """View for displaying a single wish item (staff only)."""

    template_name = "staff/wishes/wish_detail.html"

    def get(self, request, *args, **kwargs):
        """Get a single wish item."""
        wish_id = kwargs.get("pk")
        wish = get_object_or_404(Wish, id=wish_id)

        self.context["wish"] = wish
        return self.render(request)


class WishCreateView(StaffRequiredMixin, MainContentView):
    """View for creating a new wish item (staff only)."""

    template_name = "staff/wishes/wish_form.html"

    def get(self, request, *args, **kwargs):
        """Display the wish form."""
        self.context["form"] = WishForm()
        self.context["form_title"] = "Create New Wish"
        self.context["form_submit_url"] = reverse("staff:wish-create")
        return self.render(request)

    def post(self, request, *args, **kwargs):
        """Process the wish form submission."""
        form = WishForm(request.POST)

        if form.is_valid():
            # Save the form but don't commit
            wish = form.save(commit=False)
            # Set status to DRAFT explicitly for new wishes
            wish.status = Wish.STATUS_DRAFT
            wish.save()
            
            messages.success(request, f"Wish '{wish.title}' was created successfully.")
            return redirect("staff:wish-list")

        self.context["form"] = form
        self.context["form_title"] = "Create New Wish"
        self.context["form_submit_url"] = reverse("staff:wish-create")
        return self.render(request)


class WishUpdateView(StaffRequiredMixin, MainContentView):
    """View for updating an existing wish item (staff only)."""

    template_name = "staff/wishes/wish_form.html"

    def get(self, request, *args, **kwargs):
        """Display the wish form with existing data."""
        wish_id = kwargs.get("pk")
        wish = get_object_or_404(Wish, id=wish_id)

        # For updates, we need to use a form class that includes the status field
        class WishUpdateForm(WishForm):
            class Meta(WishForm.Meta):
                fields = WishForm.Meta.fields + ["status"]

        form = WishUpdateForm(instance=wish)
        self.context["form"] = form
        self.context["form_title"] = f"Edit Wish: {wish.title}"
        self.context["form_submit_url"] = reverse(
            "staff:wish-update", kwargs={"pk": wish_id}
        )
        self.context["wish"] = wish
        return self.render(request)

    def post(self, request, *args, **kwargs):
        """Process the wish form submission for updates."""
        wish_id = kwargs.get("pk")
        wish = get_object_or_404(Wish, id=wish_id)

        # For updates, we need to use a form class that includes the status field
        class WishUpdateForm(WishForm):
            class Meta(WishForm.Meta):
                fields = WishForm.Meta.fields + ["status"]

        form = WishUpdateForm(request.POST, instance=wish)

        if form.is_valid():
            wish = form.save()
            messages.success(request, f"Wish '{wish.title}' was updated successfully.")
            return redirect("staff:wish-detail", pk=wish.id)

        self.context["form"] = form
        self.context["form_title"] = f"Edit Wish: {wish.title}"
        self.context["form_submit_url"] = reverse(
            "staff:wish-update", kwargs={"pk": wish_id}
        )
        self.context["wish"] = wish
        return self.render(request)


class WishDeleteModalView(StaffRequiredMixin, HTMXView):
    """HTMX view for showing the delete confirmation modal (staff only)."""

    template_name = "components/modals/modal_confirm.html"

    def get(self, request, *args, **kwargs):
        """Show the delete confirmation modal."""
        wish_id = kwargs.get("pk")
        wish = get_object_or_404(Wish, id=wish_id)

        # Determine context from referrer
        referrer = request.META.get("HTTP_REFERER", "")
        is_on_detail_page = "/staff/wishes/" + str(wish.id) in referrer
        is_on_list_page = "/staff/wishes/" in referrer and not is_on_detail_page

        # Determine where to redirect after deletion
        if is_on_detail_page:
            # If coming from detail page
            redirect_after = reverse("staff:wish-list")
        else:
            # If coming from list or other page, stay there
            redirect_after = request.META.get(
                "HTTP_REFERER", reverse("staff:wish-list")
            )

        # Set up context for the confirmation modal
        self.context.update(
            {
                "modal_id": f"delete-wish-{wish.id}",
                "modal_title": "Delete Wish",
                "message": f"Are you sure you want to delete the wish <strong>{wish.title}</strong>? This action cannot be undone.",
                "confirm_url": reverse("staff:wish-delete", kwargs={"pk": wish.id}),
                "confirm_method": "post",  # Use POST instead of DELETE for better compatibility
                "confirm_text": "Delete",
                "cancel_text": "Cancel",
                "icon": "danger",
                # For HTMX row manipulation
                "is_list_view": is_on_list_page,
                "row_id": f"wish-row-{wish.id}",
                # Store redirect URL for the delete view to use
                "redirect_after": redirect_after,
            }
        )

        return self.render(request)


class WishDeleteView(StaffRequiredMixin, HTMXView):
    """View for deleting a wish item (staff only)."""

    def get(self, request, *args, **kwargs):
        """For regular GET requests, forward to the confirmation page."""
        # If it's an HTMX request, it should go to the modal view
        if getattr(request, "htmx", False):
            return redirect("staff:wish-delete-modal", pk=kwargs.get("pk"))

        # For non-HTMX requests, use the classic confirmation template
        wish_id = kwargs.get("pk")
        wish = get_object_or_404(Wish, id=wish_id)

        self.context["wish"] = wish
        self.template_name = "staff/wishes/wish_confirm_delete.html"
        return self.render(request)

    def post(self, request, *args, **kwargs):
        """Handle POST request for deleting a wish item."""
        wish_id = kwargs.get("pk")
        wish = get_object_or_404(Wish, id=wish_id)

        # Get the wish details before deletion
        wish_title = wish.title
        is_on_list_page = "wish-list" in request.META.get("HTTP_REFERER", "")

        # Delete the wish
        wish.delete()

        # Add success message
        messages.success(request, f"Wish '{wish_title}' was deleted successfully.")

        # Get the redirect URL from the request data
        redirect_url = request.POST.get("redirect_after", reverse("staff:wish-list"))

        # For HTMX requests, handle differently based on context
        if getattr(request, "htmx", False):
            if is_on_list_page:
                # If deleted from list view, return empty response with HX-Trigger
                # to trigger a removal animation
                response = HttpResponse("")
                response["HX-Trigger"] = f"wishDeleted-{wish_id}"
                return response
            else:
                # If deleted from detail view, redirect to list
                response = HttpResponse()
                response["HX-Redirect"] = redirect_url
                return response

        # For non-HTMX requests, use a standard redirect
        return redirect(redirect_url)


class WishCreateModalView(StaffRequiredMixin, HTMXView):
    """HTMX view for showing the create wish form in a modal."""
    
    template_name = "components/modals/modal_form.html"
    
    def get(self, request, *args, **kwargs):
        """Show the create wish form in a modal."""
        form = WishForm()
        
        self.context.update({
            "modal_id": "create-wish-modal",
            "modal_title": "Create New Wish",
            "form": form,
            "submit_url": reverse("staff:wish-create-submit"),
            "submit_text": "Create",
            "cancel_text": "Cancel",
            "target": "#modal-container",
            "trigger": "submit",
            "form_id": "create-wish-form",
            "modal_size": "xl",
        })
        
        return self.render(request)


class WishCreateSubmitView(StaffRequiredMixin, HTMXView):
    """HTMX view to handle the submission of the create wish form."""
    
    def post(self, request, *args, **kwargs):
        """Process the wish form submission from the modal."""
        form = WishForm(request.POST)
        
        if form.is_valid():
            # Save the form but don't commit
            wish = form.save(commit=False)
            # Set status to DRAFT explicitly for new wishes
            wish.status = Wish.STATUS_DRAFT
            wish.save()
            
            messages.success(request, f"Wish '{wish.title}' was created successfully.")
            
            # Return a response that will close the modal and refresh the page
            response = HttpResponse()
            response["HX-Refresh"] = "true"
            return response
        
        # If form is invalid, re-render the modal with errors
        self.context.update({
            "modal_id": "create-wish-modal",
            "modal_title": "Create New Wish",
            "form": form,
            "submit_url": reverse("staff:wish-create-submit"),
            "submit_text": "Create",
            "cancel_text": "Cancel",
            "target": "#modal-container",
            "trigger": "submit",
            "form_id": "create-wish-form",
            "modal_size": "xl",
        })
        
        # Render the form with validation errors
        self.template_name = "components/modals/modal_form.html"
        response = self.render(request)
        
        # Add a toast notification for validation errors via htmx
        if getattr(request, "htmx", False):
            error_toast = render_to_string("components/common/error_message.html", {
                "error_code": "form_validation",
                "status_code": 400,
                "error_message": "Please correct the errors in the form and try again.",
            }, request=request)
            response["HX-Trigger"] = json.dumps({"showToast": error_toast})
            
        return response


class WishCompleteView(StaffRequiredMixin, HTMXView):
    """View for marking a wish item as done or not done (staff only)."""

    def post(self, request, *args, **kwargs):
        """Mark the wish item as done or not done, or set a specific status."""
        wish_id = kwargs.get("pk")
        wish = get_object_or_404(Wish, id=wish_id)

        # Check if we're marking as incomplete
        mark_incomplete = request.GET.get("mark_incomplete", False)
        
        # Check if we're setting a specific status
        set_status = request.GET.get("set_status")

        if mark_incomplete:
            # Mark as incomplete (reopen)
            if wish.status == "DONE":
                wish.status = "TODO"  # Reset to TODO status
                wish.completed_at = None
                wish.save()
                messages.success(
                    request, f"Wish '{wish.title}' was marked as not done."
                )
        elif set_status:
            # Set a specific status (e.g., move from DRAFT to TODO)
            if set_status in dict(Wish.STATUS_CHOICES):
                old_status = wish.get_status_display()
                wish.status = set_status
                wish.save()
                messages.success(
                    request, f"Wish '{wish.title}' was moved from '{old_status}' to '{wish.get_status_display()}'."
                )
        else:
            # Use the model's complete method to mark as done
            wish.complete()
            messages.success(request, f"Wish '{wish.title}' was marked as done.")

        # Set up the context
        self.context["wish"] = wish

        # Handle both HTMX and regular requests
        if getattr(request, "htmx", False):
            # Check which view triggered this based on target
            target = request.headers.get("HX-Target", "")

            if "wish-row" in target:
                # For list view updates
                self.template_name = "staff/wishes/partials/wish_row.html"
                row_html = f'<tr id="wish-row-{wish.id}">{render_to_string(self.template_name, self.context, request=request)}</tr>'
                return HttpResponse(row_html)
            else:
                # For detail view updates
                self.template_name = "staff/wishes/partials/wish_detail.html"
                return self.render(request)
        else:
            # For standard requests, redirect to the detail page
            return redirect("staff:wish-detail", pk=wish.id)
