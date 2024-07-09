from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.generics import ListAPIView, RetrieveAPIView
import requests
from apps.common.pagination import AppPagination
from apps.common.serializers import get_app_read_only_serializer
from apps.common.views.api.base import AppAPIView, NonAuthenticatedAPIMixin
from apps.common.views.api.generic import (
    DEFAULT_IDENTITY_DISPLAY_FIELDS,
    AbstractLookUpFieldMixin,
)
from apps.jobs.models import (
    EducationQualification,
    FunctionalArea,
    HiringCompany,
    Industry,
    Job,
    Location,
    Role,
    JobAppliedList
)
from apps.jobs.serializers import JobApplicantAssessmentResultSerializer, JobSerializer, JobDetailSerializer, JobApplicantListSerializer
from apps.learning.models import Skill
from apps.meta.models import UserGender
from apps.access.authentication import get_user_headers
from apps.web_portal.models.assessment import JobAssessmentResult
from config import settings


class JobsListAPIView(NonAuthenticatedAPIMixin, ListAPIView, AppAPIView):
    """Sends out data for the Jobs Listing Page."""

    filter_backends = [DjangoFilterBackend]
    filterset_fields = "__all__"
    pagination_class = AppPagination
    serializer_class = JobSerializer
    queryset = Job.objects.all()

    def get_queryset(self, *args, **kwargs):
        return Job.objects.filter(created_by=self.get_user())


class JobsDetailAPIView(
    NonAuthenticatedAPIMixin, AbstractLookUpFieldMixin, RetrieveAPIView, AppAPIView
):
    """Sends out data for the Jobs Detail Page."""

    serializer_class = JobDetailSerializer
    queryset = Job.objects.all()


class JobsFilterMetaAPIView(NonAuthenticatedAPIMixin, AppAPIView):
    """This API returns the metadata for Jobs filter in listing page."""

    def get(self, request, *args, **kwargs):
        filter_meta_data = {
            "companies": get_app_read_only_serializer(
                HiringCompany, meta_fields=DEFAULT_IDENTITY_DISPLAY_FIELDS
            )(HiringCompany.objects.all(), many=True).data,
            "skills": get_app_read_only_serializer(
                Skill, meta_fields=DEFAULT_IDENTITY_DISPLAY_FIELDS
            )(Skill.objects.filter(is_archived=False), many=True).data,
            "role": get_app_read_only_serializer(
                Role, meta_fields=DEFAULT_IDENTITY_DISPLAY_FIELDS
            )(Role.objects.all(), many=True).data,
            "locations": get_app_read_only_serializer(
                Location, meta_fields=DEFAULT_IDENTITY_DISPLAY_FIELDS
            )(Location.objects.all(), many=True).data,
            "education_qualification": get_app_read_only_serializer(
                EducationQualification, meta_fields=DEFAULT_IDENTITY_DISPLAY_FIELDS
            )(EducationQualification.objects.all(), many=True).data,
            "functional_areas": get_app_read_only_serializer(
                FunctionalArea, meta_fields=DEFAULT_IDENTITY_DISPLAY_FIELDS
            )(FunctionalArea.objects.all(), many=True).data,
            "industry_type": get_app_read_only_serializer(
                Industry, meta_fields=DEFAULT_IDENTITY_DISPLAY_FIELDS
            )(Industry.objects.all(), many=True).data,
            "genders": get_app_read_only_serializer(
                UserGender, meta_fields=DEFAULT_IDENTITY_DISPLAY_FIELDS
            )(UserGender.objects.all(), many=True).data,
        }
        return self.send_response(data=filter_meta_data)
    
class JobApplicantListAPIView(ListAPIView, AppAPIView):

    filter_backends = [DjangoFilterBackend]
    filterset_fields = "__all__"
    pagination_class = AppPagination
    serializer_class = JobApplicantListSerializer
    
    def get_queryset(self):
        user = self.get_user()
        return JobAppliedList.objects.filter(job__created_by=user).exclude(status="pending_assessment")
    
class GetAssessmentList(AppAPIView):

    def get(self, request, *args, **kwargs):
       
        """Use IDP to handle the same."""
        user = self.get_user()
        headers = get_user_headers(user)
        result_data = []

        idp_response = requests.get(settings.IDP_CONFIG['yaksha_host'] + settings.IDP_CONFIG['yaksha_assessment_get_url'], headers=headers)
        
        data = idp_response.json()
        assessment_data = data["result"]["assessments"]
        for assessment in assessment_data:
            name = assessment["name"]
            assessment_id = assessment["assessmentIdNumber"]
            result = {
                "identity" : name,
                "id" : assessment_id
            }
            result_data.append(result)
        return self.send_response(data=result_data)


class GetJobAplicantAsessmentResult(AppAPIView):

    def get(self, request, job_id, user_id, *args, **kwargs):
        applicant_assessment_results = JobAssessmentResult.objects.filter(
            job_id = job_id, user = user_id
        )
        serializer = JobApplicantAssessmentResultSerializer(applicant_assessment_results, many=True)

        result_data = serializer.data
        return self.send_response(data=result_data)