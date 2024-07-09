from apps.cms.serializers import StudentDetailSerializer
from apps.cms.views.user import convert_date_format
from apps.common.views.api import AppAPIView
from apps.common.serializers import AppWriteOnlyModelSerializer, AppModelSerializer, get_app_read_only_serializer, AppReadOnlyModelSerializer
from apps.access.models import (
    User, 
    InstitutionDetail, 
    InstitutionUserGroupDetail, 
    EmployerDetail,
    StudentReportFile, 
    StudentReportDetail, 
    InstitutionUserGroupContent, 
    ReportFilterParameter,
    UserRole
)
from rest_framework.generics import RetrieveAPIView, ListAPIView
from apps.service_idp.views import valid_idp_response
from apps.learning.models import Course
from apps.learning.models import Course, CourseImage, LearningPath, LearningPathImage, CertificationPath, CertificationPathImage
from apps.common.views.api.generic import (
    AbstractLookUpFieldMixin,
)
from rest_framework import serializers
from apps.cms.celery import generate_report
from django_filters.rest_framework import DjangoFilterBackend
from apps.common.pagination import AppPagination
from apps.common.helpers import get_file_field_url, make_http_request, send_welcome_email, EmailNotification
from rest_framework.filters import SearchFilter
import io,csv
from django.conf import settings
from apps.access.models import UserRole
from apps.meta.models import location as location_models
from apps.meta.models import profile as profile_models
from apps.jobs.models import Job
from django.db.models import Count
from apps.web_portal.serializers import ExploreSerializer
from apps.my_learnings.models import UserCourseTracker, UserLearningPathTracker, UserCertificatePathTracker
from datetime import date
from apps.my_learnings.models import (
    UserCourseTracker,
    UserLearningPathTracker,
    UserCertificatePathTracker,
    StudentEnrolledCertificatePathTracker,
    StudentEnrolledLearningPathTracker,
    StudentEnrolledCourseTracker,
    UserSubscriptionPlanCertificatePathTracker,
    UserSubscriptionPlanLearningPathTracker,
    UserSubscriptionPlanCourseTracker,
)
from apps.cms.serializers.hackathon import HackathonImageSerializer
from apps.webinars.models import Webinar, WebinarImage
from apps.hackathons.models import hackathon as hackathon_models
import requests

class AdminDetailHomeAPIView(AppAPIView):
    class _CourseSerializer(serializers.ModelSerializer):      
        total_learners = serializers.SerializerMethodField()
        class Meta:
            fields = ["id", "uuid", "identity", "total_learners"]
            model = Course

        def get_total_learners(self,obj):
            count = (
                UserCourseTracker.objects.filter(entity=obj).count()
                + StudentEnrolledCourseTracker.objects.filter(entity=obj).count()
                + UserSubscriptionPlanCourseTracker.objects.filter(entity=obj).count()
            )
            return count

    class _LearningPathSerializer(serializers.ModelSerializer):      
        total_learners = serializers.SerializerMethodField()
        class Meta:
            fields = ["id", "uuid", "identity", "total_learners"]
            model = LearningPath

        def get_total_learners(self,obj):
            count = (
                UserLearningPathTracker.objects.filter(entity=obj).count()
                + StudentEnrolledLearningPathTracker.objects.filter(entity=obj).count()
                + UserSubscriptionPlanLearningPathTracker.objects.filter(entity=obj).count()
            )
            return count

    class _CertificationPathSerializer(serializers.ModelSerializer):      
        total_learners = serializers.SerializerMethodField()
        class Meta:
            fields = ["id", "uuid", "identity", "total_learners"]
            model = CertificationPath

        def get_total_learners(self,obj):
            count = (
                UserCertificatePathTracker.objects.filter(entity=obj).count()
                + StudentEnrolledCertificatePathTracker.objects.filter(entity=obj).count()
                + UserSubscriptionPlanCertificatePathTracker.objects.filter(entity=obj).count()
            )
            return count
    
    def get(self, *args, **kwargs):
        """Handle on get method."""

        # trending_learning = {
        #     "courses": sorted(
        #         self._CourseSerializer(Course.objects.all(), many=True).data,
        #         key=lambda x: x["total_learners"],
        #         reverse=True
        #     )[:30],
        #     "learning_paths": sorted(
        #         self._LearningPathSerializer(LearningPath.objects.all(), many=True).data,
        #         key=lambda x: x["total_learners"],
        #         reverse=True
        #     )[:30],
        #     "certification_paths": sorted(
        #         self._CertificationPathSerializer(CertificationPath.objects.all(), many=True).data,
        #         key=lambda x: x["total_learners"],
        #         reverse=True
        #     )[:30],
        # }

        total_learners = (
            Count('usercoursetracker') + Count('studentenrolledcoursetracker') + Count('usersubscriptionplancoursetracker')
        )
        top_trending_courses = Course.objects.annotate(total_learners=total_learners).order_by('-total_learners')[:30]

        total_learners = (
            Count('userlearningpathtracker') + Count('studentenrolledlearningpathtracker') + Count('usersubscriptionplanlearningpathtracker')
        )
        top_trending_lp_courses = LearningPath.objects.annotate(total_learners=total_learners).order_by('-total_learners')[:30]

        total_learners = (
            Count('usercertificatepathtracker') + Count('studentenrolledcertificatepathtracker') + Count('usersubscriptionplancertificatepathtracker')
        )
        top_trending_clp_courses = CertificationPath.objects.annotate(total_learners=total_learners).order_by('-total_learners')[:30]

        trending_learning = {
            "courses": self._CourseSerializer(top_trending_courses, many=True).data,
            "learning_paths": self._LearningPathSerializer(top_trending_lp_courses, many=True).data,
            "certification_paths": self._CertificationPathSerializer(top_trending_clp_courses, many=True).data,
        }

        trending_jobs = Job.objects.values('identity').annotate(count=Count('identity')).order_by('-count')[:10]

        return self.send_response(
            data ={
                "trending_learning":trending_learning,
                "trending_jobs":trending_jobs,
            }
        )

