from django.db import models

from apps.common import model_fields
from apps.common.models import (
    COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG,
    COMMON_CHAR_FIELD_MAX_LENGTH,
    BaseModel,
    FileOnlyModel,
)


class TestimonialImage(FileOnlyModel):
    """Image data for a `Testimonial`."""

    file = model_fields.AppSingleFileField(
        upload_to="files/testimonials/image/",
    )


class Testimonial(BaseModel):
    """Model for Testimonial Block in website"""

    DYNAMIC_KEY = "testimonial"

    name = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH)
    designation = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH)
    image = models.ForeignKey(
        to=TestimonialImage,
        on_delete=models.SET_NULL,
        **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG
    )
    video_url = models.URLField(
        **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG,
        max_length=COMMON_CHAR_FIELD_MAX_LENGTH
    )
    message = models.TextField()
