from django.db import models
from apps.access.models import User
from apps.learning.models import Course
from apps.common.models import (
    COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG,
    COMMON_CHAR_FIELD_MAX_LENGTH,
    BaseModel,
)
from apps.jobs.models import Job
from apps.learning.models.linkages import JobEligibleSkill

class UserAssessmentResult(BaseModel):
    """Model to store Assessment Result of a User"""

    DYNAMIC_KEY = "user-assessment-result"

    result = models.JSONField()
    user = models.ForeignKey(
        to=User, 
        on_delete=models.SET_NULL,
        null = True
    )
    assessment_id = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH, **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    assessment_name = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH)
    assessment_date = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH)
    score_percentage = models.FloatField(
        **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG
    )
    result_status = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH)
    course = models.ForeignKey(to=Course, on_delete=models.SET_NULL, null=True)

class JobAssessmentResult(BaseModel):
    """Model to store Job assessment results"""

    DYNAMIC_KEYS = "job-assessment-result"

    result = models.JSONField()
    user = models.ForeignKey(to=User, on_delete=models.SET_NULL, null=True)
    assessment_id = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH, **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    assessment_name = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH)
    assessment_date = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH)
    score_percentage = models.FloatField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    result_status = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH)
    job = models.ForeignKey(to=Job, on_delete=models.SET_NULL, null=True)

class JobEligibleSkillAssessment(BaseModel):
    """Model to store Job Eligible Skill Assessment Result"""

    DYNAMIC_KEY = "job-eligible-skill-assessment-result"

    result = models.JSONField()
    user = models.ForeignKey(
        to=User, 
        on_delete=models.SET_NULL,
        null = True
    )
    assessment_id = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH, **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    assessment_name = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH)
    assessment_date = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH)
    score_percentage = models.FloatField(
        **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG
    )
    result_status = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH)
    job_eligible_skill = models.ForeignKey(to=JobEligibleSkill, on_delete=models.SET_NULL, null=True)       