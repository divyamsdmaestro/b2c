from apps.common.helpers import EmailNotification
from apps.common.views.api import AppAPIView
from apps.common.serializers import AppWriteOnlyModelSerializer
from apps.access.models import User, UserRole, InstitutionDetail
from apps.learning.models.linkages import LearningRole
from apps.service_idp.views import valid_idp_response
from apps.cms.serializers import StudentSerializer, StaffSerializer
from apps.common.serializers import AppWriteOnlyModelSerializer, AppReadOnlyModelSerializer, get_app_read_only_serializer
from rest_framework.generics import RetrieveAPIView
from apps.common.views.api.generic import (
    AbstractLookUpFieldMixin,
)
from apps.common.pagination import AppPagination
from apps.meta.models import EducationDetail, EducationUniversity
from apps.meta.models import profile as profile_models
from apps.meta.models import location as location_models
from apps.my_learnings.models import UserCourseTracker
from apps.my_learnings.helpers import get_one_year_datetime_from_now
from apps.common.serializers import simple_serialize_instance, simple_serialize_queryset
from apps.my_learnings.models import UserCourseTracker
# import pandas as pd
from apps.learning.models import Course, CourseModule, CourseSubModule, Skill, Category, ModuleType
from django.db import IntegrityError
from apps.learning.models import (
    Accreditation,
    Author,
    Tutor,
    Vendor,
    Language,
    CourseLevel,
    Proficiency,
    CourseImage,
)
from apps.jobs.models import EducationQualification
from datetime import datetime
import io,csv
import requests
from django.conf import settings
from apps.my_learnings.models import UserSubscriptionPlanCourseTracker, UserSubscriptionPlanCourseModuleTracker, UserSubscriptionPlanCourseSubModuleTracker


class CreateUserAPIView(AppAPIView):
    """
    API to add user from cms.
    """

    class _Serializer(AppWriteOnlyModelSerializer):
        class Meta(AppWriteOnlyModelSerializer.Meta):
            fields = ["first_name", "middle_name", "last_name", "user_role", "alternative_email", "address", "country", "state", "city", "pincode"]
            model = User

    serializer_class = _Serializer

    def post(self, *args, **kwargs):
        """Use IDP to handle the same."""

        serializer = self.get_valid_serializer()
        # idp_response = valid_idp_response(
        #     url_path="/api/access/v1/simple-signup/",
        #     request=self.get_request(),
        #     method="POST",
        # )

        # serializer.save(idp_user_id=idp_response["user"]["uuid"])
        # idp_response["user"] = {**idp_response["user"], **serializer.data}
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
        data = idp_response.json()
        user_id = User.objects.filter(idp_user_id=data.get('userId')).first()
        if user_id is None:
            role = UserRole.objects.get(id=self.request.data["user_role"])
            serializer.save(idp_user_id=data.get('userId'), password=data.get('password'), idp_email=data.get('email'), user_name=data.get('email'), first_name=data.get('name'), last_name=data.get('surname'), full_name=name, user_role=role)
            return self.send_response()
        else:
            return self.send_error_response(data={'detail': "User Already exists"})

class UpdateUserAPIView(AppAPIView):
    """This APIView is to edit the user profiles Details"""

    class _Serializer(AppWriteOnlyModelSerializer):
        class Meta(AppWriteOnlyModelSerializer.Meta):
            model = User
            fields = [
                "first_name",
                "middle_name",
                "last_name",
                "user_role",
                "alternative_email",
                "address",
                "country",
                "state",
                "city",
                "pincode",
            ]
    serializer_class = _Serializer

    def put(self, request, pk):
        try:
            instance = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return self.send_response()
        serializer = self.get_valid_serializer(instance=instance)
        if serializer.is_valid():
            serializer.save()
            return self.send_response(serializer.data)
        return self.send_error_response(serializer.errors)

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
    
