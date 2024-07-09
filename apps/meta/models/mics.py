from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from apps.common.models import (
    COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG,
    COMMON_CHAR_FIELD_MAX_LENGTH,
    BaseModel,
)


class UserAskedQuestion(BaseModel):
    """
    Holds data for user asked questions. The created_by holds
    user. This is specific to the user level.
    """

    question = models.TextField()
    answer = models.TextField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    is_active = models.BooleanField(default=True)


class FrequentlyAskedQuestion(BaseModel):
    """Holds data for FAQ's linked the application. This is not linked to user."""
    DYNAMIC_KEY = "faq"

    question = models.TextField()
    answer = models.TextField()
    is_active = models.BooleanField(default=True)


class UserContactedDetail(BaseModel):
    """Holds data of users who reached out to the admin."""

    name = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH)
    company_name = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH, **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)

    phone_number = PhoneNumberField()
    email = models.EmailField()

    country = models.ForeignKey(to="meta.Country", on_delete=models.CASCADE)

    looking_for = models.TextField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    message = models.TextField()
