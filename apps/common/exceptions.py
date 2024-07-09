from django.utils.translation import gettext_lazy as _
from rest_framework import status
from rest_framework.exceptions import APIException


class ObjectExpired(APIException):
    """
    Custom exception to state that an object has expired. Ideally
    it's a 404, but instead of telling the user that. We tell
    them that it has expired. In a subtle way.
    """

    status_code = status.HTTP_410_GONE
    default_detail = _("The requested URL has expired.")
    default_code = "url_expired"