class StudentCreateAPIView(AppAPIView):
    """
    API to add a student from CMS.
    """

    serializer_class = StudentSerializer

    def post(self, *args, **kwargs):
        """Use IDP to handle the same."""
        user=self.get_user()
        serializer = self.get_valid_serializer()
        serializer.is_valid(raise_exception=True)

        education_details_data = serializer.validated_data.pop('education_details', [])
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
        data = idp_response.json()
        user_id = User.objects.filter(idp_user_id=data.get('userId')).first()
        # full_name = data.get('name') + data.get('surname')
        if user_id is None and data.get('password') is not None:
            role = UserRole.objects.get(identity__icontains="Student")
            serializer.save(idp_user_id=data.get('userId'), password=data.get('password'), idp_email=data.get('email'), user_name=data.get('email'), first_name=data.get('name'), last_name=data.get('surname'), full_name=name, user_role=role)
            # Create education details
            # for education_detail_data in education_details_data:
            #     serializer.education_details.create(**education_detail_data)

            # return self.send_response()
        else:
            return self.send_error_response(data={'detail': "User Already exists"})
        
        # serializer.validated_data["idp_user_id"] = data.get('userId')
        
        # user = serializer.save(user_role=role) # set user role here
          
        
        # idp_response["user"] = {**idp_response["user"], **serializer.data}

        # return self.send_response()
        institute=InstitutionDetail.objects.get(representative=user)
        EmailNotification(
            email_to=email,
            template_code='student_signup',
            kwargs={
                "first_name": data.get('name'), 
                "institute_name": institute.identity,
                "link": f"{settings.FRONTEND_WEB_URL}institute/student/login/",
                "email": data.get('email'),
                "password": data.get('password')
            }
        )

        return self.send_response()

class StudentEditAPIView(AppAPIView):
    """This APIView is to edit the student profiles Details"""

    serializer_class = StudentSerializer

    def get_object(self, id):
        return User.objects.get(id=id)

    def post(self, *args, **kwargs):
        data = self.get_object(kwargs["id"])
        serializer = self.get_valid_serializer(instance=data)
        serializer.save()
        return self.send_response()


class StudentDeleteAPIView(AppAPIView):
    """This APIView is to delete the user"""

    def get_object(self, id):
        return User.objects.get(id=id)

    def post(self, *args, **kwargs):
        instance = self.get_object(kwargs["id"])
        instance.status = User.USER_STATUS_CHOICES[1][1]
        instance.save()

        return self.send_response()


class StudentDetailAPIView(
    AbstractLookUpFieldMixin, RetrieveAPIView, AppAPIView
):
    """
    This APIView gives student details.
    """

    class _Serializer(AppReadOnlyModelSerializer):
        class _EducationDetailSerializer(AppReadOnlyModelSerializer):
            qualification = get_app_read_only_serializer(EducationQualification, meta_fields="__all__")()
            university_name = get_app_read_only_serializer(EducationUniversity, meta_fields="__all__")()
            degree = get_app_read_only_serializer(profile_models.OnboardingHighestEducation, meta_fields="__all__")()

            class Meta:
                model = EducationDetail
                fields = ["qualification", "university_name", "degree", "college_name"]

        education_details = _EducationDetailSerializer(many=True)
        gender = get_app_read_only_serializer(profile_models.UserGender, meta_fields="__all__")()
        # martial_status = get_app_read_only_serializer(profile_models.UserMartialStatus, meta_fields="__all__")()
        identification_type = get_app_read_only_serializer(profile_models.UserIdentificationType, meta_fields="__all__")()
        state = get_app_read_only_serializer(location_models.State, meta_fields="__all__")()
        city = get_app_read_only_serializer(location_models.City, meta_fields="__all__")()
        country = get_app_read_only_serializer(location_models.Country, meta_fields="__all__")()

        class Meta(AppReadOnlyModelSerializer.Meta):
            model = User
            fields = [
                "first_name",
                "middle_name",
                "last_name",
                "gender",
                # "martial_status",
                "birth_date",
                "identification_type",
                "identification_number",
                "address",
                "country",
                "state",
                "city",
                "pincode",
                "education_details",
            ]

    serializer_class = _Serializer
    queryset = User.objects.all()


# class StudentListAPIView(NonAuthenticatedAPIMixin, ListAPIView, AppAPIView):

#     filter_backends = [DjangoFilterBackend]
#     filterset_fields = ["first_name", "alternative_email", "status"]
#     pagination_class = AppPagination
#     serializer_class = get_app_read_only_serializer(
#         meta_model=User, meta_fields=['id', 'first_name', 'phone_number', 'email', 'status'],
#     )

#     def get_queryset(self):
#         data = {}
#         queryset = User.objects.filter(created_by=self.get_user())
#         serializer = self.serializer_class(queryset, many=True)
#         data['data'] = serializer.data
#         return data


