from django.db import models
from apps.learning.models import Skill
from apps.forums.models import PostType, PostImage, SubjectivePostImage
from apps.access.models import User, UserRole, InstitutionUserGroupDetail
from rest_framework import serializers
from ...common.serializers import get_app_read_only_serializer as read_serializer
from apps.forums.models import Forum, ForumImage, PostLike, PostPollOptionClick
from ...common.serializers import (
    AppReadOnlyModelSerializer,
    AppWriteOnlyModelSerializer
)
from apps.forums.models import Post, PostPollOption, ZoneType, ZoneJoin, ZoneImage, Zone
from apps.meta.models import UserProfileImage
from django.contrib.auth.models import AnonymousUser
from apps.blogs.models import Blog
from apps.hackathons.models import hackathon as hackathon_models
from apps.webinars.models import Webinar

class UserProfileSerializer(AppReadOnlyModelSerializer):
    profile_image = read_serializer(UserProfileImage, meta_fields="__all__")(UserProfileImage.objects.all())
    user_role = read_serializer(UserRole, meta_fields="__all__")()
    full_name = serializers.SerializerMethodField()
    class Meta(AppReadOnlyModelSerializer.Meta):
        fields = ["id","uuid","full_name","profile_image","user_role"]
        model = User

    def get_full_name(self,obj):
        if obj.last_name and obj.first_name:
            return obj.first_name + " "+ obj.last_name
        return obj.first_name
        
class ForumSerializer(AppReadOnlyModelSerializer):
    """This serializer contains configuration for Forum."""

    image = read_serializer(ForumImage, meta_fields=["id","uuid","file"])(
        ForumImage.objects.all()
    )

    class Meta:
        fields = "__all__"
        model = Forum

class ZoneSerializer(AppReadOnlyModelSerializer):
    """This serializer contains configuration for Zone."""

    assign_members = read_serializer(InstitutionUserGroupDetail, meta_fields=["id","uuid","identity"])(
        InstitutionUserGroupDetail.objects.all(), many=True
    )
    forums = ForumSerializer(many=True)
    skills = read_serializer(Skill, meta_fields=["id","uuid","identity"])(
        Skill.objects.filter(is_archived=False), many=True
    )
    image = read_serializer(ZoneImage, meta_fields=["id","uuid","file"])(
        ZoneImage.objects.all()
    )
    zone_type = read_serializer(ZoneType, meta_fields=["id","uuid","identity"])(
        ZoneType.objects.all()
    )
    is_joined = serializers.SerializerMethodField()
    forums_count = serializers.SerializerMethodField()
    hackathons_count = serializers.SerializerMethodField()
    webinars_count = serializers.SerializerMethodField()
    blogs_count = serializers.SerializerMethodField()
    members_count = serializers.SerializerMethodField()

    class Meta:
        fields = "__all__"
        model = Zone

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

    def get_members_count(self, obj):
        return obj.assign_members.all().count()
    def get_forums_count(self, obj):
        return obj.forums.all().count()
    def get_hackathons_count(self, obj):
        return hackathon_models.Hackathon.objects.filter(zone=obj).count()
    def get_webinars_count(self, obj):
        return Webinar.objects.filter(zone=obj).count()
    def get_blogs_count(self, obj):
        return Blog.objects.filter(zone=obj).count()

class PostSerializer(AppReadOnlyModelSerializer):
    """This serializer contains configuration for Post."""

    poll_options = read_serializer(PostPollOption, meta_fields=["id","uuid","identity","clicked_count"])(
        PostPollOption.objects.all(),many=True
    )
    post_type = read_serializer(PostType, meta_fields=["id","uuid","identity"])(
        PostType.objects.all()
    )
    image = read_serializer(PostImage, meta_fields=["id","uuid","file"])(PostImage.objects.all())

    subjective_image = read_serializer(SubjectivePostImage, meta_fields=["id","uuid","file"])(SubjectivePostImage.objects.all())
    
    created_by = UserProfileSerializer()
    likes_count = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()
    is_poll_option_clicked = serializers.SerializerMethodField()
    is_my_post = serializers.SerializerMethodField()

    class Meta(AppReadOnlyModelSerializer.Meta):
        model = Post
        fields = [
            "id",
            "uuid",
            "post_type",
            "forum",
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
            "likes_count",
            "comments_count",
            "created_by",
            "created",
            "modified",
            "is_liked",
            "is_poll_option_clicked",
            "is_my_post",
            "subjective_image", 
            "subjective_description",
        ]
    def get_likes_count(self, obj):
        return obj.get_likes_count()

    def get_comments_count(self, obj):
        return obj.get_comments_count()

    def get_is_liked(self, obj):
        user = self.get_user()
        """This function used to get post is already liked or not"""
        if isinstance(user, AnonymousUser) or user == None:
            return False
        else:
            is_liked = PostLike.objects.filter(
                is_liked=True, created_by=user,post=obj
            ).exists()
            return is_liked
        
    def get_is_poll_option_clicked(self, obj):
        user = self.get_user()
        """This function used to get post is already liked or not"""
        if isinstance(user, AnonymousUser) or user == None:
            return False
        else:
            is_clicked = PostPollOptionClick.objects.filter(
                created_by=user,post=obj
            ).first()
            return is_clicked.poll_option.id if is_clicked else None

    def get_is_my_post(self, obj):
        user = self.get_user()
        if isinstance(user, AnonymousUser) or user == None:
            return 'False'
        else:
            return 'True' if obj.created_by == user else 'False'

class ForumCreateSerializer(AppWriteOnlyModelSerializer):
    """This serializer contains configuration for Forum."""
    class Meta(AppWriteOnlyModelSerializer.Meta):
        fields = ["identity","description","image"]
        model = Forum

class PollOptionsHandleSerializer(AppWriteOnlyModelSerializer):
    class Meta(AppWriteOnlyModelSerializer.Meta):
        model = PostPollOption
        fields = ["identity"]

class ZoneAppliedListSerializer(AppReadOnlyModelSerializer):

    zone = ZoneSerializer()
    class Meta:
        fields = "__all__"
        model = ZoneJoin

class ZoneSkillSerializer(AppReadOnlyModelSerializer):

    class Meta(AppReadOnlyModelSerializer.Meta):
        fields=['id','uuid','identity','description','image','hash_tags','is_active']
        model = Zone
