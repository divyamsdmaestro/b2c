from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.filters import SearchFilter
from rest_framework import serializers
from datetime import datetime
from apps.common.views.api import AppAPIView
from apps.common.views.api.base import NonAuthenticatedAPIMixin
from apps.hackathons.models import hackathon as hackathon_models
from apps.hackathons.models import industry as industry_models
from apps.hackathons.models import round_details as round_models
from apps.cms.serializers import HackathonListSerializer
from apps.my_learnings.models.trackers import UserSkillTracker
from ...common.pagination import AppPagination
from apps.common.views.api.generic import (
    DEFAULT_IDENTITY_DISPLAY_FIELDS,
    AbstractLookUpFieldMixin,
)
from ...common.serializers import get_app_read_only_serializer, get_read_serializer
from apps.learning.models import Skill
from apps.access.models import User
from ...common.serializers import (
    AppWriteOnlyModelSerializer,
    AppReadOnlyModelSerializer
)
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter
from apps.cms.serializers import UserProfileSerializer
from django.contrib.auth.models import AnonymousUser
from django_filters.rest_framework import DjangoFilterBackend
from apps.meta.models import UserProfileImage

today = datetime.now().date()


class HackathonMetaAPIView(NonAuthenticatedAPIMixin, AppAPIView):
    """Provides Meta Data for skills filtering"""

    def get(self, request):
        data = {
            "type":[
                {
                    "identity":"Sponsored"
                },
                {
                    "identity":"Free" 
                }
            ],
            "skills": get_read_serializer(
                Skill,  DEFAULT_IDENTITY_DISPLAY_FIELDS
            )(Skill.objects.filter(is_archived=False), many=True).data,
        }

        return self.send_response(data=data)

class HackathonPageAPIView(NonAuthenticatedAPIMixin, ListAPIView, AppAPIView):
    queryset = hackathon_models.Hackathon.objects.filter(start_date__gte=today)
    serializer_class = HackathonListSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = "__all__"
    search_fields = ['identity']
    pagination_class = AppPagination

    def get_queryset(self):
        queryset = hackathon_models.Hackathon.objects.filter(start_date__gte=today)
        hackathon_type = self.request.query_params.get('type')
        if hackathon_type == "free":
            queryset = queryset.filter(is_free=True)
        elif hackathon_type == "sponsored":
            queryset = queryset.filter(is_free=False)
        
        return queryset

class HackathonDetailAPIView(NonAuthenticatedAPIMixin, AbstractLookUpFieldMixin, RetrieveAPIView, AppAPIView):
    """
    This view provides endpoint to access hackathon in detail along with
    expanded related views.
    """
    serializer_class = HackathonListSerializer
    queryset = hackathon_models.Hackathon.objects.all()

class HackathonJoinMetaAPIView(ListAPIView, AppAPIView):
    """Provides meta-data for industry and skills and join hackathon types."""

    def get(self, request, *args, **kwargs):
        data = {
            # "industry": get_app_read_only_serializer(
            #     industry_models.Industry, meta_fields=['id', 'uuid', 'identity']
            # )(industry_models.Industry.objects.all(), many=True).data,
            # "skills": get_app_read_only_serializer(
            #     Skill, meta_fields=['id', 'uuid', 'identity']
            # )(Skill.objects.all(), many=True).data,
            #  "email_data": get_app_read_only_serializer(
            #     User, meta_fields=['id', 'uuid', 'idp_user_id']
            # )(User.objects.all(), many=True).data,
        }
        return self.send_response(data=data)

class HackathonJoinAPIView(AppAPIView):
    """
    View used to hackathon join form.
    """

    class _Serializer(serializers.ModelSerializer):

        class Meta:
            model = hackathon_models.HackathonParticipant
            fields = ["entity"]

    serializer_class = _Serializer

    def post(self, request, *args, **kwargs):
        user = self.get_user()
        try:
            hackathon = hackathon_models.Hackathon.objects.get(uuid=kwargs['uuid'])
            hackathon_models.HackathonParticipant.objects.filter(created_by=user, entity=hackathon).delete()

            hackathon_models.HackathonParticipant.objects.create(
                created_by=user, entity=hackathon
            )
            return self.send_response()

        except hackathon_models.Hackathon.DoesNotExist:
            return self.send_error_response()


