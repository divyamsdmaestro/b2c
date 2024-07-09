import base64
from django.utils.datetime_safe import datetime
import requests
from apps.access.models import User
from apps.common.helpers import EmailNotification, get_file_field_url
from apps.common.serializers import AppReadOnlyModelSerializer
from apps.common.views.api import AppAPIView
from rest_framework.generics import ListAPIView
from apps.jobs.models.job import FresherPoolApplicantStatus, Job, JobAppliedList
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter
from apps.common.pagination import AppPagination
from apps.learning.models.certificate import Certificate
from apps.learning.models.course import Course, CourseSubModule
from apps.meta.models.profile import EducationDetail
from apps.meta.models import profile as profile_models
from apps.my_learnings.models.trackers import StudentEnrolledCourseTracker, UserCourseTracker
from rest_framework import serializers
from apps.common.serializers import get_app_read_only_serializer as read_serializer
from apps.web_portal.models.assessment import UserAssessmentResult
from django.db.models import Subquery


class FresherPoolListAPIView(ListAPIView, AppAPIView):
    class _Serializer(AppReadOnlyModelSerializer):
        course = serializers.SerializerMethodField()
        status = serializers.SerializerMethodField()

        class Meta:
            fields = ["id", "uuid", "full_name", "idp_email", "phone_number", "course", "status"]
            model = User
        
        def get_course(self, obj):
            user_course = StudentEnrolledCourseTracker.objects.filter(created_by=obj, progress=100).order_by("-created").first()
            if user_course:
                return user_course.entity.identity
            else:
                return None
        
        def get_status(self, obj):
            try:
                applicant_status = FresherPoolApplicantStatus.objects.get(user=obj)
                return applicant_status.status
            except FresherPoolApplicantStatus.DoesNotExist:
                return "new"

    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = "__all__"
    search_fields = ["full_name", "idp_email"]
    pagination_class = AppPagination
    serializer_class = _Serializer

    def get_queryset(self, *args, **kwargs):
        user = self.get_user()
        jobs = Job.objects.filter(created_by=user)
        all_skills = []
        for job in jobs:
            skills = job.skills.all()
            all_skills.extend(skills)
        unique_skills = list(set(all_skills))
        students = User.objects.filter(user_role__identity="Student")
        students_with_matching_skills = User.objects.none()
        for student in students:
            courses = StudentEnrolledCourseTracker.objects.filter(created_by=student, progress=100)
            course_list = [course.entity for course in courses]
            for course in course_list:
                course_skills = course.skills.all()
                if any(skill in unique_skills for skill in course_skills):
                    students_with_matching_skills |= User.objects.filter(pk=student.pk)
            # skills = [skill.skills for skill in course_list]
        return students_with_matching_skills
    
class FresherPoolsMeta(AppAPIView):
    def get(self, request, *args, **kwargs):
        data={}
        data['columns']={
            "full_name": "First Name",
            "course": "Recent Course",
            "idp_email": "Email",
            "phone_number": "Phone Number",
            "status": "Status"
        }
        return self.send_response(data=data)
    
class EducationDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = EducationDetail
        fields = "__all__"

class GenderSerializer(serializers.ModelSerializer):
    class Meta:
        model = profile_models.UserGender
        fields = ['id', 'identity']

class ProfileImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = profile_models.UserProfileImage
        fields = ['id', 'uuid', 'file']

class UserSerializer(serializers.ModelSerializer):
    education_details = EducationDetailSerializer(many=True)
    gender = GenderSerializer()
    profile_image = ProfileImageSerializer()

    class Meta:
        model = User
        fields = ["full_name", "idp_email", "gender", "user_name", "phone_number", "education_details", "profile_image"]


