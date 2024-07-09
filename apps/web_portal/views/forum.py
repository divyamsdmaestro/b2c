from django.db import models
from apps.cms.serializers import PollOptionsHandleSerializer, PostSerializer, UserProfileSerializer, ZoneAppliedListSerializer, ZoneSerializer
from rest_framework import serializers
from rest_framework.generics import ListAPIView, RetrieveAPIView
from apps.common.views.api.generic import AbstractLookUpFieldMixin
from apps.common.views.api import AppAPIView
from apps.common.views.api.base import NonAuthenticatedAPIMixin
from ...common.serializers import get_app_read_only_serializer as read_serializer
from ...common.serializers import (
    AppWriteOnlyModelSerializer,
    AppReadOnlyModelSerializer
)
from apps.forums.models import (
    Forum,
    Post,
    PostReply,
    PostComment,
    PostLike,
    PostType,
    PostPollOptionClick,
    PostPollOption,
    PostReport,
    Zone,
    ZoneJoin,
    ZoneImage,
    ZoneType,
    PostImage,
    SubjectivePostImage
)
from django_filters.rest_framework import DjangoFilterBackend
from apps.common.pagination import AppPagination
from rest_framework.filters import SearchFilter
from datetime import date
from django.db.models import Q
from django.contrib.auth.models import AnonymousUser
from apps.hackathons.models import hackathon as hackathon_models
from apps.cms.serializers import HackathonListSerializer
from apps.web_portal.serializers.webinar import WebinarSerializer, WebinarFilter
from apps.webinars.models import Webinar
from apps.blogs.models import Blog, BlogImage
from apps.learning.models import Category
from datetime import datetime
from apps.access.models import InstitutionUserGroupDetail
today = datetime.now().date()

class ZonePageAPIView(NonAuthenticatedAPIMixin,ListAPIView, AppAPIView):
    """Sends out data for the zone Listing Page."""

    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = "__all__"
    search_fields = ["identity"]
    pagination_class = AppPagination
    serializer_class = ZoneSerializer

    def get_queryset(self):
        qs = Zone.objects.filter(zone_type__identity__icontains="public")
        auth_user = self.get_authenticated_user()
        if auth_user:
            if auth_user.user_role and auth_user.user_role.identity == "Student":
                user_group = InstitutionUserGroupDetail.objects.filter(user__id__icontains=auth_user.id)
                if user_group:
                    qs = Zone.objects.filter(assign_members__in=user_group)
                else:
                    qs = Zone.objects.none()
            elif auth_user.user_role and auth_user.user_role.identity == "Learner":
                user_group = InstitutionUserGroupDetail.objects.filter(user__id__icontains=auth_user.id)
                if user_group:
                    qs = Zone.objects.filter(Q(assign_members__in=user_group) | Q(zone_type__identity__icontains="public")).distinct()

        return qs
    
class ZonePageRecommentationAPIView(NonAuthenticatedAPIMixin, ListAPIView, AppAPIView):
    """Zone Recommandation page."""

    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = "__all__"
    search_fields = ["identity"]
    pagination_class = AppPagination
    serializer_class = ZoneSerializer

    def get_queryset(self):
        qs = Zone.objects.none()
        auth_user = self.get_authenticated_user()
        if auth_user:
            user_group = InstitutionUserGroupDetail.objects.filter(user__id__icontains=auth_user.id)
            if user_group:
                qs = Zone.objects.filter(Q(assign_members__in=user_group) | Q(zone_type__identity__icontains="public"), skills__in=auth_user.onboarding_area_of_interests.values_list("id", flat=True)).distinct()[:6]
            else:
                qs = Zone.objects.filter(zone_type__identity__icontains="public", skills__in=auth_user.onboarding_area_of_interests.values_list("id", flat=True)).distinct()[:6]

        return qs