class StaffCreateAPIView(AppAPIView):
    """
    API to add a staff from CMS.
    """

    serializer_class = StaffSerializer

    def post(self, *args, **kwargs):
        """Use IDP to handle the same."""

        serializer = self.get_valid_serializer()
        serializer.is_valid(raise_exception=True)

        # idp_response = valid_idp_response(
        #     url_path="/api/access/v1/simple-signup/",
        #     request=self.get_request(),
        #     method="POST",
        # )
        # serializer.validated_data["idp_user_id"] = idp_response["user"]["uuid"]
        # role = UserRole.objects.get(identity__icontains="Staff")
        # user = serializer.save(user_role=role)
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
        data = idp_response.json()
        user_id = User.objects.filter(idp_user_id=data.get('userId')).first()
        # full_name = data.get('name') + data.get('surname')
        if user_id is None and data.get('password') is not None:
            role = UserRole.objects.get(identity__icontains="Staff")
            serializer.save(idp_user_id=data.get('userId'), password=data.get('password'), idp_email=data.get('email'), user_name=data.get('email'), first_name=data.get('name'), last_name=data.get('surname'), full_name=name, user_role=role)
            return self.send_response()
        else:
            return self.send_error_response(data={'detail': "User Already exists"})


class StaffEditAPIView(AppAPIView):
    """This class provides edit the staff profiles Details"""

    serializer_class = StaffSerializer

    def get_object(self, id):
        return User.objects.get(id=id)

    def post(self, *args, **kwargs):
        data = self.get_object(kwargs["id"])
        serializer = self.get_valid_serializer(instance=data)
        serializer.save()
        return self.send_response()


class StaffDeleteAPIView(AppAPIView):
    """This view used to delete"""

    def get_object(self, id):
        return User.objects.get(id=id)

    def post(self, *args, **kwargs):
        instance = self.get_object(kwargs["id"])
        instance.status = User.USER_STATUS_CHOICES[1][1]
        instance.save()

        return self.send_response()


class StaffDetailAPIView(
    AbstractLookUpFieldMixin, RetrieveAPIView, AppAPIView
):
    """
    This view staff details.
    """
    class _Serializer(AppReadOnlyModelSerializer):
        user_role = get_app_read_only_serializer(UserRole, meta_fields="__all__")()

        class Meta(AppReadOnlyModelSerializer.Meta):
            model = User
            fields = [
                "first_name",
                "middle_name",
                "last_name",
                "user_role"
            ]

    serializer_class = _Serializer
    queryset = User.objects.all()


# class StaffListAPIView(NonAuthenticatedAPIMixin, ListAPIView, AppAPIView):

#     filter_backends = [DjangoFilterBackend]
#     filterset_fields = "__all__"
#     pagination_class = AppPagination
#     serializer_class = get_app_read_only_serializer(
#         meta_model=User, meta_fields=['id', 'first_name', 'phone_number', 'email', 'status'],
#     )

#     def get_queryset(self):
#         data = {}
#         queryset = User.objects.filter(created_by=self.get_user())
#         serializer = self.serializer_class(queryset, many=True)
#         data['data'] = serializer.data
#         return data



class StudentMyLearningsAPIView(AppAPIView):
    """Returns the data for my learnings home/list page."""

    def get(self, request, *args, **kwargs):
        """Handle on get."""

        user = User.objects.get(uuid=kwargs["uuid"])
        trackers = [
            *UserCourseTracker.objects.filter(created_by=user)
            .select_related("entity", "entity__author")
            .prefetch_related("entity__skills")
        ]

        return self.send_response(data=[self.serialize_trackers(_) for _ in trackers])

    @staticmethod
    def serialize_trackers(tracker):
        """Serialize data for the front-end."""

        entity = tracker.entity

        data = simple_serialize_instance(
            instance=tracker,
            keys=[
                "uuid",
                "created",
                "valid_till",
                "progress",
                "last_accessed_on",
            ],
            parent_data={
                "entity": simple_serialize_instance(
                    instance=entity,
                    keys=[
                        "identity",
                        "image.file.url",
                        "uuid",
                        "__class__.__name__",
                    ],
                    parent_data={
                        "skills": simple_serialize_queryset(
                            queryset=entity.skills.all(), fields=["identity", "uuid"]
                        ),
                        "tutor": simple_serialize_instance(
                            instance=entity.author,
                            keys=["id", "identity", "designation"],
                        ),
                    },
                    display={
                        "image.file.url": "image",
                        "__class__.__name__": "type",
                    },
                ),
            },
        )

        return data

