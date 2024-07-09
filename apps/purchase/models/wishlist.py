from django.db import models
from apps.hackathons.models import hackathon as hackathon_models
from apps.common.models import (
    COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG,
    COMMON_CHAR_FIELD_MAX_LENGTH,
    BaseModel,
)

class CourseWishlist(BaseModel):
    """
    Holds courses that are in the users wishlist.
    The created_by holds the user data.
    """

    entity = models.ForeignKey(
        to="learning.Course",
        on_delete=models.CASCADE,
    )

class MMLCourseWishlist(BaseModel):
    """
    Holds mml courses that are in the users wishlist.
    The created_by holds the user data.
    """

    entity = models.ForeignKey(
        to="learning.MMLCourse",
        on_delete=models.CASCADE,
    )

class LearningPathWishlist(BaseModel):
    """
    Holds learning paths that are in the users wishlist.
    The created_by holds the user data.
    """

    entity = models.ForeignKey(
        to="learning.LearningPath",
        on_delete=models.CASCADE,
    )


class CertificationPathWishlist(BaseModel):
    """
    Holds certification paths that are in the users wishlist.
    The created_by holds the user data.
    """

    entity = models.ForeignKey(
        to="learning.CertificationPath",
        on_delete=models.CASCADE,
    )

class SkillWishlist(BaseModel):

    entity = models.ForeignKey(
        to='learning.Skill',
        on_delete=models.CASCADE,
    )

class SubscriptionPlanWishlist(BaseModel):

    entity = models.ForeignKey(
        to='payments.SubscriptionPlan',
        on_delete=models.CASCADE,
    )
    is_monthly_or_yearly = models.BooleanField(default=False)

class BlendedLearningPathWishlist(BaseModel):
    """
    Holds blended learning paths that are in the users wishlist.
    The created_by holds the user data.
    """

    entity = models.ForeignKey(
        to="learning.BlendedLearningPath",
        on_delete=models.CASCADE,
    )
    mode = models.CharField( max_length=COMMON_CHAR_FIELD_MAX_LENGTH,
        **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG,)

class JobEligibilitySkillWishlist(BaseModel):
    """
    Holds blended learning paths that are in the users wishlist.
    The created_by holds the user data.
    """

    entity = models.ForeignKey(
        to="learning.JobEligibleSkill",
        on_delete=models.CASCADE,
    )