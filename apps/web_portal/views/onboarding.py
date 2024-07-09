from rest_framework import serializers
from rest_framework.generics import ListAPIView

from apps.access.models import User
from apps.common.views.api import AppAPIView
from apps.meta.models import (
    OnboardingAreaOfInterest,
    OnboardingHighestEducation,
    OnboardingLevel,
)

from ...common.serializers import get_read_serializer
from apps.learning.models import Category, Skill
from ...common.serializers import AppWriteOnlyModelSerializer

class OnboardingMetaAPIView(ListAPIView, AppAPIView):
    """Provides meta-data for highest education and area of interest."""

    def get(self, request, *args, **kwargs):
        data = {
            "onboarding_level": get_read_serializer(
                OnboardingLevel, meta_fields=['id', 'uuid', 'identity']
            )(OnboardingLevel.objects.all(), many=True).data,
            "highest_education": get_read_serializer(
                OnboardingHighestEducation, meta_fields=['id', 'uuid', 'identity']
            )(OnboardingHighestEducation.objects.all(), many=True).data,
            "area_of_interest": get_read_serializer(
                Skill, meta_fields=['id', 'uuid', 'identity']
            )(Skill.objects.filter(is_archived=False), many=True).data,
        }
        return self.send_response(data=data)


class OnBoardingLevelStepOneAPIView(AppAPIView):
    """
    View used to add user onboarding level select details like (I am beginner)
    into the user's data. This works after signed up.
    """

    class _Serializer(serializers.ModelSerializer):
        class Meta:
            model = User
            fields = ["onboarding_level"]

    serializer_class = _Serializer

    def post(self, request):
        serializer = self._Serializer(self.get_user(), data=request.data)
        if serializer.is_valid():
            serializer.save()
            return self.send_response()
        return self.send_error_response(serializer.errors)


# class OnBoardingTechnologyStepTwoAPIView(AppAPIView):
#     """
#     View used to add user onboarding area of interests and higher education details
#     into the users data. This works after signed up.
#     """

#     class _Serializer(serializers.ModelSerializer):
#         class Meta:
#             model = User
#             fields = [
#                 "onboarding_highest_education",
#                 "onboarding_area_of_interests",
#             ]

#     def post(self, request):
#         serializer = self._Serializer(self.get_user(), data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return self.send_response()
#         return self.send_error_response(serializer.errors)


class OnBoardingTechnologyStepTwoAPIView(AppAPIView):
    """
    View used to add user onboarding area of interests and higher education details
    into the users data. This works after signed up.
    """
    class _Serializer(AppWriteOnlyModelSerializer):
        onboarding_area_of_interests = serializers.PrimaryKeyRelatedField(
            queryset=Skill.objects.filter(is_archived=False),
            many=True,
            required=False
        )
        class Meta(AppWriteOnlyModelSerializer.Meta):
            model = User
            fields = [
                "onboarding_highest_education",
                "onboarding_area_of_interests",
            ]

        def update(self, instance, validated_data):
            # Remove the many-to-many field data from the validated data
            area_of_interests = validated_data.pop("onboarding_area_of_interests", [])

            # Call the parent update method to save other fields
            instance = super().update(instance, validated_data)

            # Clear existing many-to-many relationships and add the new ones
            instance.onboarding_area_of_interests.clear()
            instance.onboarding_area_of_interests.add(*area_of_interests)

            return instance

    serializer_class = _Serializer
    
    def post(self, *args, **kwargs):
        serializer = self.get_valid_serializer(instance=self.get_user())
        serializer.save()
        return self.send_response()