class EnrolledHackathonAPIView(ListAPIView, AppAPIView):
    """
    View to list enrolled hackathon
    """
    class _Serializer(serializers.ModelSerializer):
        class Meta:
            model = hackathon_models.Hackathon
            fields = "__all__"

    serializer_class = _Serializer

    def get_queryset(self):
        user = self.get_user()
        print("user", user)
        enrolled_hackathons = hackathon_models.HackathonParticipant.objects.filter(created_by=user).values_list('entity_id', flat=True)
        print("er", enrolled_hackathons)
        print(hackathon_models.Hackathon.objects.filter(
            id__in=enrolled_hackathons,
            end_date__gt=today
        ))
        return hackathon_models.Hackathon.objects.filter(
            id__in=enrolled_hackathons,
            end_date__gte=today
        )

class CompletedHackathonAPIView(ListAPIView, AppAPIView):
    """
    View to list enrolled hackathon
    """
    class _Serializer(serializers.ModelSerializer):
        class Meta:
            model = hackathon_models.Hackathon
            fields = "__all__"

    serializer_class = _Serializer

    def get_queryset(self):
        user = self.get_user()
        enrolled_hackathons = hackathon_models.HackathonParticipant.objects.filter(created_by=user).values_list('entity_id', flat=True)
        return hackathon_models.Hackathon.objects.filter(
            id__in=enrolled_hackathons,
            end_date__lt=today
        )

class HackathonUpdateListAPIView(ListAPIView, AppAPIView):
    """
    View used to list updates of hackathon.
    """
    serializer_class = get_app_read_only_serializer(
        meta_model=hackathon_models.HackathonUpdates, meta_fields=['id', 'uuid', 'hackathon', 'desc', 'created'],
    )
    
    def get_queryset(self):
        uuid = self.kwargs.get('uuid')
        # Filter the FAQs based on the logged-in user
        return hackathon_models.HackathonUpdates.objects.filter(hackathon__uuid=uuid).order_by('-created')
    
class HackathonSubmissionAPIView(AppAPIView):
    """
    View used to submit the hackathons by user.
    """
    class _Serializer(serializers.ModelSerializer):
        class _HackathonProjectLinksSerializer(AppWriteOnlyModelSerializer):
            class Meta(AppWriteOnlyModelSerializer.Meta):
                model = round_models.HackathonProjectLinks
                fields = ["project_link"]

        project_links = _HackathonProjectLinksSerializer(many=True, allow_empty=False)
        class Meta:
            model = hackathon_models.HackathonSubmission
            fields = ["round", "project_name", "elevator_pitch", "about_project", "built_with", "project_links", "project_media"]
    
        def create(self, validated_data):
            project_links_data = validated_data.pop('project_links')
            submission = hackathon_models.HackathonSubmission.objects.create(**validated_data)
            for link_data in project_links_data:
                round_models.HackathonProjectLinks.objects.create(**link_data)
            return submission
    
    serializer_class = _Serializer

    def post(self, request, *args, **kwargs):
        user = self.get_user()
        hackathon = hackathon_models.Hackathon.objects.get(uuid=kwargs['uuid'])
        serializer = self._Serializer(data=request.data)
        if serializer.is_valid():
            serializer.validated_data['hackathon'] = hackathon
            serializer.save(created_by=user)
            return self.send_response()
        return self.send_error_response(serializer.errors)
    
    # def post(self, request, *args, **kwargs):
    #     hackathon = self.kwargs['uuid']
    #     serializer = self._Serializer(data=request.data)
    #     if serializer.is_valid():
    #         serializer.validated_data['hackathon'] = hackathon
    #         serializer.save()
    #         return self.send_response()
    #     return self.send_error_response(serializer.errors)

class HackathonDiscussionCreateAPIView(AppAPIView):
    """View used to create Hackathon Discussion by users"""

    class _Serializer(AppWriteOnlyModelSerializer):
        """Handle input data."""

        class Meta(AppWriteOnlyModelSerializer.Meta):
            fields = ["title", "message"]
            model = hackathon_models.HackathonDiscussion

    serializer_class = _Serializer

    def post(self, request, *args, **kwargs):
        hackathon = hackathon_models.Hackathon.objects.get(uuid=kwargs['uuid'])
        serializer = self.get_valid_serializer()
        if serializer.is_valid():
            serializer.save(hackathon=hackathon)  # set hackathon here
            return self.send_response(serializer.data)
        return self.send_error_response(serializer.errors)

class HackathonDiscussionEditAPIView(AppAPIView):
    """View used to edit Hackathon Discussion by users"""

    class _Serializer(AppWriteOnlyModelSerializer):
        """Handle input data."""

        class Meta(AppWriteOnlyModelSerializer.Meta):
            fields = ["title", "message"]
            model = hackathon_models.HackathonDiscussion

    serializer_class = _Serializer

    def post(self, request, *args, **kwargs):
        discussion_id = kwargs['discussion_id']
        hackathon_discussion = hackathon_models.HackathonDiscussion.objects.get(id=discussion_id)
        user = self.get_user()
        if hackathon_discussion.created_by == user:
            serializer = self.get_valid_serializer(instance=hackathon_discussion)
            serializer.save()
            return self.send_response()
        return self.send_error_response()
    
