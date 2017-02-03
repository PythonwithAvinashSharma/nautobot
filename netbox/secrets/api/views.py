import base64
from Crypto.PublicKey import RSA

from django.http import HttpResponseBadRequest

from rest_framework.authentication import BasicAuthentication, SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from extras.api.renderers import FormlessBrowsableAPIRenderer, FreeRADIUSClientsRenderer
from secrets.filters import SecretFilter
from secrets.models import Secret, SecretRole, SessionKey, UserKey
from utilities.api import WritableSerializerMixin

from . import serializers


ERR_USERKEY_MISSING = "No UserKey found for the current user."
ERR_USERKEY_INACTIVE = "UserKey has not been activated for decryption."
ERR_PRIVKEY_MISSING = "Private key was not provided."
ERR_PRIVKEY_INVALID = "Invalid private key."


#
# Secret Roles
#

class SecretRoleViewSet(ModelViewSet):
    queryset = SecretRole.objects.all()
    serializer_class = serializers.SecretRoleSerializer
    permission_classes = [IsAuthenticated]


#
# Secrets
#

# TODO: Need to implement custom create() and update() methods to handle secret encryption.
class SecretViewSet(WritableSerializerMixin, ModelViewSet):
    queryset = Secret.objects.select_related(
        'device__primary_ip4', 'device__primary_ip6', 'role',
    ).prefetch_related(
        'role__users', 'role__groups',
    )
    serializer_class = serializers.SecretSerializer
    write_serializer_class = serializers.WritableSecretSerializer
    filter_class = SecretFilter
    # DRF's BrowsableAPIRenderer can't support passing the secret key as a header, so we disable it.
    renderer_classes = [FormlessBrowsableAPIRenderer, JSONRenderer, FreeRADIUSClientsRenderer]
    # Enabled BasicAuthentication for testing (until we have TokenAuthentication implemented)
    authentication_classes = [BasicAuthentication, SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def _get_master_key(self, request):

        # Check for a session key provided as a cookie or header
        if 'session_key' in request.COOKIES:
            session_key = base64.b64decode(request.COOKIES['session_key'])
        elif 'HTTP_X_SESSION_KEY' in request.META:
            session_key = base64.b64decode(request.META['HTTP_X_SESSION_KEY'])
        else:
            return None

        # Retrieve session key cipher (if any) for the current user
        try:
            sk = SessionKey.objects.get(user=request.user)
        except SessionKey.DoesNotExist:
            return None

        # Recover master key
        # TODO: Exception handling
        master_key = sk.get_master_key(session_key)

        return master_key

    def retrieve(self, request, *args, **kwargs):
        master_key = self._get_master_key(request)
        secret = self.get_object()

        if master_key is not None:
            secret.decrypt(master_key)

        serializer = self.get_serializer(secret)
        return Response(serializer.data)

    def list(self, request, *args, **kwargs):
        master_key = self._get_master_key(request)
        queryset = self.filter_queryset(self.get_queryset())

        # Pagination
        page = self.paginate_queryset(queryset)
        if page is not None:
            secrets = []
            if master_key is not None:
                for secret in page:
                    secret.decrypt(master_key)
                    secrets.append(secret)
                serializer = self.get_serializer(secrets, many=True)
            else:
                serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class GetSessionKey(APIView):
    """
    Cache an encrypted copy of the master key derived from the submitted private key.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):

        # Read private key
        private_key = request.POST.get('private_key', None)
        if private_key is None:
            return HttpResponseBadRequest(ERR_PRIVKEY_MISSING)

        # Validate user key
        try:
            user_key = UserKey.objects.get(user=request.user)
        except UserKey.DoesNotExist:
            return HttpResponseBadRequest(ERR_USERKEY_MISSING)
        if not user_key.is_active():
            return HttpResponseBadRequest(ERR_USERKEY_INACTIVE)

        # Validate private key
        master_key = user_key.get_master_key(private_key)
        if master_key is None:
            return HttpResponseBadRequest(ERR_PRIVKEY_INVALID)

        # Delete the existing SessionKey for this user if one exists
        SessionKey.objects.filter(user=request.user).delete()

        # Create a new SessionKey
        sk = SessionKey(user=request.user)
        sk.save(master_key=master_key)

        # Return the session key both as JSON and as a cookie
        response = Response({
            'session_key': base64.b64encode(sk.key),
            'expiration_time': sk.expiration_time,
        })
        # TODO: Limit cookie path to secrets API URLs
        response.set_cookie('session_key', base64.b64encode(sk.key), expires=sk.expiration_time)
        return response


class RSAKeyGeneratorView(APIView):
    """
    Generate a new RSA key pair for a user. Authenticated because it's a ripe avenue for DoS.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):

        # Determine what size key to generate
        key_size = request.GET.get('key_size', 2048)
        if key_size not in range(2048, 4097, 256):
            key_size = 2048

        # Export RSA private and public keys in PEM format
        key = RSA.generate(key_size)
        private_key = key.exportKey('PEM')
        public_key = key.publickey().exportKey('PEM')

        return Response({
            'private_key': private_key,
            'public_key': public_key,
        })
