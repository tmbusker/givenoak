from rest_framework import viewsets
from rest_framework import permissions
from cmm.models.base import AuthUser, AuthGroup
from cmm.serializer import GroupSerializer, UserSerializer

class UserViewSet(viewsets.ModelViewSet):
    """User View"""
    queryset = AuthUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = AuthGroup.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAuthenticated]
