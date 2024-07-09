from django.db import models

from apps.common import model_fields
from apps.common.models import (
    COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG,
    COMMON_CHAR_FIELD_MAX_LENGTH,
    BaseModel,
    FileOnlyModel,
)
from apps.common.helpers import validate_rating
class Language(BaseModel):
    DYNAMIC_KEY = "languages"
    identity = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH, unique=True)
    code = models.CharField(
        max_length=COMMON_CHAR_FIELD_MAX_LENGTH,
        **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG
    )


class Accreditation(BaseModel):
    DYNAMIC_KEY = "accreditations"
    identity = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH, unique=True)


class VendorImage(FileOnlyModel):
    """Holds the image data for a `Vendor`."""

    file = model_fields.AppSingleFileField(
        upload_to="files/vendor/image/",
    )


class Vendor(BaseModel):
    """Holds the Vendor related data."""

    DYNAMIC_KEY = "vendor"

    identity = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH, unique=True)
    image = models.ForeignKey(
        to=VendorImage,
        on_delete=models.SET_NULL,
        **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG
    )


class AuthorImage(FileOnlyModel):
    """Holds the image data for an `Author`."""

    file = model_fields.AppSingleFileField(
        upload_to="files/author/image/",
    )


class Author(BaseModel):
    """Author of a `Course`."""

    DYNAMIC_KEY = "author"

    identity = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH, unique=True)
    designation = models.CharField(
        max_length=COMMON_CHAR_FIELD_MAX_LENGTH,
        **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG
    )
    image = models.ForeignKey(
        to=AuthorImage,
        on_delete=models.SET_NULL,
        **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG
    )
    rating = models.FloatField(default=5, validators=[validate_rating])  # aggregated on runtime
    vendor = models.ManyToManyField(
        to=Vendor,
        related_name="related_vendors",
        blank=True
    )


class Tutor(BaseModel):
    """The instructor or the one who teaches a given course."""
    DYNAMIC_KEY = "tutor"
    identity = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH)


class CourseWhatWillYouLearn(BaseModel):
    """The model class contains Course what will you learn details."""

    course = models.ForeignKey("learning.Course", on_delete=models.CASCADE)
    description = models.TextField()