class AdminHomeAPIView(AppAPIView):
    """Sends out data for the website home/landing page."""
    class _WebinarSerializer(AppReadOnlyModelSerializer):
        image = get_app_read_only_serializer(WebinarImage, meta_fields="__all__")()

        class Meta(AppReadOnlyModelSerializer.Meta):
            model = Webinar
            fields = ["id","uuid", "identity", "image", "description", "participant_limit", "start_date"]

    class _HackathonSerializer(AppReadOnlyModelSerializer):
        image = HackathonImageSerializer()

        class Meta(AppReadOnlyModelSerializer.Meta):
            model = hackathon_models.Hackathon
            fields = ['id','uuid','identity','image','description','no_of_participants_limit','start_date']

    def get(self, *args, **kwargs):
        """Handle on get method."""

        today = date.today()
        users_count = User.objects.all().count()
        registered_users_count = User.objects.filter(created__date=today).count()
        course_count = Course.objects.all().count()
        learning_path_count = LearningPath.objects.all().count()
        certification_path_count = CertificationPath.objects.all().count()
        institute_count = InstitutionDetail.objects.all().count()
        institute_students_count = User.objects.filter(user_role__identity__icontains="Student").count()
        corporate_count = EmployerDetail.objects.all().count()

        users = {
            "users_count":users_count,
            "registered_users_count":registered_users_count
        }
        course = {
            "course_count": course_count,
            "learning_path_count": learning_path_count,
            "certification_path_count": certification_path_count
        }
        institute = {
            "institute_count": institute_count,
            "institute_users_count": institute_count + institute_students_count,
        }

        upcoming_events = {
            "webinars":self._WebinarSerializer(Webinar.objects.filter(start_date__gte=today), many=True).data,
            "hackathons":self._HackathonSerializer(hackathon_models.Hackathon.objects.filter(start_date__gte=today), many=True).data
        }

        return self.send_response(
            data={
                "users":users,
                "course":course,
                "institute":institute,
                "corporate_count": corporate_count,
                "upcoming_events":upcoming_events
            }
        )

class InstitutionAdminDashboardAPIView(AppAPIView):
    """Sends out data for the website home/landing page."""
    class _InstitutionUserGroupSerializer(AppReadOnlyModelSerializer):
        count = serializers.SerializerMethodField()
        class Meta(AppReadOnlyModelSerializer.Meta):
            fields = ["id", "identity", "count"]
            model = InstitutionUserGroupDetail

        def get_count(self, obj):
            student_ids = [student.id for student in obj.user.all()]
            return User.objects.filter(id__in=student_ids).count()
        
    class _InstitutionContentGroupSerializer(AppReadOnlyModelSerializer):
        count = serializers.SerializerMethodField()
        class Meta(AppReadOnlyModelSerializer.Meta):
            fields = ["id", "identity", "count"]
            model = InstitutionUserGroupContent

        def get_count(self, obj):
            user_group_ids = [user_group.id for user_group in obj.user_group.all()]
            return InstitutionUserGroupDetail.objects.filter(id__in=user_group_ids).count()

    def get(self, *args, **kwargs):
        """Handle on get method."""
        if self.get_user().user_role.identity == "Staff":
            institution = InstitutionDetail.objects.get(representative=self.get_user().created_by)
        else:
            institution = InstitutionDetail.objects.get(representative=self.get_user())
        
        user_group = InstitutionUserGroupDetail.objects.filter(institution=institution)
        content_group =InstitutionUserGroupContent.objects.filter(user_group__in=user_group).distinct()

        course_ids = [course.id for course in institution.courses.all()]
        lp_ids = [learning_path.id for learning_path in institution.learning_paths.all()]
        alp_ids = [certification_path.id for certification_path in institution.certification_paths.all()]

        # Student counts details
        if self.get_user().user_role.identity == "Staff":
            student_count = User.objects.filter(created_by=self.get_user().created_by,user_role__identity="Student").count()
            active_student_count = User.objects.filter(created_by=self.get_user().created_by,user_role__identity="Student",status="active").count()
            blocked_student_count = User.objects.filter(created_by=self.get_user().created_by,user_role__identity="Student",status="inactive").count()
        else:
            student_count = User.objects.filter(created_by=self.get_user(),user_role__identity="Student").count()
            active_student_count = User.objects.filter(created_by=self.get_user(),user_role__identity="Student",status="active").count()
            blocked_student_count = User.objects.filter(created_by=self.get_user(),user_role__identity="Student",status="inactive").count()

        # Course Learning Content counts details
        course_learning_content_count = Course.objects.filter(id__in=course_ids).count()
        lp_learning_content_count = LearningPath.objects.filter(id__in=lp_ids).count()
        alp_learning_content_count = CertificationPath.objects.filter(id__in=alp_ids).count()
        total_content_count = course_learning_content_count + lp_learning_content_count + alp_learning_content_count
        
        # Job Top List
        job_details = Job.objects.values('job_role').annotate(count=Count('job_role')).order_by('-count')[:3]
        total_job_count = sum(item['count'] for item in job_details)
        for item in job_details:
            item['percentage'] = (item['count'] / total_job_count) * 100

        # Institute User Group Content count details
        institute_user_group_count = user_group.count()
        user_group_list = self._InstitutionUserGroupSerializer(user_group.order_by("created")[:3], many=True).data

        # Institute Content Group count details
        institute_content_group_count = content_group.count()
        content_group_list = self._InstitutionContentGroupSerializer(content_group.order_by("created")[:3], many=True).data

        student={
            "total_student": student_count,
            "active_student": active_student_count,
            "blocked_student": blocked_student_count
        }
        learning_content={
            "total_content_count": total_content_count,
            "course_count": course_learning_content_count,
            "lp_count": lp_learning_content_count,
            "alp_count": alp_learning_content_count
        }
        institute_user_group={
            "institute_user_group_count": institute_user_group_count,
            "user_group_list": user_group_list
        }

        institute_content_group={
            "institute_content_group_count": institute_content_group_count,
            "content_group_list": content_group_list
        }
        return self.send_response(
            data={
                "student": student,
                "learning_content": learning_content,
                "institute_user_group": institute_user_group,
                "institute_content_group": institute_content_group,
                "top_job": job_details
            }
        )
    
