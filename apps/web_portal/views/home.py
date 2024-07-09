from django.db.models import IntegerField, Value
from rest_framework import serializers
from apps.common.pagination import AppPagination, HomePageAppPagination, HomePageAppCoursePagination
from apps.learning.models.mml_course import MMLCourse
from apps.webinars.models import Webinar
from apps.common.serializers import FileModelToURLField, AppWriteOnlyModelSerializer, AppSerializer
from apps.common.serializers import get_app_read_only_serializer as read_serializer
from apps.common.views.api import AppAPIView
from apps.common.views.api.base import NonAuthenticatedAPIMixin
from apps.learning.models.blended_learning_path import BlendedLearningPath
from apps.my_learnings.models.trackers import StudentEnrolledCourseTracker, UserCertificatePathTracker, UserCourseTracker, UserLearningPathTracker
from apps.forums.models import Zone
from ...common.helpers import get_file_field_url, send_welcome_email
from ...common.serializers import simple_serialize_queryset
from ...learning.models import Category, CertificationPath, Course, LearningPath, Tag, LearningRoleImage, LearningRole, Skill
from .. import fakers
from ..models import Testimonial
from apps.payments.models import SubscriptionPlan
from ..serializers import CourseSerializer
from ...common.serializers import get_app_read_only_serializer, simple_serialize_queryset
from apps.learning.models import CourseImage
from apps.web_portal.serializers.explore import ExploreSerializer, LinkageFieldsSerializer, ExploreRecommendationSerializer
import requests
from config import settings
from apps.access.models import User, UserRole, InstitutionDetail, GuestUser
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content
from rest_framework.authtoken.views import ObtainAuthToken
from django.contrib.auth import get_user_model
from rest_framework.response import Response
from rest_framework.authtoken.models import Token as AuthToken
from apps.access.authentication import get_user_headers
from django.http import JsonResponse
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from rest_framework.generics import ListAPIView
from apps.common.serializers import AppReadOnlyModelSerializer
from django.db.models import Q
from apps.hackathons.models import hackathon as hackathon_models
from datetime import datetime
from apps.common.helpers import EmailNotification
from apps.ecash.reward_points import trigger_reward_points
from apps.purchase.models import SubscriptionPlanAddToCart
today = datetime.now().date()

class HomeSupportAPIView(NonAuthenticatedAPIMixin, AppAPIView):

    def post(self, request, *args, **kwargs):
        name = self.request.data["name"]
        email = self.request.data["email"]
        phone = self.request.data["phone"]
        message = self.request.data["message"]

        EmailNotification(
            email_to="support@techademy.com",
            template_code='support_to_admin',
            kwargs={
                "name": name, 
                "email": email,
                "phone": phone,
                "message": message
            }
        )
        return self.send_response()

class HomePageRecommendationAPIView(NonAuthenticatedAPIMixin, ListAPIView, AppAPIView):
    """Sends out data for the website Explore page."""

    pagination_class = HomePageAppPagination

    def get_validated_serialized_data(self):
        serializer = ExploreRecommendationSerializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        return data

    def get_model_for_serializer(self):
        data = self.get_validated_serialized_data()

        MODEL_CHOICES = {
            "courses": Course,
            "learning_paths": LearningPath,
            "certification_paths": CertificationPath,
            "blended_learning_paths": BlendedLearningPath,
            "mml_courses": MMLCourse,
            "hackathons": hackathon_models.Hackathon,
            "webinars": Webinar,
            "zones": Zone
        }

        model = MODEL_CHOICES[data["type"]]
        return model
    

    def get_queryset(self):

        model = self.get_model_for_serializer()
        user = self.get_user()
        if user == None:
            return model.objects.none()
        else:
            if model == hackathon_models.Hackathon or model == Webinar:
                return model.objects.filter(skills__in=user.onboarding_area_of_interests.values_list("id", flat=True), start_date__gte=today).distinct()
            elif model == Zone:
                return model.objects.filter(skills__in=user.onboarding_area_of_interests.values_list("id", flat=True)).distinct()
            return model.objects.filter(skills__in=user.onboarding_area_of_interests.values_list("id", flat=True)).exclude(is_private_course=True).distinct()

    def get_serializer_class(self):
        data_model = self.get_model_for_serializer()
        class _Serializer(get_app_read_only_serializer(data_model, "__all__")):
            def to_representation(self, instance):
                data = super().to_representation(instance=instance)

                if data_model.__name__ == 'Course':
                    enrolled_count = UserCourseTracker.objects.filter(entity_id=instance.id).count()
                    data["enrolled_count"] = enrolled_count
                elif data_model.__name__ == 'LearningPath':
                    enrolled_count = UserLearningPathTracker.objects.filter(entity_id=instance.id).count()
                    data["enrolled_count"] = enrolled_count
                elif data_model.__name__ == 'CertificationPath':
                    enrolled_count = UserCertificatePathTracker.objects.filter(entity_id=instance.id).count()
                    data["enrolled_count"] = enrolled_count

                image_url = "https://b2cstagingv2.blob.core.windows.net/appuploads/media/"
                if instance.image:
                    image = str(instance.image.file)
                    data["image"] = image_url+image
                return data

        return _Serializer

    def post(self, request, *args, **kwargs):
        return self.get(request, *args, **kwargs)

