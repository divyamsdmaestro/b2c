from django.db import models

from apps.common.models import (
    COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG,
    COMMON_CHAR_FIELD_MAX_LENGTH,
    BaseModel,
)


class Payment(BaseModel):
    razorpay_order_id = models.CharField(
        max_length=COMMON_CHAR_FIELD_MAX_LENGTH,
        **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG
    )

    razorpay_order_data = models.JSONField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)

    verification_signature = models.JSONField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    PAYMENT_STATUS_CHOICES = (
        ("on_process", "on_process"),
        ("success", "success"),
        ("failed", "failed"),
    )
    status = models.CharField(
        choices=PAYMENT_STATUS_CHOICES,
        default="on_process",
        max_length=COMMON_CHAR_FIELD_MAX_LENGTH,
    )
