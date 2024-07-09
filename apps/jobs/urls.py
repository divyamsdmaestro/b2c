from django.urls import path
from rest_framework.routers import SimpleRouter
from apps.common.serializers import get_app_read_only_serializer as read_serializer
from apps.jobs.serializers import JobAppliedListAssessmentSerializer
from ..cms.views import get_model_cud_api_viewset, get_model_list_api_viewset, get_employer_job_list_api_viewset, get_job_applied_list_api_viewset
from ..common.views.api import get_upload_api_view
from ..learning.models import Skill, JobEligibleSkill, Category
from ..meta.models import UserGender
from apps.access.models import User
from . import models, views
from .models import Job
from apps.meta.models import location as location_models
from apps.hackathons.models import industry as industry_models
from apps.jobs.models import linkages as linkage_models
from apps.meta.models import profile as profile_models

app_name = "jobs"
API_ADMIN_URL_PREFIX = "api/cms/"
API_URL_PREFIX = "api/jobs/"


router = SimpleRouter()


# Job Related Models
# --------------------------------------------------------------------------------------
router.register(
    f"{API_ADMIN_URL_PREFIX}job/cud",
    get_model_cud_api_viewset(
        meta_model=Job,
        meta_fields=[
            "identity",
            "job_role",
            "job_image",
            "description",
            "benefits",
            "categories",
            "skills",
            "job_eligibility_skills",
            "country",
            "state",
            "city",
            "workplace_type",
            "employement_type",
            "number_of_vacancies",
            "salary_detail",
            "industry",
            "functional_area",
            "education_expect",
            # "minimum_experience",
            # "maximum_experience",
            # "eligibility_criteria",
            "job_round_details",
        ],
        meta_extra_kwargs={
            "categories": {"allow_empty": False},
            "job_eligibility_skills": {"allow_empty": False},
        },
        get_serializer_meta=lambda x: {
            "categories": x.serialize_for_meta(Category.objects.all()),
            "skills": x.serialize_for_meta(Skill.objects.filter(is_archived=False), fields=["id", "identity", "category"]),
            "job_eligibility_skills": x.serialize_for_meta(JobEligibleSkill.objects.all(), fields=["id", "identity", "category"]),
            "country": x.serialize_for_meta(location_models.Country.objects.all()),
            "state": x.serialize_for_meta(location_models.State.objects.all(), fields=['id', 'uuid', 'identity','country']),
            "city": x.serialize_for_meta(location_models.City.objects.all(), fields=['id', 'uuid', 'identity','state']),
            "industry": x.serialize_for_meta(industry_models.IndustryType.objects.all()),
            "criteria": x.serialize_for_meta(linkage_models.JobCriteria.objects.all()),
            "functional_area": x.serialize_for_meta(linkage_models.FunctionalArea.objects.all()),
            "education_expect": x.serialize_for_meta(linkage_models.EducationQualification.objects.all()),
        },
    ),
)
router.register(
    f"{API_ADMIN_URL_PREFIX}job/list",
    get_employer_job_list_api_viewset(
        meta_queryset=models.Job.objects.all(),
        meta_all_table_columns={"identity": "Job Title", "job_role": "Job Role", "city": "Job Location", "employement_type": "Employement Type"},
    ),
)

# Job Applied List
router.register(
    f"{API_ADMIN_URL_PREFIX}applicant/list",
    get_job_applied_list_api_viewset(
        meta_queryset=models.JobAppliedList.objects.all(),
        meta_all_table_columns={"user__first_name": "Applicant Name", "job_detail__identity":"Applied For Job", "user__idp_email": "Contact Email", "status":"status"},
        meta_init_fields_config={
            "job_detail": read_serializer(
                meta_model=Job, meta_fields=['id', 'identity'],
            )(source="job"),
            "user": read_serializer(
                meta_model=User, meta_fields=['id', 'uuid', 'first_name', 'idp_email'],
                init_fields_config={
                    "resume_detail": read_serializer(
                        meta_model=profile_models.UserProfileResume, meta_fields=['id', 'file']
                    )(source="resume"),
                }
            )(source="created_by"),
            "round_details": JobAppliedListAssessmentSerializer(source="*"),
        },
        fields_to_filter=["status"]
    ),
)


# Hiring Company Related Models
# --------------------------------------------------------------------------------------
router.register(
    f"{API_ADMIN_URL_PREFIX}{models.HiringCompany.DYNAMIC_KEY}/cud",
    get_model_cud_api_viewset(
        meta_model=models.HiringCompany,
        meta_fields=[
            "identity",
            "description",
            "image",
        ],
        meta_extra_kwargs={},
        get_serializer_meta=lambda x: {},
    ),
)
router.register(
    f"{API_ADMIN_URL_PREFIX}{models.Job.DYNAMIC_KEY}/list",
    get_model_list_api_viewset(
        meta_queryset=models.Job.objects.all(),
        meta_all_table_columns={"identity": "Name", "description": "Description"},
    ),
)


# Job Perks Related Models
# --------------------------------------------------------------------------------------
router.register(
    f"{API_ADMIN_URL_PREFIX}{models.JobPerk.DYNAMIC_KEY}/cud",
    get_model_cud_api_viewset(
        meta_model=models.JobPerk,
        meta_fields=[
            "identity",
            "description",
        ],
        meta_extra_kwargs={},
        get_serializer_meta=lambda x: {},
    ),
)
router.register(
    f"{API_ADMIN_URL_PREFIX}{models.JobPerk.DYNAMIC_KEY}/list",
    get_model_list_api_viewset(
        meta_queryset=models.JobPerk.objects.all(),
        meta_all_table_columns={"identity": "Name", "description": "Description"},
        fields_to_filter=["job"],
    ),
)


urlpatterns = [
    path(
        f"{API_ADMIN_URL_PREFIX}job/job_image/upload/",
        get_upload_api_view(meta_model=models.JobImage).as_view(),
    ),
    path(
        f"{API_ADMIN_URL_PREFIX}{models.HiringCompanyImage.DYNAMIC_KEY}/image/upload/",
        get_upload_api_view(meta_model=models.HiringCompanyImage).as_view(),
    ),
    path(
        f"{API_URL_PREFIX}filters/meta/",
        views.JobsFilterMetaAPIView.as_view(),
    ),
    path(
        f"{API_ADMIN_URL_PREFIX}job/<uuid>/view/",
        views.JobsDetailAPIView.as_view(),
    ),
    path(
        f"{API_ADMIN_URL_PREFIX}job/assessment/list/",
        views.GetAssessmentList.as_view(),
    ),
    path(
        f"{API_ADMIN_URL_PREFIX}job/applicant/",
        views.JobApplicantListAPIView.as_view(),
    ),
    path(
        f"{API_ADMIN_URL_PREFIX}job/applicant/result/<job_id>/<user_id>/",
        views.GetJobAplicantAsessmentResult.as_view(),
    )
] + router.urls