def convert_date_format(date_str):
    # Convert from "d/m/Y" to "Y-m-d H:i:s"
    
    # print(date_obj.strftime("%Y-%m-%d %H:%M:%S"))
    # breakpoint()
    if date_str:
        date_obj = datetime.strptime(date_str, "%d/%m/%Y")
        return date_obj
    else:
        return None
    
class SubPlanBulkUploadAPIView(AppAPIView):
      # Course Bulk Upload
    def post(self, request, *args, **kwargs):
        file_obj = request.FILES.get("file")
        if file_obj:
            paramFile = io.TextIOWrapper(file_obj.file)
            portfolio1 = csv.DictReader(paramFile)
            list_of_dict = list(portfolio1)
        else:
            list_of_dict = None
            return self.send_error_response()
        # Process the data and save to the database
        for row in list_of_dict:
            try:
                UserSubscriptionPlanCourseTracker.objects.create(
                    progress=0,
                    created_by_id=2621,
                    entity_id=row['entity_id'],
                    parent_tracker_id = 41
                )
            except Exception as e:
                # print('failed')
                # Handle the exception according to your requirements
                print(e)
                # breakpoint()
                # print(e)
            # if created:
            #     obj.save()
        return self.send_response()

class SubPlanModuleBulkUploadAPIView(AppAPIView):
      # Course Bulk Upload
    def post(self, request, *args, **kwargs):
        file_obj = request.FILES.get("file")
        if file_obj:
            paramFile = io.TextIOWrapper(file_obj.file)
            portfolio1 = csv.DictReader(paramFile)
            list_of_dict = list(portfolio1)
        else:
            list_of_dict = None
            return self.send_error_response()
        # Process the data and save to the database
        for row in list_of_dict:
            try:
                UserSubscriptionPlanCourseModuleTracker.objects.create(
                    progress=0,
                    created_by_id=2621,
                    entity_id=row['entity_id'],
                    parent_tracker_id =row['parent_tracker_id']
                )
            except Exception as e:
                # print('failed')
                # Handle the exception according to your requirements
                print(e)
                # breakpoint()
                # print(e)
            # if created:
            #     obj.save()
        return self.send_response()

class SubPlanSubModuleBulkUploadAPIView(AppAPIView):
      # Course Bulk Upload
    def post(self, request, *args, **kwargs):
        file_obj = request.FILES.get("file")
        if file_obj:
            paramFile = io.TextIOWrapper(file_obj.file)
            portfolio1 = csv.DictReader(paramFile)
            list_of_dict = list(portfolio1)
        else:
            list_of_dict = None
            return self.send_error_response()
        # Process the data and save to the database
        for row in list_of_dict:
            try:
                UserSubscriptionPlanCourseSubModuleTracker.objects.create(
                    progress=0,
                    created_by_id=2621,
                    entity_id=row['entity_id'],
                    parent_tracker_id = row['parent_tracker_id']
                )
            except Exception as e:
                # print('failed')
                # Handle the exception according to your requirements
                print(e)
                # breakpoint()
                # print(e)
            # if created:
            #     obj.save()
        return self.send_response()
    
