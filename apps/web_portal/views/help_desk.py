from rest_framework import generics
from rest_framework.generics import ListAPIView
from apps.common.views.api.base import NonAuthenticatedAPIMixin
from apps.common.views.api import AppAPIView, AppCreateAPIView
from apps.meta.models import (
    FrequentlyAskedQuestion,
    UserAskedQuestion,
    UserContactedDetail,
)

from ...common.serializers import AppModelSerializer, get_app_read_only_serializer, get_read_serializer
from apps.meta.models import Country


class HelpDeskFaqAPIView(NonAuthenticatedAPIMixin, ListAPIView, AppAPIView):
    """List down FAQs to the user. This is a read only view."""

    queryset = FrequentlyAskedQuestion.objects.all()
    serializer_class = get_app_read_only_serializer(
        meta_model=FrequentlyAskedQuestion, meta_fields="__all__"
    )


class HelpDeskContactUsAPIView(AppCreateAPIView):
    """View used to create contact-us details of user from web portal."""

    class _Serializer(AppModelSerializer):
        class Meta(AppModelSerializer.Meta):
            model = UserContactedDetail
            fields = "__all__"

    serializer_class = _Serializer
    queryset = UserContactedDetail.objects.all()


class HelpDeskUserAskedQuestionAPIView(generics.ListCreateAPIView):
    """View used to create help desk, ask a question created by user."""

    class _Serializer(AppModelSerializer):
        class Meta(AppModelSerializer.Meta):
            model = UserAskedQuestion
            fields = "__all__"

    serializer_class = _Serializer
    queryset = UserAskedQuestion.objects.all()

class ContactUsMetaAPIView(NonAuthenticatedAPIMixin, AppAPIView):
    """Provides meta-data for the `UserPrivacyEditAPIView` edit page."""

    def get(self, request, *args, **kwargs):
        data = {
            "country": get_read_serializer(Country, meta_fields="__all__")(
                Country.objects.all(), many=True
            ).data,
        }

        return self.send_response(data=data)
