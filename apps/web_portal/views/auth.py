from apps.access.models import User, UserRole
from apps.common.serializers import AppWriteOnlyModelSerializer
from apps.common.views.api import AppAPIView
from apps.common.views.api.base import NonAuthenticatedAPIMixin
from apps.service_idp.views import proxy_to_idp_view, valid_idp_response
from config import settings


class AuthMetaInfoAPIView(NonAuthenticatedAPIMixin, AppAPIView):
    """View to send out the authentication metadata. Includes oauth data."""

    def get(self, *args, **kwargs):
        """Handle on get."""

        return self.send_response(
            {
                "oauth_redirects": {
                    "google": f"{settings.IDP_CONFIG['host']}/oauth/provider/google/"
                }
            }
        )


class UserSignUpAPIView(NonAuthenticatedAPIMixin, AppAPIView):
    """
    API from where the user can sign up.

    User creation can happen in two ways:
    1. B2C to IDP
    2. IDP to B2C
    """

    class _Serializer(AppWriteOnlyModelSerializer):
        class Meta(AppWriteOnlyModelSerializer.Meta):
            fields = ["full_name"]
            model = User

    serializer_class = _Serializer

    def post(self, *args, **kwargs):
        """Use IDP to handle the same."""

        serializer = self.get_valid_serializer()
        idp_response = valid_idp_response(
            url_path="/api/access/v1/simple-signup/",
            request=self.get_request(),
            method="POST",
        )

        role = UserRole.objects.get(identity__icontains="Learner")
        serializer.save(idp_user_id=idp_response["user"]["uuid"], user_role=role)
        idp_response["user"] = {**idp_response["user"], **serializer.data}

        return self.send_response(idp_response)


class AddExtraDataToUserResponseMixin:
    """On auth success responses, this mixin will add extra data to the user dict."""

    def dispatch(self, *args, **kwargs):
        """Handle on end response."""

        response = super().dispatch(*args, **kwargs)

        if response.data["status"] == "success":
            user = User.objects.get(idp_user_id=response.data["data"]["user"]["uuid"])
            response.data["data"]["user"]["full_name"] = user.full_name

        return response


class UserSignInAPIView(
    AddExtraDataToUserResponseMixin,
    proxy_to_idp_view(url_path="/api/access/v1/simple-login/"),
):
    """User login view. Overridden to add extra fields on success."""

    pass


class UserRefreshAPIView(
    AddExtraDataToUserResponseMixin,
    proxy_to_idp_view(url_path="/api/access/v1/refresh/"),
):
    """User refresh view. Overridden to add extra fields on success."""

    pass
