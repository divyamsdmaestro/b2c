from django.db import models

from apps.common import model_fields
from apps.common.models import (
    COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG,
    COMMON_CHAR_FIELD_MAX_LENGTH,
    BaseModel,
    FileOnlyModel,
)
from apps.learning.models import Course, LearningPath, CertificationPath

class CertificateSponsorImage(FileOnlyModel):
    """Image data for a `CertificationPath`."""
    DYNAMIC_KEY = "certificate-sponsor-image"
    file = model_fields.AppSingleFileField(
        upload_to="files/certificate-sponsor/image/",
    )

class CertificateImage(FileOnlyModel):
    """Image data for a `CertificationPath`."""
    DYNAMIC_KEY = "certificate-image"

    file = model_fields.AppSingleFileField(
        upload_to="files/certificate/image/",
    )
class CertificateLearningType(BaseModel):
    """Holds data for a `Certificate Learning Type`."""

    DYNAMIC_KEY = "certificate-learning-type"
    identity = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH)

class Certificate(BaseModel):
    """Holds data for a `Certificate`."""

    DYNAMIC_KEY = "certificate"

    # LEARNING_TYPE_CHOICES = (("course", "course"),("learning_path", "learning_path"), ("advanced_learning_path", "advanced_learning_path"))
    LOGO_TYPE_CHOICES = (("yes", "yes"),("no", "no"))
    ORIENTATION_CHOICES = (("landspace", "landspace"),("portrait", "portrait"))
    
    # course = models.ForeignKey(to=Course,
    #     on_delete=models.SET_NULL,
    #     **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG,
    # )
    # learning_path = models.ForeignKey(to=LearningPath,
    #     on_delete=models.SET_NULL,
    #     **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG,
    # )
    # advanced_learning_path = models.ForeignKey(to=CertificationPath,
    #     on_delete=models.SET_NULL,
    #     **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG,
    # )
    learning_type = models.ForeignKey(
        to=CertificateLearningType,
        on_delete=models.SET_NULL,
        **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG
    )
    sponsor_logo = models.ForeignKey(
        to=CertificateSponsorImage,
        on_delete=models.SET_NULL,
        **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG
    )
    keep_techademy_logo = models.CharField(
        max_length=COMMON_CHAR_FIELD_MAX_LENGTH,
        choices=LOGO_TYPE_CHOICES,
    )
    orientation = models.CharField(
        max_length=COMMON_CHAR_FIELD_MAX_LENGTH,
        choices=ORIENTATION_CHOICES,
    )
    headline_text = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH)
    body_text = models.TextField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    image = models.ForeignKey(
        to=CertificateImage,
        on_delete=models.SET_NULL,
        **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG
    )