class InstitutionAdminDashboardTrendingAPIView(ListAPIView, AppAPIView):
    """Sends out data for the Institute Dashboard page."""

    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = "__all__"
    search_fields = ["identity"]
    pagination_class = AppPagination

    def get_validated_serialized_data(self):
        serializer = ExploreSerializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        return data

    def get_model_for_serializer(self):
        data = self.get_validated_serialized_data()

        MODEL_CHOICES = {
            "courses": Course,
            "learning_paths": LearningPath,
            "certification_paths": CertificationPath,
        }

        model = MODEL_CHOICES[data["type"]]
        return model
    
    def get_queryset(self):
        model = self.get_model_for_serializer()
        
        if model.__name__ == "Course":
            qs = model.objects.filter(make_this_course_trending=True)[:50]
        elif model.__name__ == "LearningPath":
            qs = model.objects.filter(make_this_lp_trending=True)[:50]
        elif model.__name__ == "CertificationPath":
            qs = model.objects.filter(make_this_alp_trending=True)[:50]

        return qs
    
    def get_serializer_class(self):
        data_model = self.get_model_for_serializer()
        class _Serializer(get_app_read_only_serializer(data_model, "__all__")):
            def to_representation(self, instance):
                data = super().to_representation(instance=instance)

                if instance:
                    image = get_file_field_url(instance, "image")
                    data["image"] = image

                if data_model == 'Course':
                    enrolled_count = UserCourseTracker.objects.filter(entity_id=instance.id).count()
                    data["enrolled_count"] = enrolled_count
                elif data_model == 'LearningPath':
                    enrolled_count = UserLearningPathTracker.objects.filter(entity_id=instance.id).count()
                    data["enrolled_count"] = enrolled_count
                else:
                    enrolled_count = UserCertificatePathTracker.objects.filter(entity_id=instance.id).count()
                    data["enrolled_count"] = enrolled_count
                
                return data
        return _Serializer
    
    def post(self, request, *args, **kwargs):
        return self.get(request, *args, **kwargs)

def get_admin_headers():

    data_token = get_admin_token()
    header = {
        'Content-Type' : 'application/json',
        'Authorization': f'Bearer {data_token}'
    }
    return header

def get_admin_token():

    try:
        payload = {
            "userNameOrEmailAddress": settings.APP_SUPER_ADMIN['email'],
            "password": settings.APP_SUPER_ADMIN['password'],
            "rememberClient": True,
            "tenancyName": settings.IDP_TENANT_NAME
        }
        response = requests.post(settings.IDP_CONFIG['host'] + settings.IDP_CONFIG['authenticate_url'], json=payload)
        data = response.json()
        return data.get('accessToken')
    except Exception as e:
        raise e   
    

class CreateInstitutionAPIView(AppAPIView):
    """
    API to Create Institution from CMS.
    """

    class _Serializer(AppWriteOnlyModelSerializer):

        class Meta(AppWriteOnlyModelSerializer.Meta):
            fields = ["first_name", "middle_name", "last_name", "alternative_email"]
            model = User

    serializer_class = _Serializer

    def post(self, request, *args, **kwargs):
        """Use IDP to handle the same."""
        
        serializer = self.get_valid_serializer()
        class _InstitutionSerializer(AppModelSerializer):
            class Meta(AppWriteOnlyModelSerializer.Meta):
                model = InstitutionDetail
                fields = [
                    "identity", 
                    "banner_image", 
                    "contact_email_id", 
                    "alternative_conatct_email_id", 
                    "contact_number",
                    "accreditation",
                    "locality_street_address",
                    "country",
                    "state",
                    "city",
                    "pincode",
                    "courses",
                    "learning_paths",
                    "certification_paths",
                    "representative"
                ]

        serializer_class = _InstitutionSerializer  # Assign the serializer class

        institution_serializer = serializer_class(data=self.request.data)
        institution_serializer.is_valid(raise_exception=True)
        # idp_response = valid_idp_response(
        #     url_path="/api/access/v1/simple-signup/",
        #     request=self.get_request(),
        #     method="POST",
        # )
        headers = get_admin_headers()
        email = self.request.data["email"]
        password = self.request.data["password"]
        name = self.request.data["first_name"]
        payload = {
            "userId": 0,
            "tenantId": settings.IDP_TENANT_ID,
            "tenantDisplayName": name,
            "tenantName": settings.IDP_TENANT_NAME,
            "role": "TenantUser",
            "email": email,
            "name": name,
            "surname": name,
            "configJson": "string",
            "password": password,
            "businessUnitName": "test",
            "userIdNumber": "string",
            "userGrade": "string",
            "isOnsiteUser": "yes",
            "managerName": "test",
            "managerEmail": "test@gmail.com",
            "managerId": 0,
            "organizationUnitId": 0
        }

        idp_response = requests.post(settings.IDP_CONFIG['host'] + settings.IDP_CONFIG['user_create_url'], json=payload, headers=headers)
        # print(idp_response)
        # breakpoint()
        data = idp_response.json()
        # full_name = data.get('name') + data.get('surname')
        user_id = User.objects.filter(idp_user_id=data.get('userId')).first()
        if user_id is None and data.get('password') is not None:
            role = UserRole.objects.get(identity__icontains="IR")
            serializer.save(idp_user_id=data.get('userId'), password=data.get('password'), idp_email=data.get('email'), user_name=data.get('email'), first_name=data.get('name'), last_name=data.get('surname'), full_name=name, user_role=role)
            # return self.send_response()
            # serializer.save(idp_user_id=idp_response["user"]["uuid"],user_role=role)
            # idp_response["user"] = {**idp_response["user"], **serializer.data}

            # print(idp_response["user"]["id"])

            if data:
                user = User.objects.get(idp_user_id=data.get('userId'))
                institution_serializer.save(representative=user)

        else:
            return self.send_error_response(data={'detail': "User Already exists"})

        # idp_response["institution"] = institution_serializer.data

        # return self.send_response()
        html_content=f'Welcome, you have successfully signed up <br> Your signed up details are: <br> Full Name: {name} <br> Email Id: {email} <br> Password: {password}'
        success, message = send_welcome_email(email, 'Welcome', html_content)

        if success:
            return self.send_response(data={'detail': message})
        else:
            return self.send_error_response(data={'detail': message})
    
