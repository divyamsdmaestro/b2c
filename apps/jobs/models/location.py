from django.db import models

from apps.common.models import COMMON_CHAR_FIELD_MAX_LENGTH, BaseModel


class Location(BaseModel):
    """This model holds the fields of `Location` where the Job is."""

    DYNAMIC_KEY = "job-location"
    identity = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH)