class HomePageAPIView(NonAuthenticatedAPIMixin, AppAPIView):
    """Sends out data for the website home/landing page."""

    MAX_INSTANCES_COUNT = 20

    class _FreeCourseSerializer(LinkageFieldsSerializer):
            """This serializer contains configuration for Course."""
            image = get_app_read_only_serializer(CourseImage, meta_fields="__all__")()
            categories = get_app_read_only_serializer(Category, meta_fields=["id","uuid","identity"])(many=True)
            class Meta:
                model = Course
                fields = ["uuid","identity","description","rating","duration","image","categories",
                        "current_price_inr","make_this_course_popular","make_this_course_trending",
                        "make_this_course_best_selling","editors_pick","is_certification_enabled","is_private_course"]

    def get(self, *args, **kwargs):
        """Handle on get method."""

        launch_a_new_career_qs = (
            LearningRole.objects.filter(
                skills__isnull=False,
            ).distinct()[: self.MAX_INSTANCES_COUNT]
            # .annotate(
            #     learners=Value(100000, output_field=IntegerField()),
            # )
            # .prefetch_related("tags")[: self.MAX_INSTANCES_COUNT]
        )

        trending_serializer = lambda model, extra_annotate={}: read_serializer(  # noqa
            meta_fields=[
                "uuid",
                "identity",
                "description",
                "rating",
                "duration",
                "learners",
                "image",
                "categories",
                # "actual_price_inr",
                "current_price_inr",
                "make_this_course_popular",
                "make_this_course_trending",
                "make_this_course_best_selling",
                "editors_pick",
                "is_certification_enabled",
                "is_private_course",
            ],
            meta_model=model,
            init_fields_config={"image": FileModelToURLField(),
                                 "category": read_serializer(
            meta_model=Category, meta_fields=['id','uuid','identity'],
            # queryset=model.objects.exclude(is_private_course=True)
        )(many=True, source="categories"),},
        )(
            model.objects.annotate(
                **{
                    "learners": Value(100000, output_field=IntegerField()),
                    **extra_annotate,
                }
            )[: self.MAX_INSTANCES_COUNT],
            many=True,
        ).data

        return self.send_response(
            data={
                "trending": {
                    "courses": trending_serializer(Course),
                    "learning_paths": trending_serializer(
                        LearningPath,
                        extra_annotate={},
                    ),
                    "advanced_learning_paths": trending_serializer(
                        CertificationPath,
                        extra_annotate={},
                    ),
                    "free": self._FreeCourseSerializer(Course.objects.filter(is_free=True,is_private_course=False),
                                                        many=True,
                                                        context={'request':self.get_request()}
                                                        ).data,
                },
                "launch_a_new_career": {
                    "filter": read_serializer(meta_model=Skill)(
                        Skill.objects.filter(
                            related_learning_role__in=launch_a_new_career_qs
                        ),
                        many=True,
                    ).data,
                    "data": read_serializer(
                        meta_model=LearningRole,
                        meta_fields=[
                            "id",
                            "uuid",
                            "identity",
                            "description",
                            # "tags",
                            "rating",
                            "duration",
                            # "learners",
                            # "categories",
                            "image",
                            # "actual_price_inr",
                            "current_price_inr",
                            "make_this_role_popular",
                            "make_this_role_trending",
                            "make_this_role_best_selling"
                        ],
                        init_fields_config={
                            # "tags": read_serializer(
                            #     meta_model=Tag, meta_fields=["uuid", "identity"]
                            # )(many=True),
                            "skills": read_serializer(
                                meta_model=Skill, meta_fields=["id", "uuid", "identity", "make_this_skill_popular"]
                            )(many=True),
                            # "rating": serializers.FloatField(),
                            "image": FileModelToURLField(),
                        },
                    )(launch_a_new_career_qs, many=True).data,
                },
                "courses_you_can_complete_in_a_day": [
                    {
                        "uuid": str(_.uuid),
                        "identity": _.identity,
                        "description": _.description,
                        "current_price_inr": _.current_price_inr,
                        "make_this_course_popular": _.make_this_course_popular,
                        "make_this_course_trending": _.make_this_course_trending,
                        "make_this_course_best_selling": _.make_this_course_best_selling,
                        "is_certification_enabled": _.is_certification_enabled,
                        "editors_pick":_.editors_pick,
                        "image": get_file_field_url(_, "image"),
                        # "category": read_serializer(meta_model=Category, meta_fields=['id','uuid','identity'])(many=True, source="categories")
                    }
                    for _ in Course.objects.filter(complete_in_a_day=True)[: self.MAX_INSTANCES_COUNT]
                ],
                "categories": [
                    {
                        "id": str(_.id),
                        "uuid": str(_.uuid),
                        "identity": _.identity,
                        "image": get_file_field_url(_, "image"),
                    }
                    for _ in Category.objects.all()[: self.MAX_INSTANCES_COUNT]
                ],
                # "categories": simple_serialize_queryset(
                #     queryset=Category.objects.all(),
                #     fields=["uuid", "identity", "image"],
                # ),
                "testimonials": read_serializer(
                    meta_model=Testimonial, meta_fields="__all__"
                )(Testimonial.objects.all()[:5], many=True).data,
                "subscription_plans": read_serializer(
                    meta_model=SubscriptionPlan, meta_fields="__all__"
                )(SubscriptionPlan.objects.filter(status="active"), many=True).data,
            }
        )


class HomePageCareerAPIView(NonAuthenticatedAPIMixin, AppAPIView, ListAPIView):

    class _Serializer(AppReadOnlyModelSerializer):
            image = get_app_read_only_serializer(LearningRoleImage, meta_fields=['id', 'uuid', 'file'])()
            skills = get_app_read_only_serializer(Skill, meta_fields=["id","uuid","identity"])(many=True)
            class Meta:
                model = LearningRole
                fields = ["id",
                            "uuid",
                            "identity",
                            "description",
                            # "tags",
                            "rating",
                            "duration",
                            # "learners",
                            # "categories",
                            "image",
                            "skills",
                            # "actual_price_inr",
                            # "current_price_inr"
                            "make_this_role_popular",
                            "make_this_role_trending",
                            "make_this_role_best_selling"]
                
    pagination_class = HomePageAppPagination
    serializer_class = _Serializer
 
    def get_queryset(self, *args, **kwargs):
        skills = self.request.GET.getlist('skills')
        if not skills:
            return LearningRole.objects.all()
        q_filter = Q(skills__identity__in=skills)
        return LearningRole.objects.filter(q_filter).distinct()

class HomePageCategoryAPIView(NonAuthenticatedAPIMixin, AppAPIView):
    MAX_INSTANCES_COUNT = 20
    def get(self, *args, **kwargs):
        launch_a_new_career_qs = (
            LearningRole.objects.filter(
                skills__isnull=False,
            ).distinct()[: self.MAX_INSTANCES_COUNT]
        )
        return self.send_response(
            data = {
                "categories": [
                    {
                        "id": str(_.id),
                        "uuid": str(_.uuid),
                        "identity": _.identity,
                        # "image": get_file_field_url(_, "image"),
                    }
                    for _ in Category.objects.all()
                ],
                "testimonials": read_serializer(
                    meta_model=Testimonial, meta_fields="__all__"
                )(Testimonial.objects.all()[:5], many=True).data,
                "subscription_plans": read_serializer(
                    meta_model=SubscriptionPlan, meta_fields="__all__"
                )(SubscriptionPlan.objects.filter(status="active"), many=True).data,
                "skills_meta": read_serializer(meta_model=Skill)(
                        Skill.objects.filter(
                            related_learning_role__in=launch_a_new_career_qs
                        ).distinct(),
                        many=True,
                    ).data,
            }
        )

class HomePageCoursesAPIView(NonAuthenticatedAPIMixin, AppAPIView, ListAPIView):
    class _Serializer(LinkageFieldsSerializer):
            image = get_app_read_only_serializer(CourseImage, meta_fields="__all__")()
            categories = get_app_read_only_serializer(Category, meta_fields=["id","uuid","identity"])(many=True)
            class Meta:
                model = Course
                fields = ["uuid","identity","description","rating","duration","image","categories",
                        "current_price_inr","make_this_course_popular","make_this_course_trending",
                        "make_this_course_best_selling","editors_pick","is_certification_enabled","is_private_course"]
    
    pagination_class = HomePageAppCoursePagination
    serializer_class = _Serializer
 
    def get_queryset(self, *args, **kwargs):
        return Course.objects.filter(complete_in_a_day=True).exclude(is_private_course=True)


class HomePageTrendingAPIView(NonAuthenticatedAPIMixin, ListAPIView, AppAPIView):
    """Sends out data for the website Explore page."""

    pagination_class = HomePageAppPagination

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
            "blended_learning_paths": BlendedLearningPath,
            "mml_courses": MMLCourse,
        }

        model = MODEL_CHOICES[data["type"]]
        return model
    

    def get_queryset(self):

        model = self.get_model_for_serializer()
        
        qs = model.objects.exclude(is_private_course=True)

        return qs

    def get_serializer_class(self):
        data_model = self.get_model_for_serializer()
        class _Serializer(get_app_read_only_serializer(data_model, "__all__")):
            def to_representation(self, instance):
                data = super().to_representation(instance=instance)

                if data_model.__name__ == 'Course':
                    enrolled_count = UserCourseTracker.objects.filter(entity_id=instance.id).count()
                    data["enrolled_count"] = enrolled_count
                elif data_model.__name__ == 'LearningPath':
                    enrolled_count = UserLearningPathTracker.objects.filter(entity_id=instance.id).count()
                    data["enrolled_count"] = enrolled_count
                else:
                    enrolled_count = UserCertificatePathTracker.objects.filter(entity_id=instance.id).count()
                    data["enrolled_count"] = enrolled_count

                image_url = "https://b2cstagingv2.blob.core.windows.net/appuploads/media/"
                if instance.image:
                    image = str(instance.image.file)
                    data["image"] = image_url+image
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
    
class SignUpAPIView(NonAuthenticatedAPIMixin,AppAPIView):

    class _Serializer(AppWriteOnlyModelSerializer):
        class Meta(AppWriteOnlyModelSerializer.Meta):
            fields = ["first_name", "last_name"]
            model = User

    serializer_class = _Serializer

    def post(self, request, *args, **kwargs):

        """Use IDP to handle the same."""
        serializer = self.get_valid_serializer()
        headers = get_admin_headers()
        email = self.request.data["email"]
        password = self.request.data["password"]
        first_name = self.request.data["first_name"]
        last_name = self.request.data["last_name"]
        name = f"{first_name} {last_name}"
        # name = self.request.data["full_name"]
        phone_number = self.request.data["phone_number"]
        payload = {
            "userId": 0,
            "tenantId": settings.IDP_TENANT_ID,
            "tenantDisplayName": name,
            "tenantName": settings.IDP_TENANT_NAME,
            "role": "TenantUser",
            "email": email,
            "name": first_name,
            "surname": last_name,
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
            role = UserRole.objects.get(identity__icontains="Learner")
            serializer.save(idp_user_id=data.get('userId'), password=data.get('password'), idp_email=data.get('email'), user_name=data.get('email'), first_name=data.get('name'), last_name=data.get('surname'), full_name=data.get('tenantDisplayName'), phone_number=phone_number, user_role=role)
            # return self.send_response()
            get_user = User.objects.get(idp_email=self.request.data["email"])
            trigger_reward_points(get_user, action="New User")

        else:
            return self.send_error_response(data={'detail': "User Already exists"})

        # if user_id is None:
        #     serializer.save(idp_user_id=data.get('userId'), password=data.get('password'), idp_email=data.get('email'), user_name=data.get('email'), first_name=data.get('name'), last_name=data.get('surname'), full_name=name, phone_number=phone_number)
        #     return self.send_response()
        # else:
        #     return self.send_error_response(data={'detail': "User Already exists"})
        
        # message = Mail(
        #     from_email='vashanth@geopits.com',
        #     to_emails= email,
        #     subject='Welcome',
        #     html_content=f'Welcome, you have successfully signed up <br> Your signed up details are: <br> Full Name: {name} <br> Email Id: {email} <br> Phone Number: {phone_number} <br> Password: {password}'
        # )
        # try:
        #     sg = SendGridAPIClient(api_key=settings.ANYMAIL["SENDGRID_API_KEY"])
        #     response = sg.send(message)
        #     if response.status_code == 202:
        #         return self.send_response(data={'detail': 'Email sent.'})
        #     else:
        #         return self.send_error_response(data={'detail': 'Failed to send email.'})

        # except Exception as e:
        #     return self.send_error_response(data={'detail': f'An error occurred: {str(e)}'})
        
        html_content=f'Welcome, you have successfully signed up <br> Your signed up details are: <br> Full Name: {name} <br> Email Id: {email} <br> Phone Number: {phone_number} <br> Password: {password}'
        success, message = send_welcome_email(email, 'Welcome', html_content)

        if success:
            return self.send_response(data={'detail': message})
        else:
            return self.send_error_response(data={'detail': message})

class GuestUserSignUpAPIView(NonAuthenticatedAPIMixin,AppAPIView):

    class _Serializer(AppWriteOnlyModelSerializer):
        class Meta(AppWriteOnlyModelSerializer.Meta):
            fields = ["first_name", "last_name"]
            model = User

    serializer_class = _Serializer

    def post(self, request, *args, **kwargs):

        """Use IDP to handle the same."""
        serializer = self.get_valid_serializer()
        headers = get_admin_headers()
        email = self.request.data["email"]
        first_name = self.request.data["first_name"]
        last_name = self.request.data["last_name"]
        guest_id = self.request.data["guest_id"]
        name = f"{first_name} {last_name}"
        payload = {
            "userId": 0,
            "tenantId": settings.IDP_TENANT_ID,
            "tenantDisplayName": name,
            "tenantName": settings.IDP_TENANT_NAME,
            "role": "TenantUser",
            "email": email,
            "name": first_name,
            "surname": last_name,
            "configJson": "string",
            "password": email,
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
            role = UserRole.objects.get(identity__icontains="Learner")
            serializer.save(idp_user_id=data.get('userId'), password=data.get('password'), idp_email=data.get('email'), user_name=data.get('email'), first_name=data.get('name'), last_name=data.get('surname'), full_name=data.get('tenantDisplayName'), user_role=role)
            # return self.send_response()
            get_user = User.objects.get(idp_email=self.request.data["email"])
            trigger_reward_points(get_user, action="New User")

        else:
            return self.send_error_response(data={'detail': "User Already exists"})
        
        html_content=f'Welcome, you have successfully signed up <br> Your signed up details are: <br> Full Name: {name} <br> Email Id: {email} <br> Password: {email}<br>.Please find the <a href=f"{settings.FRONTEND_WEB_URL}" target="/blank">link</a> to reset your password if required.'
        success, message = send_welcome_email(email, 'Welcome', html_content)

        if success:
            try:
                user = User.objects.get(user_name=email)
                if user.socail_oauth:
                    return Response({'error': 'Try login with social link'}, status=401)
                if user.user_role.identity == 'Student':
                    ir_details = InstitutionDetail.objects.filter(representative=user.created_by).first()
                    if ir_details is None:
                        return Response({'error': "You don't have permission to access"}, status=401)
                payload = {
                    "userNameOrEmailAddress": email,
                    "password": email,
                    "rememberClient": True,
                    "tenancyName": settings.IDP_TENANT_NAME,
                }
                idp_response = requests.post(settings.IDP_CONFIG['host'] + settings.IDP_CONFIG['authenticate_url'], json=payload)
                data = idp_response.json()
                if user.onboarding_area_of_interests.exists():
                    onboarding=True
                else:
                    onboarding=False
            except Exception as e:
                return Response({'error': 'Invalid email or password'}, status=401)
            if data.get("errorMessage") == None:
                token ,created= AuthToken.objects.get_or_create(user=user)
                response_data = {
                    'full_name': user.full_name,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'uuid': user.uuid,
                    'role': user.user_role.identity,
                    'email': user.idp_email,
                    'token': token.key,
                    'idp_token': data.get("accessToken"),
                    'encryptedAccessToken': data.get("encryptedAccessToken"),
                    'expireInSeconds': data.get("expireInSeconds"),
                    'userId': data.get("userId"),
                    'onboarding': onboarding
                }
                if guest_id is not None:
                    subscription = SubscriptionPlanAddToCart.objects.filter(guest_id=guest_id)
                    for sub in subscription:
                        SubscriptionPlanAddToCart.objects.get_or_create(
                            entity = sub.entity, created_by=user
                        )
                        sub.delete()
                    GuestUser.objects.filter(id=guest_id).delete()
                else:
                    pass
            return self.send_response(data={'detail': message, 'login_data': response_data})
        else:
            return self.send_error_response(data={'detail': message})

class GenerateGuestUserIDAPIView(NonAuthenticatedAPIMixin,AppAPIView):
    class _Serializer(AppWriteOnlyModelSerializer):
        class Meta(AppWriteOnlyModelSerializer.Meta):
            fields = "__all__"
            model = GuestUser

    serializer_class = _Serializer

    def get(self, request, *args, **kwargs):
        serializer = self.get_valid_serializer()
        if serializer.is_valid():
            instance = serializer.save()
            # Return a successful response with the relevant data
            return self.send_response(data={'id': instance.id,'uuid': instance.uuid})
        else:
            # Handle the case where the serializer is not valid
            return self.send_response(errors=serializer.errors, status=400)


class SignInAPIView(ObtainAuthToken):

   def post(self, request):
        username = self.request.data['username']
        password = self.request.data['password']
        guest_id = self.request.data['guest_id'] #primary key
        User = get_user_model()
        
        try:
            user = User.objects.get(user_name=username)
            if user.socail_oauth:
                return Response({'error': 'Try login with social link'}, status=401)
            if user.user_role.identity == 'Student':
                ir_details = InstitutionDetail.objects.filter(representative=user.created_by).first()
                if ir_details is None:
                    return Response({'error': "You don't have permission to access"}, status=401)
            payload = {
                "userNameOrEmailAddress": username,
                "password": password,
                "rememberClient": True,
                "tenancyName": settings.IDP_TENANT_NAME,
            }
            idp_response = requests.post(settings.IDP_CONFIG['host'] + settings.IDP_CONFIG['authenticate_url'], json=payload)
            data = idp_response.json()
            if user.onboarding_area_of_interests.exists():
                onboarding=True
            else:
                onboarding=False
        except Exception as e:
            return Response({'error': 'Invalid email or password'}, status=401)
        if data.get("errorMessage") == None:
            token ,created= AuthToken.objects.get_or_create(user=user)
            response_data = {
                'id': user.id,
                'full_name': user.full_name,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'uuid': user.uuid,
                'role': user.user_role.identity,
                'email': user.idp_email,
                'token': token.key,
                'idp_token': data.get("accessToken"),
                'encryptedAccessToken': data.get("encryptedAccessToken"),
                'expireInSeconds': data.get("expireInSeconds"),
                'userId': data.get("userId"),
                'onboarding': onboarding
            }
            if guest_id is not None:
                subscription = SubscriptionPlanAddToCart.objects.filter(guest_id=guest_id)
                for sub in subscription:
                    SubscriptionPlanAddToCart.objects.get_or_create(
                        entity = sub.entity, created_by=user
                    )
                    sub.delete()
                GuestUser.objects.filter(id=guest_id).delete()
            else:
                pass
            return Response(response_data)
        else:
            return Response({'error': data.get("errorMessage")}, status=401)

        
class LogoutAPIView(AppAPIView):
    def post(self, *args, **kwargs):
        user = self.get_user()
        headers = get_user_headers(user)
        idp_response = requests.post(settings.IDP_CONFIG['host'] + settings.IDP_CONFIG['logout_url'], headers=headers)
        if idp_response.json() == True:
            response_data = {
                'status' : "Success"
            }
            return JsonResponse(response_data)
        else:
            response_data = {
                'status': "Error"
            }
            return JsonResponse(response_data)
        
class ChangePasswordAPIView(AppAPIView):
    def post(self, request, *args, **kwargs):
        current_password = self.request.data['current_password']
        new_password = self.request.data['new_password']
        user = get_user_model()
        headers = get_user_headers(user)
        payload = {
            "currentPassword": current_password,
            "newPassword": new_password
        }
        idp_response = requests.post(settings.IDP_CONFIG['host'] + settings.IDP_CONFIG['change_password_url'], json=payload, headers=headers)
        data = idp_response.json()
        return data
    
class ForgotPasswordAPIView(NonAuthenticatedAPIMixin, AppAPIView):
    """View to send out a forgot password email with token."""

    class _Serializer(AppSerializer):
        email = serializers.EmailField()

    serializer_class = _Serializer

    def get_validated_serialized_data(self):
        serializer= self.serializer_class(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        return data
    
    def get_email_for_serializer(self):
        data = self.get_validated_serialized_data()
        email = data["email"]
        return email
    
    def post(self, request, *args, **kwargs):
        email = self.get_email_for_serializer()
        try:
            user = User.objects.get(idp_email=email,user_name=email)
        except User.DoesNotExist:
            return Response({'error': 'User with this email does not exist.'}, status=401)
        if user.socail_oauth:
            return Response({'error': 'Try login using Social Links'}, status=401)
        token = default_token_generator.make_token(user)
        uidb64 = urlsafe_base64_encode(force_bytes(user.id))
        if user.user_role.identity == 'IR':
            reset_link = f"{settings.FRONTEND_CMS_URL}institute/forgot-password/{uidb64}/{token}/"
        if user.user_role.identity == 'Employer':
            reset_link = f"{settings.FRONTEND_CMS_URL}employer/forgot-password/{uidb64}/{token}/"
        if user.user_role.identity == 'Interview Panel Member':
            reset_link = f"{settings.FRONTEND_CMS_URL}interview-panel/forgot-password/{uidb64}/{token}/"
        if user.user_role.identity == 'Learner':
            reset_link = f"{settings.FRONTEND_WEB_URL}reset-password/{uidb64}/{token}/"
        if user.user_role.identity == 'Student':
            reset_link = f"{settings.FRONTEND_WEB_URL}institute/student/reset-password/{uidb64}/{token}/"
        # return Response({'detail': 'Password reset email sent.', 'reset link': {reset_link}})
        
        message = Mail(
            from_email='welcome@techademy.com',
            to_emails= email,
            subject='Password Reset',
            html_content=f'Click <a href="{reset_link}">here</a> to reset your password.'
        )
        try:
            sg = SendGridAPIClient(api_key=settings.ANYMAIL["SENDGRID_API_KEY"])
            response = sg.send(message)
            if response.status_code == 202:
                return self.send_response({'detail': 'Password reset email sent.', 'reset_link': reset_link})
            else:
                return self.send_error_response(data={'detail': 'Failed to send email.'})

        except Exception as e:
            return self.send_error_response(data={'detail': f'An error occurred: {str(e)}'})
               
        
class ForgotResetPasswordAPIView(NonAuthenticatedAPIMixin, AppAPIView):
    """View to verify the token sent to user's email is valid and resets password."""

    def post(self, request, user_id, token):
        """Reset password for the user."""

        user_id = force_str(urlsafe_base64_decode(user_id))
        user = User.objects.get(id=user_id)
        headers = get_user_headers(user)

        if user is not None and default_token_generator.check_token(user, token):
            password = self.request.data['password']
            payload = {
                "userName": user.user_name,
                "tenantName": settings.IDP_TENANT_NAME,
                "newPassword": password
            }
            idp_response = requests.post(settings.IDP_CONFIG['host'] + settings.IDP_CONFIG['external_reset_password_url'], json=payload, headers=headers)
            if idp_response.json() == True:
                return self.send_response()
            else:
                return self.send_error_response(
                    data={"idp error": "please contact develooper."}
                )

        return self.send_error_response(
            data={"link": "The reset password link is invalid."}
        )
# TODO: ACTUAL DATA WHERE EVER NEEDED