from rest_framework import viewsets, status, serializers
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.common.models import UserAPIKey, TeamAPIKey, TeamMember


class UserAPIKeySerializer(serializers.ModelSerializer):
    """Serializer for the UserAPIKey model."""
    key = serializers.CharField(read_only=True)
    
    class Meta:
        model = UserAPIKey
        fields = ['id', 'name', 'prefix', 'created_at', 'revoked', 'key']
        read_only_fields = ['id', 'prefix', 'created_at', 'revoked']


class UserAPIKeyViewSet(viewsets.ModelViewSet):
    """
    API endpoints for managing user API keys.
    
    Users can create, list, and revoke their own API keys.
    The full API key is only returned once when creating a new key.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = UserAPIKeySerializer
    
    def get_queryset(self):
        """Return only API keys belonging to the current user."""
        return UserAPIKey.objects.filter(user=self.request.user)
    
    def create(self, request, *args, **kwargs):
        """Create a new API key for the current user."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        name = serializer.validated_data['name']
        api_key, key = UserAPIKey.objects.create_key(
            name=name, 
            user=request.user
        )
        
        # Include the generated key in the response (only time it's available)
        serializer = self.get_serializer(api_key)
        data = serializer.data
        data['key'] = key
        
        return Response(data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'])
    def revoke(self, request, pk=None):
        """Revoke an API key."""
        api_key = self.get_object()
        api_key.revoked = True
        api_key.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class TeamAPIKeySerializer(serializers.ModelSerializer):
    """Serializer for the TeamAPIKey model."""
    key = serializers.CharField(read_only=True)
    
    class Meta:
        model = TeamAPIKey
        fields = ['id', 'name', 'team', 'prefix', 'created_at', 'revoked', 'key']
        read_only_fields = ['id', 'prefix', 'created_at', 'revoked']


class TeamAPIKeyViewSet(viewsets.ModelViewSet):
    """
    API endpoints for managing team API keys.
    
    Team owners and admins can create, list, and revoke API keys for their teams.
    The full API key is only returned once when creating a new key.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = TeamAPIKeySerializer
    
    def get_queryset(self):
        """Return only API keys for teams the user is a member of."""
        return TeamAPIKey.objects.filter(team__members__user=self.request.user)
    
    def create(self, request, *args, **kwargs):
        """Create a new API key for a team."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        name = serializer.validated_data['name']
        team = serializer.validated_data['team']
        
        # Verify user has permission to create API keys for this team
        team_member = TeamMember.objects.filter(
            user=request.user, 
            team=team, 
            role__in=['OWNER', 'ADMIN']
        ).first()
        
        if not team_member:
            return Response(
                {"detail": "You don't have permission to create API keys for this team"}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        api_key, key = TeamAPIKey.objects.create_key(
            name=name, 
            team=team
        )
        
        # Include the generated key in the response (only time it's available)
        serializer = self.get_serializer(api_key)
        data = serializer.data
        data['key'] = key
        
        return Response(data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'])
    def revoke(self, request, pk=None):
        """Revoke a team API key."""
        api_key = self.get_object()
        
        # Verify user has permission to revoke this API key
        team_member = TeamMember.objects.filter(
            user=request.user, 
            team=api_key.team, 
            role__in=['OWNER', 'ADMIN']
        ).first()
        
        if not team_member:
            return Response(
                {"detail": "You don't have permission to revoke this API key"}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        api_key.revoked = True
        api_key.save()
        return Response(status=status.HTTP_204_NO_CONTENT)