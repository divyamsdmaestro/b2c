from django.db import models
from apps.common import model_fields
from apps.common.models import (
    COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG,
    COMMON_CHAR_FIELD_MAX_LENGTH,
    BaseModel,
    FileOnlyModel,
)

class NewsThumbnailImage(FileOnlyModel):
    """Image data for a `News`."""

    file = model_fields.AppSingleFileField(
        upload_to="files/news/thumbnail/image/",
    )

class NewsDetail(BaseModel):
    """Model for news in website"""

    DYNAMIC_KEY = "news"

    title = models.TextField()
    image = models.ForeignKey(
        to=NewsThumbnailImage,
        on_delete=models.SET_NULL,
        **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG
    )
    news_link = models.URLField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    published_by = models.CharField(
        max_length=COMMON_CHAR_FIELD_MAX_LENGTH,
        **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG
        )
    published_on = models.DateField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    tags = models.TextField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    skills = models.ManyToManyField(
        to="learning.Skill",
        blank=True,
    )