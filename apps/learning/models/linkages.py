from django.db import models

from apps.common import model_fields
from apps.common.models import (
    COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG,
    COMMON_CHAR_FIELD_MAX_LENGTH,
    BaseModel,
    FileOnlyModel,
)
from apps.learning.models.price import AbstractPriceModelFields
from apps.common.helpers import validate_rating

class CategoryImage(FileOnlyModel):
    file = model_fields.AppSingleFileField(
        upload_to="files/category/image/",
    )


class SkillImage(FileOnlyModel):
    file = model_fields.AppSingleFileField(
        upload_to="files/skill/image/",
    )

class JobEligibleSkillImage(FileOnlyModel):
    file = model_fields.AppSingleFileField(
        upload_to = "files/job_eligible_skill/image/",
    )


class CategoryPopularity(BaseModel):
    """Holds the `Category's Popularity` data for a course."""

    DYNAMIC_KEY = "category-popularity"
    identity = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH)


class SkillPopularity(BaseModel):
    """Holds the `Skill's Popularity` data for a course."""

    DYNAMIC_KEY = "skill-popularity"
    identity = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH)


class Tag(BaseModel):
    """Holds the `Tag` data for a course."""

    DYNAMIC_KEY = "tag"

    identity = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH, unique=True)


class Category(BaseModel):
    """Holds the `Category` data for a course."""

    DYNAMIC_KEY = "category"

    identity = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH, unique=True)
    image = models.ForeignKey(
        to=CategoryImage,
        on_delete=models.SET_NULL,
        **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG
    )
    popularity = models.ForeignKey(
        to=CategoryPopularity,
        on_delete=models.SET_NULL,
        **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG
    )


class Skill(AbstractPriceModelFields, BaseModel):
    """Holds the `Skill` data for a course."""

    DYNAMIC_KEY = "skill"

    identity = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH, unique=True)
    description = models.TextField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    image = models.ForeignKey(
        to=SkillImage,
        on_delete=models.SET_NULL,
        **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG
    )
    category = models.ManyToManyField(to="learning.Category", blank=True)
    make_this_skill_popular = models.BooleanField(default=False)
    mml_sku_id = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH, **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    vm_name = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH, **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    assessmentID = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH, **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    is_archived = models.BooleanField(default=False)

class JobEligibleSkill(AbstractPriceModelFields, BaseModel):
    """ Holds the `skill` eligible for a job. """
    
    DYNAMIC_KEY = "job-eligible-skill"

    identity = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH, unique=True)
    description = models.TextField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    image = models.ForeignKey(
        to=JobEligibleSkillImage,
        on_delete=models.SET_NULL,
        **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG
    )

    category = models.ManyToManyField(to="learning.Category", blank=True)
    make_this_skill_popular = models.BooleanField(default=False)
    assessment_id = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH, **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    
    courses = models.ManyToManyField(
        to="learning.Course",
        blank=True,
    )

    learning_paths = models.ManyToManyField(
        to="learning.LearningPath",
        blank=True,
    )

    certification_paths = models.ManyToManyField(
        to="learning.CertificationPath",
        blank=True,
    )

class LearningRoleImage(FileOnlyModel):
    """Image data for a `LearningRole`."""

    file = model_fields.AppSingleFileField(
        upload_to="files/learning-role/image/",
    )

class LearningRole(BaseModel):

    class Meta(BaseModel.Meta):
        default_related_name = "related_learning_role"

    DYNAMIC_KEY = "learning-role"

    identity = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH)
    description = models.TextField()
    image = models.ForeignKey(
        to=LearningRoleImage,
        on_delete=models.SET_NULL,
        **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG
    )
    skills = models.ManyToManyField(
        to="learning.Skill",
        blank=True,
    )
    make_this_role_popular = models.BooleanField(default=False)
    make_this_role_trending = models.BooleanField(default=False)
    make_this_role_best_selling = models.BooleanField(default=False)

    is_certification_enabled = models.BooleanField(default=False)

    duration = models.PositiveIntegerField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    enable_ratings = models.BooleanField(default=False)
    rating = models.FloatField(default=5, validators=[validate_rating])

class Proficiency(BaseModel):
    """Proficiencies of course and LP etc."""

    DYNAMIC_KEY = "proficiency"

    identity = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH)

class BaseLinkagesModel(models.Model):
    """
    Inherited by models that require linkages mentioned in this file.

    Inherited by:
        1. Course               (Actual & Main Data)
        2. LearningPath         (Performance Enhancements - Set Using Chain Of Responsibility)
        3. CertificationPath    (Performance Enhancements - Set Using Chain Of Responsibility)
    """

    class Meta:
        abstract = True

    proficiency = models.ForeignKey(
        to="learning.Proficiency",
        on_delete=models.SET_NULL,
        null=True,
    )
    tags = models.ManyToManyField(
        to="learning.Tag",
        blank=True,
    )
    skills = models.ManyToManyField(
        to="learning.Skill",
        blank=True,
    )
    categories = models.ManyToManyField(
        to="learning.Category",
        blank=True,
    )
    learning_role = models.ForeignKey(
        LearningRole, on_delete=models.SET_NULL,
        null=True
    )