class CourseBulkUploadAPIView(AppAPIView):
     # Course Bulk Upload
    def post(self, request, *args, **kwargs):
        file_obj = request.FILES.get("file")
        if file_obj:
            paramFile = io.TextIOWrapper(file_obj.file)
            portfolio1 = csv.DictReader(paramFile)
            list_of_dict = list(portfolio1)
        else:
            list_of_dict = None
            return self.send_error_response()
        # Process the data and save to the database
        for row in list_of_dict:   
            # Save the data to the database
            accreditation = Accreditation.objects.get(identity=row['accreditation'])
            # course_image = CourseImage.objects.get(id=row[20])
            language = Language.objects.get(identity=row['language'])
            course_level = CourseLevel.objects.get(identity=row['course_level'])
            module_type = ModuleType.objects.get(identity=row['module_type'])
            converted_start_date = convert_date_format(row['start_date'])
            converted_end_date = convert_date_format(row['end_date'])
            author, _ = Author.objects.get_or_create(identity=row['author'])
            vendor, _ = Vendor.objects.get_or_create(identity=row['vendor'])
            learning_role, _ = LearningRole.objects.get_or_create(identity=row['learning_role'])

            if vendor not in author.vendor.all():
                author.vendor.add(vendor)

            if row['mml_sku_id']:
                mml_sku_id = row['mml_sku_id']
            else:
                mml_sku_id = None
            
            if row['vm_name']:
                vm_name = row['vm_name']
            else:
                vm_name = None

            if row['assessmentID']:
                assessmentID = row['assessmentID']
            else:
                assessmentID = 'NULL'
            course_data = {
                'current_price_inr': row['current_price_inr'],
                'cms_reference': row['cms_reference'],
                'identity': row['course_identity'],
                'code' : row['code'],
                'description' :row['course_description'],
                'duration' : row['course_duration'],
                'start_date' : converted_start_date,
                'end_date': converted_end_date,
                'enable_ratings' : row['enable_ratings'],
                'enable_feedback_comments' : row['enable_feedback_comments'],
                'sequential_course_flow':row['sequential_course_flow'],
                'is_certification_enabled' : row['is_certification_enabled'],
                'make_this_course_popular' : row['make_this_course_popular'],
                'make_this_course_trending' : row['make_this_course_trending'],
                'make_this_course_best_selling' : row['make_this_course_best_selling'],
                'editors_pick' : row['editors_pick'],
                'complete_in_a_day': row['complete_in_a_day'],
                'requirements': row['requirements'],
                'highlights' : row['highlights'],
                'rating': row['rating'],
                'validity': row['validity'],
                'accreditation_id':accreditation.id,
                'author_id': author.id,
                # 'image_id': course_image.id,
                'language_id' : language.id,
                'level_id': course_level.id,
                'vendor_id' : vendor.id,
                'is_free': row['is_free'],
                'mml_sku_id': mml_sku_id,
                'vm_name': vm_name,
                'virtual_lab': row['virtual_lab'],
                'is_private_course': row['is_private_course'],
                'learning_role': learning_role
                # Add other course fields as needed
            }
            course_module_data = {
                'identity': row['course_module_identity'],
                'description': row['course_module_description'],
                'position': row['course_module_position']
                # Add other course module fields as needed
            }
            course_submodule_data = {
                'identity': row['course_submodule_identity'],
                'description': row['course_submodule_description'],
                'duration': row['course_submodule_duration'],
                'position': row['course_submodule_position'],
                'module_type' : module_type,
                'video_url': row['video_url'],
                'assessmentID': assessmentID
            }
            
            # breakpoint()
            categoryies_list = row['categories'].split(',')
            skills_list = row['skills'].split(',')

            # Create a list to store Skill objects related to this course
            skills_objects = []
            categoryies_objects = []

            # Get or create the Skill objects and add them to the list
            for skill_name in skills_list:
                skill_name = skill_name.strip()  # Remove leading/trailing spaces
                skill, _ = Skill.objects.get_or_create(identity=skill_name)

                # Now, associate categories with the skill
                for category_name in categoryies_list:
                    category_name = category_name.strip()  # Remove leading/trailing spaces
                    category, _ = Category.objects.get_or_create(identity=category_name)
                    # Check if the category is already associated with the skill
                    if category not in skill.category.all():
                        skill.category.add(category)  # Associate the category with the skill

                    categoryies_objects.append(category)

                skills_objects.append(skill)
                
            try:
                obj, created = Course.objects.update_or_create(
                    identity=row['course_identity'],
                    code = row['code'],
                    defaults=course_data
                )
                obj.skills.set(skills_objects)
                obj.categories.set(categoryies_objects)

                course_module_data['course_id'] = obj.id
                course_module, created = CourseModule.objects.update_or_create(
                    identity=course_module_data['identity'],
                    course__code=row['code'],
                    defaults=course_module_data
                )
                course_submodule_data['module_id'] = course_module.id
                course_submodule, created = CourseSubModule.objects.update_or_create(
                    identity=course_submodule_data['identity'],
                    module__course__code=row['code'],
                    defaults=course_submodule_data
                )
            except Exception as e:
                # print('failed')
                # Handle the exception according to your requirements
                print(e)
                # breakpoint()
                # print(e)
            # if created:
            #     obj.save()
        return self.send_response()

class VideoLinkAPIView(AppAPIView):
     # Course Bulk Upload
    def post(self, request, *args, **kwargs):
        file_obj = request.FILES.get("file")
        if file_obj:
            paramFile = io.TextIOWrapper(file_obj.file)
            portfolio1 = csv.DictReader(paramFile)
            list_of_dict = list(portfolio1)
        else:
            list_of_dict = None
            return self.send_error_response()
        
        for row in list_of_dict:
            sub_module = CourseSubModule.objects.get(uuid=row['uuid'])

            if sub_module:
                sub_module.video_url = row['video_url']
                sub_module.save()
        
        return self.send_response()
        