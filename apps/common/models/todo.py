from django.db import models
from django.urls import reverse
from django.utils import timezone

from apps.common.behaviors import Timestampable


class TodoItem(Timestampable, models.Model):
    """
    A model representing an internal system improvement task.

    Allows tracking of system enhancements, bug fixes, and other internal tasks
    with priorities, categories, and assignees.

    Attributes:
        title (str): Brief description of the task
        description (str): Detailed explanation of what needs to be done
        priority (str): Task priority level (LOW, MEDIUM, HIGH)
        category (str): The area of the system this task relates to
        status (str): Current status of the task (TODO, IN_PROGRESS, BLOCKED, DONE)
        assignee (ForeignKey): User assigned to complete this task
        due_at (DateTimeField): When this task should be completed by
        completed_at (DateTimeField): When this task was marked as completed
    """

    # Priority choices
    PRIORITY_LOW = "LOW"
    PRIORITY_MEDIUM = "MEDIUM"
    PRIORITY_HIGH = "HIGH"
    PRIORITY_CHOICES = [
        (PRIORITY_LOW, "Low"),
        (PRIORITY_MEDIUM, "Medium"),
        (PRIORITY_HIGH, "High"),
    ]

    # Category choices
    CATEGORY_GENERAL = "GENERAL"
    CATEGORY_FRONTEND = "FRONTEND"
    CATEGORY_BACKEND = "BACKEND"
    CATEGORY_API = "API"
    CATEGORY_DATABASE = "DATABASE"
    CATEGORY_PERFORMANCE = "PERFORMANCE"
    CATEGORY_SECURITY = "SECURITY"
    CATEGORY_DOCUMENTATION = "DOCUMENTATION"
    CATEGORY_TESTING = "TESTING"
    CATEGORY_CHOICES = [
        (CATEGORY_GENERAL, "General"),
        (CATEGORY_FRONTEND, "Frontend"),
        (CATEGORY_BACKEND, "Backend"),
        (CATEGORY_API, "API"),
        (CATEGORY_DATABASE, "Database"),
        (CATEGORY_PERFORMANCE, "Performance"),
        (CATEGORY_SECURITY, "Security"),
        (CATEGORY_DOCUMENTATION, "Documentation"),
        (CATEGORY_TESTING, "Testing"),
    ]

    # Status choices
    STATUS_TODO = "TODO"
    STATUS_IN_PROGRESS = "IN_PROGRESS"
    STATUS_BLOCKED = "BLOCKED"
    STATUS_DONE = "DONE"
    STATUS_CHOICES = [
        (STATUS_TODO, "To Do"),
        (STATUS_IN_PROGRESS, "In Progress"),
        (STATUS_BLOCKED, "Blocked"),
        (STATUS_DONE, "Done"),
    ]

    # Fields
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, default="")
    priority = models.CharField(
        max_length=20,
        choices=PRIORITY_CHOICES,
        default=PRIORITY_MEDIUM,
    )
    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        default=CATEGORY_GENERAL,
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_TODO,
    )
    assignee = models.ForeignKey(
        "common.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_todos",
    )
    due_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    # MODEL PROPERTIES
    @property
    def is_completed(self):
        """Returns whether this todo item is completed."""
        return self.status == self.STATUS_DONE

    @property
    def is_overdue(self):
        """Returns whether this todo item is past its due date."""
        if not self.due_at:
            return False
        return self.due_at < timezone.now()

    @property
    def days_until_due(self):
        """Returns the number of days until the due date (negative if overdue)."""
        if not self.due_at:
            return None
        delta = self.due_at - timezone.now()
        return delta.days

    @property
    def time_remaining_display(self):
        """Returns a human-readable representation of time remaining."""
        if not self.due_at:
            return "No due date"

        days = self.days_until_due

        if days > 1:
            return f"{days} days remaining"
        elif days == 1:
            return "1 day remaining"
        elif days == 0:
            return "Due today"
        elif days == -1:
            return "Overdue by 1 day"
        else:
            return f"Overdue by {abs(days)} days"

    def get_absolute_url(self):
        """Returns the URL to the detail view for this todo item."""
        return reverse("public:todo-detail", kwargs={"pk": self.pk})

    def get_complete_url(self):
        """Returns the URL to mark this todo item as complete."""
        return reverse("public:todo-complete", kwargs={"pk": self.pk})

    def get_delete_url(self):
        """Returns the URL to delete this todo item."""
        return reverse("public:todo-delete", kwargs={"pk": self.pk})

    def get_delete_modal_url(self):
        """Returns the URL to show the delete confirmation modal for this todo item."""
        return reverse("public:todo-delete-modal", kwargs={"pk": self.pk})

    # MODEL FUNCTIONS
    def __str__(self):
        return f"{self.title} ({self.priority})"

    def complete(self):
        """Mark this todo item as completed."""
        self.status = self.STATUS_DONE
        self.completed_at = timezone.now()
        self.save()

    def reopen(self):
        """Reopen this todo item."""
        self.status = self.STATUS_TODO
        self.completed_at = None
        self.save()

    def set_priority(self, priority):
        """Set the priority of this todo item."""
        if priority not in dict(self.PRIORITY_CHOICES):
            raise ValueError(f"Invalid priority: {priority}")
        self.priority = priority
        self.save()

    def set_status(self, status):
        """Set the status of this todo item."""
        if status not in dict(self.STATUS_CHOICES):
            raise ValueError(f"Invalid status: {status}")

        self.status = status

        # Update completed_at if status is DONE
        if status == self.STATUS_DONE:
            self.completed_at = timezone.now()
        elif self.completed_at:  # Reset completed_at if status is not DONE
            self.completed_at = None

        self.save()

    class Meta:
        verbose_name = "Todo Item"
        verbose_name_plural = "Todo Items"
        ordering = ["-priority", "due_at", "-created_at"]
