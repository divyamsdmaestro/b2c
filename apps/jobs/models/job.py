from django.db import models
from apps.hackathons.models import industry as industry_models
from apps.common.models import (
    COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG,
    COMMON_CHAR_FIELD_MAX_LENGTH,
    BaseModel,
    FileOnlyModel
)
from apps.jobs.models import linkages as linkage_models
from apps.common import model_fields
from apps.meta.models import location as location_models


JOB_ROUND_TYPE = (
    ("assessment", "assessment"),
    ("coding", "coding"),
    ("group_discussion", "group_discussion"),
    ("interview", "interview"),
)

class JobEligibilityCriteria(BaseModel):

    DYNAMIC_KEY = "job-eligibility-criteria"

    criteria = models.ForeignKey(to=linkage_models.JobCriteria,
        on_delete=models.SET_NULL,
        **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    Value = models.FloatField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)

class JobRoundDetails(BaseModel):

    DYNAMIC_KEY = "job-round-details"

    title = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH, **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    type = models.CharField(choices=JOB_ROUND_TYPE, max_length=COMMON_CHAR_FIELD_MAX_LENGTH, default="interview")
    description = models.TextField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    assessment_id = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH, **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    hackathon_id = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH, **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)

class JobImage(FileOnlyModel):
    """Image data for a `EmployerBanner`."""

    DYNAMIC_KEY = "job-image"

    file = model_fields.AppSingleFileField(
        upload_to="files/job/image/",
    ) 

class Job(BaseModel):
    """This model holds the fields of `Job`."""

    EMPLOYEMENT_TYPE = (
        ("full_time", "full_time"),
        ("part_time", "part_time"),
        ("contract", "contract"),
    )

    WORKPALCE_TYPE = (
        ("remote", "remote"),
        ("on_site", "on_site"),
        ("hybrid", "hybrid"),
    )

    DYNAMIC_KEY = "job-detail"

    identity = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH, **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    job_role = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH)

    job_image = models.ForeignKey(to=JobImage, on_delete=models.SET_NULL,
        **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG,)
    
    description = models.TextField()

    benefits = models.TextField()

    categories = models.ManyToManyField(to="learning.Category", blank=True)
    skills = models.ManyToManyField(to="learning.Skill", blank=True,)
    job_eligibility_skills = models.ManyToManyField(to="learning.JobEligibleSkill", blank=True,)

    # location related
    city = models.ForeignKey(
        location_models.City,
        on_delete=models.SET_NULL,
        **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG,
    )
    state = models.ForeignKey(
        location_models.State,
        on_delete=models.SET_NULL,
        **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG,
    )
    country = models.ForeignKey(
        location_models.Country,
        on_delete=models.SET_NULL,
        **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG,
    )

    workplace_type = models.CharField(
        max_length=COMMON_CHAR_FIELD_MAX_LENGTH,
        choices=WORKPALCE_TYPE,
        null=True
    )

    employement_type = models.CharField(
        max_length=COMMON_CHAR_FIELD_MAX_LENGTH,
        choices=EMPLOYEMENT_TYPE,
        null=True
    )

    number_of_vacancies = models.PositiveIntegerField(default=1)

    salary_detail = models.PositiveIntegerField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)

    industry = models.ForeignKey(
        to=industry_models.IndustryType,
        on_delete=models.SET_NULL,
        null=True
    )

    functional_area = models.ManyToManyField(
        to=linkage_models.FunctionalArea
    )

    education_expect = models.ManyToManyField(
        to=linkage_models.EducationQualification
    )

    minimum_experience = models.PositiveIntegerField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    maximum_experience = models.PositiveIntegerField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)

    eligibility_criteria = models.ManyToManyField(
        to=JobEligibilityCriteria,
    )

    job_round_details = models.ManyToManyField(
        to=JobRoundDetails
    )

    is_public = models.BooleanField(
        default=True
    )

    company = models.ForeignKey(to="access.EmployerDetail", on_delete=models.SET_NULL, 
                                **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG,)

class JobSavedlist(BaseModel):
    """
    Holds Job that are in the users wishlist.
    The created_by holds the user data.
    """

    job = models.ForeignKey(
        to=Job,
        on_delete=models.CASCADE,
    )

