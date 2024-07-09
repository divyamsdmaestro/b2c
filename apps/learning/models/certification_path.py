"""
Note:
    1. This `Adaptive Learning Path` is also/will also be called as `Certification Path`.
    2. This is just a combination of `Learning Path`s.
    3. Will be using the term `Certification Path` since, `Adaptive Learning Path`
        spoils a few naming conventions in our application.
"""
from django.db import models

from apps.common import model_fields
from apps.common.models import (
    COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG,
    COMMON_CHAR_FIELD_MAX_LENGTH,
    BaseModel,
    FileOnlyModel,
)
from apps.learning.models.price import AbstractPriceModelFields

from apps.learning.models.course import CourseLevel
from apps.common.helpers import validate_rating

class CertificationPathImage(FileOnlyModel):
    """Image data for a `CertificationPath`."""

    file = model_fields.AppSingleFileField(
        upload_to="files/certification-path/image/",
    )


class CertificationPathLevel(BaseModel):
    """Holds data for a `Certification Path Level`."""

    DYNAMIC_KEY = "certification-path-level"

    identity = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH)


class CertificationPath(AbstractPriceModelFields, BaseModel):
    """Holds the Certification Path data. Just a collection of Learning Paths."""

    DYNAMIC_KEY = "certification-path"

    identity = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH)
    description = models.TextField()

    image = models.ForeignKey(
        to=CertificationPathImage,
        on_delete=models.SET_NULL,
        **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG
    )
    code = models.CharField(
        max_length=COMMON_CHAR_FIELD_MAX_LENGTH,
        **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG,
    )
    level = models.ForeignKey(
        to=CourseLevel,
        on_delete=models.SET_NULL,
        **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG
    )

    language = models.ForeignKey(
        to="learning.Language",
        on_delete=models.SET_NULL,
        **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG
    )

    duration = models.PositiveIntegerField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)

    start_date = models.DateField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    end_date = models.DateField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)

    skills = models.ManyToManyField(to="learning.Skill", blank=True)

    categories = models.ManyToManyField(to="learning.Category", blank=True)

    tags = models.ManyToManyField(
        to="learning.Tag",
        blank=True,
    )
    learning_role = models.ForeignKey(
        to='learning.LearningRole', 
        on_delete=models.SET_NULL, 
        **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG
    )

    # Feedbacks
    enable_ratings = models.BooleanField(default=False)
    enable_feedback_comments = models.BooleanField(default=False)
    is_private_course = models.BooleanField(default=False)
    sequential_course_flow = models.BooleanField(default=False)
    make_this_alp_popular = models.BooleanField(default=False)
    make_this_alp_trending = models.BooleanField(default=False)
    make_this_alp_best_selling = models.BooleanField(default=False)

    requirements = models.TextField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    highlights = models.TextField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)

    number_of_seats = models.PositiveIntegerField(
        **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG
    )

    rating = models.FloatField(default=5,validators=[validate_rating])  # aggregated on runtime

    accreditation = models.ForeignKey(
        to="learning.Accreditation",
        on_delete=models.SET_NULL,
        **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG
    )

    is_certification_enabled = models.BooleanField(default=False)
    is_free = models.BooleanField(default=False)
    mml_sku_id = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH, **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    vm_name = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH, **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    virtual_lab = models.BooleanField(default=False)

class CertificationPathLearningPath(BaseModel):
    """
    Learning Path and its `position` under a Certification Path.
    Each LP can have different positions under different CPs.
    """

    DYNAMIC_KEY = "certification-path-learning-path"

    position = models.PositiveIntegerField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    learning_path = models.ForeignKey(
        to="learning.LearningPath",
        on_delete=models.CASCADE,
        related_name="related_certification_path_learning_paths",
    )

    certification_path = models.ForeignKey(
        to=CertificationPath,
        on_delete=models.CASCADE,
        related_name="related_certification_path_learning_paths",
    )