class HackathonDiscussionDeleteAPIView(AppAPIView):
    """ View to delete the Hackathon Discussion"""

    def delete(self, request, *args, **kwargs):
        user = self.get_user()
        hackathon_discussion = hackathon_models.HackathonDiscussion.objects.get(id=kwargs['discussion_id'])
        if hackathon_discussion.created_by == user:
            hackathon_discussion.delete()
            return self.send_response()
        return self.send_error_response()

class HackathonDiscussionListAPIView(ListAPIView, AppAPIView):
    """Sends out data for the hackathon discussion Listing Page."""

    class _Serializer(AppReadOnlyModelSerializer):
        """This serializer contains configuration for Blog."""
        hackathon = get_app_read_only_serializer(hackathon_models.Hackathon, meta_fields=["id","uuid","identity"])(
            hackathon_models.Hackathon.objects.all()
        )
        comments_count = serializers.SerializerMethodField()
        is_my_discussion = serializers.SerializerMethodField()
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
                "is_my_discussion"
            ]

        def get_comments_count(self, obj):
            return obj.get_comments_count()

        def get_is_my_discussion(self, obj):
            user = self.get_user()
            if isinstance(user, AnonymousUser) or user == None:
                return False
            else:
                return True if obj.created_by == user else False

    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = "__all__"
    search_fields = ["title"]
    pagination_class = AppPagination
    serializer_class = _Serializer

    def get_queryset(self, *args, **kwargs):
        return hackathon_models.HackathonDiscussion.objects.filter(hackathon__uuid=self.kwargs['uuid'])
    
class HackathonDiscussionCommentCreateAPIView(AppAPIView):
    """view used to create Hackathon Discussion comment by user"""

    class _Serializer(AppWriteOnlyModelSerializer):
        """Handle input data."""

        class Meta(AppWriteOnlyModelSerializer.Meta):
            fields = [ "identity" ]
            model = hackathon_models.HackathonDiscussionComment

    serializer_class = _Serializer

    def post(self, request, *args, **kwargs):
        hackathon_discussion = hackathon_models.HackathonDiscussion.objects.get(id=kwargs['discussion_id'])
        serializer = self.get_valid_serializer()
        serializer.is_valid(raise_exception=True)
        serializer.save(hackathon_discussion=hackathon_discussion)  # set hackathon discussion here
        return self.send_response()

class HackathonDiscussionCommentEditAPIView(AppAPIView):
    """view used to Edit Hackathon Discussion comment by user"""

    class _Serializer(AppWriteOnlyModelSerializer):
        """Handle input data."""

        class Meta(AppWriteOnlyModelSerializer.Meta):
            fields = [ "identity" ]
            model = hackathon_models.HackathonDiscussionComment

    serializer_class = _Serializer

    def post(self, request, *args, **kwargs):
        hackathon_discussion_comment = hackathon_models.HackathonDiscussionComment.objects.get(id=kwargs['comment_id'])
        if hackathon_discussion_comment.created_by == self.get_user():
            serializer = self.get_valid_serializer(instance=hackathon_discussion_comment)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return self.send_response()
        return self.send_error_response()

class HackathonDiscussionCommentDeleteAPIView(AppAPIView):
    """View to delete the Hackathon Discussion comments"""

    def delete(self, request, *args, **kwargs):
        user = self.get_user()
        hackathon_discussion_comment = hackathon_models.HackathonDiscussionComment.objects.get(id=kwargs['comment_id'])
        if hackathon_discussion_comment.created_by == user:
            hackathon_discussion_comment.replies.all().delete()
            hackathon_discussion_comment.delete()
            return self.send_response()
        return self.send_error_response()

class HackathonDiscussionCommentListAPIView(ListAPIView, AppAPIView):
    """List down Hackathon Discussion comments to the admin. This is a read only view."""

    class _Serializer(AppReadOnlyModelSerializer):
        """Handle input data."""
        replies_count = serializers.SerializerMethodField()
        created_by = UserProfileSerializer()
        is_my_comment = serializers.SerializerMethodField()

        class Meta(AppReadOnlyModelSerializer.Meta):
            fields = ["id","uuid","identity","modified","replies_count","created_by","is_my_comment" ]
            model = hackathon_models.HackathonDiscussionComment

        def get_replies_count(self, obj):
            return obj.replies_count()
        
        def get_is_my_comment(self, obj):
            user = self.get_user()
            if isinstance(user, AnonymousUser) or user == None:
                return False
            else:
                return True if obj.created_by == user else False

    serializer_class = _Serializer

    def get_queryset(self):
        return hackathon_models.HackathonDiscussionComment.objects.filter(hackathon_discussion__id=self.kwargs['discussion_id'])
    