class ZoneJoinAPIView(AppAPIView):

    def post(self, *args, **kwargs):

        uuid = kwargs["uuid"]
        user = self.get_user()

        zone = Zone.objects.get_or_none(uuid=uuid)
        if zone and not ZoneJoin.objects.filter(zone=zone, created_by=user).exists():
            ZoneJoin.objects.create(zone=zone, created_by=user)

        return self.send_response()
    
class ZoneJoinedListAPIView(ListAPIView, AppAPIView):
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = "__all__"
    search_fields = ["identity"]
    pagination_class = AppPagination
    serializer_class = ZoneAppliedListSerializer

    def get_queryset(self, *args, **kwargs):
        user = self.get_user()
        return ZoneJoin.objects.filter(created_by=user)


    
class ForumPostCreateAPIView(AppAPIView):
    """View used to create forum posts by users"""

    class _Serializer(AppWriteOnlyModelSerializer):
        """Handle input data."""

        poll_options = PollOptionsHandleSerializer(many=True, allow_empty=False, required=False)
        # post_type = read_serializer(PostType, meta_fields=["id","uuid","identity"])(
        #     PostType.objects.all()
        # )

        class Meta(AppWriteOnlyModelSerializer.Meta):
            fields = ["post_type", "identity", "description", "post_attachment", "tags", "enable_end_time", "enable_hide_discussion", "poll_options","image", "subjective_image", "subjective_description"]
            model = Post

        def create(self, validated_data):

            poll_options_data = validated_data.pop('poll_options', None)
            post = super().create(validated_data)

            if poll_options_data:
                for poll_options in poll_options_data:
                    options = PostPollOption.objects.create(post=post, **poll_options)
                    post.poll_options.add(options)

            return post

    serializer_class = _Serializer

    def post(self, request, *args, **kwargs):
        forum = Forum.objects.get(id=kwargs['forum_id'])
        serializer = self.get_valid_serializer()
        if serializer.is_valid():
            serializer.save(forum=forum)  # set forum here
            return self.send_response(serializer.data)
        return self.send_error_response(serializer.errors)

class ForumPostEditAPIView(AppAPIView):
    """View used to edit Forum posts by users"""

    class _Serializer(AppWriteOnlyModelSerializer):
        """Handle input data."""

        poll_options = PollOptionsHandleSerializer(many=True, required=False)

        class Meta(AppWriteOnlyModelSerializer.Meta):
            fields = ["post_type", "identity", "description", "post_attachment", "tags", "poll_options", "enable_end_time", "start_date", "end_date", "enable_hide_discussion","subjective_description"]
            model = Post

        def update(self, instance, validated_data):
            poll_options_data = validated_data.pop("poll_options", [])
            instance = super().update(validated_data=validated_data, instance=instance)

            # M2M fields
            if poll_options_data:
                instance.poll_options.clear()
                for data in poll_options_data:
                    poll_options = PostPollOption.objects.filter(**data)
                    if poll_options.exists():
                        poll_option = poll_options.first()
                    else:
                        poll_option = PostPollOption.objects.create(**data)
                    instance.poll_options.add(poll_option)
            return instance

    serializer_class = _Serializer

    def post(self, request, *args, **kwargs):
        post_id = kwargs['post_id']
        post = Post.objects.get(id=post_id)
        user = self.get_user()
        if post.created_by == user:
            serializer = self.get_valid_serializer(instance=post)
            serializer.save()
            return self.send_response()
        return self.send_error_response()

class ForumPostEditMetaAPIView(RetrieveAPIView, AppAPIView):
    class _Serializer(AppReadOnlyModelSerializer):

        poll_options = read_serializer(PostPollOption, meta_fields=["id","uuid","identity"])(
            PostPollOption.objects.all(),many=True
        )
        post_type = read_serializer(PostType, meta_fields=["id","uuid","identity"])(
            PostType.objects.all()
        )

        image = read_serializer(PostImage, meta_fields=["id","uuid","file"])(PostImage.objects.all())

        subjective_image = read_serializer(SubjectivePostImage, meta_fields=["id","uuid","file"])(SubjectivePostImage.objects.all())

        class Meta(AppReadOnlyModelSerializer.Meta):
            model = Post
            fields = [
                "post_type",
                "identity",
                "description",
                "tags",
                "image",
                "poll_options",
                "post_attachment",
                "enable_end_time",
                "start_date",
                "end_date",
                "enable_hide_discussion",
                "subjective_image", 
                "subjective_description",
                "created",
            ]
    lookup_field = "id"
    serializer_class = _Serializer
    queryset = Post.objects.all()

