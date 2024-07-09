from apps.common.serializers import (
    AppReadOnlyModelSerializer,
    get_app_read_only_serializer,
)
from apps.common.views.api.generic import DEFAULT_IDENTITY_DISPLAY_FIELDS
from apps.webinars.models import (Webinar, WebinarImage, Participant,
                                  WebinarRegistration, PaymentMode)

from apps.learning.models import Skill, Language
import django_filters
# from django.contrib.postgres.fields import JSONField
from django_filters import rest_framework as filters
from rest_framework import serializers
from django.contrib.postgres.fields import JSONField
from django.contrib.auth.models import AnonymousUser
from datetime import datetime

today = datetime.now().date()

class SmilarWebinarSerializer(AppReadOnlyModelSerializer):
    image = get_app_read_only_serializer(WebinarImage, meta_fields="__all__")()

    class Meta:
        fields = ["id","uuid","identity", "image", "description", "participant_limit", "start_date"]
        model = Webinar
    

class WebinarSerializer(AppReadOnlyModelSerializer):
    """This Serializer contains data for Jobs output structure."""

    skills = get_app_read_only_serializer(
        Skill, meta_fields=DEFAULT_IDENTITY_DISPLAY_FIELDS
    )(many=True)
    language = get_app_read_only_serializer(
        Language, meta_fields=DEFAULT_IDENTITY_DISPLAY_FIELDS
    )()
    image = get_app_read_only_serializer(WebinarImage, meta_fields=["id", "uuid", "file"])()
    payment_mode = get_app_read_only_serializer(
        PaymentMode, meta_fields=DEFAULT_IDENTITY_DISPLAY_FIELDS
    )()
    payment = serializers.SerializerMethodField()

    smilar_webinar = serializers.SerializerMethodField()

    class Meta:
        model = Webinar
        fields = "__all__"

    def get_payment(self, obj):
        user = self.get_user()
        if isinstance(user, AnonymousUser) or user == None:
            return 'Failed'
        else:
            payment = WebinarRegistration.objects.filter(webinar=obj,
                                                         user=self.get_user(),
                                                         status='success').exists()
            return "Success" if payment else "Failed"
        # webinar_data = WebinarRegistration.objects.filter(webinar=obj,
        #                                                   user=self.get_user()).values(
        #     'status')
        # payment = None
        # for status in webinar_data:
        #     if status == 'success':
        #         payment = True
        #     else:
        #         payment = False
        # return payment

    def get_smilar_webinar(self, obj):
        webinar_data = Webinar.objects.filter(start_date__gte=today).exclude(id=obj.id)[:2]
        webinar_serializer = SmilarWebinarSerializer(webinar_data, many=True)
        return webinar_serializer.data
    
    
class WebinarRegistrationSerializer(AppReadOnlyModelSerializer):
    webinar_name = serializers.CharField(source='webinar.identity', read_only=True)

    class Meta:
        model = WebinarRegistration
        fields = ['id', 'webinar', 'webinar_name', 'user',
                  'registration_date', 'is_attended',
                  'payment', 'payment_amount', 'status']


class WebinarFilter(filters.FilterSet):
    session_detail = filters.CharFilter(field_name='session_detail',
                                        lookup_expr='exact')

    class Meta:
        model = Webinar
        fields = ['identity', 'language', 'image', 'description', 'webinar_link',
                  'participant_limit', 'user_group', 'skills',
                  'is_paid_webinar', 'webinar_fee', 'payment_mode',
                  'payment_mode_details', 'start_date', 'end_date', 'status',
                  'session_detail']


class WebinarDetailSerializer(serializers.ModelSerializer):
    webinar = WebinarSerializer()

    class Meta:
        model = WebinarRegistration
        fields = [
            "registration_date",
            "webinar",
            "uuid",
            "status",
        ]

class WebinarJobDetailSerializer(serializers.ModelSerializer):
    image = get_app_read_only_serializer(WebinarImage, meta_fields="__all__")()

    class Meta:
        model = Webinar
        fields = ["id","uuid", "identity", "image", "description", "participant_limit", "start_date"]