class JobAppliedList(BaseModel):

    JOB_STATUS = (
        ("pending_assessment", "pending_assessment"),
        ("shortlist", "shortlist"),
        ("applied_for_job", "applied_for_job"),
        ("interview_scheduled", "interview_scheduled"),
        ("recommended", "recommended"),
        ("offer_letter_initiated", "offer_letter_initiated"),
        ("rejected", "rejected"),
    )

    job=models.ForeignKey(
        to=Job, 
        on_delete=models.CASCADE,
    )

    status=models.CharField(
        max_length=COMMON_CHAR_FIELD_MAX_LENGTH,
        choices=JOB_STATUS,
        default="applied_for_job"
    )

class JobFeedbackAttachment(FileOnlyModel):

    DYNAMIC_KEY = "feedback-attachment"

    file = model_fields.AppSingleFileField(
        upload_to="files/feedback/image/",
    )

class JobFeedbackQuestion(BaseModel):
    """
    Model to store Feedback Questions
    """

    QUESTION_TYPE=(
        ("multiple_choice", "multiple_choice"),
        ("text_field", "text_field")
    )

    question = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH, **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    answer_type = models.CharField(
        max_length=COMMON_CHAR_FIELD_MAX_LENGTH,
        choices=QUESTION_TYPE,
        default="multiple_choice"
    )
    choice1 = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH, **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    choice2 = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH, **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    choice3 = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH, **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    choice4 = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH, **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)

class JobFeedbackQuestionAnswer(BaseModel):

    feedback_question = models.ForeignKey(
        to=JobFeedbackQuestion,
        on_delete=models.SET_NULL,
        null=True
    )

    text_area = models.TextField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)

    choice1 = models.BooleanField(default=False)
    choice2 = models.BooleanField(default=False)
    choice3 = models.BooleanField(default=False)
    choice4 = models.BooleanField(default=False)

class JobFeedbackTemplate(BaseModel):
    """
    Models to store Feedback Template
    """

    DYNAMIC_KEY = "feedback-template"

    identity = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH, **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    description = models.TextField()

    industry_type = models.ForeignKey(
        to=industry_models.IndustryType,
        on_delete=models.SET_NULL,
        null=True
    )

    comment_box_enable = models.BooleanField(
        default=True
    )

    attachment_enable = models.BooleanField(
        default=True
    )

    feedback_question = models.ManyToManyField(
        JobFeedbackQuestion,
    )

class JobInterviewSchedule(BaseModel):
    """
    Models to store Interview Schedules
    """

    INTERVIEW_STATUS = (
        ("in_process", "in_process"),
        ("shortlisted", "shortlisted"),
        ("rejected", "rejected"),
    )

    identity = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH, **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    description = models.TextField()

    applicant = models.ForeignKey(
        to="access.User",
        on_delete=models.CASCADE
    )

    job = models.ForeignKey(
        to=Job,
        on_delete=models.SET_NULL,
        null=True
    )

    job_round = models.ForeignKey(
        to=JobRoundDetails,
        on_delete=models.SET_NULL,
        null=True
    )

    schedule_date = models.DateField()
    start_time = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH, **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    end_time = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH, **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)

    interview_link = models.URLField(
        **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG
    )

    interview_panel = models.ForeignKey(
        to="access.User", on_delete=models.SET_NULL,
        null=True, related_name='interview_panel'
    )

    interview_status = models.CharField(
        max_length=COMMON_CHAR_FIELD_MAX_LENGTH,
        choices=INTERVIEW_STATUS,
        default="in_process"
    )

    interview_feedback_template = models.ForeignKey(
        to=JobFeedbackTemplate,
        on_delete=models.SET_NULL,
        null=True
    )

    is_feedback_send = models.BooleanField(
        default=False
    )

class JobFeedbackOption(BaseModel):
    """
    Feedback Options input
    """

    DYNAMIC_KEY = "feedback-option"

    interview_schedule = models.ForeignKey(
        to=JobInterviewSchedule,
        on_delete=models.SET_NULL,
        null=True
    )

    comment = models.TextField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    attachment = models.ManyToManyField(
        to=JobFeedbackAttachment, blank=True
    )

    feedback_question_answer = models.ManyToManyField(
        to=JobFeedbackQuestionAnswer,
    )

    is_shortlisted = models.BooleanField(
        default=True
    )

class FresherPoolApplicantStatus(BaseModel):
    STATUS_CHOICES = (
        ("new", "new"),
        ("shortlisted", "shortlisted"),
        ("rejected", "rejected")
    )

    user = models.ForeignKey(
        to="access.User",
        on_delete=models.SET_NULL,
        **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG
    )

    status = models.CharField(
        max_length=COMMON_CHAR_FIELD_MAX_LENGTH,
        choices=STATUS_CHOICES,
        default="new"
    )