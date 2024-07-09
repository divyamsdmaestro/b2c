from django.utils.datetime_safe import datetime
from rest_framework import serializers, parsers
from rest_framework import generics
from rest_framework.generics import ListAPIView
from apps.hackathons.models import industry as industry_models
from apps.access.models import User
from apps.common.helpers import get_file_field_url
from apps.jobs.models import EducationQualification
from apps.common.views.api import AppAPIView, AppViewMixin
from apps.learning.models.certificate import Certificate
from apps.learning.models.course import Course, CourseModule, CourseSubModule
from apps.learning.models.learning_path import LearningPath, LearningPathCourse
from apps.meta.models import (
    City,
    Country,
    State,
    UserJobDetail,
    UserEducationDetail,
    UserGender,
    UserIdentificationType,
    UserMartialStatus,
    UserProfileImage,
    UserProfileResume,
    EmploymentType
)
from apps.my_learnings.models.trackers import UserCourseTracker, StudentEnrolledCourseTracker, UserSkillTracker, StudentEnrolledLearningPathTracker, UserLearningPathTracker
from apps.my_learnings.views.home import MyLearningsCertificateDownloadAPIView
from apps.web_portal.models.assessment import UserAssessmentResult

from ...common.serializers import AppWriteOnlyModelSerializer, AppModelSerializer, AppReadOnlyModelSerializer, get_app_read_only_serializer, get_read_serializer
from ...common.serializers import get_app_read_only_serializer as read_serializer
# from django.http import HttpResponse
# from django.template.loader import get_template
# from xhtml2pdf import pisa
from rest_framework.generics import RetrieveAPIView
from apps.web_portal.serializers import UserSerializer
from apps.meta.models import EducationDetail, EducationUniversity, CareerHighlights, UserProject, OnboardingAreaOfInterest
from apps.jobs.models import EducationQualification,Industry
from apps.meta.models import profile as profile_models
from apps.meta.models import location as location_models
from apps.learning.models import Skill,Language
from django.db.models import Subquery, OuterRef
import base64,requests
from rest_framework.exceptions import ValidationError

class UpdateUserProfileMetaAPIView(ListAPIView, AppAPIView):
    """Provides meta-data for `UserProfileEditAPIView`."""

    def get(self, request, *args, **kwargs):
        data = {
            "genders": get_read_serializer(UserGender)(
                UserGender.objects.all(), many=True
            ).data,
            "identification_type": get_read_serializer(UserIdentificationType)(
                    UserIdentificationType.objects.all(), many=True
            ).data,
            "country": get_read_serializer(Country)(
                Country.objects.all(), many=True
            ).data,
            "state": get_read_serializer(State, meta_fields=['id', 'uuid', 'identity', 'country'])(
                State.objects.all(), many=True
            ).data,
            "city": get_read_serializer(City, meta_fields=['id', 'uuid', 'identity', 'state'])(
                City.objects.all(), many=True
            ).data,
            "qualification":get_read_serializer(EducationQualification)(
                EducationQualification.objects.all(), many=True
            ).data,
            "university_name":get_read_serializer(EducationUniversity)(
                EducationUniversity.objects.all(), many=True
            ).data,
            "degree":get_read_serializer(profile_models.OnboardingHighestEducation)(
                profile_models.OnboardingHighestEducation.objects.all(), many=True
            ).data,
            "employment_type":get_read_serializer(EmploymentType)(
                EmploymentType.objects.all(), many=True
            ).data,
            # "job_title":read_serializer(JobTitle, meta_fields="__all__")(
            #     JobTitle.objects.all(), many=True
            # ).data,
            "industry":get_read_serializer(industry_models.IndustryType)(
                industry_models.IndustryType.objects.all(), many=True
            ).data,
            "skills":get_read_serializer(Skill)(
                Skill.objects.filter(is_archived=False), many=True
            ).data,
            "languages":get_read_serializer(Language)(
                Language.objects.all(), many=True
            ).data,
            "interests":get_read_serializer(profile_models.OnboardingAreaOfInterest)(
                profile_models.OnboardingAreaOfInterest.objects.all(), many=True
            ).data,
        }
        return self.send_response(data=data)

