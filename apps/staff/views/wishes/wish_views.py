from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, StaffMemberRequiredMixin
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.template.loader import render_to_string
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.generic import DeleteView

from apps.common.forms.wish import WishForm
from apps.common.models import Wish
from apps.public.helpers import MainContentView
from apps.public.helpers.htmx_view import HTMXView


class StaffRequiredMixin(LoginRequiredMixin):
    """Mixin to require staff privileges for access to views."""
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)


class WishListView(StaffRequiredMixin, MainContentView):
    """View for listing all wish items (staff only)."""

    template_name = "staff/wishes/wish_list.html"

    def get(self, request, *args, **kwargs):
        """Get all wishes with filtering options."""
        queryset = Wish.objects.all()

        # Filter by status if provided
        status = request.GET.get("status")
        if status:
            queryset = queryset.filter(status=status)

        # Filter by priority if provided
        priority = request.GET.get("priority")
        if priority:
            queryset = queryset.filter(priority=priority)

        # Filter by category if provided
        category = request.GET.get("category")
        if category:
            queryset = queryset.filter(category=category)

        # Filter by assignee if provided
        assignee = request.GET.get("assignee")
        if assignee == "me":
            queryset = queryset.filter(assignee=request.user)
        elif assignee == "unassigned":
            queryset = queryset.filter(assignee__isnull=True)

        # Set the context
        self.context["wishes"] = queryset
        self.context["status_choices"] = Wish.STATUS_CHOICES
        self.context["priority_choices"] = Wish.PRIORITY_CHOICES
        self.context["category_choices"] = Wish.CATEGORY_CHOICES
        self.context["current_filters"] = {
            "status": status,
            "priority": priority,
            "category": category,
            "assignee": assignee,
        }

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
            # Save and set the current user as assignee if not specified
            wish = form.save(user=request.user)
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

        form = WishForm(instance=wish)
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

        form = WishForm(request.POST, instance=wish)

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


class WishCompleteView(StaffRequiredMixin, HTMXView):
    """View for marking a wish item as done or not done (staff only)."""

    def post(self, request, *args, **kwargs):
        """Mark the wish item as done or not done."""
        wish_id = kwargs.get("pk")
        wish = get_object_or_404(Wish, id=wish_id)

        # Check if we're marking as incomplete
        mark_incomplete = request.GET.get("mark_incomplete", False)

        if mark_incomplete:
            # Mark as incomplete (reopen)
            if wish.status == "DONE":
                wish.status = "TODO"  # Reset to TODO status
                wish.completed_at = None
                wish.save()
                messages.success(
                    request, f"Wish '{wish.title}' was marked as not done."
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