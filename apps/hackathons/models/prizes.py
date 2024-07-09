from django.db import models

from apps.common.models import (
    COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG,
    BaseModel,
)

class HackathonPrizeDetails(BaseModel):
    """
    This model holds information about the hackathon prize Details.
    """

    DYNAMIC_KEY = "hackathon-prize-details"

    rank = models.PositiveIntegerField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    prize_amount = models.FloatField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)