from django.db import models
from apps.learning.models import Category
from rest_framework.generics import RetrieveAPIView, ListAPIView
from apps.common.views.api.base import AppAPIView
from apps.blogs.models import Blog, BlogImage, BlogLike, BlogComment, BlogCommentReply

from rest_framework import serializers
from ...common.serializers import get_app_read_only_serializer as read_serializer
from ...common.serializers import (
    AppReadOnlyModelSerializer
)
from django.contrib.auth.models import AnonymousUser
from apps.cms.serializers import UserProfileSerializer

class BlogDetailAPIView(RetrieveAPIView, AppAPIView):
    """
    This APIView gives Blog details.
    """
    class _Serializer(AppReadOnlyModelSerializer):
        """This serializer contains configuration for Blog."""

        category = read_serializer(Category, meta_fields=["id","uuid","identity"])(
            Category.objects.all()
        )
        image = read_serializer(BlogImage, meta_fields="__all__")(BlogImage.objects.all())
        created_by = UserProfileSerializer()
        likes_count = serializers.SerializerMethodField()
        comments_count = serializers.SerializerMethodField()
        is_liked = serializers.SerializerMethodField()

        class Meta(AppReadOnlyModelSerializer.Meta):
            fields = "__all__"
            model = Blog

        def get_likes_count(self, obj):
            return obj.get_likes_count()

        def get_comments_count(self, obj):
            return obj.get_comments_count()
        
        def get_is_liked(self, obj):
            user = self.get_user()
            """This function used to get Blog is already liked or not"""
            if isinstance(user, AnonymousUser) or user == None:
                return False
            else:
                is_liked = BlogLike.objects.filter(
                    is_liked=True, created_by=user,blog=obj
                ).exists()
                return is_liked

    lookup_field = "id"
    serializer_class = _Serializer
    queryset = Blog.objects.all()

class BlogLikeAPIView(AppAPIView):
    """ View to like the blog"""

    def post(self, request, *args, **kwargs):
        blog = Blog.objects.get(id=kwargs['id'])
        user = self.get_user()

        blog_like, created = BlogLike.objects.get_or_create(blog=blog, created_by=user)
        if created:
            blog_like.is_liked = True
        else:
            blog_like.is_liked = not blog_like.is_liked
        blog_like.save()
        return self.send_response()
    
class BlogCommentListAPIView(ListAPIView, AppAPIView):

    class _Serializer(AppReadOnlyModelSerializer):
        """Handle input data."""
        replies_count = serializers.SerializerMethodField()
        is_my_comment = serializers.SerializerMethodField()
        created_by = UserProfileSerializer()

        class Meta(AppReadOnlyModelSerializer.Meta):
            fields = ["id","uuid","identity","modified","replies_count","created_by","is_my_comment" ]
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
        return BlogComment.objects.filter(blog__id=self.kwargs['id'])
    
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
    
class BlogArchieveAPIView(AppAPIView):
    """ View to archieve the blog"""

    def post(self, request, *args, **kwargs):
        blog = Blog.objects.get(uuid=kwargs['uuid'])
        blog.status = "archieve"
        blog.save()
        return self.send_response()
    
class BlogApproveAPIView(AppAPIView):
    """ View to approve the blog"""

    def post(self, request, *args, **kwargs):
        blog = Blog.objects.get(uuid=kwargs['uuid'])
        blog.status = "active"
        blog.save()
        return self.send_response()
    
class BlogDeclineAPIView(AppAPIView):
    """ View to decline the blog"""

    def post(self, request, *args, **kwargs):
        blog = Blog.objects.get(uuid=kwargs['uuid'])
        blog.status = "inactive"
        blog.save()
        return self.send_response()