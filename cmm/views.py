from rest_framework import viewsets

from cmm.models.base import AuthUser
from cmm.serializer import UserSerializer

class UserViewSet(viewsets.ModelViewSet):
    """User View"""
    queryset = AuthUser.objects.all()
    serializer_class = UserSerializer
