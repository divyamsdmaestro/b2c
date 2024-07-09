from rest_framework import serializers
from rest_framework.generics import RetrieveAPIView

from apps.access.models import User
from apps.common.views.api import AppAPIView
from apps.meta.models import FontStyle, SocialPlatform, UserSocialMediaHandle

from ...common.serializers import (
    AppReadOnlyModelSerializer,
    AppWriteOnlyModelSerializer,
)
from ...common.serializers import get_app_read_only_serializer as read_serializer


class UserPrivacyEditMetaAPIView(AppAPIView):
    """Provides meta-data for the `UserPrivacyEditAPIView` edit page."""

    def get(self, request, *args, **kwargs):
        data = {
            "fonts": read_serializer(FontStyle, meta_fields="__all__")(
                FontStyle.objects.all(), many=True
            ).data,
            "social_platform": read_serializer(SocialPlatform, meta_fields="__all__")(
                SocialPlatform.objects.all(), many=True
            ).data,
        }

        return self.send_response(data=data)


class UserPrivacyEditAPIView(AppAPIView):
    """View used to update privacy setting for a user."""

    class _Serializer(AppWriteOnlyModelSerializer):
        """Handle input data."""

        class _SocialHandleSerializer(AppWriteOnlyModelSerializer):
            class Meta(AppWriteOnlyModelSerializer.Meta):
                model = UserSocialMediaHandle
                fields = ["platform", "link"]

        social_handles = _SocialHandleSerializer(many=True, allow_empty=False)

        class Meta(AppWriteOnlyModelSerializer.Meta):
            fields = [
                "enable_font_style",
                "font_style",
                "enable_education",
                "enable_address",
                "enable_profile_picture",
                "enable_pause_notification",
                "enable_autoplay_video",
                "enable_social_handles",
                "social_handles",
            ]
            model = User

        def update(self, instance, validated_data):
            social_handles = validated_data.pop("social_handles", [])

            instance = super().update(instance=instance, validated_data=validated_data)

            # M2M fields
            instance.social_handles.clear()
            for handle in social_handles:
                handle_instance, _ = UserSocialMediaHandle.objects.get_or_create(
                    **handle
                )
                instance.social_handles.add(handle_instance)

            return instance

    serializer_class = _Serializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_valid_serializer(instance=self.get_user())
        serializer.save()
        return self.send_response()


class UserPrivacyDetailAPIView(RetrieveAPIView, AppAPIView):
    """View used to get privacy setting details of a user."""

    queryset = User.objects.prefetch_related("social_handles").select_related(
        "font_style"
    )

    def get_object(self):
        return self.get_authenticated_user()

    def get_serializer_class(self):
        class _SocialHandleSerializer(AppReadOnlyModelSerializer):
            platform = serializers.SerializerMethodField()

            def get_platform(self, obj):
                return obj.platform.identity

            class Meta(AppReadOnlyModelSerializer.Meta):
                model = UserSocialMediaHandle
                fields = ["platform", "link", "uuid"]

        return read_serializer(
            meta_model=User,
            meta_fields=[
                "id",
                "uuid",
                "enable_education",
                "enable_address",
                "enable_profile_picture",
                "enable_social_handles",
                "enable_pause_notification",
                "enable_font_style",
                "enable_autoplay_video",
                "font_style",
                "social_handles",
            ],
            init_fields_config={
                "social_handles": _SocialHandleSerializer(many=True),
                "font_style": read_serializer(
                    meta_model=FontStyle, meta_fields=["uuid", "identity"]
                )(),
            },
        )
