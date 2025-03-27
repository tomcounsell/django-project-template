from rest_framework import viewsets, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone

from apps.common.models import TodoItem
from apps.api.serializers import TodoItemSerializer, TodoItemListSerializer


class TodoItemViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing todo items.

    Provides CRUD operations for TodoItem model and additional endpoints
    for filtering and actions like complete and reopen.
    """

    queryset = TodoItem.objects.all()
    serializer_class = TodoItemSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["priority", "category", "status", "assignee"]
    search_fields = ["title", "description"]
    ordering_fields = ["created_at", "modified_at", "due_at", "priority"]
    ordering = ["-priority", "due_at", "-created_at"]  # Default ordering

    def get_serializer_class(self):
        """Return different serializers for list vs detail views."""
        if self.action == "list":
            return TodoItemListSerializer
        return TodoItemSerializer

    def perform_create(self, serializer):
        """Set the current user as assignee if not specified."""
        if "assignee" not in serializer.validated_data:
            serializer.save(assignee=self.request.user)
        else:
            serializer.save()

    @action(detail=True, methods=["post"])
    def complete(self, request, pk=None):
        """Mark the todo item as completed."""
        todo_item = self.get_object()
        todo_item.complete()
        return Response(TodoItemSerializer(todo_item).data)

    @action(detail=True, methods=["post"])
    def reopen(self, request, pk=None):
        """Reopen a completed todo item."""
        todo_item = self.get_object()
        todo_item.reopen()
        return Response(TodoItemSerializer(todo_item).data)

    @action(detail=False, methods=["get"])
    def overdue(self, request):
        """Get all overdue todo items."""
        now = timezone.now()
        queryset = self.get_queryset().filter(
            due_at__lt=now,
            status__in=[
                TodoItem.STATUS_TODO,
                TodoItem.STATUS_IN_PROGRESS,
                TodoItem.STATUS_BLOCKED,
            ],
        )
        queryset = self.filter_queryset(queryset)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def my_todos(self, request):
        """Get todo items assigned to the current user."""
        queryset = self.get_queryset().filter(assignee=request.user)
        queryset = self.filter_queryset(queryset)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def unassigned(self, request):
        """Get todo items with no assignee."""
        # Print debug information to help with testing
        import logging

        logger = logging.getLogger(__name__)

        queryset = self.get_queryset().filter(assignee__isnull=True)
        logger.info(f"Unassigned TODO count: {queryset.count()}")
        logger.info(
            f"Unassigned TODO titles: {list(queryset.values_list('title', flat=True))}"
        )

        queryset = self.filter_queryset(queryset)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
