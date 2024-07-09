"""Holds models related to `Add To Cart` functionality."""

from django.db import models
from apps.hackathons.models import hackathon as hackathon_models
from apps.common.models import (
    COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG,
    COMMON_CHAR_FIELD_MAX_LENGTH,
    BaseModel,
)

class CourseAddToCart(BaseModel):
    """
    Holds courses that are added to cart by the user.
    The created_by field holds the user data.
    """

    entity = models.ForeignKey(
        to="learning.Course",
        on_delete=models.CASCADE,
    )

class MMLCourseAddToCart(BaseModel):
    """
    Holds MML courses that are added to cart by the user.
    The created_by field holds the user data.
    """

    entity = models.ForeignKey(
        to="learning.MMLCourse",
        on_delete=models.CASCADE,
    )

class LearningPathAddToCart(BaseModel):
    """
    Holds learning paths that are added to cart by the user.
    The created_by field holds the user data.
    """

    entity = models.ForeignKey(
        to="learning.LearningPath",
        on_delete=models.CASCADE,
    )


class CertificationPathAddToCart(BaseModel):
    """
    Holds certification paths that are added to cart by the user.
    The created_by field holds the user data.
    """

    entity = models.ForeignKey(
        to="learning.CertificationPath",
        on_delete=models.CASCADE,
    )


class DiscountAddToCart(BaseModel):
    """
    Holds discount that is applied to the cart.
    The created_by field holds the user data.
    """

    discount = models.ForeignKey(
        to="payments.Discount",
        on_delete=models.CASCADE,
    )

class SkillAddToCart(BaseModel):

    entity = models.ForeignKey(
        to='learning.Skill',
        on_delete=models.CASCADE,
    )

class SubscriptionPlanAddToCart(BaseModel):

    entity = models.ForeignKey(
        to='payments.SubscriptionPlan',
        on_delete=models.CASCADE,
    )
    guest = models.ForeignKey(
        to='access.GuestUser',
        on_delete=models.CASCADE,
        **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG
    )
    is_monthly_or_yearly = models.BooleanField(default=False)

class BlendedLearningPathAddToCart(BaseModel):
    """
    Holds blended learning paths that are added to cart by the user.
    The created_by field holds the user data.
    """

    # entity = models.ForeignKey(
    #     to="learning.BlendedLearningUserEnroll",
    #     on_delete=models.CASCADE,
    # )
    entity = models.ForeignKey(
        to="learning.BlendedLearningPath",
        on_delete=models.CASCADE,
    )
    mode = models.CharField( max_length=COMMON_CHAR_FIELD_MAX_LENGTH,
        **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG,)
    course = models.ForeignKey(
        to="learning.Course",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    session_details = models.JSONField(default=dict)
    schedule_details = models.ForeignKey(to="learning.BlendedLearningPathScheduleDetails", on_delete=models.CASCADE, null=True, blank=True)
    


class JobEligibilitySkillAddToCart(BaseModel):
    """
    Holds blended learning paths that are added to cart by the user.
    The created_by field holds the user data.
    """

    entity = models.ForeignKey(
        to="learning.JobEligibleSkill",
        on_delete=models.CASCADE,
    )
    
    
class EcashAddToCart(BaseModel):
    """
    Holds ecash that is applied to the cart.
    The created_by field holds the user data.
    """

    ecash = models.BooleanField(default=False)