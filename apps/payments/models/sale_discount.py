from django.db import models
from apps.common import model_fields
from apps.common.models import (
    COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG,
    COMMON_CHAR_FIELD_MAX_LENGTH,
    BaseModel,
    FileOnlyModel,
)

class SaleDiscountImage(FileOnlyModel):
    """Image data for a `SaleDiscount`."""

    file = model_fields.AppSingleFileField(
        upload_to="files/sale_discount/image/",
    )

SALES_FOR_CHOICES = (
    ("learning_content", "learning_content"),
    ("subscription_plan", "subscription_plan"),
)

class SaleDiscount(BaseModel):
    """
    This model holds information about the sales discount that will be provided.
    """

    DYNAMIC_KEY = "sale-discount"

    identity = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH)
    sale_code = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH, 
                                 **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    description = models.TextField()

    start_date = models.DateField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    end_date = models.DateField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)

    sale_discount_percentage = models.FloatField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)

    image = models.ForeignKey(to=SaleDiscountImage, on_delete=models.SET_NULL,
        **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG,)
    
    courses = models.ManyToManyField(to="learning.Course",
        blank=True,)
    
    learning_paths = models.ManyToManyField(to="learning.LearningPath",
        blank=True,)
    
    certification_paths = models.ManyToManyField(to="learning.CertificationPath",
        blank=True,)
    
    # sale_for = models.ForeignKey(to=SaleDiscountChoices, on_delete=models.SET_NULL, **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    sale_for = models.CharField(
        choices=SALES_FOR_CHOICES,
        default="learning_content",
        max_length=COMMON_CHAR_FIELD_MAX_LENGTH,
    )


class SubscriptionPlanSaleDiscount(BaseModel):
    """
    This model holds information about the sales discount for Subscription Plan.
    """

    DYNAMIC_KEY = "subscription-plan-sale-discount"

    subscription_plan = models.ForeignKey(to='payments.SubscriptionPlan', on_delete=models.SET_NULL,
        **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG,)

    sale_code = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH, 
                                 **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    
    # Validity
    start_date = models.DateField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    end_date = models.DateField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)

    # Yearly Subscription Plan Offer
    is_yearly_subscription_plan_offer = models.BooleanField(default=True)

    # Yearly Discount Percentage
    is_yearly_discount_percentage = models.BooleanField(default=True)
    yearly_discount_percentage = models.FloatField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)

    # Yearly Discount Amount
    is_yearly_discount_amount = models.BooleanField(default=False)
    yearly_discount_amount = models.FloatField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)

    # Monthly Subscription Plan Offer
    is_monthly_subscription_plan_offer = models.BooleanField(default=False)

    # Monthly Discount Percentage
    is_monthly_discount_percentage = models.BooleanField(default=True)
    monthly_discount_percentage = models.FloatField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)

    # Yearly Discount Amount
    is_monthly_discount_amount = models.BooleanField(default=False)
    monthly_discount_amount = models.FloatField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)

    sale_for = models.CharField(
        choices=SALES_FOR_CHOICES,
        default="subscription_plan",
        max_length=COMMON_CHAR_FIELD_MAX_LENGTH,
    )