"""User views."""
from rest_framework import viewsets

from .models import User
from .serializers import UserSerializer


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for user operations."""

    queryset = User.objects.all()
    serializer_class = UserSerializer
