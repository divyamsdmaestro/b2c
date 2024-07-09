from apps.common.serializers import (
    AppReadOnlyModelSerializer,
    AppModelSerializer,
    AppWriteOnlyModelSerializer
)
from apps.common.views.api.generic import DEFAULT_IDENTITY_DISPLAY_FIELDS
from apps.jobs.models import (
    EducationQualification,
    FunctionalArea,
    Job,
    JobEligibilityCriteria,
    JobRoundDetails,
    JobSavedlist,
    JobAppliedList,
    JobFeedbackQuestion,
    JobImage,
    JobAppliedList,
    JobInterviewSchedule,
)
from apps.learning.models import Skill, JobEligibleSkill
from apps.meta.models import location as location_models
from apps.jobs.models import linkages as linkage_models
from rest_framework import serializers
from apps.access.models import EmployerDetail, EmployerLogoImage, User
from django.contrib.auth.models import AnonymousUser

from apps.web_portal.models.assessment import JobAssessmentResult, JobEligibleSkillAssessment
from ..common.serializers import get_app_read_only_serializer as read_serializer
from apps.hackathons.models import industry as industry_models
from apps.my_learnings.models import (
    UserJobEligibleSkillTracker,
    UserCourseTracker, 
    UserLearningPathTracker, 
    UserCertificatePathTracker,
    UserSubscriptionPlanCourseTracker,
    UserSubscriptionPlanLearningPathTracker,
    UserSubscriptionPlanCertificatePathTracker,
    UserSkillCourseTracker,
    UserSkillLearningPathTracker,
    UserSkillCertificatePathTracker,
    )
from apps.common.helpers import is_list2_in_list1
from apps.meta.models import profile as profile_models

class SkillSerializer(AppReadOnlyModelSerializer):
    class Meta:
        model = Skill
        fields = ["id", "identity", "description"]

class CitySerializer(AppReadOnlyModelSerializer):
    class Meta:
        model = location_models.City
        fields = ["id", "identity"]

class StateSerializer(AppReadOnlyModelSerializer):
    class Meta:
        model = location_models.State
        fields = ["id", "identity"]

class CountrySerializer(AppReadOnlyModelSerializer):
    class Meta:
        model = location_models.Country
        fields = ["id", "identity"]

class IndustryTypeSerializer(AppReadOnlyModelSerializer):

    class Meta:
        model = industry_models.IndustryType
        fields = ["id", "identity"]

class FunctionalAreaSerializer(AppReadOnlyModelSerializer):
    class Meta:
        model = FunctionalArea
        fields = ["id", "identity"]

class EducationQualificationSerializer(AppReadOnlyModelSerializer):
    class Meta:
        model = EducationQualification
        fields = ["id", "identity"]

class CriteriaSerializer(AppReadOnlyModelSerializer):
    class Meta:
        model=linkage_models.JobCriteria
        fields= ['id', 'identity']

class JobEligibilityCriteriaSerializer(AppReadOnlyModelSerializer):
    criteria=CriteriaSerializer()
    class Meta:
        model = JobEligibilityCriteria
        fields = ['criteria', 'Value']

class JobCriteriaSerializer(AppReadOnlyModelSerializer):
    class Meta:
        model = JobEligibilityCriteria
        fields = ['criteria', 'Value']

class JobRoundDetailSerializer(AppReadOnlyModelSerializer):
    class Meta:
        model = JobRoundDetails
        fields = ['title', 'type', 'description', 'assessment_id', 'hackathon_id']

class CompanySerializer(AppReadOnlyModelSerializer):
    logo_image = read_serializer(EmployerLogoImage, meta_fields=['id','uuid','file'])(EmployerLogoImage.objects.all())

    class Meta:
        model = EmployerDetail
        fields = ['id', 'identity', 'logo_image']

