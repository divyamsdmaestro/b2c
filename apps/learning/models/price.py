from django.db import models

from apps.common.models import COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG, BaseModel


class AbstractPriceModelFields(BaseModel):
    class Meta:
        abstract = True

    actual_price_inr = models.PositiveIntegerField(
        **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG
    )
    current_price_inr = models.PositiveIntegerField(
        **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG
    )
