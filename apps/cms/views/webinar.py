from apps.webinars.models import Webinar, WebinarDiscussion, WebinarDiscussionComment, WebinarDiscussionReply, WebinarRegistration
from apps.common.views.api import AppAPIView
from rest_framework import serializers
from rest_framework.generics import ListAPIView
from ...common.serializers import get_app_read_only_serializer as read_serializer
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter
from apps.common.pagination import AppPagination
from ...common.serializers import AppReadOnlyModelSerializer
from apps.cms.serializers import UserProfileSerializer
from apps.access.models import User

class WebinarDiscussionListAPIView(ListAPIView, AppAPIView):
    """Sends out data for the webinar discussion Listing Page."""

    class _Serializer(AppReadOnlyModelSerializer):
        """This serializer contains configuration for Blog."""
        webinar = read_serializer(Webinar, meta_fields=["id","uuid","identity"])(
            Webinar.objects.all()
        )
        comments_count = serializers.SerializerMethodField()
        class Meta(AppReadOnlyModelSerializer.Meta):
            model = WebinarDiscussion
            fields = [
                "id",
                "uuid",
                "webinar",
                "title",
                "message",
                "comments_count",
                "created",
                "modified",
            ]
        def get_comments_count(self, obj):
            return obj.get_comments_count()

    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = "__all__"
    search_fields = ["title"]
    pagination_class = AppPagination
    serializer_class = _Serializer

    def get_queryset(self, *args, **kwargs):
        return WebinarDiscussion.objects.filter(webinar__id=self.kwargs['id'])

class WebinarRegistrationListAPIViewset(ListAPIView, AppAPIView):
    class _Serializer(AppReadOnlyModelSerializer):
        """Handle input data."""
        webinar = read_serializer(Webinar, meta_fields=["id","uuid","identity", "is_paid_webinar"])(
            Webinar.objects.all()
        )
        user = read_serializer(User, meta_fields=["id","uuid","full_name", "idp_email", "phone_number"])(
            User.objects.all()
        )
        serial_number = serializers.SerializerMethodField()
        class Meta(AppReadOnlyModelSerializer.Meta):
            fields = ["id","uuid","serial_number","webinar","user","created" ]
            model = WebinarRegistration

        def get_serial_number(self, obj):
            """Method to get the serial number for each item."""
            queryset = WebinarRegistration.objects.all().order_by("-created")
            return list(queryset).index(obj) + 1

    pagination_class = AppPagination        
    serializer_class = _Serializer

    def get_queryset(self):
        return WebinarRegistration.objects.all().order_by("-created")
    
class WebinarDiscussionCommentListAPIView(ListAPIView, AppAPIView):
    """List down Webinar Discussion comments to the admin. This is a read only view."""

    class _Serializer(AppReadOnlyModelSerializer):
        """Handle input data."""
        replies_count = serializers.SerializerMethodField()
        created_by = UserProfileSerializer()

        class Meta(AppReadOnlyModelSerializer.Meta):
            fields = ["id","uuid","identity","modified","replies_count","created_by" ]
            model = WebinarDiscussionComment

        def get_replies_count(self, obj):
            return obj.replies_count()

    serializer_class = _Serializer

    def get_queryset(self):
        return WebinarDiscussionComment.objects.filter(webinar_discussion__id=self.kwargs['discussion_id'])
    
class WebinarDiscussionReplyListAPIView(ListAPIView, AppAPIView):
    """List down forums Webinar Discussion comments reply to the admin. This is a read only view."""

    class _Serializer(AppReadOnlyModelSerializer):
        """Handle input data."""
        created_by = UserProfileSerializer()
        class Meta(AppReadOnlyModelSerializer.Meta):
            fields = ["id","uuid","identity","modified","created_by" ]
            model = WebinarDiscussionReply

    serializer_class = _Serializer

    def get_queryset(self):
        return WebinarDiscussionReply.objects.filter(comment_id=self.kwargs["comment_id"])