class UpdateInstitutionAPIView(AppAPIView):
    """This class provides edit the user Details from Admin"""

    class _InstitutionSerializer(AppWriteOnlyModelSerializer):

        class Meta(AppWriteOnlyModelSerializer.Meta):
            model = InstitutionDetail
            fields = [
                "identity", 
                "banner_image", 
                "contact_email_id", 
                "alternative_conatct_email_id", 
                "contact_number",
                "accreditation",
                "locality_street_address",
                "country",
                "state",
                "city",
                "pincode",
                "courses",
                "learning_paths",
                "certification_paths",
                # "representative"
            ]

        def update(self, instance, validated_data):
            instance = super().update(validated_data=validated_data, instance=instance)
            return instance

    serializer_class = _InstitutionSerializer


    def post(self, *args, **kwargs):
        institute = InstitutionDetail.objects.get(id=kwargs['id'])
        serializer = self.get_valid_serializer(instance=institute)
        serializer.save()
        return self.send_response()


class CreateInstitutionUserGroupAPIView(AppAPIView):
    """
    API to Create Institution from CMS.
    """

    def post(self, request, *args, **kwargs):
        """Use IDP to handle the same."""

        class _InstitutionUserGroupSerializer(AppModelSerializer):
            class Meta(AppWriteOnlyModelSerializer.Meta):
                model = InstitutionUserGroupDetail
                fields = [
                    "identity", 
                    "description",
                    "user",
                ]

        serializer_class = _InstitutionUserGroupSerializer  # Assign the serializer class

        institution_user_group_serializer = serializer_class(data=self.request.data)
        institution_user_group_serializer.is_valid(raise_exception=True)
        user = self.get_user()
        institution = InstitutionDetail.objects.get_or_none(representative=user)
        if institution:
            institution_user_group_serializer.save(institution=institution, admin_created=False)

        institution_user_group = institution_user_group_serializer.data

        return self.send_response(institution_user_group)
    
class UpdateInstitutionUserGroupAPIView(AppAPIView):
    """This class provides edit the user Details from Admin"""

    class _InstitutionInstitutionUserGroupSerializer(AppWriteOnlyModelSerializer):

        class Meta(AppWriteOnlyModelSerializer.Meta):
            model = InstitutionUserGroupDetail
            fields = [
                "identity", 
                "description",
                "user",
            ]

        def update(self, instance, validated_data):
            instance = super().update(validated_data=validated_data, instance=instance)
            return instance

    serializer_class = _InstitutionInstitutionUserGroupSerializer

    def post(self, *args, **kwargs):
        institute = InstitutionUserGroupDetail.objects.get(id=kwargs['id'])
        serializer = self.get_valid_serializer(instance=institute)
        serializer.save()

        return self.send_response()
    
class DetailInstitutionUserGroupAPIView(AbstractLookUpFieldMixin, RetrieveAPIView, AppAPIView):
    """
    This APIView gives Institution User Group details.
    """
    class _Serializer(AppReadOnlyModelSerializer):

        user = get_app_read_only_serializer(User, meta_fields="__all__")(many=True)

        class Meta(AppReadOnlyModelSerializer.Meta):
            model = InstitutionUserGroupDetail
            fields = [
                "id",
                "uuid",
                "identity",
                "description",
                "user"
            ]

    serializer_class = _Serializer
    queryset = InstitutionUserGroupDetail.objects.all()
    
class MetaInstitutionUserGroupAPIView(AppAPIView):

    def get(self, request, *args, **kwargs):
        user = self.get_user()

        data = {
            "students": get_app_read_only_serializer(
                User, meta_fields=['id', 'uuid', 'first_name', 'middle_name', 'last_name', 'alternative_email'],
                init_fields_config={
                    "user_role_detail": get_app_read_only_serializer(
                        meta_model= UserRole, meta_fields=['id','identity']
                    )(source="user_role"),
                }
            )(User.objects.filter(created_by=user, user_role__identity="Student"), many=True).data,
        }
        return self.send_response(data=data)

