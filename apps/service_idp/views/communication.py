from rest_framework import serializers
from rest_framework.authentication import get_authorization_header
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token as AuthToken
from apps.common.views.api import AppAPIView
from apps.common.views.api.base import NonAuthenticatedAPIMixin
from apps.service_idp.helpers import IDPCommunicator
from apps.access.authentication import get_user_headers
from config import settings
import requests
from django.http import JsonResponse
from apps.access.models import User, InstitutionDetail

def proxy_to_idp_view(url_path):
    """
    Proxies the request to the given IDP's view.
    Returns the response from the same.
    """

    class _ProxyView(NonAuthenticatedAPIMixin, AppAPIView):
        """View to proxy."""

        def get(self, *args, **kwargs):
            """Handle get."""

            response = idp_get_request(url_path=url_path, request=self.get_request())
            return Response(data=response, status=response["status_code"])

        def post(self, *args, **kwargs):
            """Handle post."""

            response = idp_post_request(url_path=url_path, request=self.get_request())
            return Response(data=response, status=response["status_code"])

    return _ProxyView


def idp_post_request(url_path, request):
    """Makes an IDP post request. Used in the view layer."""

    return IDPCommunicator().post(
        url_path=url_path,
        data=request.data,
        auth_token=get_auth_token(request),
        # TODO: later
        # params=request.query_params,
    )


def idp_get_request(url_path, request):
    """Makes an IDP get request. Used in the view layer."""

    return IDPCommunicator().get(
        url_path=url_path,
        auth_token=get_auth_token(request),
        params=request.query_params,
    )


def valid_idp_response(
    url_path, request, method, exception=serializers.ValidationError
):
    """
    Raises an exception if any error is given from IDP.
    This in turn uses `idp_post_request`.
    """

    if method == "POST":
        response = idp_post_request(url_path=url_path, request=request)
    else:
        response = idp_get_request(url_path=url_path, request=request)

    if response["status"] == "error":
        # TODO: `source` in response
        raise exception(response["data"])

    return response["data"]


def get_auth_token(request):
    """Returns the auth token passed in header."""

    auth = get_authorization_header(request).split()

    if not auth or len(auth) != 2:
        return None

    return auth[1].decode()

class CMSLoginAPIView(ObtainAuthToken):

    def post(self, request):
        username = self.request.data['username']
        password = self.request.data['password']
        User = get_user_model()
        
        try:
            user = User.objects.get(user_name=username)
            if user.user_role and user.user_role.identity == 'IR':
                ir_details = InstitutionDetail.objects.get_or_none(representative=user.id)
                if ir_details is None:
                    return Response({'error': "You don't have permission to access"}, status=401)
            payload = {
                "userNameOrEmailAddress": username,
                "password": password,
                "rememberClient": True,
                "tenancyName": settings.IDP_TENANT_NAME,
            }
            idp_response = requests.post(settings.IDP_CONFIG['host'] + settings.IDP_CONFIG['authenticate_url'], json=payload)
            data = idp_response.json()
        except Exception as e:
            return Response({'error': 'Invalid email or password'}, status=401)
        if data.get("errorMessage") == None:
            token ,created= AuthToken.objects.get_or_create(user=user)
            response_data = {
                'name': user.full_name,
                'uuid': user.uuid,
                'role': user.user_role.identity,
                'email': user.idp_email,
                'token': token.key,
            }
            return Response(response_data)
        else:
            return Response({'error': data.get("errorMessage")}, status=401)
        

class LogoutAPIView(AppAPIView):
    def post(self, *args, **kwargs):
        user = self.get_user()
        headers = get_user_headers(user)
        idp_response = requests.post(settings.IDP_CONFIG['host'] + settings.IDP_CONFIG['logout_url'], headers=headers)
        # print(idp_response.json())
        # breakpoint()
        if idp_response.json() == True:
            response_data = {
                'status' : "Success"
            }
            return JsonResponse(response_data)
        else:
            response_data = {
                'status': "Error"
            }
            return JsonResponse(response_data)