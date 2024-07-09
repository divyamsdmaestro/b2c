from apps.common.views.api.base import NonAuthenticatedAPIMixin
from rest_framework.generics import ListAPIView, RetrieveAPIView
from apps.common.views.api import AppAPIView
from apps.jobs.models import job as job_models
from apps.jobs.serializers import JobLearnerListSerializer, JobLearnerDetailSerializer, JobSavedlistSerializer, JobAppliedListSerializer
from rest_framework.filters import SearchFilter
from ...common.pagination import AppPagination
from apps.common.views.api.generic import AbstractLookUpFieldMixin, DEFAULT_IDENTITY_DISPLAY_FIELDS
from django_filters.rest_framework import DjangoFilterBackend
from ..models import Testimonial
from apps.hackathons.models import hackathon as hackathon_models
from apps.common.serializers import get_app_read_only_serializer as read_serializer
from apps.jobs.models import linkages as linkage_models
from apps.access.models import EmployerDetail
from apps.meta.models import City
from datetime import datetime, timedelta


class JobPageAPIView(NonAuthenticatedAPIMixin, ListAPIView, AppAPIView):
    serializer_class = JobLearnerListSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = "__all__"
    search_fields = ['identity']
    pagination_class = AppPagination

    def get_queryset(self):
        qs = job_models.Job.objects.exclude(company=None)
        auth_user = self.get_authenticated_user()
        if auth_user:
            if auth_user.user_role and auth_user.user_role.identity == "Student":
                qs = job_models.Job.objects.filter(minimum_experience=0).exclude(company=None)

        return qs

class JobDetailPageAPIView(NonAuthenticatedAPIMixin, AbstractLookUpFieldMixin, RetrieveAPIView, AppAPIView):
    queryset = job_models.Job.objects.all()
    serializer_class = JobLearnerDetailSerializer

class JobAddToSavedlistAPIView(AppAPIView):
    """
    View used to add entities like Course, Learning Path, Certification Path
    into the users wishlist. This works in a toggle way(add & then delete).
    """

    def post(self, *args, **kwargs):
        """Handle on post."""

        uuid = kwargs["uuid"]
        user = self.get_user()

        job = job_models.Job.objects.get_or_none(uuid=uuid)
        if job:
            savedlist_instance = job_models.JobSavedlist.objects.get_or_none(
                job=job, created_by=user
            )

            if savedlist_instance:
                savedlist_instance.delete()
            else:
                job_models.JobSavedlist.objects.create(job=job, created_by=user)

        return self.send_response()

class MyJobSavedlistAPIView(ListAPIView, AppAPIView):
    """Sends out data for the Forum Post Listing Page."""

    filter_backends = [DjangoFilterBackend]
    filterset_fields = "__all__"
    pagination_class = AppPagination
    serializer_class = JobSavedlistSerializer
    queryset = job_models.JobSavedlist.objects.all()

    def get_queryset(self, *args, **kwargs):
        return job_models.JobSavedlist.objects.filter(created_by=self.get_user())
    
class JobAppliedAPIView(AppAPIView):
    """
    View used to add entities like Course, Learning Path, Certification Path
    into the users wishlist. This works in a toggle way(add & then delete).
    """

    def post(self, *args, **kwargs):
        """Handle on post."""

        uuid = kwargs["uuid"]
        user = self.get_user()
        data = {}

        job = job_models.Job.objects.get_or_none(uuid=uuid)
        if job:
            instance = job_models.JobAppliedList.objects.get_or_none(
                job=job, created_by=user
            )
            rejected_applications = job_models.JobAppliedList.objects.filter(created_by=user, job__created_by=job.created_by, status="rejected")
            for rejected_application in rejected_applications:
                applied_date = rejected_application.created
                if isinstance(applied_date, datetime):
                    converted_applied_date = applied_date
                else:
                    converted_applied_date = datetime.strptime(applied_date, "%Y-%m-%d %H:%M:%S.%f")
                current_date = datetime.now()
                difference = current_date - converted_applied_date
                if difference < timedelta(days=6 * 30):
                    return self.send_error_response("User has rejected applications from the same employer")
            if instance:
                pass
            else:
                if job.job_round_details.filter(type='assessment').exists():
                    job_models.JobAppliedList.objects.create(job=job, created_by=user, status="pending_assessment")
                    data = {"assessment": True}
                else:
                    job_models.JobAppliedList.objects.create(job=job, created_by=user)

        return self.send_response(data=data)
    