class DetailInstitutionUserGroupContentAPIView(AbstractLookUpFieldMixin, RetrieveAPIView, AppAPIView):
    """
    This APIView gives Institution User Group details.
    """
        
    class _Serializer(AppReadOnlyModelSerializer):
        class _CourseSerializer(AppReadOnlyModelSerializer):      
            image = get_app_read_only_serializer(CourseImage, meta_fields="__all__")()
            enrolled_count = serializers.SerializerMethodField()

            class Meta(AppReadOnlyModelSerializer.Meta):
                fields = ["id", "uuid", "identity","description","image","rating","duration", "enrolled_count"]
                model = Course

            def get_enrolled_count(self,obj):
                count = (
                    UserCourseTracker.objects.filter(entity=obj).count()
                    + StudentEnrolledCourseTracker.objects.filter(entity=obj).count()
                    + UserSubscriptionPlanCourseTracker.objects.filter(entity=obj).count()
                )
                return count

        class _LearningPathSerializer(AppReadOnlyModelSerializer):      
            image = get_app_read_only_serializer(LearningPathImage, meta_fields="__all__")()
            enrolled_count = serializers.SerializerMethodField()

            class Meta(AppReadOnlyModelSerializer.Meta):
                fields = ["id", "uuid", "identity","description","image","rating","duration", "enrolled_count"]
                model = LearningPath

            def get_enrolled_count(self,obj):
                count = (
                    UserLearningPathTracker.objects.filter(entity=obj).count()
                    + StudentEnrolledLearningPathTracker.objects.filter(entity=obj).count()
                    + UserSubscriptionPlanLearningPathTracker.objects.filter(entity=obj).count()
                )
                return count

        class _CertificationPathSerializer(AppReadOnlyModelSerializer):      
            image = get_app_read_only_serializer(CertificationPathImage, meta_fields="__all__")()
            enrolled_count = serializers.SerializerMethodField()
            
            class Meta(AppReadOnlyModelSerializer.Meta):
                fields = ["id", "uuid", "identity","description","image","rating","duration", "enrolled_count"]
                model = CertificationPath

            def get_enrolled_count(self,obj):
                count = (
                    UserCertificatePathTracker.objects.filter(entity=obj).count()
                    + StudentEnrolledCertificatePathTracker.objects.filter(entity=obj).count()
                    + UserSubscriptionPlanCertificatePathTracker.objects.filter(entity=obj).count()
                )
                return count
        
        courses = _CourseSerializer(Course.objects.all(), many=True)
        learning_path = _LearningPathSerializer(LearningPath.objects.all(), many=True)
        certification_path = _CertificationPathSerializer(CertificationPath.objects.all(), many=True)

        user_group = get_app_read_only_serializer(InstitutionUserGroupDetail, meta_fields="__all__")(many=True)

        class Meta(AppReadOnlyModelSerializer.Meta):
            model = InstitutionUserGroupContent
            fields = [
                "id",
                "uuid",
                "identity",
                "description",
                "user_group",
                "courses",
                "learning_path",
                "certification_path",
            ]

    serializer_class = _Serializer
    queryset = InstitutionUserGroupContent.objects.all()
    
class DetailInstitutionUserGroupContentAPIView(AbstractLookUpFieldMixin, RetrieveAPIView, AppAPIView):
    """
    This APIView gives Institution User Group details.
    """

    class _Serializer(AppReadOnlyModelSerializer):
        class _CourseSerializer(AppReadOnlyModelSerializer):      
            image = get_app_read_only_serializer(CourseImage, meta_fields="__all__")()
            enrolled_count = serializers.SerializerMethodField()

            class Meta(AppReadOnlyModelSerializer.Meta):
                fields = ["id", "uuid", "identity","description","image","rating","duration", "enrolled_count"]
                model = Course

            def get_enrolled_count(self,obj):
                count = (
                    UserCourseTracker.objects.filter(entity=obj).count()
                    + StudentEnrolledCourseTracker.objects.filter(entity=obj).count()
                    + UserSubscriptionPlanCourseTracker.objects.filter(entity=obj).count()
                )
                return count

        class _LearningPathSerializer(AppReadOnlyModelSerializer):      
            image = get_app_read_only_serializer(LearningPathImage, meta_fields="__all__")()
            enrolled_count = serializers.SerializerMethodField()

            class Meta(AppReadOnlyModelSerializer.Meta):
                fields = ["id", "uuid", "identity","description","image","rating","duration", "enrolled_count"]
                model = LearningPath

            def get_enrolled_count(self,obj):
                count = (
                    UserLearningPathTracker.objects.filter(entity=obj).count()
                    + StudentEnrolledLearningPathTracker.objects.filter(entity=obj).count()
                    + UserSubscriptionPlanLearningPathTracker.objects.filter(entity=obj).count()
                )
                return count

        class _CertificationPathSerializer(AppReadOnlyModelSerializer):      
            image = get_app_read_only_serializer(CertificationPathImage, meta_fields="__all__")()
            enrolled_count = serializers.SerializerMethodField()

            class Meta(AppReadOnlyModelSerializer.Meta):
                fields = ["id", "uuid", "identity","description","image","rating","duration", "enrolled_count"]
                model = CertificationPath

            def get_enrolled_count(self,obj):
                count = (
                    UserCertificatePathTracker.objects.filter(entity=obj).count()
                    + StudentEnrolledCertificatePathTracker.objects.filter(entity=obj).count()
                    + UserSubscriptionPlanCertificatePathTracker.objects.filter(entity=obj).count()
                )
                return count
        
        class _UserGroupDetailsSerializer(AppReadOnlyModelSerializer):
            user = StudentDetailSerializer(many=True)
            class Meta(AppReadOnlyModelSerializer.Meta):
                fields = ["id", "uuid", "identity", "user"]
                model = InstitutionUserGroupDetail
        
        courses = _CourseSerializer(Course.objects.all(), many=True)
        learning_path = _LearningPathSerializer(LearningPath.objects.all(), many=True)
        certification_path = _CertificationPathSerializer(CertificationPath.objects.all(), many=True)
        user_group = _UserGroupDetailsSerializer(InstitutionUserGroupDetail.objects.all(), many=True)

        # user_group = get_app_read_only_serializer(InstitutionUserGroupDetail, meta_fields="__all__")(many=True)

        class Meta(AppReadOnlyModelSerializer.Meta):
            model = InstitutionUserGroupContent
            fields = [
                "id",
                "uuid",
                "identity",
                "description",
                "user_group",
                "courses",
                "learning_path",
                "certification_path",
            ]

    serializer_class = _Serializer
    queryset = InstitutionUserGroupContent.objects.all()
    