class ZoneDetailAPIView(
    AbstractLookUpFieldMixin, RetrieveAPIView, AppAPIView
):
    """
    This view provides an endpoint to access zone in detail along with
    expanded related views.
    """

    serializer_class = ZoneSerializer
    queryset = Zone.objects.all()

class ForumPostListAPIView(ListAPIView, AppAPIView):
    """Sends out data for the Forum Post Listing Page."""

    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = "__all__"
    search_fields = ["identity"]
    pagination_class = AppPagination
    serializer_class = PostSerializer

    def get_queryset(self, *args, **kwargs):
        forum = Forum.objects.get(id=self.kwargs['forum_id'])
        reported_posts = PostReport.objects.filter(post__forum=forum, created_by=self.get_user(), is_reported=True)
        reported_post_ids = reported_posts.values_list('post__id', flat=True)
        return Post.objects.filter(forum=forum).filter(
            Q(enable_end_time=False) | Q(enable_end_time=True, end_date__gt=date.today())
            ).exclude(id__in=reported_post_ids).order_by('-created')

class ForumPostDeleteAPIView(AppAPIView):
    """ View to delete the forum post"""

    def delete(self, request, *args, **kwargs):
        user = self.get_user()
        post = Post.objects.get(id=kwargs['post_id'])
        if post.created_by == user:
            post.delete()
            return self.send_response()
        return self.send_error_response()
    
class ForumPostLikeAPIView(AppAPIView):
    """ View to like the forum post"""

    def post(self, request, *args, **kwargs):
        post = Post.objects.get(id=kwargs['post_id'])
        user = self.get_user()

        post_like, created = PostLike.objects.get_or_create(post=post, created_by=user)
        if created:
            post_like.is_liked = True
        else:
            post_like.is_liked = not post_like.is_liked
        post_like.save()

        return self.send_response()

class ForumPostCommentListAPIView(ListAPIView, AppAPIView):
    """List down forums Posts comments to the user. This is a read only view."""

    class _Serializer(AppReadOnlyModelSerializer):
        """Handle input data."""

        replies_count = serializers.SerializerMethodField()
        is_my_comment = serializers.SerializerMethodField()
        created_by = UserProfileSerializer()

        class Meta(AppReadOnlyModelSerializer.Meta):
            fields = ["id","uuid","identity","created","modified","replies_count","created_by","is_my_comment"]
            model = PostComment

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
        return PostComment.objects.filter(post_id=self.kwargs['post_id'])
    

class ForumPostCommentCreateAPIView(AppAPIView):
    """view used to create Forum post comment by user"""

    class _Serializer(AppWriteOnlyModelSerializer):
        """Handle input data."""

        class Meta(AppWriteOnlyModelSerializer.Meta):
            fields = [ "identity" ]
            model = PostComment

    serializer_class = _Serializer

    def post(self, request, *args, **kwargs):
        post = Post.objects.get(id=kwargs['post_id'])
        serializer = self.get_valid_serializer()
        serializer.is_valid(raise_exception=True)
        serializer.save(post=post)  # set post here
        return self.send_response()

class ForumPostCommentEditAPIView(AppAPIView):
    """view used to Edit Forum post comment by user"""

    class _Serializer(AppWriteOnlyModelSerializer):
        """Handle input data."""

        class Meta(AppWriteOnlyModelSerializer.Meta):
            fields = [ "identity" ]
            model = PostComment

    serializer_class = _Serializer

    def post(self, request, *args, **kwargs):
        post_comment = PostComment.objects.get(id=kwargs['comment_id'])
        if post_comment.created_by == self.get_user():
            serializer = self.get_valid_serializer(instance=post_comment)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return self.send_response()
        return self.send_error_response()

