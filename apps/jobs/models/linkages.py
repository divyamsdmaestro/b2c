from django.db import models
from apps.common import model_fields
from apps.common.models import (
    COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG,
    COMMON_CHAR_FIELD_MAX_LENGTH,
    BaseModel,
    FileOnlyModel
)

class JobCriteria(BaseModel):
    DYNAMIC_KEY = "job-criteria"
    identity = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH,**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)

class EducationQualification(BaseModel):
    """This model holds the fields of `EducationQualification`."""

    DYNAMIC_KEY = "education-qualification"
    identity = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH)

class FunctionalAreaImage(FileOnlyModel):

    file = model_fields.AppSingleFileField(
        upload_to="files/functional_area/image/",
    )

class FunctionalArea(BaseModel):
    """This model holds the fields of `FunctionalArea`."""

    DYNAMIC_KEY = "job-functional-area"
    identity = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH)
    image = models.ForeignKey(to=FunctionalAreaImage, on_delete=models.SET_NULL,
        **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG,)
    is_this_functional_area_popular=models.BooleanField(default=False)


class Industry(BaseModel):
    """This model holds the fields of `Industry`."""

    DYNAMIC_KEY = "job-industry"
    identity = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH)


class Role(BaseModel):
    """This model holds the fields of `Role`."""

    DYNAMIC_KEY = "job-role"
    identity = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH)


class JobPerk(BaseModel):
    """This model holds the fields of `JobPerk`."""

    DYNAMIC_KEY = "job-perks"

    job = models.ForeignKey(
        to="jobs.Job",
        related_name="related_perks",
        on_delete=models.SET_NULL,
        **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG
    )

    identity = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH)
    description = models.TextField()

# class JobTitle(BaseModel):
#     """This model holds the fields of `JobTitle`."""

#     DYNAMIC_KEY = "job-title"
#     identity = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH)
class BulkUploadTemplate(FileOnlyModel):
    file = model_fields.AppSingleFileField(
        upload_to="files/upload/bulk-template/",
    )

class BulkUploadTemplateData(BaseModel):
    DYNAMIC_KEY = "bulk-upload-template"

    identity = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH)
    image = models.ForeignKey(
        to=BulkUploadTemplate,
        on_delete=models.SET_NULL,
        **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG
    )