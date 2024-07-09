from rest_framework.authentication import (
    TokenAuthentication,
    exceptions,
    get_authorization_header,
)
import requests
from config import settings
from rest_framework.authtoken.models import Token as AuthToken


def get_user_headers(user):
    data_token = get_user_token(user)
    header = {
        'Content-Type' : 'application/json',
        'Authorization': f'Bearer {data_token}'
    }
    return header

def get_user_token(user):
    try:
        payload = {
            "userNameOrEmailAddress": user.idp_email,
            "password": user.password,
            "rememberClient": True,
            "tenancyName": settings.IDP_TENANT_NAME
        }
        response = requests.post(settings.IDP_CONFIG['host'] + settings.IDP_CONFIG['authenticate_url'], json=payload)
        data = response.json()
        return data.get('accessToken')
    except Exception as e:
        # print(e)
        # breakpoint()
        raise e

class AppTokenAuthentication(TokenAuthentication):
    """
    App's TokenAuthentication used to skip authentication for proxy views.

    The default class in rest_framework raises "Invalid Token" error if
    any invalid token is passed. But this should not be raised for any.

    Error should come from IDP server.
    """

    def authenticate(self, request):
        """
        Skip for proxy views. Note that all proxy views must
        have `/proxy/` in their request.path.

        This also checks the token passed with the IDP server.
        """

        from apps.access.models import User
        from apps.service_idp.views import valid_idp_response

        # Auth header is not passed or Proxy Views
        # if "/proxy/" in request.path or not get_authorization_header(request).split():
        #     return None

        # Auth header is passed, check auth token from IDP
        # response = valid_idp_response(
        #     url_path="/api/access/v1/refresh/",
        #     request=request,
        #     method="GET",
        #     exception=exceptions.AuthenticationFailed,
        # )
        user=None

        token = get_authorization_header(request).split()
        if len(token)>=2:
            response = AuthToken.objects.get(key=token[1].decode('utf-8'))

            # get user and update fields from IDP
            user_data = response
            user = User.objects.get(id=user_data.user_id)

        return user, None