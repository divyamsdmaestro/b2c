from django.db import models

from apps.common.models import (
    COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG,
    COMMON_CHAR_FIELD_MAX_LENGTH,
    BaseModel,
    FileOnlyModel,
)
from apps.common import model_fields

class JudgeImage(FileOnlyModel):
    """Image data for a `Hackathon`."""

    file = model_fields.AppSingleFileField(
        upload_to="files/judge/image/",
    )

class HackathonJudge(BaseModel):
    """
    This model holds information about the hackathon round Details.
    """

    DYNAMIC_KEY = "hackathon-judge"

    identity = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH)
    designation = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH, null=True)
    image = models.ForeignKey(to=JudgeImage, on_delete=models.SET_NULL, null=True)

class HackathonRoundDetails(BaseModel):
    """
    This model holds information about the hackathon round Details.
    """

    DYNAMIC_KEY = "hackathon-round-details"

    round_no = models.IntegerField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    desc = models.TextField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    round_start_date =  models.DateField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    round_start_time = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH,**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    round_end_date =  models.DateField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    round_end_time = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH,**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    passing_points = models.PositiveIntegerField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    # Judging Details
    judge = models.ForeignKey(to=HackathonJudge, on_delete=models.SET_NULL, null=True)
    judging_criteria = models.TextField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    judging_start_date =  models.DateField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    judging_end_date =  models.DateField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    judging_announcement_date =  models.DateField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)


class HackathonProjectLinks(BaseModel):
    """
    This model holds information about the hackathon project links details.
    """
    DYNAMIC_KEY = "hackathon-project-links"

    project_link = models.URLField(blank=True, default=None, null=True)

class HackathonSubmissionMediaFiles(BaseModel):
    """
    This model holds information about the hackathon project links details.
    """
    DYNAMIC_KEY = "hackathon-submission-media-files"

    file = model_fields.AppSingleFileField(
        upload_to="files/hackathon/submission/media/",
    )