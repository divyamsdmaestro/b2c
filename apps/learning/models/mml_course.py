from apps.common.helpers import validate_rating
from apps.common.models import (
    COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG,
    COMMON_CHAR_FIELD_MAX_LENGTH,
    BaseModel,
    FileOnlyModel,
)
from django.db import models
from apps.learning.models.course import RESOURCE_TYPE, CourseLevel, CourseResource
from apps.learning.models.linkages import BaseLinkagesModel
from apps.learning.models.price import AbstractPriceModelFields
from apps.common import model_fields

class MMLCourseImage(FileOnlyModel):
    """Image data for a `MML Course`."""

    file = model_fields.AppSingleFileField(
        upload_to="files/mml-course/image/",
    )


class MMLCourseLevel(BaseModel):
    """Holds data for a `MML Course Level`."""

    DYNAMIC_KEY = "mml-course-level"

    identity = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH)


class MMLCourse(BaseLinkagesModel, AbstractPriceModelFields, BaseModel):
    """Holds the mml course data."""

    class Meta(BaseModel.Meta):
        default_related_name = "mml_related_courses"

    DYNAMIC_KEY = "mml-course"

    cms_reference = models.CharField(
        max_length=COMMON_CHAR_FIELD_MAX_LENGTH,
        **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG,
    )

    identity = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH)
    code = models.CharField(
        max_length=COMMON_CHAR_FIELD_MAX_LENGTH,
        **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG,
    )
    description = models.TextField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)

    level = models.ForeignKey(
        to=CourseLevel,
        on_delete=models.SET_NULL,
        **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG,
    )

    language = models.ForeignKey(
        to="learning.Language",
        on_delete=models.SET_NULL,
        **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG,
    )

    image = models.ForeignKey(
        to=MMLCourseImage,
        on_delete=models.SET_NULL,
        **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG,
    )

    duration = models.PositiveIntegerField(default=1)  # denoted in minutes

    start_date = models.DateField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    end_date = models.DateField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)

    # Feedbacks
    enable_ratings = models.BooleanField(default=False)
    enable_feedback_comments = models.BooleanField(default=False)

    sequential_course_flow = models.BooleanField(default=False)

    is_certification_enabled = models.BooleanField(default=False)

    is_private_course = models.BooleanField(default=False)

    make_this_course_popular = models.BooleanField(default=False)
    make_this_course_trending = models.BooleanField(default=False)
    make_this_course_best_selling = models.BooleanField(default=False)

    accreditation = models.ForeignKey(
        to="learning.Accreditation",
        on_delete=models.SET_NULL,
        **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG,
    )
    is_free = models.BooleanField(default=False)
    tutor = models.ForeignKey(
        to="learning.Tutor",
        related_name="related_mml_courses_tutor",
        null=True,
        on_delete=models.SET_NULL,
    )
    author = models.ForeignKey(
        to="learning.Author",
        related_name="related_mml_courses_author",
        null=True,
        on_delete=models.SET_NULL,
    )
    vendor = models.ForeignKey(
        to="learning.Vendor",
        related_name="related_mml_courses_vendor",
        null=True,
        on_delete=models.SET_NULL,
    )

    requirements = models.TextField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    highlights = models.TextField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)

    rating = models.FloatField(default=5, validators=[validate_rating])  # aggregated on runtime
    validity = models.IntegerField(
        **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG
    )
    resource_title = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH, **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    resource_type = models.CharField(
        choices=RESOURCE_TYPE,
        max_length=COMMON_CHAR_FIELD_MAX_LENGTH,
        **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG
    )
    resource = models.ForeignKey(
        to=CourseResource,
        on_delete=models.SET_NULL,
        **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG,
    )
    complete_in_a_day = models.BooleanField(default=False)
    editors_pick = models.BooleanField(default=False)
    mml_sku_id = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH, **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    vm_name = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH, **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    virtual_lab = models.BooleanField(default=False)