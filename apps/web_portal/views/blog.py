from django.db import models
from rest_framework import serializers
from rest_framework.generics import ListAPIView, RetrieveAPIView
from apps.common.views.api.generic import AbstractLookUpFieldMixin
from apps.common.views.api import AppAPIView
from apps.common.views.api.base import NonAuthenticatedAPIMixin
from ...common.serializers import (
    get_app_read_only_serializer as read_serializer,
    AppWriteOnlyModelSerializer,
    AppReadOnlyModelSerializer
)
from django_filters.rest_framework import DjangoFilterBackend
from apps.common.pagination import AppPagination
from rest_framework.filters import SearchFilter
from django.contrib.auth.models import AnonymousUser

from apps.blogs.models import Blog,BlogComment,BlogCommentReply,BlogLike, BlogImage
from apps.learning.models import Category
from apps.cms.serializers import UserProfileSerializer
from apps.forums.models import Zone

class BlogCreateAPIView(AppAPIView):
    """View used to create Blog by users"""

    class _Serializer(AppWriteOnlyModelSerializer):
        """Handle input data."""
        class Meta(AppWriteOnlyModelSerializer.Meta):
            model = Blog
            fields = [
            "identity",
            "description",
            "hash_tags",
            "image",
            "category",
            "zone",
            ]

    serializer_class = _Serializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_valid_serializer()
        if serializer.is_valid():
            serializer.save(status="pending_approval")
            return self.send_response(serializer.data)
        return self.send_error_response(serializer.errors)

class BlogEditAPIView(AppAPIView):
    """View used to edit Blog by users"""

    class _Serializer(AppWriteOnlyModelSerializer):
        """Handle input data."""
        class Meta(AppWriteOnlyModelSerializer.Meta):
            model = Blog
            fields = [
            "identity",
            "description",
            "hash_tags",
            "image",
            "category",
            "zone",
            ]

    serializer_class = _Serializer

    def post(self, request, *args, **kwargs):
        blog_uuid = kwargs['uuid']
        blog = Blog.objects.get(uuid=blog_uuid)
        user = self.get_user()
        if blog.created_by == user:
            serializer = self.get_valid_serializer(instance=blog)
            serializer.save()
            return self.send_response()
        return self.send_error_response()

class BlogEditMetaAPIView(RetrieveAPIView, AppAPIView):

    class _Serializer(AppReadOnlyModelSerializer):
        category = read_serializer(Category,meta_fields=['id', 'uuid', 'identity'])()
        zone = read_serializer(Zone,meta_fields=['id', 'uuid', 'identity'])()
        class Meta(AppReadOnlyModelSerializer.Meta):
            model = Blog
            fields = [
            "identity",
            "description",
            "hash_tags",
            "image",
            "status",
            "category",
            "zone",
            ]

    lookup_field = "uuid"
    serializer_class = _Serializer
    queryset = Blog.objects.all()

class BlogDeleteAPIView(AppAPIView):
    """ View to delete the Blog"""

    def delete(self, request, *args, **kwargs):
        user = self.get_user()
        blog = Blog.objects.get(uuid=kwargs['uuid'])
        if blog.created_by == user:
            blog.delete()
            return self.send_response()
        return self.send_error_response()

class BlogListAPIView(NonAuthenticatedAPIMixin,ListAPIView, AppAPIView):
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

class BlogDetailAPIView(
    AbstractLookUpFieldMixin, RetrieveAPIView, AppAPIView
):
    """
    This view provides an endpoint to access Blog in detail along with
    expanded related views.
    """
    class _Serializer(AppReadOnlyModelSerializer):
        """This serializer contains configuration for Post."""

        image = read_serializer(BlogImage,meta_fields=['id', 'uuid', 'file'])(BlogImage.objects.all())
        category = read_serializer(Category,meta_fields=['id', 'uuid', 'identity'])()
        created_by = UserProfileSerializer()
        likes_count = serializers.SerializerMethodField()
        comments_count = serializers.SerializerMethodField()
        is_liked = serializers.SerializerMethodField()
        is_my_post = serializers.SerializerMethodField()

        class Meta(AppReadOnlyModelSerializer.Meta):
            model = Blog
            fields = [
                "id",
                "uuid",
                "image",
                "identity", 
                "description",
                "created",
                "modified",
                "created_by",
                "category",
                "likes_count",
                "comments_count",
                "is_liked",
                "is_my_post"
            ]
        def get_likes_count(self, obj):
            return obj.get_likes_count()

        def get_comments_count(self, obj):
            return obj.get_comments_count()

        def get_is_liked(self, obj):
            """This function used to get blog is already liked or not"""
            user = self.get_user()
            if isinstance(user, AnonymousUser) or user == None:
                return False
            else:
                is_liked = BlogLike.objects.filter(
                    is_liked=True, created_by=user,blog=obj
                ).exists()
                return is_liked

        def get_is_my_post(self, obj):
            user = self.get_user()
            if isinstance(user, AnonymousUser) or user == None:
                return False
            else:
                return True if obj.created_by == user else False

    serializer_class = _Serializer
    queryset = Blog.objects.all()

