from django.db import models
from apps.cms.serializers import ForumSerializer, PostSerializer, UserProfileSerializer, ZoneSerializer
from rest_framework.generics import RetrieveAPIView, ListAPIView
from apps.forums.models import Forum, Post, PostComment, PostReply, PostLike, PostPollOptionClick, PostPollOption, Zone, ZoneType
from apps.common.views.api.base import AppAPIView
from ...common.serializers import get_app_read_only_serializer as read_serializer
from apps.access.models import User
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter
from apps.common.pagination import AppPagination
from ...common.serializers import AppReadOnlyModelSerializer
from rest_framework import serializers

class ZoneDetailAPIView(RetrieveAPIView, AppAPIView):
    """
    This APIView gives Zone details.
    """

    lookup_field = "id"
    serializer_class = ZoneSerializer
    queryset = Zone.objects.all()

class ZoneListAPIView(ListAPIView, AppAPIView):
    """Sends out data for the zone Listing Page."""

    class _Serializer(AppReadOnlyModelSerializer):
        """This serializer contains configuration for Zone."""

        no_of_forums = serializers.SerializerMethodField()
        members_count = serializers.SerializerMethodField()
        no_of_posts = serializers.SerializerMethodField()
        status = serializers.SerializerMethodField()
        serial_number = serializers.SerializerMethodField()

        class Meta:
            fields = ["id","uuid","identity","created","no_of_forums","members_count","no_of_posts","status","serial_number"]
            model = Zone

        def get_no_of_forums(self, obj):
            return obj.forums.count()
        def get_members_count(self, obj):
            return obj.assign_members.count()
        def get_no_of_posts(self, obj):
            forums = obj.forums.all()
            total_count = 0
            for forum in forums:
                total_count+=Post.objects.filter(forum=forum).count()
            return total_count
        def get_status(self, obj):
            return "Active" if obj.is_active else "Inactive"
        def get_serial_number(self, obj):
            """Method to get the serial number for each item."""
            queryset = Zone.objects.all()
            return list(queryset).index(obj) + 1

    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = "__all__"
    search_fields = ["identity"]
    pagination_class = AppPagination
    serializer_class = _Serializer
    queryset = Zone.objects.all()

class ForumPostListAPIView(ListAPIView, AppAPIView):
    """Sends out data for the Forum Post Listing Page."""

    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = "__all__"
    search_fields = ["identity"]
    pagination_class = AppPagination
    serializer_class = PostSerializer

    def get_queryset(self, *args, **kwargs):
        
        return Post.objects.filter(forum_id=self.kwargs['forum_id'])

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
    """List down forums Posts comments to the admin. This is a read only view."""

    class _Serializer(AppReadOnlyModelSerializer):
        """Handle input data."""
        replies_count = serializers.SerializerMethodField()
        created_by = UserProfileSerializer()

        class Meta(AppReadOnlyModelSerializer.Meta):
            fields = ["id","uuid","identity","modified","replies_count","created_by" ]
            model = PostComment

        def get_replies_count(self, obj):
            return obj.replies_count()

    serializer_class = _Serializer

    def get_queryset(self):
        return PostComment.objects.filter(post_id=self.kwargs['post_id'])
    
class ForumPostReplyListAPIView(ListAPIView, AppAPIView):
    """List down forums Posts comments reply to the admin. This is a read only view."""

    class _Serializer(AppReadOnlyModelSerializer):
        """Handle input data."""
        created_by = UserProfileSerializer()
        class Meta(AppReadOnlyModelSerializer.Meta):
            fields = ["id","uuid","identity","modified","created_by" ]
            model = PostReply

    serializer_class = _Serializer

    def get_queryset(self):
        return PostReply.objects.filter(comment_id=self.kwargs["comment_id"])

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


class DeleteForumComment(AppAPIView):
    def post(self, request, *args, **kwargs):
        comment = PostComment.objects.get(uuid=kwargs['uuid'])
        comment.delete()
        return self.send_response()
