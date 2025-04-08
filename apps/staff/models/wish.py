from django.db import models
from django.urls import reverse
from django.utils import timezone

from apps.common.behaviors import Timestampable


class Wish(Timestampable, models.Model):
    """
    A model representing a wish/desire/goal to be tracked and managed.

    Allows tracking of wishes and goals with priorities, tags, effort, value, and cost.

    Attributes:
        title (str): Brief description of the wish
        description (str): Detailed explanation of what is wished for
        priority (str): Wish priority level (LOW, MEDIUM, HIGH)
        tags (JSONField): List of tags for categorizing this wish
        status (str): Current status of the wish (TODO, IN_PROGRESS, BLOCKED, DONE)
        effort (str): Estimated effort to complete this wish (sm, 1, 2, 4, 8, breakdown)
        value (str): Business value of this wish (1-5 stars)
        cost_estimate (int): Estimated cost in dollars (integer, no cents)
        due_at (DateTimeField): When this wish should be fulfilled by
        completed_at (DateTimeField): When this wish was marked as completed
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

    # Status choices
    STATUS_DRAFT = "DRAFT"
    STATUS_TODO = "TODO"
    STATUS_IN_PROGRESS = "IN_PROGRESS"
    STATUS_BLOCKED = "BLOCKED"
    STATUS_DONE = "DONE"
    STATUS_CHOICES = [
        (STATUS_DRAFT, "Draft"),
        (STATUS_TODO, "To Do"),
        (STATUS_IN_PROGRESS, "In Progress"),
        (STATUS_BLOCKED, "Blocked"),
        (STATUS_DONE, "Done"),
    ]
    
    # Effort choices
    EFFORT_SMALL = "sm"
    EFFORT_ONE = "1"
    EFFORT_TWO = "2"
    EFFORT_FOUR = "4"
    EFFORT_EIGHT = "8"
    EFFORT_BREAKDOWN = "breakdown"
    EFFORT_CHOICES = [
        (EFFORT_SMALL, "Small"),
        (EFFORT_ONE, "1 point"),
        (EFFORT_TWO, "2 points"),
        (EFFORT_FOUR, "4 points"),
        (EFFORT_EIGHT, "8 points"),
        (EFFORT_BREAKDOWN, "Needs breakdown"),
    ]
    
    # Value choices
    VALUE_ONE = "⭐️"
    VALUE_TWO = "⭐️⭐️"
    VALUE_THREE = "⭐️⭐️⭐️"
    VALUE_FOUR = "⭐️⭐️⭐️⭐️"
    VALUE_FIVE = "⭐️⭐️⭐️⭐️⭐️"
    VALUE_CHOICES = [
        (VALUE_ONE, "⭐️"),
        (VALUE_TWO, "⭐️⭐️"),
        (VALUE_THREE, "⭐️⭐️⭐️"),
        (VALUE_FOUR, "⭐️⭐️⭐️⭐️"),
        (VALUE_FIVE, "⭐️⭐️⭐️⭐️⭐️"),
    ]

    # Fields
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, default="")
    priority = models.CharField(
        max_length=20,
        choices=PRIORITY_CHOICES,
        default=PRIORITY_MEDIUM,
    )
    tags = models.JSONField(default=list, blank=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_DRAFT,
    )
    effort = models.CharField(
        max_length=10,
        choices=EFFORT_CHOICES,
        default=EFFORT_SMALL,
        null=True,
        blank=True,
    )
    value = models.CharField(
        max_length=10,
        choices=VALUE_CHOICES,
        default=VALUE_THREE,
        null=True,
        blank=True,
    )
    cost_estimate = models.PositiveIntegerField(
        null=True, 
        blank=True,
        help_text="Estimated cost in dollars (no cents)"
    )
    due_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    # MODEL PROPERTIES
    @property
    def is_completed(self):
        """Returns whether this wish is completed."""
        return self.status == self.STATUS_DONE

    @property
    def is_overdue(self):
        """Returns whether this wish is past its due date."""
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
            
    @property
    def formatted_cost(self):
        """Returns the cost estimate formatted as currency."""
        if self.cost_estimate is None:
            return None
        return f"${self.cost_estimate:,}"

    def get_absolute_url(self):
        """Returns the URL to the detail view for this wish."""
        return reverse("staff:wish-detail", kwargs={"pk": self.pk})

    def get_complete_url(self):
        """Returns the URL to mark this wish as complete."""
        return reverse("staff:wish-complete", kwargs={"pk": self.pk})

    def get_delete_url(self):
        """Returns the URL to delete this wish."""
        return reverse("staff:wish-delete", kwargs={"pk": self.pk})

    def get_delete_modal_url(self):
        """Returns the URL to show the delete confirmation modal for this wish."""
        return reverse("staff:wish-delete-modal", kwargs={"pk": self.pk})

    # MODEL FUNCTIONS
    def __str__(self):
        return f"{self.title} ({self.priority})"

    def complete(self):
        """Mark this wish as completed."""
        self.status = self.STATUS_DONE
        self.completed_at = timezone.now()
        self.save()

    def reopen(self):
        """Reopen this wish."""
        self.status = self.STATUS_TODO
        self.completed_at = None
        self.save()

    def set_priority(self, priority):
        """Set the priority of this wish."""
        if priority not in dict(self.PRIORITY_CHOICES):
            raise ValueError(f"Invalid priority: {priority}")
        self.priority = priority
        self.save()
        
    def add_tag(self, tag):
        """Add a tag to this wish if it doesn't already exist."""
        if not isinstance(self.tags, list):
            self.tags = []
        
        tag = tag.strip().lower()
        if tag and tag not in self.tags:
            self.tags.append(tag)
            self.save()
            
    def remove_tag(self, tag):
        """Remove a tag from this wish."""
        if not isinstance(self.tags, list):
            self.tags = []
            return
            
        tag = tag.strip().lower()
        if tag in self.tags:
            self.tags.remove(tag)
            self.save()
            
    def set_effort(self, effort):
        """Set the effort estimation for this wish."""
        if effort not in dict(self.EFFORT_CHOICES):
            raise ValueError(f"Invalid effort: {effort}")
        self.effort = effort
        self.save()
        
    def set_value(self, value):
        """Set the business value for this wish."""
        if value not in dict(self.VALUE_CHOICES):
            raise ValueError(f"Invalid value: {value}")
        self.value = value
        self.save()
        
    def set_cost_estimate(self, cost_estimate):
        """Set the cost estimate for this wish in dollars."""
        if cost_estimate is not None:
            try:
                # Convert to int in case it's passed as a string
                cost_estimate = int(cost_estimate)
                if cost_estimate < 0:
                    raise ValueError("Cost estimate cannot be negative")
            except (ValueError, TypeError):
                raise ValueError("Cost estimate must be a positive integer or None")
                
        self.cost_estimate = cost_estimate
        self.save()

    def set_status(self, status):
        """Set the status of this wish."""
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
        verbose_name = "Wish"
        verbose_name_plural = "Wishes"
        ordering = ["-priority", "due_at", "-created_at"]
