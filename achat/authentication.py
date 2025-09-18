from django.contrib.auth.backends import BaseBackend
from django.contrib.auth import get_user_model
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from .models import UserToken

User = get_user_model()


class CustomAuthBackend(BaseBackend):
    """
    Custom authentication backend pour identifier (email ou telephone)
    """
    def authenticate(self, request, identifier=None, password=None, **kwargs):
        if identifier is None or password is None:
            return None
        
        try:
            user = User.objects.get(identifier=identifier)
            if user.check_password(password):
                return user
        except User.DoesNotExist:
            return None
        
        return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None


class UUIDTokenAuthentication(BaseAuthentication):
    """
    Custom token authentication basé sur UUID
    """
    def authenticate(self, request):
        auth_header = request.META.get('HTTP_AUTHORIZATION')
        
        if not auth_header or not auth_header.startswith('Bearer '):
            return None
        
        try:
            token = auth_header.split(' ')[1]
            user_token = UserToken.objects.select_related('user').get(token=token, is_active=True)
            return (user_token.user, user_token.token)
        except (UserToken.DoesNotExist, IndexError, ValueError):
            raise AuthenticationFailed('Token invalide ou inactif')

    def authenticate_header(self, request):
        return 'Bearer'