class MetaInstitutionUserGroupContentAPIView(AppAPIView):

    def get(self, request, *args, **kwargs):
        user = self.get_user()
        institution = InstitutionDetail.objects.get(representative=user)
        course_ids = [course.id for course in institution.courses.all()]
        lp_ids = [lp.id for lp in institution.learning_paths.all()]
        alp_ids = [alp.id for alp in institution.certification_paths.all()]

        # Retrieve the InstitutionUserGroupDetail objects and serialize them
        user_groups = InstitutionUserGroupDetail.objects.filter(institution=institution)
        user_group_serializer = get_app_read_only_serializer(
            InstitutionUserGroupDetail,
            meta_fields=['id', 'uuid', 'identity', 'description', 'user']
        )
        serialized_user_groups = user_group_serializer(user_groups, many=True).data

        # Retrieve the Course objects and serialize them
        courses = Course.objects.filter(id__in=course_ids)
        course_serializer = get_app_read_only_serializer(Course, 
            meta_fields=['id', 'uuid','identity', 'code', 'description', 'image', 'duration', 'rating', 'validity'],
            init_fields_config={
                "image_details": get_app_read_only_serializer(
                    meta_model= CourseImage, meta_fields=['id','uuid','file']
                )(source="image"),
            }
        )
        serialized_courses = course_serializer(courses, many=True).data

        # Retrieve the Course objects and serialize them
        learning_paths = LearningPath.objects.filter(id__in=lp_ids)
        lp_serializer = get_app_read_only_serializer(LearningPath,
            meta_fields=['id', 'uuid','identity', 'code', 'description', 'image', 'duration', 'rating', 'validity'],
            init_fields_config={
                "image_details": get_app_read_only_serializer(
                    meta_model= LearningPathImage, meta_fields=['id','uuid','file']
                )(source="image"),
            }
        )
        serialized_lp = lp_serializer(learning_paths, many=True).data

        # Retrieve the Course objects and serialize them
        certification_paths = CertificationPath.objects.filter(id__in=alp_ids)
        alp_serializer = get_app_read_only_serializer(CertificationPath,
            meta_fields=['id', 'uuid','identity', 'code', 'description', 'image', 'duration', 'rating', 'validity'],
            init_fields_config={
                "image_details": get_app_read_only_serializer(
                    meta_model= CertificationPathImage, meta_fields=['id','uuid','file']
                )(source="image"),
            }
        )
        serialized_alp = alp_serializer(certification_paths, many=True).data

        data = {
            "user_group": serialized_user_groups,
            "courses": serialized_courses,
            "learning_paths": serialized_lp,
            "certification_path": serialized_alp
        }
        return self.send_response(data=data)

    # filter_backends = [DjangoFilterBackend, SearchFilter]
    # filterset_fields = "__all__"
    # search_fields = ["identity"]

    # def get_validated_serialized_data(self):
    #     serializer = ExploreSerializer(data=self.request.data)
    #     serializer.is_valid(raise_exception=True)
    #     data = serializer.validated_data
    #     return data

    # def get_model_for_serializer(self):
    #     data = self.get_validated_serialized_data()

    #     MODEL_CHOICES = {
    #         "courses": Course,
    #         "learning_paths": LearningPath,
    #         "certification_paths": CertificationPath,
    #     }

    #     model = MODEL_CHOICES[data["type"]]
    #     return model

    # def get_queryset(self):
    #     model = self.get_model_for_serializer()
    #     institution = InstitutionDetail.objects.get(representative=self.get_user())
    #     if model == Course:
    #         ids = institution.courses.all().values_list('id', flat=True)
    #     elif model == LearningPath:
    #         ids = institution.learning_paths.all().values_list('id', flat=True)
    #     elif model == CertificationPath:
    #         ids = institution.certification_paths.all().values_list('id', flat=True)
    #     qs = model.objects.filter(id__in=ids)
    #     return qs

    # def get_serializer_class(self):
    #     class LearningContentSerializer(serializers.ModelSerializer):
    #         def to_representation(self, instance):
    #             data = super().to_representation(instance=instance)

    #             image_url = "https://b2cstagingv2.blob.core.windows.net/appuploads/media/"
    #             if instance.image:
    #                 image = str(instance.image.file)
    #                 data["image"] = image_url+image
    #             return data
    #         class Meta:
    #             model = self.get_model_for_serializer()
    #             fields = ["id", "uuid", "identity", "description", "image", "current_price_inr", "rating", "duration"]
        
    #     return LearningContentSerializer

    # def post(self, request, *args, **kwargs):
    #     return self.get(request, *args, **kwargs)