class ForumPostCommentDeleteAPIView(AppAPIView):
    """View to delete the forum post comments"""

    def delete(self, request, *args, **kwargs):
        user = self.get_user()
        post_comment = PostComment.objects.get(id=kwargs['comment_id'])
        if post_comment.created_by == user:
            post_comment.replies.all().delete()
            post_comment.delete()
            return self.send_response()
        return self.send_error_response()

class ForumPostReplyListAPIView(ListAPIView, AppAPIView):
    """List down forums Posts comments reply to the user. This is a read only view."""

    class _Serializer(AppReadOnlyModelSerializer):
        """Handle input data."""

        created_by = UserProfileSerializer()
        is_my_reply = serializers.SerializerMethodField()
        class Meta(AppReadOnlyModelSerializer.Meta):
            fields = ["id","uuid","identity","created","modified","created_by","is_my_reply"]
            model = PostReply

        def get_is_my_reply(self, obj):
            user = self.get_user()
            if isinstance(user, AnonymousUser) or user == None:
                return False
            else:
                return True if obj.created_by == user else False

    serializer_class = _Serializer

    def get_queryset(self):
        post_comment = PostComment.objects.get(id=self.kwargs['comment_id'])
        return post_comment.replies.all()

class ForumPostReplyCreateAPIView(AppAPIView):
    """view used to create Forum post comment reply by user"""

    class _Serializer(AppWriteOnlyModelSerializer):
        """Handle input data."""

        class Meta(AppWriteOnlyModelSerializer.Meta):
            fields = [ "identity" ]
            model = PostReply

    serializer_class = _Serializer

    def post(self, request, *args, **kwargs):
        post_comment = PostComment.objects.get(id=kwargs['comment_id'])
        serializer = self.get_valid_serializer()
        serializer.is_valid(raise_exception=True)
        comment_reply = serializer.save(comment=post_comment)
        post_comment.replies.add(comment_reply)
        post_comment.save()
        return self.send_response()

class ForumPostReplyEditAPIView(AppAPIView):
    """view used to Edit Forum post comment reply by user"""

    class _Serializer(AppWriteOnlyModelSerializer):
        """Handle input data."""

        class Meta(AppWriteOnlyModelSerializer.Meta):
            fields = [ "identity" ]
            model = PostReply

    serializer_class = _Serializer

    def post(self, request, *args, **kwargs):
        post_comment_reply = PostReply.objects.get(id=kwargs['reply_id'])
        if post_comment_reply.created_by == self.get_user():
            serializer = self.get_valid_serializer(instance=post_comment_reply)
            serializer.is_valid(raise_exception=True)
            serializer.save()
        return self.send_response()

class ForumPostReplyDeleteAPIView(AppAPIView):
    """View to delete the forum post comment replies"""

    def delete(self, request, *args, **kwargs):
        user = self.get_user()
        post_comment = PostComment.objects.get(id=kwargs['comment_id'])
        reply = PostReply.objects.get(id=kwargs['reply_id'])
        if reply.created_by == user:
            post_comment.replies.remove(reply)
            reply.delete()
            return self.send_response()
        return self.send_error_response()
    
