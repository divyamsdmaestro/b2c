from django.db import models

from apps.common.models import (
    COMMON_CHAR_FIELD_MAX_LENGTH,
    BaseModel,
)

class IndustryType(BaseModel):
    """
    This model holds information about the hackathon industry Details.
    """
    DYNAMIC_KEY = "hackathon-industry"

    identity = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH)