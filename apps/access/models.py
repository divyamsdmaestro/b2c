from django.contrib.auth.base_user import AbstractBaseUser
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
# from apps.badges.models.badges import Badges
from apps.common import model_fields
from apps.common.models import (
    COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG,
    COMMON_CHAR_FIELD_MAX_LENGTH,
    COMMON_NULLABLE_FIELD_CONFIG,
    BaseModel,
    FileOnlyModel,
)
from apps.meta.models import location as location_models
from apps.meta.models import profile as profile_models
from apps.learning.models import (
    Accreditation
)
from apps.common.helpers import validate_pincode
from apps.hackathons.models import industry as industry_models

class Permission(BaseModel):
    """
    Model Holds Permission Details
    """
    DYNAMIC_KEY = "permission"

    identity = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH)
    description = models.TextField()

class PermissionCategory(BaseModel):
    """
    Models Holds Permission Category Details"""
    DYNAMIC_KEY = "permission-category"

    identity = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH)
    permissions = models.ManyToManyField(Permission)

class RolePermission(BaseModel):
    """
    Model holds the detail of permission belongs to user role
    """
    DYNAMIC_KEY = "role-permission"

    permission = models.ForeignKey(
        Permission, on_delete=models.SET_NULL,
        **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG,
    )

    to_create = models.BooleanField(default=False)
    to_view = models.BooleanField(default=False)
    to_edit = models.BooleanField(default=False)
    to_delete = models.BooleanField(default=False)

class UserRole(BaseModel):
    """
    Model holds the detail of user roles
    """
    DYNAMIC_KEY = "role"

    identity = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH)
    description = models.TextField()
    role_permissions = models.ManyToManyField(RolePermission)


