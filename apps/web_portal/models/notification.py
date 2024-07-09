from apps.access.models import User
from apps.common.models import (
    COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG,
    COMMON_CHAR_FIELD_MAX_LENGTH,
    COMMON_NULLABLE_FIELD_CONFIG,
    BaseModel,
    FileOnlyModel,
)
from django.db import models
from apps.learning.models.certification_path import CertificationPath
from apps.learning.models.course import Course
from apps.learning.models.learning_path import LearningPath


class Notification(BaseModel):
    user = models.ForeignKey(
        User, on_delete=models.SET_NULL,
        **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG,
    )
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    course = models.ForeignKey(
        Course, on_delete=models.SET_NULL,
        **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG,
    )
    learning_path = models.ForeignKey(
        LearningPath, on_delete=models.SET_NULL,
        **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG,
    )
    certification_path = models.ForeignKey(
        CertificationPath, on_delete=models.SET_NULL,
        **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG,
    )
    NOTIFICATION_TYPE_CHOICES = ((
        ("enrolled", "enrolled"),
        ("completed", "completed")
    ))
    purpose = models.CharField(
        max_length=COMMON_CHAR_FIELD_MAX_LENGTH,
        choices=NOTIFICATION_TYPE_CHOICES,
    )
    is_delete = models.BooleanField(default=False)