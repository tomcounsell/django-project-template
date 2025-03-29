from apps.common.models import Image
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import authentication, filters, permissions, serializers, viewsets


class ImageSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    modified_at = serializers.DateTimeField(read_only=True)
    thumbnail_url = serializers.URLField(read_only=True)
    meta_data = serializers.DictField(read_only=True)

    class Meta:
        model = Image
        fields = [
            "id",
            "created_at",
            "modified_at",
            "original",
            "thumbnail_url",
            "meta_data",
        ]


class ImageViewSet(viewsets.ModelViewSet):
    queryset = Image.objects.all()
    serializer_class = ImageSerializer
    # Set authentication to session based
    authentication_classes = [authentication.SessionAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter)
    filterset_fields = ("modified_at",)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class ImageUploadView(viewsets.ModelViewSet):
    """API view for uploading images."""
    queryset = Image.objects.all()
    serializer_class = ImageSerializer
    permission_classes = [permissions.IsAuthenticated]