class UserProfileDetailAPIView(generics.RetrieveAPIView, AppViewMixin):
    """This class provides details of user profiles Details"""

    def get_serializer_class(self):
        class _EducationDetailSerializer(AppReadOnlyModelSerializer):
            """This serializer contains configuration for EducationDetails."""
            qualification = read_serializer(EducationQualification, meta_fields="__all__")()
            university_name = read_serializer(EducationUniversity, meta_fields="__all__")()
            degree = read_serializer(profile_models.OnboardingHighestEducation, meta_fields="__all__")()

            class Meta:
                model = EducationDetail
                fields = ["qualification", "university_name", "degree", "college_name", "class_name", "overall_percentage"]

        class _UserProfileResumeSerializer(AppReadOnlyModelSerializer):
            """This serializer contains configuration for UserProfileResume."""
            class Meta(AppReadOnlyModelSerializer.Meta):
                model = UserProfileResume
                fields = "__all__"

        class _UserProfileImageSerializer(AppReadOnlyModelSerializer):
            """This serializer contains configuration for UserProfileImage."""
            class Meta(AppReadOnlyModelSerializer.Meta):
                model = UserProfileImage
                fields = "__all__"

        class _CareerHighlightSerializer(AppReadOnlyModelSerializer):
            class _ProjectSerializer(AppReadOnlyModelSerializer):
                class Meta(AppReadOnlyModelSerializer.Meta):
                    model =  UserProject
                    fields = ['identity', 'description']
            projects = _ProjectSerializer(many=True)
            languages = get_app_read_only_serializer(Language, meta_fields="__all__")(many=True)

            class Meta(AppReadOnlyModelSerializer.Meta):
                model = CareerHighlights
                fields = [
                    "languages",
                    "projects",
                    "achievements",
                    ]
        class _JobDetailSerializer(AppReadOnlyModelSerializer):

            employment_type = read_serializer(EmploymentType, meta_fields="__all__")()
            location = read_serializer(location_models.City, meta_fields="__all__")()
            industry = read_serializer(industry_models.IndustryType, meta_fields="__all__")()
            class Meta(AppReadOnlyModelSerializer.Meta):
                model = UserJobDetail
                fields = ["employment_type","job_title","location","industry","employer_name","job_summary","start_date","end_date"]
        
        class _AreaofInterestSerializer(AppReadOnlyModelSerializer):

            class Meta(AppReadOnlyModelSerializer.Meta):
                model = Skill
                fields = ['uuid', 'id', 'identity']

        return read_serializer(
            meta_model=User,
            meta_fields=[
                "first_name",
                "middle_name",
                "last_name",
                "phone_number",
                "gender",
                "birth_date",
                "identification_type",
                "identification_number",
                "address",
                "country",
                "state",
                "city",
                "pincode",
                "education_details",
                "resume",
                "profile_image",
                "career_highlights",
                "job_details",
                "onboarding_area_of_interests"
            ],
            init_fields_config={
                "gender": read_serializer(meta_model=UserGender,meta_fields="__all__")(),
                "identification_type": read_serializer(
                    meta_model=UserIdentificationType,meta_fields="__all__"
                )(),
                "city": read_serializer(meta_model=City,meta_fields="__all__")(),
                "state": read_serializer(meta_model=State,meta_fields="__all__")(),
                "country": read_serializer(meta_model=Country,meta_fields="__all__")(),
                "education_details": _EducationDetailSerializer(many=True),
                "resume": _UserProfileResumeSerializer(),
                "profile_image": _UserProfileImageSerializer(),
                "career_highlights": _CareerHighlightSerializer(),
                "job_details": _JobDetailSerializer(many=True),
                "onboarding_area_of_interests": _AreaofInterestSerializer(many=True)
            },
        )

    def get_object(self):
        return self.get_authenticated_user()


