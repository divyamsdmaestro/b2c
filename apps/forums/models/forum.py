from django.db import models

from apps.common import model_fields
from apps.common.models import (
    COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG,
    COMMON_CHAR_FIELD_MAX_LENGTH,
    BaseModel,
    FileOnlyModel,
)
from apps.access.models import InstitutionUserGroupDetail

class ZoneImage(FileOnlyModel):
    """Image data for a `Zone`."""

    file = model_fields.AppSingleFileField(
        upload_to="files/zone/image/",
    )

class ZoneType(BaseModel):
    """Holds data for a `Community zone Type`."""

    DYNAMIC_KEY = "zone-type"

    identity = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH, unique=True)

class Zone(BaseModel):
    """Holds the Zone data."""

    DYNAMIC_KEY = "community-zone"

    identity = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH)
    description = models.TextField()
    image = models.ForeignKey(
        to=ZoneImage,
        on_delete=models.SET_NULL,
        **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG
    )
    hash_tags = models.TextField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    assign_members = models.ManyToManyField(
        InstitutionUserGroupDetail, blank=True
    )
    # eg :  Public, Private, Moderate
    zone_type = models.ForeignKey(
        to=ZoneType,
        on_delete=models.SET_NULL,
        **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG
    )
    forums = models.ManyToManyField(to="forums.Forum",blank=True)
    skills = models.ManyToManyField(to="learning.Skill", blank=True)
    categories = models.ManyToManyField(to="learning.Category", blank=True)
    is_active = models.BooleanField(default=True)

class ForumImage(FileOnlyModel):
    """Image data for a `Forum`."""

    file = model_fields.AppSingleFileField(
        upload_to="files/forum/image/",
    )

class Forum(BaseModel):
    """Holds the forum data."""

    DYNAMIC_KEY = "community-forum"

    identity = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH)
    description = models.TextField()
    image = models.ForeignKey(
        to=ForumImage,
        on_delete=models.SET_NULL,
        **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG
    )


class PostType(BaseModel):
    """Holds data for a `Post Type`. eg: question/poll based type"""

    DYNAMIC_KEY = "post-type"

    identity = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH)

class PostPollOption(BaseModel):
    """Holds the data for user's social media handles."""

    identity = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH,**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)

    clicked_count = models.IntegerField(default=0)

class PostImage(FileOnlyModel):
    """Image data for a `Forum`."""

    file = model_fields.AppSingleFileField(
        upload_to="files/forum/post/image/",
    )

class SubjectivePostImage(FileOnlyModel):
    """Image data for a `Forum`."""

    file = model_fields.AppSingleFileField(
        upload_to="files/forum/post/subjective-image/",
    )

class Post(BaseModel):
    """Holds the forum post data."""

    DYNAMIC_KEY = "forum-post"
     
    forum = models.ForeignKey(
        to = Forum,
        on_delete=models.SET_NULL,
        **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG
    )
    # eg:questions / poll based post type
    post_type = models.ForeignKey(
        to=PostType,
        on_delete=models.SET_NULL,
        **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG
    )
    image = models.ForeignKey(
        to=PostImage,
        on_delete=models.SET_NULL,
        **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG
    )
    subjective_image = models.ForeignKey(
        to=SubjectivePostImage,
        on_delete=models.SET_NULL,
        **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG
    )
    identity = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH, **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG) # question
    # description field only for question based post type
    description = models.TextField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    subjective_description = models.TextField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    tags = models.TextField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    # poll options field only for poll based post type
    poll_options = models.ManyToManyField(PostPollOption, blank=True,)
    post_attachment = models.URLField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    enable_end_time = models.BooleanField(default=False)
    # start and end date shows when end time is true
    start_date = models.DateField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    end_date = models.DateField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    enable_hide_discussion = models.BooleanField(default=False)

    def get_likes_count(self):
        return PostLike.objects.filter(post=self,is_liked=True).count()

    def get_comments_count(self):
        comments = PostComment.objects.filter(post=self)
        return comments.count()

class PostReply(BaseModel):
    """Holds the Forum post comments replies data."""

    DYNAMIC_KEY = "post-comment-reply"

    comment = models.ForeignKey(
        to = "forums.PostComment",
        on_delete=models.SET_NULL,
        **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG
    )

    identity = models.TextField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)


class PostComment(BaseModel):
    """Holds the Forum post comments data."""

    DYNAMIC_KEY = "post-comment"
     
    post = models.ForeignKey(
        to = "forums.Post",
        related_name="comments",
        on_delete=models.SET_NULL,
        **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG
    )
    identity = models.TextField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)

    replies = models.ManyToManyField(PostReply, blank=True)

    def replies_count(self):
        return self.replies.all().count()


class PostLike(BaseModel):
    """Holds the Forum post likes data."""

    DYNAMIC_KEY = "post-likes"
     
    post = models.ForeignKey(
        to = "forums.Post",
        related_name="likes",
        on_delete=models.SET_NULL,
        **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG
    )
    is_liked = models.BooleanField(default=False)

class PostPollOptionClick(BaseModel):
    """Holds the Forum post poll option clicks data."""

    DYNAMIC_KEY = "poll-clicks"
     
    post = models.ForeignKey(
        to = "forums.Post",
        related_name="poll_option_clicks",
        on_delete=models.SET_NULL,
        **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG
    )
    poll_option = models.ForeignKey(
        to = "forums.PostPollOption",
        related_name="clicks",
        on_delete=models.SET_NULL,
        **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG
    )  

class ZoneJoin(BaseModel):

    DYNAMIC_KEY = "zone-join"

    zone=models.ForeignKey(
        to=Zone, 
        on_delete=models.CASCADE,
    )

    status=models.BooleanField(default=True)

class PostReport(BaseModel):
    """Holds the post reported data."""

    DYNAMIC_KEY = "post-report"
     
    post = models.ForeignKey(
        to = "forums.Post",
        on_delete=models.SET_NULL,
        **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG
    )
    is_reported = models.BooleanField(default=False)