class ReportGenerateAPIView(AppAPIView):
    
    class _Serializer(AppWriteOnlyModelSerializer):
        """Handle input data."""
        class Meta(AppWriteOnlyModelSerializer.Meta):
            fields = ["identity", "user_group", "content_group", "start_date", "end_date", "filter_parameters"]
            model = StudentReportDetail

    serializer_class = _Serializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_valid_serializer()
        serializer.is_valid(raise_exception=True)
        report_detail = serializer.save()

        generate_report.delay(report_detail.id)
        response_data = {'status': "your report is processing"}

        return self.send_response(data=response_data)


class ReportListAPIView(ListAPIView, AppAPIView):
    """Sends out data for the report Listing Page."""

    class _Serializer(AppReadOnlyModelSerializer):
        """Handle input data."""
        report = get_app_read_only_serializer(StudentReportFile, meta_fields=["id","uuid","file"])()
        status = serializers.SerializerMethodField()
        created = serializers.SerializerMethodField()
        serial_number = serializers.SerializerMethodField()

        class Meta(AppReadOnlyModelSerializer.Meta):
            fields = ["id","uuid","identity","created","report","start_date","end_date","status","serial_number"]
            model = StudentReportDetail
        
        def get_status(self, obj):
            return "Generated" if obj.report else "Processing"
        
        def get_created(self, obj):
            return obj.created.date()

        def get_serial_number(self, obj):
            queryset = StudentReportDetail.objects.filter(created_by=self.get_user())
            return list(queryset).index(obj) + 1

    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = "__all__"
    search_fields = ["identity"]
    pagination_class = AppPagination
    serializer_class = _Serializer

    def get_queryset(self, *args, **kwargs):
        user = self.get_user()
        return StudentReportDetail.objects.filter(created_by=user)

class ReportDeleteAPIView(AppAPIView):
    """This view used to delete report of a student"""

    def get_object(self, pk):
        return StudentReportDetail.objects.get(pk=pk)
    
    def delete(self, request, pk, format=None):
        data = self.get_object(pk)
        user = self.get_user()
        if data.created_by == user:
            data.delete()
            return self.send_response()
        return self.send_error_response()
    
class ReportGenerateMetaAPIView(AppAPIView):

    def get(self, request, *args, **kwargs):
        user = self.get_user()
        institution = InstitutionDetail.objects.get(representative=user)
        user_group = InstitutionUserGroupDetail.objects.filter(institution=institution)
        data = {
            "user_group": get_app_read_only_serializer(
                InstitutionUserGroupDetail, meta_fields=['id', 'uuid', 'identity']
            )(InstitutionUserGroupDetail.objects.filter(institution=institution), many=True).data,
            "content_group": get_app_read_only_serializer(
                InstitutionUserGroupContent, meta_fields=['id', 'uuid', 'identity']
            )(InstitutionUserGroupContent.objects.filter(user_group__in=user_group).distinct(), many=True).data,
            "filter_parameters": get_app_read_only_serializer(
                ReportFilterParameter, meta_fields=['id', 'uuid', 'identity'],
            )(ReportFilterParameter.objects.all(), many=True).data,
        }
        return self.send_response(data=data)
    
class LogoImageAPIView(AppAPIView):
    def get(self, request):
        auth_user = self.get_user()
        if auth_user:
            if auth_user.user_role:
                if auth_user.user_role.identity == "Student":
                    institution = InstitutionDetail.objects.filter(representative=auth_user.created_by).first()
                    if institution:
                        image=get_file_field_url(institution, "banner_image")
                elif auth_user.user_role.identity == "Institution Representative":
                    institution = InstitutionDetail.objects.get(representative=self.get_user())
                    if institution:
                        image=get_file_field_url(institution, "banner_image")
                elif auth_user.user_role.identity == "Employer":
                    employer = EmployerDetail.objects.get(representative=self.get_user())
                    if employer:
                        image=get_file_field_url(employer, "logo_image")
                else:
                    image=None
            else:
                image=None
        else:
            image=None

        data= {
            "image": image
        }

        return self.send_response(data=data) 
    
