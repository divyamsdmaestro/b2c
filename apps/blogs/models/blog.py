from django.db import models

from apps.common import model_fields
from apps.common.models import (
    COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG,
    COMMON_CHAR_FIELD_MAX_LENGTH,
    BaseModel,
    FileOnlyModel,
)
from apps.learning.models import Category

class BlogImage(FileOnlyModel):
    """Image data for a `blog`."""

    file = model_fields.AppSingleFileField(
        upload_to="files/blog/image/",
    )


class Blog(BaseModel):
    """Holds the blog data."""

    DYNAMIC_KEY = "blog"
    BLOG_STATUS_CHOICES = (
        ("active", "Active"),
        ("inactive", "Inactive"),
        ("pending_approval", "Pending Approval"),
        ("archieve", "Archieve"),
        ("published", "Published"),
    )

    status = models.CharField(
        choices=BLOG_STATUS_CHOICES,
        default="published",
        max_length=COMMON_CHAR_FIELD_MAX_LENGTH,
    )

    identity = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH)
    description = models.TextField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    hash_tags = models.TextField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    image = models.ForeignKey(
        to=BlogImage,
        on_delete=models.SET_NULL,
        **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG
    )
    category = models.ForeignKey(
        to=Category,
        on_delete=models.SET_NULL,
        **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG
    )
    zone = models.ForeignKey(
        to="forums.Zone",
        on_delete=models.SET_NULL,
        **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG,
    )
    def get_likes_count(self):
        return BlogLike.objects.filter(blog=self,is_liked=True).count()

    def get_comments_count(self):
        return BlogComment.objects.filter(blog=self).count()

class BlogCommentReply(BaseModel):
    """Holds the Blog comments replies data."""

    DYNAMIC_KEY = "blog-comment-reply"

    comment = models.ForeignKey(
        to = "blogs.BlogComment",
        on_delete=models.SET_NULL,
        **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG
    )

    identity = models.TextField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)


class BlogComment(BaseModel):
    """Holds the blog comments data."""

    DYNAMIC_KEY = "blog-comment"
     
    blog = models.ForeignKey(
        to = "blogs.Blog",
        on_delete=models.SET_NULL,
        **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG
    )
    identity = models.TextField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)

    replies = models.ManyToManyField(BlogCommentReply, blank=True)

    def replies_count(self):
        return self.replies.all().count()


class BlogLike(BaseModel):
    """Holds the Blog likes data."""

    DYNAMIC_KEY = "blog-like"
     
    blog = models.ForeignKey(
        to = "blogs.Blog",
        on_delete=models.SET_NULL,
        **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG
    )
    is_liked = models.BooleanField(default=False)