from django.db import models

from apps.common import model_fields
from apps.common.models import (
    COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG,
    COMMON_CHAR_FIELD_MAX_LENGTH,
    BaseModel,
    FileOnlyModel,
)


class HiringCompanyImage(FileOnlyModel):
    """This model holds image of `HiringCompany`."""

    DYNAMIC_KEY = "hiring-company-image"

    file = model_fields.AppSingleFileField(
        upload_to="files/hiring_company/image/",
    )


class HiringCompany(BaseModel):
    """This model holds the fields of `HiringCompany`."""

    DYNAMIC_KEY = "hiring-company"

    identity = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH)
    description = models.TextField()
    image = models.ForeignKey(
        to=HiringCompanyImage,
        on_delete=models.SET_NULL,
        **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG
    )