class User(BaseModel, AbstractBaseUser):
    """
    User model for the entire B2C application. There is no authentication
    involved with this model. Auth happen in the IDP server.

    This models holds data other than auth related data.
    """

    USERNAME_FIELD = "idp_user_id"

    # IDP & General
    # ----------------------------------------------------------------------------------
    idp_user_id = models.UUIDField(unique=True)

    full_name = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH)

    # Social Oauth
    # ----------------------------------------------------------------------------------
    socail_oauth = models.BooleanField(default=False)
    social_provider = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH, **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)

    # User Role
    # ----------------------------------------------------------------------------------
    user_role = models.ForeignKey(
        UserRole, on_delete=models.SET_NULL,
        **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG,
    )

    # Status active/inactive
    # ----------------------------------------------------------------------------------
    USER_STATUS_CHOICES = (
        ("active", "active"),
        ("inactive", "inactive"),
    )

    status = models.CharField(
        choices=USER_STATUS_CHOICES,
        default="active",
        max_length=COMMON_CHAR_FIELD_MAX_LENGTH,
    )

    user_name = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH,**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    idp_email = models.EmailField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG,)
    
    # Email ID
    alternative_email = models.EmailField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG,)
    phone_number = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH,**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    # Onboarding
    # ----------------------------------------------------------------------------------
    onboarding_level = models.ForeignKey(
        to="meta.OnboardingLevel",
        on_delete=models.SET_NULL,
        **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG,
    )
    onboarding_highest_education = models.ForeignKey(
        to="meta.OnboardingHighestEducation",
        on_delete=models.SET_NULL,
        **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG,
    )
    onboarding_area_of_interests = models.ManyToManyField(
        to="learning.Skill", blank=True,
    )

    # Settings
    # ----------------------------------------------------------------------------------
    # privacy settings
    enable_education = models.BooleanField(default=False)
    enable_address = models.BooleanField(default=False)
    enable_profile_picture = models.BooleanField(default=False)
    enable_social_handles = models.BooleanField(default=False)

    # notification settings
    enable_pause_notification = models.BooleanField(default=False)

    # general Settings
    enable_font_style = models.BooleanField(default=False)
    font_style = models.ForeignKey(
        to="meta.FontStyle",
        on_delete=models.SET_NULL,
        **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG,
    )
    enable_autoplay_video = models.BooleanField(default=False)

    # social handles
    social_handles = models.ManyToManyField(
        to="meta.UserSocialMediaHandle",
    )
    
    #reward points
    current_reward_points = models.IntegerField(default=0)
    total_reward_points = models.IntegerField(default=0)
    used_reward_points = models.IntegerField(default=0)
    
    #badge points
    # total_badge_points = models.IntegerField(default=0)


    # Profile
    # ----------------------------------------------------------------------------------
    # student
    first_name = models.CharField(
        max_length=COMMON_CHAR_FIELD_MAX_LENGTH,
        **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG,
    )
    middle_name = models.CharField(
        max_length=COMMON_CHAR_FIELD_MAX_LENGTH,
        **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG,
    )
    last_name = models.CharField(
        max_length=COMMON_CHAR_FIELD_MAX_LENGTH,
        **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG,
    )
    admission_id = models.CharField(
        max_length=COMMON_CHAR_FIELD_MAX_LENGTH,
        **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG,
    )

    gender = models.ForeignKey(
        to="meta.UserGender",
        on_delete=models.SET_NULL,
        **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG,
    )
    # martial_status = models.ForeignKey(
    #     profile_models.UserMartialStatus,
    #     on_delete=models.SET_NULL,
    #     **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG,
    # )
    birth_date = models.DateField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)

    # identification
    identification_type = models.ForeignKey(
        to="meta.UserIdentificationType",
        on_delete=models.SET_NULL,
        **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG,
    )
    identification_number = models.CharField(
        max_length=COMMON_CHAR_FIELD_MAX_LENGTH,
        **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG,
    )

    # location related
    address = models.TextField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
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
    pincode = models.PositiveIntegerField(validators=[validate_pincode],**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)

    # user resume
    resume = models.ForeignKey(
        to="meta.UserProfileResume",
        on_delete=models.SET_NULL,
        **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG,
    )
    # user profile image
    profile_image = models.ForeignKey(
        to="meta.UserProfileImage",
        on_delete=models.SET_NULL,
        **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG,
    )
    # user education details
    education_details = models.ManyToManyField(
        to="meta.EducationDetail",
        blank=True
    )
    # user job details
    job_details = models.ManyToManyField(
        to="meta.UserJobDetail",
        blank=True
    )
    # user career highlights
    career_highlights = models.ForeignKey(
        to="meta.CareerHighlights",
        on_delete=models.SET_NULL,
        **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG
    )

    # Interview Panel Additional Details
    job_role = models.CharField(
        max_length=COMMON_CHAR_FIELD_MAX_LENGTH,
        **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG,
    )
    experience_years = models.PositiveIntegerField(
        **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG
    )
    industry_type = models.ForeignKey(
        to=industry_models.IndustryType,
        on_delete=models.SET_NULL,
        null=True
    )
    corporate = models.ForeignKey(
        to="access.EmployerDetail",
        on_delete=models.SET_NULL,
        **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG
    )

    def __str__(self):
        return f"{self.idp_user_id} - {self.full_name}"
    
# Employer Details
class EmployerLogoImage(FileOnlyModel):
    """Image data for a `EmployerBanner`."""

    DYNAMIC_KEY = "Employer-logo-image"

    file = model_fields.AppSingleFileField(
        upload_to="files/employer_logo/image/",
    ) 

class EmployerDetail(BaseModel):
    DYNAMIC_KEY = "corporate"
    """
    Model to Save Employer Detail.
    """
    identity = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH)
    description = models.TextField()
    logo_image = models.ForeignKey(to=EmployerLogoImage, on_delete=models.SET_NULL,
        **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG,)
    
    # Contact Details
    contact_email_id = models.EmailField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG,)
    alternative_conatct_email_id = models.EmailField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG,)
    contact_number = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH)

    # location related
    locality_street_address = models.TextField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
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
    pincode = models.PositiveIntegerField(validators=[validate_pincode],**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)

    # Representative 
    representative = models.ForeignKey(
        to=User, on_delete=models.SET_NULL,
        **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG,
    )