class HackathonDiscussionReplyCreateAPIView(AppAPIView):
    """view used to create Hackathon Discussion reply by user"""

    class _Serializer(AppWriteOnlyModelSerializer):
        """Handle input data."""

        class Meta(AppWriteOnlyModelSerializer.Meta):
            fields = [ "identity" ]
            model = hackathon_models.HackathonDiscussionReply

    serializer_class = _Serializer

    def post(self, request, *args, **kwargs):
        hackathon_discussion_comment = hackathon_models.HackathonDiscussionComment.objects.get(id=kwargs['comment_id'])
        serializer = self.get_valid_serializer()
        serializer.is_valid(raise_exception=True)
        comment_reply = serializer.save(comment=hackathon_discussion_comment)
        hackathon_discussion_comment.replies.add(comment_reply)
        hackathon_discussion_comment.save()
        return self.send_response()

class HackathonDiscussionReplyEditAPIView(AppAPIView):
    """view used to Edit Hackathon Discussion reply by user"""

    class _Serializer(AppWriteOnlyModelSerializer):
        """Handle input data."""

        class Meta(AppWriteOnlyModelSerializer.Meta):
            fields = [ "identity" ]
            model = hackathon_models.HackathonDiscussionReply

    serializer_class = _Serializer

    def post(self, request, *args, **kwargs):
        hackathon_discussion_reply = hackathon_models.HackathonDiscussionReply.objects.get(id=kwargs['reply_id'])
        if hackathon_discussion_reply.created_by == self.get_user():
            serializer = self.get_valid_serializer(instance=hackathon_discussion_reply)
            serializer.is_valid(raise_exception=True)
            serializer.save()
        return self.send_response()

class HackathonDiscussionReplyDeleteAPIView(AppAPIView):
    """View to delete the Hackathon Discussion replies"""

    def delete(self, request, *args, **kwargs):
        user = self.get_user()
        hackathon_discussion_comment = hackathon_models.HackathonDiscussionComment.objects.get(id=kwargs['comment_id'])
        reply = hackathon_models.HackathonDiscussionReply.objects.get(id=kwargs['reply_id'])
        if reply.created_by == user:
            hackathon_discussion_comment.replies.remove(reply)
            reply.delete()
            return self.send_response()
        return self.send_error_response()

class HackathonDiscussionReplyListAPIView(ListAPIView, AppAPIView):
    """List down forums Hackathon Discussion comments reply to the admin. This is a read only view."""

    class _Serializer(AppReadOnlyModelSerializer):
        """Handle input data."""
        created_by = UserProfileSerializer()
        is_my_reply = serializers.SerializerMethodField()
        class Meta(AppReadOnlyModelSerializer.Meta):
            fields = ["id","uuid","identity","modified","created_by","is_my_reply" ]
            model = hackathon_models.HackathonDiscussionReply

        def get_is_my_reply(self, obj):
            user = self.get_user()
            if isinstance(user, AnonymousUser) or user == None:
                return False
            else:
                return True if obj.created_by == user else False

    serializer_class = _Serializer

    def get_queryset(self):
        return hackathon_models.HackathonDiscussionReply.objects.filter(comment_id=self.kwargs["comment_id"])


class HackathonParticipantsListAPIView(ListAPIView, AppAPIView):
    class _Serializer(AppReadOnlyModelSerializer):
        skills = serializers.SerializerMethodField()
        profile_image = get_read_serializer(UserProfileImage, ['id', 'uuid', 'file'])
        
        class Meta(AppReadOnlyModelSerializer.Meta):
            fields = ["id","uuid","full_name","skills","profile_image"]
            model = User
        
        def get_skills(self, user):
            completed_skills = UserSkillTracker.objects.filter(
                created_by=user,
                progress=100
            ).values_list('entity__identity', flat=True)

            return list(completed_skills)

    serializer_class = _Serializer

    def get_queryset(self):
        hackathon = hackathon_models.Hackathon.objects.get(uuid=self.kwargs["uuid"])
        hackathon_participants = hackathon_models.HackathonParticipant.objects.filter(entity=hackathon)
        user_ids = hackathon_participants.values_list('created_by', flat=True)
        return User.objects.filter(id__in=user_ids)