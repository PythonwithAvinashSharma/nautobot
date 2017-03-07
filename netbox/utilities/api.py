from django.conf import settings
from django.utils import timezone

from rest_framework import authentication, exceptions
from rest_framework.exceptions import APIException
from rest_framework.permissions import DjangoModelPermissions, SAFE_METHODS
from rest_framework.serializers import Field

from users.models import Token


WRITE_OPERATIONS = ['create', 'update', 'partial_update', 'delete']


class ServiceUnavailable(APIException):
    status_code = 503
    default_detail = "Service temporarily unavailable, please try again later."


class TokenAuthentication(authentication.TokenAuthentication):
    """
    A custom authentication scheme which enforces Token expiration times.
    """
    model = Token

    def authenticate_credentials(self, key):
        model = self.get_model()
        try:
            token = model.objects.select_related('user').get(key=key)
        except model.DoesNotExist:
            raise exceptions.AuthenticationFailed("Invalid token")

        # Enforce the Token's expiration time, if one has been set.
        if token.expires and token.expires < timezone.now():
            raise exceptions.AuthenticationFailed("Token expired")

        if not token.user.is_active:
            raise exceptions.AuthenticationFailed("User inactive")

        return token.user, token


class TokenPermissions(DjangoModelPermissions):
    """
    Custom permissions handler which extends the built-in DjangoModelPermissions to validate a Token's write ability
    for unsafe requests (POST/PUT/PATCH/DELETE).
    """
    def __init__(self):
        # LOGIN_REQUIRED determines whether read-only access is provided to anonymous users.
        self.authenticated_users_only = settings.LOGIN_REQUIRED
        super(TokenPermissions, self).__init__()

    def has_permission(self, request, view):
        # If token authentication is in use, verify that the token allows write operations (for unsafe methods).
        if request.method not in SAFE_METHODS and isinstance(request.auth, Token):
            if not request.auth.write_enabled:
                return False
        return super(TokenPermissions, self).has_permission(request, view)


class ChoiceFieldSerializer(Field):
    """
    Represent a ChoiceField as (value, label).
    """
    def __init__(self, choices, **kwargs):
        self._choices = {k: v for k, v in choices}
        super(ChoiceFieldSerializer, self).__init__(**kwargs)

    def to_representation(self, obj):
        return obj, self._choices[obj]

    def to_internal_value(self, data):
        return self._choices.get(data)


class WritableSerializerMixin(object):
    """
    Allow for the use of an alternate, writable serializer class for write operations (e.g. POST, PUT).
    """
    def get_serializer_class(self):
        if self.action in WRITE_OPERATIONS and hasattr(self, 'write_serializer_class'):
            return self.write_serializer_class
        return self.serializer_class