class UserProfileResumeDeleteAPIView(AppAPIView):
    """This view used to delete resume of a user"""

    def get_object(self, pk):
        return UserProfileResume.objects.get(pk=pk)
    
    def delete(self, request, pk, format=None):
        data = self.get_object(pk)
        data.delete()
        return self.send_response()
    

class UserProfileImageDeleteAPIView(AppAPIView):
    """This view used to delete profile image of a user"""
    def get_object(self, pk):
        return UserProfileImage.objects.get(pk=pk)
    
    def delete(self, request, pk, format=None):
        data = self.get_object(pk)
        data.delete()
        return self.send_response()


class UserOneProfileDownloadAPIView(AppAPIView):
    """This view used to download the profile details of a user"""
    def get(self, request, *args, **kwargs):
        user = self.get_user()
        user_details = User.objects.get(idp_user_id=user.uuid)
        file_name = user_details.full_name
        base_url = "https://b2cstagingv2.blob.core.windows.net/appuploads/media/"

        # Generate HTML content using Django template
        if  user_details.profile_image:
            profile_image =  user_details.profile_image.file
        else:
            profile_image = None
        if  user_details.gender:
            gender =  user_details.gender.identity
        else:
            gender = None
        # if  user_details.martial_status:
        #   martial_status =  user_details.martial_status.identity
        # else:
        #     martial_status = None
        if  user_details.identification_type:
            identification_type =  user_details.identification_type.identity
        else:
            identification_type = None
        context = {'full_name': user_details.full_name,
                    'mobile_number': "+918056972325",
                    'email': "test@cyces.co",
                    'profile_image': base_url+profile_image,
                    'gender' : gender,
                    # 'martial_status': martial_status,
                    'dob': user_details.birth_date,
                    'identification_type' :identification_type,
                    'identification_number': user_details.identification_number,
                    'address': user_details.address,                   
                    }
        
        return self.send_response(context)
        # template = get_template('one_profile.html')
        # html = template.render(context)

        # response = HttpResponse(content_type='application/pdf')
        # response['Content-Disposition'] = 'filename="f{file_name}.pdf"'

        # pisa_status = pisa.CreatePDF(html, dest=response)
        # if pisa_status.err:
        #     return HttpResponse('PDF generation failed.')
        # return response
class QualificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = profile_models.EducationQualification
        fields = ['id', 'uuid','identity']

class UniversitySerializer(serializers.ModelSerializer):
    class Meta:
        model = profile_models.EducationUniversity
        fields = ['id', 'uuid','identity']

class DegreeSerializer(serializers.ModelSerializer):
    class Meta:
        model = profile_models.OnboardingHighestEducation
        fields = ['id', 'uuid','identity']

class EducationDetailSerializer(serializers.ModelSerializer):
    qualification = QualificationSerializer()
    university_name = UniversitySerializer()
    degree = DegreeSerializer()
    class Meta:
        model = EducationDetail
        fields = ["id", "uuid", "college_name", "class_name", "overall_percentage", "qualification", "university_name", "degree"]

class GenderSerializer(serializers.ModelSerializer):
    class Meta:
        model = profile_models.UserGender
        fields = ['id', 'identity']

class ProfileImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = profile_models.UserProfileImage
        fields = ['id', 'uuid', 'file']

class UserOneProfileSerializer(serializers.ModelSerializer):
    education_details = EducationDetailSerializer(many=True)
    gender = GenderSerializer()
    profile_image = ProfileImageSerializer()

    class Meta:
        model = User
        fields = ["full_name", "idp_email", "gender", "user_name", "phone_number", "education_details", "profile_image"]

