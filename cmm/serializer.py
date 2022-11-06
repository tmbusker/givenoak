from rest_framework import serializers, viewsets

from cmm.models.base import AuthUser, AuthGroup

# Serializers define the API representation.
class UserSerializer(serializers.HyperlinkedModelSerializer):
    """User Serializer"""
    class Meta:
        model = AuthUser
        fields = ['url', 'username', 'email', 'is_staff']

class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = AuthGroup
        fields = ['url', 'name']
