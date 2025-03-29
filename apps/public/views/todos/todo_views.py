from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from django.views.generic import DeleteView

from apps.common.forms.todo import TodoItemForm
from apps.common.models import TodoItem
from apps.public.helpers import MainContentView


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


class TodoDeleteView(LoginRequiredMixin, DeleteView):
    """View for deleting a todo item."""
    
    model = TodoItem
    template_name = "todos/todo_confirm_delete.html"
    success_url = reverse_lazy("public:todo-list")
    
    def delete(self, request, *args, **kwargs):
        """Delete the todo item and show a success message."""
        todo = self.get_object()
        messages.success(request, f"Todo '{todo.title}' was deleted successfully.")
        return super().delete(request, *args, **kwargs)


class TodoCompleteView(LoginRequiredMixin, MainContentView):
    """View for marking a todo item as complete."""
    
    def post(self, request, *args, **kwargs):
        """Mark the todo item as complete."""
        todo_id = kwargs.get("pk")
        todo = get_object_or_404(TodoItem, id=todo_id)
        
        # Use the model's complete method
        todo.complete()
        
        messages.success(request, f"Todo '{todo.title}' was marked as completed.")
        return redirect("public:todo-detail", pk=todo.id)