class AdminStudentOneProfileAPIView(AppAPIView):
    def get(self, request, *args, **kwargs):
        user_details = User.objects.get(uuid = kwargs['uuid'])

        tracker_model = UserCourseTracker
        # user_details = User.objects.get(idp_user_id=user.uuid)
        serializer = UserSerializer(user_details)
        data = serializer.data
            
        if user_details.user_role:
            if user_details.user_role.identity == "Student":
                tracker_model = StudentEnrolledCourseTracker

        completed_courses=[]
        score_percentage=None
        result_status=None
        user_tracker_subquery = tracker_model.objects.filter(created_by=user_details, progress=100).values('entity')
        courses = Course.objects.filter(id__in=Subquery(user_tracker_subquery))
        for course in courses:
            if course:
                result = UserAssessmentResult.objects.filter(user=user_details, course=course).first()
                if result:
                    score_percentage=result.score_percentage
                    result_status=result.result_status
                completed_date = tracker_model.objects.get(entity=course, created_by=user_details)
                certificate_details = Certificate.objects.get_or_none(learning_type__identity="Course")
                if certificate_details:
                    if certificate_details.sponsor_logo:
                        sponsor_logo =  get_file_field_url(certificate_details, "sponsor_logo")
                        try:
                            response = requests.get(sponsor_logo)
                            response.raise_for_status()
                        except requests.RequestException as e:
                            return e
                        image_data = response.content
                        sponsor_logo_base64 = base64.b64encode(image_data).decode('utf-8')
                    # for company image
                    if certificate_details.image:
                        company_image =  get_file_field_url(certificate_details, "image")
                        try:
                            response = requests.get(company_image)
                            response.raise_for_status()
                        except requests.RequestException as e:
                            return e
                        image_data = response.content
                        company_image_base64 = base64.b64encode(image_data).decode('utf-8')
                    else:
                        company_image_base64 = None
                    certificate = {
                                'identity': course.identity,
                                'sponsor_logo': sponsor_logo_base64,
                                'keep_techademy_logo': certificate_details.keep_techademy_logo,
                                'orientation': certificate_details.orientation,
                                'headline_text' : certificate_details.headline_text,
                                'body_text': certificate_details.body_text,
                                'image': company_image_base64,
                                'username' : user_details.full_name,
                                'created_date': datetime.now()
                        }
                else:
                    certificate=None

                completed_courses.append({
                    'course': course.identity,
                    'course type': course.level.identity,
                    'completion date': completed_date.completed_on,
                    'score': score_percentage,
                    'result': result_status,
                    'certificate': certificate
                })
        
        user_assessment_results = UserAssessmentResult.objects.filter(user=user_details)
        user_passed_assessments = UserAssessmentResult.objects.filter(user=user_details, result_status='Passed')
        # Extract relevant assessment data from the results
        assessment_data = []
        for result in user_assessment_results:
            assessment_data.append({
                'assessment_name': result.assessment_name,
                'assessment_date': result.assessment_date,
                'result_status': result.result_status,
                'score_percentage': result.score_percentage,
            })
        
        data["assessment_results"] = assessment_data
        data["completed_courses"] = completed_courses

        return self.send_response(data=data)


class UpdateFresherPoolApplicantStatus(AppAPIView):
    def post(self, request, *args, **kwargs):
        try:
            user = User.objects.get(pk=kwargs["id"])
            applicant_status, created = FresherPoolApplicantStatus.objects.get_or_create(user=user)

            new_status = request.data.get("status", "new")
            applicant_status.status = new_status
            applicant_status.save()

            return self.send_response()
        except User.DoesNotExist:
            return self.send_error_response()
        

class UpdateApplicantListStatus(AppAPIView):
    def post(self, request, *args, **kwargs):
        try:
            user = User.objects.get(pk=kwargs["user_id"])
            applicant_status, created = JobAppliedList.objects.get_or_create(created_by=user, job=kwargs["job_id"])

            new_status = request.data.get("status", "applied_for_job")
            applicant_status.status = new_status
            applicant_status.save()
            if new_status == "offer_letter_initiated":
                EmailNotification(
                            email_to=user.idp_email,
                            template_code='offer_letter_initiate',
                            kwargs={
                                "job": applicant_status.job.job_role,
                                "employer_detail": applicant_status.job.company.identity
                            }
                        )
            return self.send_response()
        except User.DoesNotExist:
            return self.send_error_response()