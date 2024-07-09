from django.db import models
from apps.common import model_fields
from apps.common.helpers import validate_rating
from apps.common.models import (
    COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG,
    COMMON_CHAR_FIELD_MAX_LENGTH,
    BaseModel,
    FileOnlyModel,
)
from apps.learning.models import Course

class SubscriptionPlanImage(FileOnlyModel):
    """Image data for a `SubscriptionPlan`."""

    file = model_fields.AppSingleFileField(
        upload_to="files/subscription_plan/image/",
    )

class SubscriptionPlan(BaseModel):
    """This models holds the data for Subscription Plan"""

    DYNAMIC_KEY = "subscription-plan"

    identity = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH)
    description = models.TextField()
    rating = models.FloatField(default=5, validators=[validate_rating])
    what_will_you_learn = models.TextField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)

    # Validity
    start_date = models.DateField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    end_date = models.DateField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)

    # Subscription Plan Popular
    make_this_subscription_plan_popular = models.BooleanField(default=False)

    # Plan Features
    skill_level_assesment = models.BooleanField(default=False)
    interactive_practices = models.BooleanField(default=False)
    certification = models.BooleanField(default=False)
    virtual_labs = models.BooleanField(default=False)
    basic_to_advance_level = models.BooleanField(default=False)
    is_duration = models.BooleanField(default=False)
    duration = models.IntegerField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    # Image
    image = models.ForeignKey(
        to=SubscriptionPlanImage,
        on_delete=models.SET_NULL,
        **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG
    )

    # Pricing
    is_yearly_subscription_plan_active = models.BooleanField(default=True)
    is_monthly_subscription_plan_active = models.BooleanField(default=True)

    yearly_price_in_inr = models.FloatField(default=0, blank=True)
    is_gst_inclusive_for_yearly = models.BooleanField(default=True)

    monthly_price_in_inr = models.FloatField(default=0, blank=True)
    is_gst_inclusive_for_monthly = models.BooleanField(default=True)

    # Contents
    courses = models.ManyToManyField(
        to=Course,
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

    STATUS_TYPE_CHOICES = (
        ("active", "active"),
        ("inactive", "inactive")
    )
   
    status = models.CharField(
        max_length=COMMON_CHAR_FIELD_MAX_LENGTH,
        choices=STATUS_TYPE_CHOICES,
        default="active"
    )

class SubscriptionPlanCustomerEnquiry(BaseModel):
    DYNAMIC_KEY = "subscription-plan-leads"

    subscription_plan = models.ForeignKey(to="payments.SubscriptionPlan", on_delete=models.CASCADE)
    name = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH)
    email = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH)
    phone_number = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH)
    is_customer = models.BooleanField(default=False)