class StudentsBulkUploadAPIView(AppAPIView):
     # Students Bulk Upload

    def post(self, request, *args, **kwargs):

        file_obj = request.FILES.get("file")
        if file_obj:
            paramFile = io.TextIOWrapper(file_obj.file)
            portfolio1 = csv.DictReader(paramFile)
            list_of_dict = list(portfolio1)

            # iterating through every row to get the data of each students
            for row in list_of_dict:
                headers = get_admin_headers()
                email = row['email']
                password = row['password']
                name = row['full_name']
                payload = {
                    "userId": 0,
                    "tenantId": settings.IDP_TENANT_ID,
                    "tenantDisplayName": name,
                    "tenantName": settings.IDP_TENANT_NAME,
                    "role": "TenantUser",
                    "email": email,
                    "name": name,
                    "surname": name,
                    "configJson": "string",
                    "password": password,
                    "businessUnitName": "test",
                    "userIdNumber": "string",
                    "userGrade": "string",
                    "isOnsiteUser": "yes",
                    "managerName": "test",
                    "managerEmail": "test@gmail.com",
                    "managerId": 0,
                    "organizationUnitId": 0
                }

                idp_response = requests.post(settings.IDP_CONFIG['host'] + settings.IDP_CONFIG['user_create_url'], json=payload, headers=headers)
                data = idp_response.json()
                user_id = User.objects.filter(idp_user_id=data.get('userId')).first()

                if user_id is None:
                    idp_user_id=data.get('userId')

                    birth_date = convert_date_format(row['birth_date'])
                    gender = row.get('gender').strip()
                    # user_role = row.get('user_role')
                    identification_type = row.get('identification_type').strip()
                    city = row.get('city').strip()
                    state = row.get('state').strip()
                    country = row.get('country').strip()
                    user_group = row.get('user_group').strip()

                    # Education details
                    qualification = row.get('qualification').strip()
                    university_name = row.get('university_name').strip()
                    degree = row.get('degree').strip()

                    # Get the related objects based on the fk
                    user_role = UserRole.objects.filter(identity="Student").first()
                    gender = profile_models.UserGender.objects.filter(identity=gender).first() if gender else None
                    identification_type = profile_models.UserIdentificationType.objects.filter(identity=identification_type).first() if identification_type else None
                    city = location_models.City.objects.filter(identity=city).first() if city else None
                    state = location_models.State.objects.filter(identity=state).first() if state else None
                    country = location_models.Country.objects.filter(identity=country).first() if country else None
                    qualification = profile_models.EducationQualification.objects.filter(identity=qualification).first() if qualification else None
                    university_name = profile_models.EducationUniversity.objects.filter(identity=university_name).first() if university_name else None
                    degree = profile_models.OnboardingHighestEducation.objects.filter(identity=degree).first() if degree else None

                    student = User.objects.create(
                            full_name=row['full_name'],
                            alternative_email=row['alternative_email'],
                            idp_user_id=idp_user_id,
                            password=row['password'],
                            idp_email=row['email'],
                            user_name=row['email'],
                            first_name=row['first_name'],
                            middle_name=row['middle_name'],
                            last_name=row['last_name'],
                            gender=gender,
                            birth_date=birth_date,
                            identification_type=identification_type,
                            identification_number=row['identification_number'],
                            address=row['address'],
                            pincode=row['pincode'],
                            admission_id=row['admission_id'],
                            city=city,
                            state=state,
                            country=country,
                            created_by=self.get_user(),
                            user_role=user_role
                        )

                    # Add the student to user group if user_group_id is present in the file
                    institution = InstitutionDetail.objects.get(representative=self.get_user())
                    if institution:
                        user_group, _ = InstitutionUserGroupDetail.objects.get_or_create(identity=user_group,institution=institution)
                        if user_group:
                            user_group.user.add(student)

                    # adding the educational details of the student (MtoM field)
                    if qualification and university_name and degree and row.get('college_name'):
                        # Create EducationDetail object
                        edu_detail = profile_models.EducationDetail.objects.create(
                            qualification=qualification,
                            university_name=university_name,
                            degree=degree,
                            college_name=row.get('college_name'),
                            class_name=row.get('college_name'),
                            overall_percentage=row.get('overall_percentage'),
                        )
                        student.education_details.add(edu_detail)

                    # html_content=f'Welcome, you have successfully signed up <br> Your signed up details are: <br> Full Name: {name} <br> Email Id: {email} <br> Password: {password}'
                    EmailNotification(
                        email_to=email,
                        template_code='student_signup',
                        kwargs={
                            "first_name": data.get('name'), 
                            "institute_name": institution.identity,
                            "link": f"{settings.FRONTEND_WEB_URL}institute/student/login/",
                            "email": data.get('email'),
                            "password": data.get('password')
                        }
                    )

                else:
                    return self.send_error_response({'message': 'Email ID and Phone number Already exists in IDP.'}) 
                
            return self.send_response() 

        return self.send_error_response() 

class UsersBulkUploadAPIView(AppAPIView):
     # Students Bulk Upload

    def post(self, request, *args, **kwargs):

        file_obj = request.FILES.get("file")
        if file_obj:
            paramFile = io.TextIOWrapper(file_obj.file)
            portfolio1 = csv.DictReader(paramFile)
            list_of_dict = list(portfolio1)

            # iterating through every row to get the data of each students
            for row in list_of_dict:
                headers = get_admin_headers()
                email = row['email']
                password = row['email']
                name = row['full_name']
                phone_number = row['phone_number']
                payload = {
                    "userId": 0,
                    "tenantId": settings.IDP_TENANT_ID,
                    "tenantDisplayName": name,
                    "tenantName": settings.IDP_TENANT_NAME,
                    "role": "TenantUser",
                    "email": email,
                    "name": name,
                    "surname": name,
                    "configJson": "string",
                    "password": password,
                    "businessUnitName": "test",
                    "userIdNumber": "string",
                    "userGrade": "string",
                    "isOnsiteUser": "yes",
                    "managerName": "test",
                    "managerEmail": "test@gmail.com",
                    "managerId": 0,
                    "organizationUnitId": 0
                }

                idp_response = requests.post(settings.IDP_CONFIG['host'] + settings.IDP_CONFIG['user_create_url'], json=payload, headers=headers)
                data = idp_response.json()
                user_id = User.objects.filter(idp_user_id=data.get('userId')).first()
                user_role = UserRole.objects.filter(identity="Learner").first()
                if user_id is None:
                    idp_user_id=data.get('userId')
                    user = User.objects.create(
                            full_name=row['full_name'],
                            alternative_email=row['email'],
                            idp_user_id=idp_user_id,
                            password=row['email'],
                            idp_email=row['email'],
                            user_name=row['email'],
                            phone_number= "+91" + str(phone_number),
                            user_role=user_role,
                            created_by=self.get_user()
                        )

                else:
                    return self.send_error_response({'message': 'Email ID and Phone number Already exists in IDP.'}) 
                
            return self.send_response() 

        return self.send_error_response() 