class MyJobAppliedlistAPIView(ListAPIView, AppAPIView):
    """Sends out data for the Forum Post Listing Page."""

    filter_backends = [DjangoFilterBackend]
    filterset_fields = "__all__"
    pagination_class = AppPagination
    serializer_class = JobAppliedListSerializer

    def get_queryset(self, *args, **kwargs):
        job_status = self.request.query_params.get('job_status')
        if job_status:
            return job_models.JobAppliedList.objects.filter(created_by=self.get_user(), status=job_status)
        else:
            return job_models.JobAppliedList.objects.filter(created_by=self.get_user())
        
class MyJobAppliedMetaAPIView(AppAPIView):

    def get(self, request):
        shotlist_count = job_models.JobAppliedList.objects.filter(created_by=self.get_user(), status="shortlist").count()
        applied_for_job_count = job_models.JobAppliedList.objects.filter(created_by=self.get_user(), status="applied_for_job").count()
        interview_sheduled_count = job_models.JobAppliedList.objects.filter(created_by=self.get_user(), status="interview_sheduled").count()
        rejected_count = job_models.JobAppliedList.objects.filter(created_by=self.get_user(), status="rejected").count()
        data =[
            {
                "identity": "shortlist",
                "count": shotlist_count
            },
            {
                "identity": "applied_for_job",
                "count": applied_for_job_count
            },
            {
                "identity": "interview_sheduled",
                "count": interview_sheduled_count
            },
            {
                "identity": "rejected",
                "count": rejected_count
            },
        ]

        return self.send_response(data=data)
    
class JobMetaAPIView(NonAuthenticatedAPIMixin, AppAPIView):
    """Provides Meta Data for filtering"""

    def get(self, request):
        data = {
            "company": read_serializer(
                EmployerDetail, DEFAULT_IDENTITY_DISPLAY_FIELDS
            )(EmployerDetail.objects.all(), many=True).data,
            "city": read_serializer(
                City, DEFAULT_IDENTITY_DISPLAY_FIELDS
            )(City.objects.all(), many=True).data,
            "functional_area": read_serializer(
                linkage_models.FunctionalArea, DEFAULT_IDENTITY_DISPLAY_FIELDS
            )(linkage_models.FunctionalArea.objects.all(), many=True).data,
            "education_expect": read_serializer(
                linkage_models.EducationQualification, DEFAULT_IDENTITY_DISPLAY_FIELDS
            )(linkage_models.EducationQualification.objects.all(), many=True).data,
        }

        return self.send_response(data=data)


class JobHomePageAPIView(NonAuthenticatedAPIMixin, AppAPIView):
    """Sends out data for the website home/landing page."""

    def get(self, *args, **kwargs):
        """Handle on get method."""

        return self.send_response(
            data={
                "popular_functional_area": read_serializer(
                    meta_model=linkage_models.FunctionalArea, meta_fields=['id', 'identity'],
                    init_fields_config={
                        "image_details": read_serializer(
                            meta_model=linkage_models.FunctionalAreaImage, meta_fields=['id', 'file']
                        )(source="image"),
                    }
                )(linkage_models.FunctionalArea.objects.all()[:5], many=True).data,
                "jobs": read_serializer(
                    meta_model=job_models.Job, meta_fields=['id', 'identity', 'description', 'city', 'created', 'employement_type', 'number_of_vacancies', 'salary_detail', 'workplace_type'],
                    init_fields_config={
                        "eligibility_criterias": read_serializer(
                            meta_model=job_models.JobEligibilityCriteria, meta_fields=['criteria', 'Value'],
                            init_fields_config={
                                "criteria_value": read_serializer(
                                    meta_model=linkage_models.JobCriteria, meta_fields=['identity'],
                                )(source="criteria"),
                            }
                        )(source="eligibility_criteria", many=True),
                    }
                )(job_models.Job.objects.all().order_by("-created")[:4], many=True).data,
                "hackathons": read_serializer(
                    meta_model=hackathon_models.Hackathon, meta_fields="__all__"
                )(hackathon_models.Hackathon.objects.all().order_by("-created")[:10], many=True).data,
                "testimonials": read_serializer(
                    meta_model=Testimonial, meta_fields="__all__"
                )(Testimonial.objects.all()[:20], many=True).data,
            }
        )