class JobDetailSerializer(AppReadOnlyModelSerializer):
    """This Serializer contains data for Jobs output structure."""
    job_image = read_serializer(JobImage, meta_fields="__all__")()
    skills=SkillSerializer(many=True)
    city=CitySerializer()
    state=StateSerializer()
    country=CountrySerializer()
    industry=IndustryTypeSerializer()
    functional_area=FunctionalAreaSerializer(many=True)
    education_expect=EducationQualificationSerializer(many=True)
    eligibility_criteria=JobEligibilityCriteriaSerializer(many=True)
    job_round_details=JobRoundDetailSerializer(many=True)
    company = CompanySerializer()

    class Meta:
        model = Job
        fields = [
            "id", 
            "uuid", 
            "identity", 
            "job_role", 
            "job_image", 
            "description", 
            "benefits", 
            "skills", 
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
            "eligibility_criteria",
            "job_round_details",
            "company",
        ]

class JobSerializer(AppReadOnlyModelSerializer):
    """This Serializer contains data for Jobs output structure."""
    city=CitySerializer()
    state=StateSerializer()
    company = CompanySerializer()

    class Meta:
        model = Job
        fields = ["id", "uuid", "identity", "job_role", "state", "city", "employement_type", "salary_detail", "company"]


class JobEligibleSkillSerializer(AppReadOnlyModelSerializer):
    skills_achieved=serializers.SerializerMethodField()
    is_in_buy=serializers.SerializerMethodField()
    class Meta:
        model = JobEligibleSkill
        fields = ["id", 'uuid', "identity", "skills_achieved", "assessment_id", "is_in_buy"]

    def get_skills_achieved(self, obj):
        user = self.get_user()
        
        if isinstance(user, AnonymousUser) or user is None:
            return None
        else:
            skill_tracker = UserJobEligibleSkillTracker.objects.filter(entity_id=obj.id, created_by=user, progress=100).exists()

            # eligible course,lp and alp to apply for job
            eligible_course = set(obj.courses.values_list("id", flat=True))
            eligible_learning_path = set(obj.learning_paths.values_list("id", flat=True))
            eligible_certification_path = set(obj.certification_paths.values_list("id", flat=True))

            # User Tracker
            courses = list(UserCourseTracker.objects.filter(created_by=user, progress=100).values_list("entity_id", flat=True))
            learning_paths = list(UserLearningPathTracker.objects.filter(created_by=user, progress=100).values_list("entity_id", flat=True))
            certification_paths = list(UserCertificatePathTracker.objects.filter(created_by=user, progress=100).values_list("entity_id", flat=True))
            
            # User Subscription Tracker
            subscribed_courses = list(UserSubscriptionPlanCourseTracker.objects.filter(created_by=user, progress=100).values_list("entity_id", flat=True))
            subscribed_learning_paths = list(UserSubscriptionPlanLearningPathTracker.objects.filter(created_by=user, progress=100).values_list("entity_id", flat=True))
            subscribed_certification_paths = list(UserSubscriptionPlanCertificatePathTracker.objects.filter(created_by=user, progress=100).values_list("entity_id", flat=True))
        
            courses.extend(subscribed_courses)
            learning_paths.extend(subscribed_learning_paths)
            certification_paths.extend(subscribed_certification_paths)

            # User Skill Tracker
            skilled_courses = list(UserSkillCourseTracker.objects.filter(created_by=user, progress=100).values_list("entity_id", flat=True))
            skilled_learning_paths = list(UserSkillLearningPathTracker.objects.filter(created_by=user, progress=100).values_list("entity_id", flat=True))
            skilled_certification_paths = list(UserSkillCertificatePathTracker.objects.filter(created_by=user, progress=100).values_list("entity_id", flat=True))
            
            courses.extend(skilled_courses)
            learning_paths.extend(skilled_learning_paths)
            certification_paths.extend(skilled_certification_paths)

            # Make lists data unique then check the condition 
            skill_course = is_list2_in_list1(list2 = list(eligible_course), list1 = list(set(courses)))
            skill_learning_paths = is_list2_in_list1(list2 = list(eligible_learning_path), list1 = list(set(learning_paths)))
            skill_certification_paths = is_list2_in_list1(list2 = list(eligible_certification_path), list1 = list(set(certification_paths)))
            
            assessment_result = JobEligibleSkillAssessment.objects.filter(user=user, job_eligible_skill=obj, result_status="Passed").first()
            if skill_tracker or (skill_course and skill_learning_paths and skill_certification_paths) or assessment_result:
                return True
            else:
                return False
            
    def get_is_in_buy(self, obj):
        user = self.get_user()
        return UserJobEligibleSkillTracker.objects.filter(entity=obj, created_by=user).exists()