class BlogLikeAPIView(AppAPIView):
    """ View to like the blog"""

    def post(self, request, *args, **kwargs):
        blog = Blog.objects.get(uuid=kwargs['uuid'])
        user = self.get_user()

        blog_like, created = BlogLike.objects.get_or_create(blog=blog, created_by=user)
        if created:
            blog_like.is_liked = True
        else:
            blog_like.is_liked = not blog_like.is_liked
        blog_like.save()
        return self.send_response()

class BlogCommentListAPIView(ListAPIView, AppAPIView):
    """List down Blog comments to the user. This is a read only view."""

    class _Serializer(AppReadOnlyModelSerializer):
        """Handle input data."""

        replies_count = serializers.SerializerMethodField()
        is_my_comment = serializers.SerializerMethodField()
        created_by = UserProfileSerializer()

        class Meta(AppReadOnlyModelSerializer.Meta):
            fields = ["id","uuid","identity","created","modified","replies_count","created_by","is_my_comment"]
            model = BlogComment

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
        return BlogComment.objects.filter(blog__uuid=self.kwargs['uuid'])
    

class BlogCommentCreateAPIView(AppAPIView):
    """view used to create Blog comment by user"""

    class _Serializer(AppWriteOnlyModelSerializer):
        """Handle input data."""

        class Meta(AppWriteOnlyModelSerializer.Meta):
            fields = [ "identity" ]
            model = BlogComment

    serializer_class = _Serializer

    def post(self, request, *args, **kwargs):
        blog = Blog.objects.get(uuid=kwargs['uuid'])
        serializer = self.get_valid_serializer()
        serializer.is_valid(raise_exception=True)
        serializer.save(blog=blog)  # set post here
        return self.send_response()

class BlogCommentEditAPIView(AppAPIView):
    """view used to Edit Blog comment by user"""

    class _Serializer(AppWriteOnlyModelSerializer):
        """Handle input data."""

        class Meta(AppWriteOnlyModelSerializer.Meta):
            fields = [ "identity" ]
            model = BlogComment

    serializer_class = _Serializer

    def post(self, request, *args, **kwargs):
        blog_comment = BlogComment.objects.get(id=kwargs['comment_id'])
        if blog_comment.created_by == self.get_user():
            serializer = self.get_valid_serializer(instance=blog_comment)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return self.send_response()
        return self.send_error_response()

class BlogCommentDeleteAPIView(AppAPIView):
    """View to delete the Blog comments"""

    def delete(self, request, *args, **kwargs):
        user = self.get_user()
        blog_comment = BlogComment.objects.get(id=kwargs['comment_id'])
        if blog_comment.created_by == user:
            blog_comment.replies.all().delete()
            blog_comment.delete()
            return self.send_response()
        return self.send_error_response()

class BlogCommentReplyListAPIView(ListAPIView, AppAPIView):

    class _Serializer(AppReadOnlyModelSerializer):
        """Handle input data."""
        created_by = UserProfileSerializer()
        is_my_reply = serializers.SerializerMethodField()
        class Meta(AppReadOnlyModelSerializer.Meta):
            fields = ["id","uuid","identity","modified","created_by","is_my_reply" ]
            model = BlogCommentReply

        def get_is_my_reply(self, obj):
            user = self.get_user()
            if isinstance(user, AnonymousUser) or user == None:
                return False
            else:
                return True if obj.created_by == user else False

    serializer_class = _Serializer

    def get_queryset(self):
        return BlogCommentReply.objects.filter(comment__id=self.kwargs["comment_id"])

class BlogCommentReplyCreateAPIView(AppAPIView):
    """view used to create Blog comment reply by user"""

    class _Serializer(AppWriteOnlyModelSerializer):
        """Handle input data."""

        class Meta(AppWriteOnlyModelSerializer.Meta):
            fields = [ "identity" ]
            model = BlogCommentReply

    serializer_class = _Serializer

    def post(self, request, *args, **kwargs):
        blog_comment = BlogComment.objects.get(id=kwargs['comment_id'])
        serializer = self.get_valid_serializer()
        serializer.is_valid(raise_exception=True)
        comment_reply = serializer.save(comment=blog_comment)
        blog_comment.replies.add(comment_reply)
        blog_comment.save()
        return self.send_response()

class BlogCommentReplyEditAPIView(AppAPIView):
    """view used to Edit Blog comment reply by user"""

    class _Serializer(AppWriteOnlyModelSerializer):
        """Handle input data."""

        class Meta(AppWriteOnlyModelSerializer.Meta):
            fields = [ "identity" ]
            model = BlogCommentReply

    serializer_class = _Serializer

    def post(self, request, *args, **kwargs):
        blog_comment_reply = BlogCommentReply.objects.get(id=kwargs['reply_id'])
        if blog_comment_reply.created_by == self.get_user():
            serializer = self.get_valid_serializer(instance=blog_comment_reply)
            serializer.is_valid(raise_exception=True)
            serializer.save()
        return self.send_response()

class BlogCommentReplyDeleteAPIView(AppAPIView):
    """View to delete the Blog comment replies"""

    def delete(self, request, *args, **kwargs):
        user = self.get_user()
        blog_comment = BlogComment.objects.get(id=kwargs['comment_id'])
        reply = BlogCommentReply.objects.get(id=kwargs['reply_id'])
        if reply.created_by == user:
            blog_comment.replies.remove(reply)
            reply.delete()
            return self.send_response()
        return self.send_error_response()
