from apps.access.models import User
from apps.common.views.api import AppAPIView
from apps.common.views.api.base import NonAuthenticatedAPIMixin


class UserCreatedByOauthWebhookAPIView(NonAuthenticatedAPIMixin, AppAPIView):
    """
    When user is created in IDP this webhook is called.
    This in turn handles the same in this service.

    User creation can happen in two ways:
    1. B2C to IDP
    2. IDP to B2C
    """

    def post(self, *args, **kwargs):
        data = self.get_request().data
        uuid = data["user"]["uuid"]

        if not User.objects.get_or_none(idp_user_id=uuid):
            User.objects.create(
                idp_user_id=uuid, full_name=data["oauth_data"]["full_name"]
            )
        return self.send_response()