class JobLearnerListSerializer(AppModelSerializer):
    """This Serializer contains data for Jobs output structure for Learner."""
    job_eligibility_skills=JobEligibleSkillSerializer(many=True)
    city=CitySerializer()
    state=StateSerializer()
    country=CountrySerializer()
    functional_area=FunctionalAreaSerializer(many=True)
    education_expect=EducationQualificationSerializer(many=True)
    eligibility_criteria=JobEligibilityCriteriaSerializer(many=True)
    job_round_details=JobRoundDetailSerializer(many=True)
    company = CompanySerializer()
    job_status = serializers.SerializerMethodField()

    is_saved = serializers.SerializerMethodField()
    is_applied = serializers.SerializerMethodField()

    class Meta:
        model = Job
        fields = [
            "id", 
            "uuid", 
            "identity", 
            "job_role",  
            "description",
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
            "minimum_experience",
            "maximum_experience",
            "eligibility_criteria",
            "job_round_details",
            "is_public",
            "company",
            "is_saved",
            "is_applied",
            "created",
            "job_status"
        ]

    def get_is_saved(self, obj):
        user = self.get_user()
        """This function used to get course is already in wishlist or not"""
        if isinstance(user, AnonymousUser) or user == None:
            return False
        else:
            is_saved = JobSavedlist.objects.filter(
                job_id=obj.id, created_by=user
            ).exists()
            return is_saved
        
    def get_is_applied(self, obj):
        user = self.get_user()
        """This function used to get course is already in wishlist or not"""
        if isinstance(user, AnonymousUser) or user == None:
            return False
        else:
            is_applied = JobAppliedList.objects.filter(
                job_id=obj.id, created_by=user
            ).exists()
            return is_applied
            
    def get_job_status(self,obj):
        user = self.get_user()
        applied_list = JobAppliedList.objects.get_or_none(job_id=obj.id, created_by=user)
        if applied_list:
            return applied_list.status
        else:
            return None

class JobLearnerDetailSerializer(AppReadOnlyModelSerializer):
    """This Serializer contains data for Jobs output structure."""
    job_image = read_serializer(JobImage, meta_fields="__all__")()
    job_eligibility_skills=JobEligibleSkillSerializer(many=True)
    city=CitySerializer()
    state=StateSerializer()
    country=CountrySerializer()
    industry=IndustryTypeSerializer()
    functional_area=FunctionalAreaSerializer(many=True)
    education_expect=EducationQualificationSerializer(many=True)
    eligibility_criteria=JobEligibilityCriteriaSerializer(many=True)
    job_round_details=JobRoundDetailSerializer(many=True)
    company = CompanySerializer()

    is_saved = serializers.SerializerMethodField()
    is_applied = serializers.SerializerMethodField()
    job_status = serializers.SerializerMethodField()
    class Meta:
        model = Job
        fields = [
            "id", 
            "uuid", 
            "identity", 
            "job_role", 
            "job_image", 
            "description", 
            "benefits", 
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
            "minimum_experience",
            "maximum_experience",
            "eligibility_criteria",
            "job_round_details",
            "is_public",
            "company",
            "is_saved",
            "is_applied",
            "created",
            "job_status"
        ]

    def get_is_saved(self, obj):
        user = self.get_user()
        """This function used to get course is already in wishlist or not"""
        if isinstance(user, AnonymousUser) or user == None:
            return False
        else:
            is_saved = JobSavedlist.objects.filter(
                job_id=obj.id, created_by=user
            ).exists()
            return is_saved
        
    def get_is_applied(self, obj):
        user = self.get_user()
        """This function used to get course is already in wishlist or not"""
        if isinstance(user, AnonymousUser) or user == None:
            return False
        else:
            is_applied = JobAppliedList.objects.filter(
                job_id=obj.id, created_by=user
            ).exists()
            return is_applied

    def get_job_status(self,obj):
        user = self.get_user()
        applied_list = JobAppliedList.objects.get_or_none(job_id=obj.id, created_by=user)
        if applied_list:
            return applied_list.status
        else:
            return None
