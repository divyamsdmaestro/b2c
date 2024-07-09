from django.conf import settings

from apps.common.helpers import make_http_request
from apps.access.models import User

class IDPCommunicator:
    """
    Communicates with IDP services and returns the response. This is the one way
    class to communicate with the running IDP service.

    IDP communicates using only two methods => `GET` & `POST`.
    """

    @staticmethod
    def get_host():
        """Returns IDP host."""

        return settings.IDP_CONFIG["host"]

    @staticmethod
    def get_headers(auth_token):
        """Headers necessary for authorization."""

        headers = {"Content-Type": "application/json"}

        if auth_token:
            headers["Authorization"] = f"Token {auth_token}"

        return headers

    def get(self, url_path, auth_token=None, params={}):  # noqa
        """Make get request."""

        response = make_http_request(
            url=f"{self.get_host()}{url_path}",
            method="GET",
            params=params,
            headers=self.get_headers(auth_token),
        )

        return self.adapt(response, method='GET')

    def post(self, url_path, data={}, auth_token=None, params={}):  # noqa
        """Make post request."""

        response = make_http_request(
            url=f"{self.get_host()}{url_path}",
            method="POST",
            data=data,
            params=params,
            headers=self.get_headers(auth_token),
        )

        return self.adapt(response, method='POST')
    @staticmethod
    def adapt(idp_response, method):
        """Change schema for application to process."""

        data = idp_response["data"]
        # user_role = None
        # if method == "GET":
        #     if data and data['data']:
        #         user_role = User.objects.get(idp_user_id=data['data']['user']['uuid'])
        #         if user_role and data['data']['user']['email'] !='superadmin@app.com':
        #             if user_role.user_role == 'Student':
        #                 user_role = 'Student'
        #             elif user_role.user_role == 'Insititution Rep':
        #                 user_role = 'IR Admin'
        #             elif user_role.user_role == None:
        #                 user_role = 'Customer'
        #         else:
        #             user_role = 'Admin'
        return {
            "status_code": idp_response["status_code"],
            "status": data["status"] if data else "error",
            "data": data["data"] if data else None,
            # "user_role": user_role if user_role else None,
            "action_code": data["action_code"] if data else "CONTACT_DEVELOPERS",
            "source": "idp",  # for diff
        }