# Institution Details
class InstitutionBannerImage(FileOnlyModel):
    """Image data for a `InstitutionBanner`."""

    DYNAMIC_KEY = "institution-banner-image"

    file = model_fields.AppSingleFileField(
        upload_to="files/institution_banner/image/",
    ) 

class InstitutionDetail(BaseModel):
    DYNAMIC_KEY = "institution"
    """
    Model to Save Institution Detail.
    """
    identity = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH)
    banner_image = models.ForeignKey(to=InstitutionBannerImage, on_delete=models.SET_NULL,
        **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG,)
    
    # Contact Details
    contact_email_id = models.EmailField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG,)
    alternative_conatct_email_id = models.EmailField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG,)
    contact_number = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH)

    # Accreditation
    accreditation = models.ForeignKey(
        to=Accreditation, on_delete=models.SET_NULL,
        **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG,
    )

    # location related
    locality_street_address = models.TextField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
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
    pincode = models.PositiveIntegerField(validators=[validate_pincode],**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)

    # Courses
    courses = models.ManyToManyField(to="learning.Course", blank=True,)
    learning_paths = models.ManyToManyField(to="learning.LearningPath", blank=True,)
    certification_paths = models.ManyToManyField(to="learning.CertificationPath", blank=True,)

    # Representative 
    representative = models.ForeignKey(
        to=User, on_delete=models.SET_NULL,
        **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG,
    )

class InstitutionUserGroupDetail(BaseModel):
    
    """
    Admin and Institute User Groups are manintaine in same table
    """

    DYNAMIC_KEY = "institution-user-group"

    identity = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH)
    description = models.TextField()
    user = models.ManyToManyField(
        to="access.User", blank=True,
    )
    institution = models.ForeignKey(
        InstitutionDetail, on_delete=models.SET_NULL,
        **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG,
    )
    status = models.BooleanField(default=True)
    admin_created = models.BooleanField(default=True)


class InstitutionUserGroupContent(BaseModel):

    DYNAMIC_KEY = "institution-user-group-content"

    identity = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH)
    description = models.TextField()
    user_group = models.ManyToManyField(
        to=InstitutionUserGroupDetail, blank=True,
    )
    courses = models.ManyToManyField(to="learning.Course", blank=True,)
    learning_path = models.ManyToManyField(to="learning.LearningPath", blank=True,)
    certification_path = models.ManyToManyField(to="learning.CertificationPath", blank=True,)
    status = models.BooleanField(default=True)


class StudentReportFile(FileOnlyModel):
    """file for a `StudentReport`."""

    DYNAMIC_KEY = "student-report"

    file = model_fields.AppSingleFileField(
        upload_to="files/student/report/",
    )

class ReportFilterParameter(BaseModel):
    """data for a `StudentReportFilterParameter`."""

    DYNAMIC_KEY = "report-filter-parameter"
    # parameters
    identity = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH)

class StudentReportDetail(BaseModel):
    """data for a `StudentReport`."""

    DYNAMIC_KEY = "student-report-detail"
    # report name
    identity = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH)
    # file
    report = models.ForeignKey(
        to=StudentReportFile,
          on_delete=models.SET_NULL,
        **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG,
        )

    user_group = models.ForeignKey(
        to=InstitutionUserGroupDetail,
          on_delete=models.SET_NULL,
        **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG,
        )

    content_group = models.ForeignKey(
        to=InstitutionUserGroupContent,
        on_delete=models.SET_NULL,
        **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG,
        )

    start_date = models.DateField()

    end_date = models.DateField()

    filter_parameters = models.ManyToManyField(to=ReportFilterParameter, blank=True)
    
# class UserBadges(BaseModel):
    
#     """
#     Holds the `All Users badges and their points` details
#     """
#     user = models.ForeignKey(to=User,on_delete=models.SET_NULL,**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
#     badges = models.ForeignKey(to=Badges,on_delete=models.SET_NULL,**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
#     points = models.IntegerField(default = 0)

class GuestUser(BaseModel):
    """
    This models holds data other than auth new user related data.
    """
    pass
