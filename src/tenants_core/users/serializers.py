"""User serializers."""
from rest_framework import serializers

from .models import User


class UserSerializer(serializers.ModelSerializer):
    """Serializer for user details."""

    class Meta:
        model = User
        fields = ["id", "email", "first_name", "last_name", "is_active", "created_at"]
        read_only_fields = ["id", "created_at"]
