from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.shortcuts import redirect, get_object_or_404
from django.template.loader import render_to_string
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from django.views.generic import DeleteView

from apps.common.forms.todo import TodoItemForm
from apps.common.models import TodoItem
from apps.public.helpers import MainContentView
from apps.public.helpers.htmx_view import HTMXView


class TodoListView(LoginRequiredMixin, MainContentView):
    """View for listing all todo items."""
    
    template_name = "todos/todo_list.html"
    
    def get(self, request, *args, **kwargs):
        """Get all todos with filtering options."""
        queryset = TodoItem.objects.all()
        
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
        self.context["todos"] = queryset
        self.context["status_choices"] = TodoItem.STATUS_CHOICES
        self.context["priority_choices"] = TodoItem.PRIORITY_CHOICES
        self.context["category_choices"] = TodoItem.CATEGORY_CHOICES
        self.context["current_filters"] = {
            "status": status,
            "priority": priority, 
            "category": category,
            "assignee": assignee
        }
        
        return self.render(request)


class TodoDetailView(LoginRequiredMixin, MainContentView):
    """View for displaying a single todo item."""
    
    template_name = "todos/todo_detail.html"
    
    def get(self, request, *args, **kwargs):
        """Get a single todo item."""
        todo_id = kwargs.get("pk")
        todo = get_object_or_404(TodoItem, id=todo_id)
        
        self.context["todo"] = todo
        return self.render(request)


class TodoCreateView(LoginRequiredMixin, MainContentView):
    """View for creating a new todo item."""
    
    template_name = "todos/todo_form.html"
    
    def get(self, request, *args, **kwargs):
        """Display the todo form."""
        self.context["form"] = TodoItemForm()
        self.context["form_title"] = "Create New Todo"
        self.context["form_submit_url"] = reverse("public:todo-create")
        return self.render(request)
    
    def post(self, request, *args, **kwargs):
        """Process the todo form submission."""
        form = TodoItemForm(request.POST)
        
        if form.is_valid():
            # Save and set the current user as assignee if not specified
            todo = form.save(user=request.user)
            messages.success(request, f"Todo '{todo.title}' was created successfully.")
            return redirect("public:todo-list")
        
        self.context["form"] = form
        self.context["form_title"] = "Create New Todo"
        self.context["form_submit_url"] = reverse("public:todo-create")
        return self.render(request)


class TodoUpdateView(LoginRequiredMixin, MainContentView):
    """View for updating an existing todo item."""
    
    template_name = "todos/todo_form.html"
    
    def get(self, request, *args, **kwargs):
        """Display the todo form with existing data."""
        todo_id = kwargs.get("pk")
        todo = get_object_or_404(TodoItem, id=todo_id)
        
        form = TodoItemForm(instance=todo)
        self.context["form"] = form
        self.context["form_title"] = f"Edit Todo: {todo.title}"
        self.context["form_submit_url"] = reverse("public:todo-update", kwargs={"pk": todo_id})
        self.context["todo"] = todo
        return self.render(request)
    
    def post(self, request, *args, **kwargs):
        """Process the todo form submission for updates."""
        todo_id = kwargs.get("pk")
        todo = get_object_or_404(TodoItem, id=todo_id)
        
        form = TodoItemForm(request.POST, instance=todo)
        
        if form.is_valid():
            todo = form.save()
            messages.success(request, f"Todo '{todo.title}' was updated successfully.")
            return redirect("public:todo-detail", pk=todo.id)
        
        self.context["form"] = form
        self.context["form_title"] = f"Edit Todo: {todo.title}"
        self.context["form_submit_url"] = reverse("public:todo-update", kwargs={"pk": todo_id})
        self.context["todo"] = todo
        return self.render(request)


