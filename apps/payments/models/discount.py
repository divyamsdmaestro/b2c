from django.db import models

from apps.common.models import (
    COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG,
    COMMON_CHAR_FIELD_MAX_LENGTH,
    BaseModel,
)


class Discount(BaseModel):
    """
    This model holds information about the discount that will be provided.
    """

    DYNAMIC_KEY = "discount"

    identity = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH)
    coupon_code = models.CharField(
        max_length=COMMON_CHAR_FIELD_MAX_LENGTH,
        **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG
    )

    is_flat_rate_discount = models.BooleanField(default=False)

    discount_in_percentage = models.FloatField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    discount_in_percentage_amount_cap = models.FloatField(
        **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG
    )

    discount_in_amount = models.FloatField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)

    enable_usage_limit = models.BooleanField(default=False)
    maximum_number_of_usages = models.PositiveIntegerField(default=0)

    per_user_usage_limit = models.IntegerField(default=0)

    # Validity
    start_date = models.DateField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    end_date = models.DateField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)

    discount_usage = models.PositiveIntegerField(default=0)

    DISCOUNT_STATUS = (
        ("active", "active"),
        ("inactive", "inactive"),
    )

    status = models.CharField(
        max_length=COMMON_CHAR_FIELD_MAX_LENGTH,
        choices=DISCOUNT_STATUS,
        default="active",
    )

    @staticmethod
    def get_discount(coupon_code):
        discount = Discount.objects.get_or_none(
            coupon_code=coupon_code, status="active"
        )

        return discount
