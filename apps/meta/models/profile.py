"""Contains models related to user's profile and onboarding."""
from django.db import models
from apps.common.helpers import validate_image, validate_resume
from apps.hackathons.models import industry as industry_models
from apps.common import model_fields
from apps.common.models import COMMON_CHAR_FIELD_MAX_LENGTH, BaseModel, FileOnlyModel
from apps.common.models import COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG
from apps.meta.models import location as location_models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from apps.jobs.models import EducationQualification

class SocialPlatform(BaseModel):
    """Contains social platforms used in the application."""

    identity = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH)


class UserEducationDetail(BaseModel):
    """Model contains educational details for user (profile settings)."""

    college_name = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH)
    university_name = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH)
    degree = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH)


class UserSocialMediaHandle(BaseModel):
    """Holds the data for user's social media handles."""

    platform = models.ForeignKey(to=SocialPlatform, on_delete=models.CASCADE)
    link = models.URLField()


class FontStyle(BaseModel):
    """Holds font-style and font related settings."""

    identity = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH)


class OnboardingLevel(BaseModel):
    """Dropdown data for onboarding step 1 page."""
    DYNAMIC_KEY = "onboarding-level"

    identity = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH)


class OnboardingHighestEducation(BaseModel):
    """Holds data for step 2 in user onboarding."""
    DYNAMIC_KEY = "onboarding-highest-education"

    identity = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH)


class OnboardingAreaOfInterest(BaseModel):
    """Data for user onboarding step 2."""
    DYNAMIC_KEY = "onboarding-area-of-interest"

    identity = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH)


class UserGender(BaseModel):
    """Holds gender data for an user."""

    DYNAMIC_KEY = "user-gender"

    identity = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH, unique=True)


class UserIdentificationType(BaseModel):
    """Holds various methods for identifying the user like pan, aadhaar etc."""
    DYNAMIC_KEY = "user-identification-type"

    identity = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH)


class UserMartialStatus(BaseModel):
    """Holds martial status of a user."""
    DYNAMIC_KEY = "user-martial-status"

    identity = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH)


class UserProfileResume(FileOnlyModel):
    """Holds the resume data for an `User`."""

    file = model_fields.AppSingleFileField(
        upload_to="files/user_profile/resume/",validators=[validate_resume]
    )


class UserProfileImage(FileOnlyModel):
    """Holds the profile image for an `User`."""

    file = model_fields.AppSingleFileField(
        upload_to="files/user_profile/image/",validators=[validate_image]
    )

class EducationUniversity(BaseModel):
    """Holds data for a `EducationUniversity`."""

    DYNAMIC_KEY = "university"
    identity = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH)


class EducationDetail(BaseModel):
    """Model contains education details for User(Student)."""

    DYNAMIC_KEY = "education-details"

    # FK fields
    qualification = models.ForeignKey(
        to=EducationQualification,
        related_name="qualification_detail",
        on_delete=models.SET_NULL,
        **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG
    )
    university_name = models.ForeignKey(
        to=EducationUniversity,
        related_name="university_name",
        on_delete=models.SET_NULL,
        **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG
    )
    degree = models.ForeignKey(
        to=OnboardingHighestEducation,
        related_name="degree",
        on_delete=models.SET_NULL,
        **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG
    )
    # fields
    college_name = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH, **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    class_name = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH, **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    overall_percentage = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH, **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)


class EmploymentType(BaseModel):
    """Holds data for a `EmploymentType`."""

    DYNAMIC_KEY = "employment-type"
    identity = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH)

class UserProject(BaseModel):
    """Holds data for a `UserProject`."""

    DYNAMIC_KEY = "user-project"
    identity = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH,**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    description = models.TextField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)

class CareerHighlights(BaseModel):
    """Holds data for a `CareerHighlights`."""

    DYNAMIC_KEY = "personal-detail"
    # M to M fields
    skills = models.ManyToManyField(
        to="learning.Skill",
        blank=True,
    )
    languages = models.ManyToManyField(
        to="learning.Language",
        blank=True,
    )
    interests = models.ManyToManyField(
        OnboardingAreaOfInterest,
        blank=True,
        )
    projects = models.ManyToManyField(
        UserProject,
        blank=True,
    )
    # Fields
    achievements = models.TextField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)


class UserJobDetail(BaseModel):
    """This model holds the fields of `Job`."""

    DYNAMIC_KEY = "user-job"

    # FK fields
    employment_type = models.ForeignKey(
        EmploymentType,
        on_delete=models.SET_NULL,
        **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG
    )
    # job_title = models.ForeignKey(
    #     to="jobs.JobTitle",
    #     on_delete=models.SET_NULL,
    #     **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG
    # )
    location = models.ForeignKey(
        location_models.City,
        on_delete=models.SET_NULL, 
        **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG
    )
    industry = models.ForeignKey(
        to=industry_models.IndustryType,
        on_delete=models.SET_NULL,
        **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG
    )
    # Fields
    job_title = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH,**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    employer_name = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH,**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    job_summary = models.TextField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    start_date = models.DateField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    end_date = models.DateField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)