class TodoDeleteModalView(LoginRequiredMixin, HTMXView):
    """HTMX view for showing the delete confirmation modal."""
    
    template_name = "components/modals/modal_confirm.html"
    
    def get(self, request, *args, **kwargs):
        """Show the delete confirmation modal."""
        todo_id = kwargs.get("pk")
        todo = get_object_or_404(TodoItem, id=todo_id)
        
        # Determine context from referrer
        referrer = request.META.get('HTTP_REFERER', '')
        is_on_detail_page = '/todos/' + str(todo.id) in referrer
        is_on_list_page = '/todos/' in referrer and not is_on_detail_page
        
        # Determine where to redirect after deletion
        if is_on_detail_page:
            # If coming from detail page
            redirect_after = reverse("public:todo-list")
        else:
            # If coming from list or other page, stay there
            redirect_after = request.META.get('HTTP_REFERER', reverse("public:todo-list"))
        
        # Set up context for the confirmation modal
        self.context.update({
            "modal_id": f"delete-todo-{todo.id}",
            "modal_title": "Delete Todo",
            "message": f"Are you sure you want to delete the todo item <strong>{todo.title}</strong>? This action cannot be undone.",
            "confirm_url": reverse("public:todo-delete", kwargs={"pk": todo.id}),
            "confirm_method": "post", # Use POST instead of DELETE for better compatibility
            "confirm_text": "Delete",
            "cancel_text": "Cancel",
            "icon": "danger",
            # For HTMX row manipulation
            "is_list_view": is_on_list_page,
            "row_id": f"todo-row-{todo.id}",
            # Store redirect URL for the delete view to use
            "redirect_after": redirect_after,
        })
        
        return self.render(request)


class TodoDeleteView(LoginRequiredMixin, HTMXView):
    """View for deleting a todo item."""
    
    def get(self, request, *args, **kwargs):
        """For regular GET requests, forward to the confirmation page."""
        # If it's an HTMX request, it should go to the modal view
        if getattr(request, "htmx", False):
            return redirect("public:todo-delete-modal", pk=kwargs.get("pk"))
            
        # For non-HTMX requests, use the classic confirmation template
        todo_id = kwargs.get("pk")
        todo = get_object_or_404(TodoItem, id=todo_id)
        
        self.context["todo"] = todo
        self.template_name = "todos/todo_confirm_delete.html"
        return self.render(request)
    
    def post(self, request, *args, **kwargs):
        """Handle POST request for deleting a todo item."""
        todo_id = kwargs.get("pk")
        todo = get_object_or_404(TodoItem, id=todo_id)
        
        # Get the todo details before deletion
        todo_title = todo.title
        is_on_list_page = 'todo-list' in request.META.get('HTTP_REFERER', '')
        
        # Delete the todo
        todo.delete()
        
        # Add success message
        messages.success(request, f"Todo '{todo_title}' was deleted successfully.")
        
        # Get the redirect URL from the request data
        redirect_url = request.POST.get('redirect_after', reverse("public:todo-list"))
        
        # For HTMX requests, handle differently based on context
        if getattr(request, "htmx", False):
            if is_on_list_page:
                # If deleted from list view, return empty response with HX-Trigger
                # to trigger a removal animation
                response = HttpResponse("")
                response["HX-Trigger"] = f"todoDeleted-{todo_id}"
                return response
            else:
                # If deleted from detail view, redirect to list
                response = HttpResponse()
                response["HX-Redirect"] = redirect_url
                return response
        
        # For non-HTMX requests, use a standard redirect
        return redirect(redirect_url)

    def delete(self, request, *args, **kwargs):
        """Use post method for DELETE requests."""
        return self.post(request, *args, **kwargs)


class TodoCompleteView(LoginRequiredMixin, HTMXView):
    """View for marking a todo item as done or not done."""
    
    def post(self, request, *args, **kwargs):
        """Mark the todo item as done or not done."""
        todo_id = kwargs.get("pk")
        todo = get_object_or_404(TodoItem, id=todo_id)
        
        # Check if we're marking as incomplete
        mark_incomplete = request.GET.get('mark_incomplete', False)
        
        if mark_incomplete:
            # Mark as incomplete (reopen)
            if todo.status == "DONE":
                todo.status = "TODO"  # Reset to TODO status
                todo.completed_at = None
                todo.save()
                messages.success(request, f"Todo '{todo.title}' was marked as not done.")
        else:
            # Use the model's complete method to mark as done
            todo.complete()
            messages.success(request, f"Todo '{todo.title}' was marked as done.")
        
        # Set up the context
        self.context["todo"] = todo
        
        # Handle both HTMX and regular requests
        if getattr(request, "htmx", False):
            # Check which view triggered this based on target
            target = request.headers.get('HX-Target', '')
            
            if 'todo-row' in target:
                # For list view updates
                self.template_name = "todos/partials/todo_row.html"
                row_html = f'<tr id="todo-row-{todo.id}">{render_to_string(self.template_name, self.context, request=request)}</tr>'
                return HttpResponse(row_html)
            else:
                # For detail view updates
                self.template_name = "todos/partials/todo_detail.html"
                return self.render(request)
        else:
            # For standard requests, redirect to the detail page
            return redirect("public:todo-detail", pk=todo.id)