class PostPollOptionClickAPIView(AppAPIView):
    """View to handle the forum poll options in poll based posts"""

    def post(self, request, *args, **kwargs):
        post = Post.objects.get(id=self.kwargs['post_id'])
        option = PostPollOption.objects.get(id=self.kwargs['poll_option_id'])
        user = self.get_user()
        # Check if the user already clicked any option before
        existing_click = PostPollOptionClick.objects.filter(
            post=post,
            created_by=user
        ).first()
        if existing_click:
            # different option, update the clicked count
            if existing_click.poll_option != option:
                existing_option = existing_click.poll_option
                existing_option.clicked_count -= 1
                existing_option.save()

                option.clicked_count += 1
                option.save()

                existing_click.poll_option = option
                existing_click.save()
            else:
                # same option again, decrease the clicked count
                option.clicked_count -= 1
                option.save()
                existing_click.delete()
        else:
            # not clicked any option, update the clicked count
            option.clicked_count += 1
            option.save()

            PostPollOptionClick.objects.create(
                post=post,
                poll_option=option,
                created_by=user
            )
        return self.send_response()

class ForumPostReportAPIView(AppAPIView):
    """ View to like the forum post report"""

    def post(self, request, *args, **kwargs):
        post = Post.objects.get(id=kwargs['post_id'])
        user = self.get_user()

        post_reported, created = PostReport.objects.get_or_create(post=post, created_by=user)
        if created:
            post_reported.is_reported = True
        else:
            post_reported.is_reported = not post_reported.is_reported
        post_reported.save()

        return self.send_response()

class ZoneRetrieveAPIView(
    AbstractLookUpFieldMixin, RetrieveAPIView, AppAPIView
):
    """
    This view provides an endpoint to access zone in detail without forum detail.
    """
    class _Serializer(AppReadOnlyModelSerializer):
        """This serializer contains configuration for Zone."""

        image = read_serializer(ZoneImage, meta_fields=["id","uuid","file"])(
            ZoneImage.objects.all()
        )
        zone_type = read_serializer(ZoneType, meta_fields=["id","uuid","identity"])(
            ZoneType.objects.all()
        )
        is_joined = serializers.SerializerMethodField()

        class Meta:
            model = Zone
            fields = "__all__"

        def get_is_joined(self, obj):
            """This function used to get course is already in cart or not"""
            user = self.get_user()
            if isinstance(user, AnonymousUser) or user == None:
                return False
            else:
                is_joined = ZoneJoin.objects.filter(
                    zone=obj.id, created_by=user
                ).exists()
                return is_joined

    serializer_class = _Serializer
    queryset = Zone.objects.all()

class ZoneHackathonListAPIView(AbstractLookUpFieldMixin, ListAPIView, AppAPIView):

    serializer_class = HackathonListSerializer
    filter_backends = [SearchFilter]
    search_fields = ['identity']
    pagination_class = AppPagination

    def get_queryset(self):
        return hackathon_models.Hackathon.objects.filter(zone__uuid=self.kwargs['uuid'],start_date__gte=today)
    
class ZoneWebinarListAPIView(AbstractLookUpFieldMixin,ListAPIView, AppAPIView):
    """Sends out data for the webinar Listing Page."""

    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_class = WebinarFilter
    search_fields = ["identity"]
    pagination_class = AppPagination
    serializer_class = WebinarSerializer

    def get_queryset(self):
        return Webinar.objects.filter(zone__uuid=self.kwargs['uuid'],start_date__gte=today)

class ZoneBlogListAPIView(AbstractLookUpFieldMixin,ListAPIView, AppAPIView):
    """Sends out data for the Blog Listing Page."""

    class _Serializer(AppReadOnlyModelSerializer):
        """Handle input data."""
        image = read_serializer(BlogImage,meta_fields=['id', 'uuid', 'file'])(BlogImage.objects.all())
        category = read_serializer(Category,meta_fields=['id', 'uuid', 'identity'])()
        created_by = UserProfileSerializer()

        class Meta(AppReadOnlyModelSerializer.Meta):
            fields = ['id', 'uuid', 'image', 'identity', 'description','created', 'created_by','category']
            model = Blog

    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = "__all__"
    search_fields = ["identity"]
    pagination_class = AppPagination
    queryset = Blog.objects.filter(status="active")
    serializer_class = _Serializer

    def get_queryset(self):
        return Blog.objects.filter(status="active",zone__uuid=self.kwargs['uuid'])