class JobSavedlistSerializer(AppReadOnlyModelSerializer):
    job = JobLearnerListSerializer()

    class Meta:
        model = JobSavedlist
        fields = ["job"]

class JobAppliedListSerializer(AppReadOnlyModelSerializer):
    job = JobLearnerListSerializer()
    status_color = serializers.SerializerMethodField()
    assessment_score = serializers.SerializerMethodField()
    assessment_status = serializers.SerializerMethodField()
    class Meta:
        model=JobAppliedList
        fields = ["job", "status", "status_color", "assessment_score", "assessment_status"]

    def get_status_color(self, obj):
        if obj.status == "offer_letter_initiated":
            return {"bg": "#4CAF5014", "border": "#4CAF50"}  #Color Code for Green
        if obj.status == "applied_for_job" or obj.status == "interview_sheduled" or obj.status == "shortlist" or obj.status == "recommended":
            return {"bg": "#EC5B0114","border":"#EC5B01"}    #Color Code for Orange
        if obj.status == "rejected":
            return {"bg": "#B0002014","border":"#B00020"}    #Color Code for Red
        
        return None
    
    def get_assessment_score(self,obj):
        assessment_details = JobAssessmentResult.objects.get_or_none(job_id=obj.job, user=self.get_user())
        if assessment_details:
            return assessment_details.score_percentage
        else:
            return None
        
    def get_assessment_status(self,obj):
        assessment_details = JobAssessmentResult.objects.get_or_none(job_id=obj.job, user=self.get_user())
        if assessment_details:
            return assessment_details.result_status
        else:
            return None

class JobFeedbackQuestionSerializer(AppWriteOnlyModelSerializer):
    """
    To handle many to many field when create
    """

    class Meta(AppWriteOnlyModelSerializer.Meta):
        model = JobFeedbackQuestion
        fields = "__all__" 

class JobApplicantListSerializer(AppReadOnlyModelSerializer):
    created_by = read_serializer(
        User, meta_fields=['id', 'uuid', 'first_name', 'idp_email'],
        init_fields_config={
            "resume_detail": read_serializer(
                meta_model=profile_models.UserProfileResume, meta_fields=['id', 'file']
            )(source="resume"),
        }
    )()
    job = read_serializer(Job, meta_fields=['id', 'identity'])()
    interview_feedback = serializers.SerializerMethodField()
    assessment = serializers.SerializerMethodField()

    class Meta(AppReadOnlyModelSerializer.Meta):
        model = JobAppliedList
        fields = "__all__"

    def get_interview_feedback(self, obj):
        feedback = JobInterviewSchedule.objects.filter(job=obj.job, applicant=obj.created_by).first()
        if feedback is not None and feedback.is_feedback_send == True:
            return {"id": feedback.id}
        else:
            return None
    
    def get_assessment(self, obj):
        job = obj.job
        return job.job_round_details.filter(assessment_id__isnull=False).exists()

class JobAppliedListAssessmentSerializer(serializers.ModelSerializer):
    assessment = serializers.SerializerMethodField()
    class Meta:
        model = JobAppliedList
        fields = ["assessment"]

    def get_assessment(self, obj):
        job = obj.job
        return job.job_round_details.filter(assessment_id__isnull=False).exists()
    
class JobApplicantAssessmentResultSerializer(serializers.ModelSerializer):
        class Meta:
            model = JobAssessmentResult
            fields = ['result']