class UserOneProfileBasicInformationAPIView(AppAPIView):
    def get(self, request, *args, **kwargs):
        user_details = self.get_user()
        tracker_model = UserCourseTracker
        lp_tracker_model = UserLearningPathTracker
        # user_details = User.objects.get(idp_user_id=user.uuid)
        serializer = UserOneProfileSerializer(user_details)
        data = serializer.data
            
        if user_details.user_role:
            if user_details.user_role.identity == "Student":
                tracker_model = StudentEnrolledCourseTracker
                lp_tracker_model = StudentEnrolledLearningPathTracker

        completed_courses=[]
        completed_lp_courses=[]
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
                    'completion date': completed_date.last_accessed_on,
                    'score': score_percentage,
                    'result': result_status,
                    'certificate': certificate
                })
        user_lp_tracker_subquery = lp_tracker_model.objects.filter(created_by=user_details, progress=100).values('entity')
        lps = LearningPath.objects.filter(id__in=Subquery(user_lp_tracker_subquery))
        for lp in lps:
            if lp:
                completed_date = lp_tracker_model.objects.get(entity=lp, created_by=user_details)
                certificate_details = Certificate.objects.get_or_none(learning_type__identity="Learning Path")
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
                                'identity': lp.identity,
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

                completed_lp_courses.append({
                    'course': lp.identity,
                    'course type': lp.level.identity,
                    'completion date': completed_date.last_accessed_on,
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
        data["total_assessments_completed"] = user_assessment_results.count()
        data["total_passed_assessments"] = user_passed_assessments.count()
        data["completed_courses"] = completed_courses
        data["completed_lp_courses"] = completed_lp_courses


        return self.send_response(data=data)


class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = ["id", "identity"]
class UserSkillTrackerSerializer(serializers.ModelSerializer):
    entity = SkillSerializer()
    class Meta:
        model = UserSkillTracker
        fields = ["id", "uuid", "entity", "progress"]

class UserOneProfilSkillAchievementAPIView(AppAPIView):
    def get(self, request, *args, **kwargs):
        user = self.get_user()
        skill_trackers = UserSkillTracker.objects.filter(created_by=user)
        serializer = UserSkillTrackerSerializer(skill_trackers, many=True)
        
        return self.send_response(data=serializer.data)

class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = profile_models.UserProject
        fields = ['identity', 'description']

class UserProfileEditAPIView(AppAPIView):

    class _Serializer(AppWriteOnlyModelSerializer):

        # Career Highlights
        class _ProfileCareerHighlight(AppModelSerializer):
            projects = ProjectSerializer(many=True)
            class Meta(AppWriteOnlyModelSerializer.Meta):
                model = profile_models.CareerHighlights
                fields = ['achievements', 'languages', 'projects']
        career_highlights = _ProfileCareerHighlight()

        # Education Details
        class _EducationDetailSerializer(AppWriteOnlyModelSerializer):
            class Meta(AppWriteOnlyModelSerializer.Meta):
                model = EducationDetail
                fields = ["class_name", "overall_percentage", "qualification", "university_name", "degree", "college_name"]
        education_details = _EducationDetailSerializer(many=True)

        # Job Details
        class _JobDetailSerializer(AppWriteOnlyModelSerializer):
            class Meta(AppWriteOnlyModelSerializer.Meta):
                model = profile_models.UserJobDetail
                fields = ["employer_name", "employment_type", "end_date", "start_date", "industry", "job_summary", "job_title", "location"]
        job_details = _JobDetailSerializer(many=True)

        class Meta(AppWriteOnlyModelSerializer.Meta):
            fields = ['first_name', 'middle_name', 'last_name', 'phone_number', 'address', 'city', 'state', 'country', 'pincode', 'resume', 'career_highlights', 'education_details', 'job_details', 'onboarding_area_of_interests']
            model = User

        def update(self, instance, validated_data):
            career_highlights_data = validated_data.pop("career_highlights", None)
            education_details_data = validated_data.pop("education_details", [])
            job_details = validated_data.pop("job_details", [])
            user = super().update(validated_data=validated_data, instance=instance)

            # Career highlighs
            if career_highlights_data:
                languages = []
                projects = []
                language_data = career_highlights_data.pop("languages", None)
                project_data = career_highlights_data.pop("projects", [])
                if language_data:
                    # Assuming language_data is a list of Language objects or their IDs
                    for lang_info in language_data:
                        if isinstance(lang_info, int):
                            language = Language.objects.get(pk=lang_info)
                            languages.append(language)
                        else:
                            languages.append(lang_info)
                
                if project_data:
                    for project_info in project_data:
                        # Assuming project_info is a dictionary with project details
                        project = profile_models.UserProject.objects.create(**project_info)
                        projects.append(project)
                
                career_highlight, created = profile_models.CareerHighlights.objects.get_or_create(**career_highlights_data)
                career_highlight.languages.set(languages)
                career_highlight.projects.set(projects)
                user.career_highlights=career_highlight
                user.save()

            # Education Details
            if education_details_data:
                user.education_details.clear()
                for data in education_details_data:
                    education_details = EducationDetail.objects.filter(**data)
                    if education_details.exists():
                        education_detail = education_details.first()
                    else:
                        education_detail = EducationDetail.objects.create(**data)
                    user.education_details.add(education_detail)

            # Job Details
            if job_details:
                user.job_details.clear()
                for data in job_details:
                    job_details = profile_models.UserJobDetail.objects.filter(**data)
                    if job_details.exists():
                        job_details = job_details.first()
                    else:
                        job_details = profile_models.UserJobDetail.objects.create(**data)
                    user.job_details.add(job_details)
            return user

    serializer_class = _Serializer
    def post(self, request, *args, **kwargs):
        serializer = self.get_valid_serializer(instance=self.get_user())
        serializer.save()
        return self.send_response()

class UserProfileImageUploadAPIView(AppAPIView):
        """View to handle the upload."""

        class _Serializer(AppWriteOnlyModelSerializer):
            """Serializer for write."""
            class Meta(AppWriteOnlyModelSerializer.Meta):
                model = UserProfileImage
                fields = ["file"]

            def create(self, validated_data):
                profile_image = super().create(validated_data)
                user = self.get_user()
                user.profile_image = profile_image
                user.save()
                return profile_image

        parser_classes = [parsers.MultiPartParser]
        serializer_class = _Serializer

        def post(self, *args, **kwargs):
            try:
                serializer = self.get_valid_serializer()
                serializer.save()
                return self.send_response()
            except ValidationError as e:
                return self.send_error_response({"error": str(e)}, status=400)

# class UserProfileImageEditAPIView(AppAPIView):
#     class _Serializer(AppWriteOnlyModelSerializer):
#         class Meta(AppWriteOnlyModelSerializer.Meta):
#             model = User
#             fields = [
#                 "profile_image"
#             ]

#         def update(self, instance, validated_data):
#             instance = super().update(validated_data=validated_data, instance=instance)
#             return instance

#     serializer_class = _Serializer
#     parser_classes = [parsers.MultiPartParser]

#     def post(self, *args, **kwargs):
#         serializer = self.get_valid_serializer(instance=self.get_user())
#         serializer.save()
#         return self.send_response()
    

class OneProfileDetailAPIView(RetrieveAPIView, AppViewMixin):
    """This class provides details of one profile Details"""

    def get_serializer_class(self):
        class _EducationDetailSerializer(AppReadOnlyModelSerializer):
            qualification = read_serializer(EducationQualification, meta_fields="__all__")()
            university_name = read_serializer(EducationUniversity, meta_fields="__all__")()
            degree = read_serializer(profile_models.OnboardingHighestEducation, meta_fields="__all__")()
            class Meta:
                model = EducationDetail
                fields = ["qualification", "university_name", "degree", "college_name"]

        class _UserProfileImageSerializer(AppReadOnlyModelSerializer):
            """This serializer contains configuration for UserProfileImage."""
            class Meta(AppReadOnlyModelSerializer.Meta):
                model = UserProfileImage
                fields = ["file"]

        return read_serializer(
            meta_model=User,
            meta_fields=[
                "first_name",
                "middle_name",
                "last_name",
                "education_details",
                "profile_image",
            ],
            init_fields_config={
                "education_details": _EducationDetailSerializer(many=True),
                "profile_image": _UserProfileImageSerializer(),
            },
        )

    def get_object(self):
        return self.get_authenticated_user()
