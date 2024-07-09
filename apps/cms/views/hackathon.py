from apps.common.views.api import AppAPIView
from rest_framework import serializers
from apps.hackathons.models import hackathon as hackathon_models
from rest_framework.generics import RetrieveAPIView, ListAPIView
from ...common.serializers import get_app_read_only_serializer as read_serializer
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter
from apps.common.pagination import AppPagination
from ...common.serializers import AppReadOnlyModelSerializer
from apps.cms.serializers import UserProfileSerializer

class CreateHackathonUpdate(AppAPIView):
    """
    View used to add user onboarding level select details like (I am beginner)
    into the user's data. This works after signed up.
    """

    class _Serializer(serializers.ModelSerializer):
        class Meta:
            model = hackathon_models.HackathonUpdates
            fields = ["desc"]

    serializer_class = _Serializer

    def post(self, request, *args, **kwargs):
        user=self.get_user()
        hackathon = hackathon_models.Hackathon.objects.get(uuid=kwargs['uuid'])
        serializer = self._Serializer(data=request.data)
        if serializer.is_valid():
            serializer.validated_data['hackathon'] = hackathon
            serializer.save(created_by=user)
            return self.send_response()
        return self.send_error_response(serializer.errors)

class HackathonDiscussionListAPIView(ListAPIView, AppAPIView):
    """Sends out data for the hackathon discussion Listing Page."""

    class _Serializer(AppReadOnlyModelSerializer):
        """This serializer contains configuration for Blog."""
        hackathon = read_serializer(hackathon_models.Hackathon, meta_fields=["id","uuid","identity"])(
            hackathon_models.Hackathon.objects.all()
        )
        comments_count = serializers.SerializerMethodField()
        class Meta(AppReadOnlyModelSerializer.Meta):
            model = hackathon_models.HackathonDiscussion
            fields = [
                "id",
                "uuid",
                "hackathon",
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
        return hackathon_models.HackathonDiscussion.objects.filter(hackathon__id=self.kwargs['id'])
    
class HackathonDiscussionCommentListAPIView(ListAPIView, AppAPIView):
    """List down Hackathon Discussion comments to the admin. This is a read only view."""

    class _Serializer(AppReadOnlyModelSerializer):
        """Handle input data."""
        replies_count = serializers.SerializerMethodField()
        created_by = UserProfileSerializer()

        class Meta(AppReadOnlyModelSerializer.Meta):
            fields = ["id","uuid","identity","modified","replies_count","created_by" ]
            model = hackathon_models.HackathonDiscussionComment

        def get_replies_count(self, obj):
            return obj.replies_count()

    serializer_class = _Serializer

    def get_queryset(self):
        return hackathon_models.HackathonDiscussionComment.objects.filter(hackathon_discussion__id=self.kwargs['discussion_id'])
    
class HackathonDiscussionReplyListAPIView(ListAPIView, AppAPIView):
    """List down forums Hackathon Discussion comments reply to the admin. This is a read only view."""

    class _Serializer(AppReadOnlyModelSerializer):
        """Handle input data."""
        created_by = UserProfileSerializer()
        class Meta(AppReadOnlyModelSerializer.Meta):
            fields = ["id","uuid","identity","modified","created_by" ]
            model = hackathon_models.HackathonDiscussionReply

    serializer_class = _Serializer

    def get_queryset(self):
        return hackathon_models.HackathonDiscussionReply.objects.filter(comment_id=self.kwargs["comment_id"])