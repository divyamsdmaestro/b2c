from django.db import models
from apps.learning.models.blended_learning_path import BlendedLearningClassroomAndVirtualDetails, BlendedLearningPathCourseModesAndFee, BlendedLearningPathCustomerEnquiry
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework import serializers
from apps.common.views.api import AppAPIView
from apps.common.views.api.base import NonAuthenticatedAPIMixin
from apps.common.views.api.generic import (
    DEFAULT_IDENTITY_DISPLAY_FIELDS,
    AbstractLookUpFieldMixin,
)
from apps.learning.models.mml_course import MMLCourse
from apps.common.views.api.generic import AppModelListAPIViewSet
from apps.purchase.models.cart import MMLCourseAddToCart
from apps.purchase.models.wishlist import MMLCourseWishlist
from apps.web_portal.models.notification import Notification
from apps.web_portal.serializers.explore import MMLCourseSerializer
from ...common.pagination import AppPagination, HomePageAppPagination
from ...common.serializers import AppReadOnlyModelSerializer, get_app_read_only_serializer, get_read_serializer
from ...learning.models import Category, CertificationPath, Course, LearningPath, Skill, BlendedLearningPath, LearningPathCourse, BlendedLearningPathPriceDetails, BlendedLearningPathScheduleDetails
from ...purchase.models import (
    CertificationPathAddToCart,
    CertificationPathWishlist,
    LearningPathAddToCart,
    LearningPathWishlist,
    BlendedLearningPathWishlist,
    BlendedLearningPathAddToCart,
)
from ..serializers import (
    CertificationPathSerializer,
    CourseSerializer,
    ExploreSearchSerializer,
    ExploreSerializer,
    LeaningPathSerializer,
    SkillListSerializer,
    SkillDetailSerializer,
    CourseUUIDListSerializer,
    CourseBulkDetailSerializer,
    BlendedLearningPathSerializer,
    LeaningPathCourseListSerializer,
    LeaningPathCoursePreviewSerializer,
    SkillCourseDetailsSerializer,
    SkillLeaningPathDetailsSerializer,
    SkillCertificationPathDetailsSerializer,
    SkillWebinarDetailSerializer,
    SkillZoneDetailsSerializer,
    SkillHackathonDetailsSerializer,
    BlendedLearningPathPriceDetailsSerializer,
    BlendedLearningPathScheduleDetailsSerializer
)
from ...payments.models import Payment, SaleDiscount
from apps.learning.models import CourseImage, LearningPathImage, CertificationPathImage, BlendedLearningPathImage
from ...purchase.models import CourseWishlist, LearningPathWishlist, CertificationPathWishlist, CourseAddToCart, LearningPathAddToCart, CertificationPathAddToCart
from apps.my_learnings.models import UserCourseTracker, StudentEnrolledCourseTracker, UserLearningPathTracker, UserCertificatePathTracker, UserBlendedLearningPathTracker
from django.contrib.auth.models import AnonymousUser
from apps.access.models import User, InstitutionDetail, InstitutionUserGroupDetail, InstitutionUserGroupContent
from datetime import datetime
from django.db.models import Q
from apps.my_learnings.models import (
    UserCourseTracker,
    UserLearningPathTracker,
    UserMMLCourseTracker,
    UserCertificatePathTracker,
    StudentEnrolledMMLCourseTracker,
    StudentEnrolledCertificatePathTracker,
    StudentEnrolledLearningPathTracker,
    StudentEnrolledCourseTracker,
    UserSubscriptionPlanCertificatePathTracker,
    UserSubscriptionPlanLearningPathTracker,
    UserSubscriptionPlanCourseTracker,
)
from datetime import date
from apps.access.models import InstitutionDetail


class StudentDashboardAPIView(AppAPIView):
    """Sends out data for the website home/landing page."""

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

    class _StudentEnrolledCourseSerializer(AppReadOnlyModelSerializer):      
        identity = serializers.SerializerMethodField()
        class Meta(AppReadOnlyModelSerializer.Meta):
            fields = ["id","uuid","identity"]
            model = StudentEnrolledCourseTracker

        def get_identity(self,obj):
            return obj.entity.identity

    def get(self, *args, **kwargs):
        """Handle on get method."""

        today = date.today()
        user = self.get_user()

        course_trackers = StudentEnrolledCourseTracker.objects.filter(created_by=user, progress=100)
        learning_path_trackers = StudentEnrolledLearningPathTracker.objects.filter(created_by=user, progress=100)
        certificate_path_trackers = StudentEnrolledCertificatePathTracker.objects.filter(created_by=user, progress=100)
        # Total number of certifications for the student
        certificates_count = course_trackers.count() + learning_path_trackers.count() + certificate_path_trackers.count()

        distinct_skill_ids = []
        # Process StudentEnrolledCourseTracker instances
        for tracker in course_trackers:
            distinct_skill_ids.extend(tracker.entity.skills.values_list('id', flat=True))

        for tracker in learning_path_trackers:
            distinct_skill_ids.extend(tracker.entity.skills.values_list('id', flat=True))

        for tracker in certificate_path_trackers:
            distinct_skill_ids.extend(tracker.entity.skills.values_list('id', flat=True))
        # Get the overall distinct skills count
        skills_count = len(set(distinct_skill_ids))

        trending_learning = {
            "courses": sorted(
                self._CourseSerializer(Course.objects.all(), many=True).data,
                key=lambda x: x["enrolled_count"],
                reverse=True
            ),
            "learning_paths": sorted(
                self._LearningPathSerializer(LearningPath.objects.all(), many=True).data,
                key=lambda x: x["enrolled_count"],
                reverse=True
            ),
            "certification_paths": sorted(
                self._CertificationPathSerializer(CertificationPath.objects.all(), many=True).data,
                key=lambda x: x["enrolled_count"],
                reverse=True
            ),
        }
        ongoing_course = StudentEnrolledCourseTracker.objects.filter(created_by=user).exclude(progress=0)
        ongoing_courses = {
            "count":ongoing_course.count(),
            "courses":self._StudentEnrolledCourseSerializer(ongoing_course, many=True).data
        }
        upcoming_course = StudentEnrolledCourseTracker.objects.filter(created_by=user,progress=0)
        upcoming_courses = {
            "count":upcoming_course.count(),
            "courses":self._StudentEnrolledCourseSerializer(upcoming_course, many=True).data
        }

        return self.send_response(
            data={
                "ongoing_courses":ongoing_courses,
                "upcoming_courses":upcoming_courses,
                "certifications":certificates_count,
                "skills_achieved":skills_count,
                "trending_learning":trending_learning
            }
        )

class ExploreMetaAPIView(NonAuthenticatedAPIMixin, AppAPIView):
    """Provides Meta Data for filtering"""

    class _CategorySerializer(AppReadOnlyModelSerializer):
        count = serializers.SerializerMethodField()
        class Meta(AppReadOnlyModelSerializer.Meta):
            fields = ["id", "uuid", "identity", "count"]
            model = Category

        def __init__(self, *args, **kwargs):
            type = kwargs.pop('type', None)
            self.type = type
            super().__init__(*args, **kwargs)

        def get_count(self, obj):
            auth_user = self.get_user()
            if auth_user and auth_user.user_role and auth_user.user_role.identity=="Student":
                if self.type == "courses":
                    institution = InstitutionDetail.objects.filter(representative=auth_user.created_by).first()
                    if institution:
                        user_group = InstitutionUserGroupDetail.objects.filter(institution=institution, user__id__icontains=auth_user.id)
                        if user_group:
                            user_group_content = InstitutionUserGroupContent.objects.filter(user_group__in=user_group)
                            course_ids = []
                            if user_group_content:
                                for content in user_group_content:
                                    course_ids.extend(list(content.courses.values_list('id', flat=True)))
                                course_list = Course.objects.filter(id__in=course_ids)
                                return Course.objects.filter(categories=obj, id__in=course_list).count()
                elif self.type == "learning_paths":
                    institution = InstitutionDetail.objects.filter(representative=auth_user.created_by).first()
                    if institution:
                        user_group = InstitutionUserGroupDetail.objects.filter(institution=institution, user__id__icontains=auth_user.id)
                        if user_group:
                            user_group_content = InstitutionUserGroupContent.objects.filter(user_group__in=user_group)
                            course_ids = []
                            if user_group_content:
                                for content in user_group_content:
                                    course_ids.extend(list(content.learning_path.values_list('id', flat=True)))
                                course_list = LearningPath.objects.filter(id__in=course_ids)
                                return LearningPath.objects.filter(categories=obj, id__in=course_list).count()
                elif self.type == "certification_paths":
                    institution = InstitutionDetail.objects.filter(representative=auth_user.created_by).first()
                    if institution:
                        user_group = InstitutionUserGroupDetail.objects.filter(institution=institution, user__id__icontains=auth_user.id)
                        if user_group:
                            user_group_content = InstitutionUserGroupContent.objects.filter(user_group__in=user_group)
                            course_ids = []
                            if user_group_content:
                                for content in user_group_content:
                                    course_ids.extend(list(content.certification_path.values_list('id', flat=True)))
                                course_list = CertificationPath.objects.filter(id__in=course_ids)
                                return CertificationPath.objects.filter(categories=obj, id__in=course_list).count()
                return 0
            else:
                if self.type == "courses":
                    return Course.objects.filter(categories=obj,is_private_course=False).count()
                elif self.type == "learning_paths":
                    return LearningPath.objects.filter(categories=obj,is_private_course=False).count()
                elif self.type == "certification_paths":
                    return CertificationPath.objects.filter(categories=obj,is_private_course=False).count()
                return 0
            
    class _SkillSerializer(AppReadOnlyModelSerializer):
        count = serializers.SerializerMethodField()
        class Meta(AppReadOnlyModelSerializer.Meta):
            fields = ["id", "uuid", "identity", "count"]
            model = Skill

        def __init__(self, *args, **kwargs):
            type = kwargs.pop('type', None)
            self.type = type
            super().__init__(*args, **kwargs)

        def get_count(self, obj):
            auth_user = self.get_user()
            if auth_user and auth_user.user_role and auth_user.user_role.identity=="Student":
                if self.type == "courses":
                    institution = InstitutionDetail.objects.filter(representative=auth_user.created_by).first()
                    if institution:
                        user_group = InstitutionUserGroupDetail.objects.filter(institution=institution, user__id__icontains=auth_user.id)
                        if user_group:
                            user_group_content = InstitutionUserGroupContent.objects.filter(user_group__in=user_group)
                            course_ids = []
                            if user_group_content:
                                for content in user_group_content:
                                    course_ids.extend(list(content.courses.values_list('id', flat=True)))
                                course_list = Course.objects.filter(id__in=course_ids)
                                return Course.objects.filter(skills=obj, id__in=course_list).count()
                elif self.type == "learning_paths":
                    institution = InstitutionDetail.objects.filter(representative=auth_user.created_by).first()
                    if institution:
                        user_group = InstitutionUserGroupDetail.objects.filter(institution=institution, user__id__icontains=auth_user.id)
                        if user_group:
                            user_group_content = InstitutionUserGroupContent.objects.filter(user_group__in=user_group)
                            course_ids = []
                            if user_group_content:
                                for content in user_group_content:
                                    course_ids.extend(list(content.learning_path.values_list('id', flat=True)))
                                course_list = LearningPath.objects.filter(id__in=course_ids)
                                return LearningPath.objects.filter(skills=obj, id__in=course_list).count()
                elif self.type == "certification_paths":
                    institution = InstitutionDetail.objects.filter(representative=auth_user.created_by).first()
                    if institution:
                        user_group = InstitutionUserGroupDetail.objects.filter(institution=institution, user__id__icontains=auth_user.id)
                        if user_group:
                            user_group_content = InstitutionUserGroupContent.objects.filter(user_group__in=user_group)
                            course_ids = []
                            if user_group_content:
                                for content in user_group_content:
                                    course_ids.extend(list(content.certification_path.values_list('id', flat=True)))
                                course_list = CertificationPath.objects.filter(id__in=course_ids)
                                return CertificationPath.objects.filter(skills=obj, id__in=course_list).count()
                return 0
            else:
                if self.type == "courses":
                    return Course.objects.filter(skills=obj,is_private_course=False).count()
                elif self.type == "learning_paths":
                    return LearningPath.objects.filter(skills=obj,is_private_course=False).count()
                elif self.type == "certification_paths":
                    return CertificationPath.objects.filter(skills=obj,is_private_course=False).count()
                return 0
            
    def get(self, request):
        type_param = self.request.query_params.get('type', None)        
        data = {
            "categories": self._CategorySerializer(
                Category.objects.all(), many=True, type=type_param, context={'request':self.get_request()}
            ).data,
            "skills": self._SkillSerializer(
                Skill.objects.all(), many=True, type=type_param, context={'request':self.get_request()}
            ).data,
            # "skills": get_read_serializer(
            #     Skill, DEFAULT_IDENTITY_DISPLAY_FIELDS
            # )(Skill.objects.filter(is_archived=False), many=True).data,
        }

        return self.send_response(data=data)

class StudentHomeAPIView(NonAuthenticatedAPIMixin, AppAPIView):
    """Provides Meta Data for filtering"""

    def get(self, request):
        auth_user = self.get_authenticated_user()
        course_count = 0
        enrolled_courses_count = 0
        completed_courses_count = 0
        if auth_user:
            if auth_user.user_role:
                if auth_user.user_role.identity=="Student":
                    institution = InstitutionDetail.objects.filter(representative=auth_user.created_by).first()
                    if institution:
                        user_group = InstitutionUserGroupDetail.objects.filter(institution=institution, user__id__icontains=auth_user.id)
                        if user_group:
                            user_group_content = InstitutionUserGroupContent.objects.filter(user_group__in=user_group)
                            course_ids = []
                            if user_group_content:
                                for content in user_group_content:
                                    course_ids.extend(list(content.courses.values_list('id', flat=True)))
                                course_count = Course.objects.filter(id__in=course_ids).count()
                                enrolled_courses_count = StudentEnrolledCourseTracker.objects.filter(entity_id__in=course_ids, created_by=auth_user).count()
                                completed_courses_count = StudentEnrolledCourseTracker.objects.filter(entity_id__in=course_ids, progress=100, created_by=auth_user).count()

        data = {
            "course_count": course_count,
            "enrolled_courses_count": enrolled_courses_count,
            "completed_courses_count": completed_courses_count
        }

        return self.send_response(data=data)

class ExploreNavigationAPIView(NonAuthenticatedAPIMixin, AppAPIView):
    """Provides Navigation Related API on the menu bar"""

    def get(self, request):
        limit = 20
        categories_qs = Category.objects.all()[:limit]
        categories = []
        MODELS_TO_FILTER = {
            "courses": Course,
            "learning_paths": LearningPath,
            # "certification_paths": CertificationPath,
        }
        category_serializer = get_read_serializer(Category)
        OTHER_SERIALIZERS = {}
        for k, v in MODELS_TO_FILTER.items():
            OTHER_SERIALIZERS[k] = get_read_serializer(v)
        for category in categories_qs:
            category_dict = category_serializer(category).data
            for k, v in OTHER_SERIALIZERS.items():
                category_dict[k] = v(
                    MODELS_TO_FILTER[k].objects.filter(categories=category, is_private_course=False)[:7],
                    many=True,
                ).data
            categories.append(category_dict)

        auth_user = self.get_authenticated_user()
        cart_count = 0
        notification_count = 0
        profile_image = None
        if auth_user:
            from apps.purchase.helpers import get_cart_data_with_pricing_information

            cart_count = len(
                get_cart_data_with_pricing_information(user=auth_user)["entities"]
            )

            notification_count = Notification.objects.filter(user=auth_user, is_read=False).count()

            auth_user = True
            image_url = "https://b2cstagingv2.blob.core.windows.net/appuploads/media/"
            if self.get_user().profile_image is not None:
                profile_image = image_url + str(self.get_user().profile_image.file)
            else:
                profile_image = None
           
        return self.send_response(
            data={"categories": categories, "cart_count": cart_count, "notification_count": notification_count, "is_authenticate": auth_user, "profile_image": profile_image}
        )

class ExplorePageCourseCompleteInaDayAPIView(NonAuthenticatedAPIMixin, ListAPIView, AppAPIView):
    """Sends out data for the website Explore page."""

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
        }

        model = MODEL_CHOICES[data["type"]]
        return model
    
    def get_filter_for_serializer(self):
        data = self.get_validated_serialized_data()

        advance_filter = data["advance_filter"]
        return advance_filter

    def get_queryset(self):
        from apps.purchase.models import CourseAddToCart, CourseWishlist

        model = self.get_model_for_serializer()
        advance_filter = self.get_filter_for_serializer()
        
        qs = model.objects.filter(complete_in_a_day=True)
        auth_user = self.get_authenticated_user()
        if auth_user:
            if auth_user.user_role and auth_user.user_role.identity == "Student":
                institution = InstitutionDetail.objects.filter(representative=auth_user.created_by).first()
                if institution:
                    user_group = InstitutionUserGroupDetail.objects.filter(institution=institution, user__id__icontains=auth_user.id)
                    if user_group:
                        user_group_content = InstitutionUserGroupContent.objects.filter(user_group__in=user_group)
                        course_ids = []
                        if user_group_content:
                            if model.__name__ == "Course":
                                for content in user_group_content:
                                    course_ids.extend(list(content.courses.values_list('id', flat=True)))
                                qs = Course.objects.filter(id__in=course_ids, complete_in_a_day=True)
                            else:
                                qs=model.objects.none()
                        else:
                            qs=model.objects.none()
                    else:
                        qs=model.objects.none()
                else:
                    qs=model.objects.none()


        if model.__name__ == "Course":
            if advance_filter == "trending_courses":
                qs = model.objects.filter(make_this_course_trending=True).exclude(is_private_course=True)
            elif advance_filter == "recently_published":
                qs = model.objects.all().order_by("-created").exclude(is_private_course=True)
            elif advance_filter == "highly_popular":
                qs = model.objects.filter(make_this_course_popular=True).exclude(is_private_course=True)
            elif advance_filter == "best_selling":
                qs = model.objects.filter(make_this_course_best_selling=True).exclude(is_private_course=True)
            elif advance_filter == "free":
                qs = model.objects.filter(is_free=True).exclude(is_private_course=True)
            elif advance_filter == "virtual_labs":
                qs = model.objects.filter(virtual_lab=True).exclude(is_private_course=True)


        if auth_user:
            if model.__name__ == "Course":
                wishlist_model = CourseWishlist
                add_to_cart_model = CourseAddToCart

            # TODO: Refactor later
            # TODO: Also check `get_cart_data_with_pricing_information`
            if auth_user.user_role:
                if auth_user.user_role.identity == "Student":
                    pass
                else: 
                    qs = qs.annotate(
                        is_in_wishlist=models.Exists(
                            wishlist_model.objects.filter(
                                entity_id=models.OuterRef("id"),created_by=auth_user
                            )
                        ),
                        is_in_cart=models.Exists(
                            add_to_cart_model.objects.filter(
                                entity_id=models.OuterRef("id"),created_by=auth_user
                            )
                        )
                    )
            else:
                qs = qs.annotate(
                    is_in_wishlist=models.Exists(
                        wishlist_model.objects.filter(
                            entity_id=models.OuterRef("id"),created_by=auth_user
                        )
                    ),
                    is_in_cart=models.Exists(
                        add_to_cart_model.objects.filter(
                            entity_id=models.OuterRef("id"),created_by=auth_user
                        )
                    )
                )

        return qs

    def get_serializer_class(self):
        data_model = self.get_model_for_serializer()
        user = self.get_user()
        # print(data_model)
        class _Serializer(get_read_serializer(data_model, "__all__")):
            def to_representation(self, instance):
                data = super().to_representation(instance=instance)
                data["is_in_cart"] = getattr(instance, "is_in_cart", False)
                data["is_in_wishlist"] = getattr(instance, "is_in_wishlist", False)

                # sale discount calcluations
                from datetime import datetime
                today = datetime.now().date()

                if data_model.__name__ == 'Course':
                    sale_discount_data = SaleDiscount.objects.filter(courses=instance.id, start_date__lte=today, end_date__gte=today).first()
                    if sale_discount_data:
                        data["sale_discount"] = True
                        data["sale_discount_percentage"] = sale_discount_data.sale_discount_percentage
                        data["discount_price"] = instance.current_price_inr - ((instance.current_price_inr*sale_discount_data.sale_discount_percentage)/100)
                    else:
                        data["sale_discount"] = False
                        data["sale_discount_percentage"] = None
                        data["discount_price"] = None
                else:
                    data["sale_discount"] = False
                    data["sale_discount_percentage"] = None
                    data["discount_price"] = None

                if isinstance(user, AnonymousUser) or user == None:
                    data["is_in_buy"] = False
                elif user.user_role and user.user_role.identity == "Student":
                    if data_model.__name__ == 'Course':
                        is_in_buy = StudentEnrolledCourseTracker.objects.filter(entity_id=instance.id, created_by=user).exists()
                        data["is_in_buy"] = is_in_buy
                else:
                    if data_model.__name__ == 'Course':
                        is_in_buy = UserCourseTracker.objects.filter(entity_id=instance.id, created_by=user).exists()
                        data["is_in_buy"] = is_in_buy

                if data_model.__name__ == 'Course':
                    enrolled_count = UserCourseTracker.objects.filter(entity_id=instance.id).count()
                    data["enrolled_count"] = enrolled_count

                image_url = "https://b2cstagingv2.blob.core.windows.net/appuploads/media/"
                if instance.image:
                    image = str(instance.image.file)
                    data["image"] = image_url+image
                return data
        return _Serializer

    def post(self, request, *args, **kwargs):
        return self.get(request, *args, **kwargs)

class ExplorePageAPIView(NonAuthenticatedAPIMixin, ListAPIView, AppAPIView):
    """Sends out data for the website Explore page."""

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
            "blended_learning_paths": BlendedLearningPath,
            "mml_courses": MMLCourse
        }

        model = MODEL_CHOICES[data["type"]]
        return model
    
    def get_filter_for_serializer(self):
        data = self.get_validated_serialized_data()

        advance_filter = data["advance_filter"]
        return advance_filter

    def get_queryset(self):
        from apps.purchase.models import CourseAddToCart, CourseWishlist

        model = self.get_model_for_serializer()
        advance_filter = self.get_filter_for_serializer()
        
        qs = model.objects.exclude(is_private_course=True)
        auth_user = self.get_authenticated_user()
        if auth_user:
            if auth_user.user_role and auth_user.user_role.identity == "Student":
                institution = InstitutionDetail.objects.filter(representative=auth_user.created_by).first()
                if institution:
                    user_group = InstitutionUserGroupDetail.objects.filter(institution=institution, user__id__icontains=auth_user.id)
                    if user_group:
                        user_group_content = InstitutionUserGroupContent.objects.filter(user_group__in=user_group)
                        course_ids = []
                        lp_ids = []
                        cp_ids = []
                        if user_group_content:
                            if model.__name__ == "Course":
                                for content in user_group_content:
                                    course_ids.extend(list(content.courses.values_list('id', flat=True)))
                                qs = Course.objects.filter(id__in=course_ids)
                            elif model.__name__ == "LearningPath":
                                for content in user_group_content:
                                    lp_ids.extend(list(content.learning_path.values_list('id', flat=True)))
                                qs=LearningPath.objects.filter(id__in=lp_ids)
                            elif model.__name__ == "CertificationPath":
                                for content in user_group_content:
                                    cp_ids.extend(list(content.certification_path.values_list('id', flat=True)))
                                qs=CertificationPath.objects.filter(id__in=cp_ids)
                            else:
                                qs=model.objects.none()
                        else:
                            qs=model.objects.none()
                    else:
                        qs=model.objects.none()
                else:
                    qs=model.objects.none()


        if model.__name__ == "Course":
            if advance_filter == "trending_courses":
                qs = model.objects.filter(make_this_course_trending=True).exclude(is_private_course=True)
            elif advance_filter == "recently_published":
                qs = model.objects.all().order_by("-created").exclude(is_private_course=True)
            elif advance_filter == "highly_popular":
                qs = model.objects.filter(make_this_course_popular=True).exclude(is_private_course=True)
            elif advance_filter == "best_selling":
                qs = model.objects.filter(make_this_course_best_selling=True).exclude(is_private_course=True)
            elif advance_filter == "free":
                qs = model.objects.filter(is_free=True).exclude(is_private_course=True)
            elif advance_filter == "virtual_labs":
                qs = model.objects.filter(virtual_lab=True).exclude(is_private_course=True)

        elif model.__name__ == "LearningPath":
            if advance_filter == "trending_courses":
                qs = model.objects.filter(make_this_lp_trending=True).exclude(is_private_course=True)
            elif advance_filter == "recently_published":
                qs = model.objects.all().order_by("-created").exclude(is_private_course=True)
            elif advance_filter == "highly_popular":
                qs = model.objects.filter(make_this_lp_popular=True).exclude(is_private_course=True)
            elif advance_filter == "best_selling":
                qs = model.objects.filter(make_this_lp_best_selling=True).exclude(is_private_course=True)
            elif advance_filter == "free":
                qs = model.objects.filter(is_free=True).exclude(is_private_course=True)
            elif advance_filter == "virtual_labs":
                qs = model.objects.filter(virtual_lab=True).exclude(is_private_course=True)

        else:
            if advance_filter == "trending_courses":
                qs = model.objects.filter(make_this_alp_trending=True).exclude(is_private_course=True)
            elif advance_filter == "recently_published":
                qs = model.objects.all().order_by("-created").exclude(is_private_course=True)
            elif advance_filter == "highly_popular":
                qs = model.objects.filter(make_this_alp_popular=True).exclude(is_private_course=True)
            elif advance_filter == "best_selling":
                qs = model.objects.filter(make_this_alp_best_selling=True).exclude(is_private_course=True)
            elif advance_filter == "free":
                qs = model.objects.filter(is_free=True).exclude(is_private_course=True)
            elif advance_filter == "virtual_labs":
                qs = model.objects.filter(virtual_lab=True).exclude(is_private_course=True)

        if auth_user:
            if model.__name__ == "Course":
                wishlist_model = CourseWishlist
                add_to_cart_model = CourseAddToCart
            elif model.__name__ == "LearningPath":
                wishlist_model = LearningPathWishlist
                add_to_cart_model = LearningPathAddToCart
            elif model.__name__ == "BlendedLearningPath":
                wishlist_model = BlendedLearningPathWishlist
                add_to_cart_model = BlendedLearningPathAddToCart
            elif model.__name__ == "MMLCourse":
                wishlist_model = MMLCourseWishlist
                add_to_cart_model = MMLCourseAddToCart
            else:
                wishlist_model = CertificationPathWishlist
                add_to_cart_model = CertificationPathAddToCart

            # TODO: Refactor later
            # TODO: Also check `get_cart_data_with_pricing_information`
            if auth_user.user_role:
                if auth_user.user_role.identity == "Student":
                    pass
                else: 
                    qs = qs.annotate(
                        is_in_wishlist=models.Exists(
                            wishlist_model.objects.filter(
                                entity_id=models.OuterRef("id"),created_by=auth_user
                            )
                        ),
                        is_in_cart=models.Exists(
                            add_to_cart_model.objects.filter(
                                entity_id=models.OuterRef("id"),created_by=auth_user
                            )
                        )
                    )
            else:
                qs = qs.annotate(
                    is_in_wishlist=models.Exists(
                        wishlist_model.objects.filter(
                            entity_id=models.OuterRef("id"),created_by=auth_user
                        )
                    ),
                    is_in_cart=models.Exists(
                        add_to_cart_model.objects.filter(
                            entity_id=models.OuterRef("id"),created_by=auth_user
                        )
                    )
                )

        return qs

    def get_serializer_class(self):
        data_model = self.get_model_for_serializer()
        user = self.get_user()
        # print(data_model)
        class _Serializer(get_read_serializer(data_model, "__all__")):
            def to_representation(self, instance):
                data = super().to_representation(instance=instance)
                data["is_in_cart"] = getattr(instance, "is_in_cart", False)
                data["is_in_wishlist"] = getattr(instance, "is_in_wishlist", False)

                # sale discount calcluations
                from datetime import datetime
                today = datetime.now().date()

                if data_model.__name__ == 'Course':
                    sale_discount_data = SaleDiscount.objects.filter(courses=instance.id, start_date__lte=today, end_date__gte=today).first()
                    if sale_discount_data:
                        data["sale_discount"] = True
                        data["sale_discount_percentage"] = sale_discount_data.sale_discount_percentage
                        data["discount_price"] = instance.current_price_inr - ((instance.current_price_inr*sale_discount_data.sale_discount_percentage)/100)
                    else:
                        data["sale_discount"] = False
                        data["sale_discount_percentage"] = None
                        data["discount_price"] = None
                elif data_model.__name__ == 'LearningPath':
                    sale_discount_data = SaleDiscount.objects.filter(learning_paths=instance.id, start_date__lte=today, end_date__gte=today).first()
                    if sale_discount_data:
                        data["sale_discount"] = True
                        data["sale_discount_percentage"] = sale_discount_data.sale_discount_percentage
                        data["discount_price"] = instance.current_price_inr - ((instance.current_price_inr*sale_discount_data.sale_discount_percentage)/100)
                    else:
                        data["sale_discount"] = False
                        data["sale_discount_percentage"] = None
                        data["discount_price"] = None
                elif data_model.__name__ == 'CertificationPath':
                    sale_discount_data = SaleDiscount.objects.filter(certification_paths=instance.id, start_date__lte=today, end_date__gte=today).first()
                    if sale_discount_data:
                        data["sale_discount"] = True
                        data["sale_discount_percentage"] = sale_discount_data.sale_discount_percentage
                        data["discount_price"] = instance.current_price_inr - ((instance.current_price_inr*sale_discount_data.sale_discount_percentage)/100)
                else:
                    data["sale_discount"] = False
                    data["sale_discount_percentage"] = None
                    data["discount_price"] = None

                if isinstance(user, AnonymousUser) or user == None:
                    data["is_in_buy"] = False
                elif user.user_role and user.user_role.identity == "Student":
                    if data_model.__name__ == 'Course':
                        is_in_buy = StudentEnrolledCourseTracker.objects.filter(entity_id=instance.id, created_by=user).exists()
                        data["is_in_buy"] = is_in_buy
                    elif data_model.__name__ == 'LearningPath':
                        is_in_buy = StudentEnrolledLearningPathTracker.objects.filter(entity_id=instance.id, created_by=user).exists()
                        data["is_in_buy"] = is_in_buy
                    else:
                        is_in_buy = StudentEnrolledCertificatePathTracker.objects.filter(entity_id=instance.id, created_by=user).exists()
                        data["is_in_buy"] = is_in_buy

                else:
                    if data_model.__name__ == 'Course':
                        is_in_buy = UserCourseTracker.objects.filter(entity_id=instance.id, created_by=user).exists()
                        data["is_in_buy"] = is_in_buy
                    elif data_model.__name__ == 'LearningPath':
                        is_in_buy = UserLearningPathTracker.objects.filter(entity_id=instance.id, created_by=user).exists()
                        data["is_in_buy"] = is_in_buy
                    elif data_model.__name__ == "MMLCourse":
                        is_in_buy = UserMMLCourseTracker.objects.filter(entity_id=instance.id, created_by=user).exists()
                        data["is_in_buy"] = is_in_buy
                    elif data_model.__name__ == "BlendedLearingPath":
                        is_in_buy = UserBlendedLearningPathTracker.objects.filter(entity_id=instance.id, created_by=user).exists()
                        data["is_in_buy"] = is_in_buy
                    else:
                        is_in_buy = UserCertificatePathTracker.objects.filter(entity_id=instance.id, created_by=user).exists()
                        data["is_in_buy"] = is_in_buy

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
    
class ExplorePageRecommentationAPIView(ListAPIView, AppAPIView):
    """Sends out data for the website Explore page."""

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
            "blended_learning_paths": BlendedLearningPath,
        }

        model = MODEL_CHOICES[data["type"]]
        return model
    
    def get_filter_for_serializer(self):
        data = self.get_validated_serialized_data()

        advance_filter = data["advance_filter"]
        return advance_filter

    def get_queryset(self):
        from apps.purchase.models import CourseAddToCart, CourseWishlist

        model = self.get_model_for_serializer()
        
        user = self.get_user()
        if isinstance(user, AnonymousUser) or user == None:
            qs = model.objects.none()
        else:
            qs = model.objects.filter(skills__in=user.onboarding_area_of_interests.values_list("id", flat=True)).exclude(is_private_course=True).distinct()[:6]

        auth_user = self.get_authenticated_user()
        if auth_user:
            if model.__name__ == "Course":
                wishlist_model = CourseWishlist
                add_to_cart_model = CourseAddToCart
            elif model.__name__ == "LearningPath":
                wishlist_model = LearningPathWishlist
                add_to_cart_model = LearningPathAddToCart
            else:
                wishlist_model = CertificationPathWishlist
                add_to_cart_model = CertificationPathAddToCart

            # TODO: Refactor later
            # TODO: Also check `get_cart_data_with_pricing_information`
            qs = qs.annotate(
                is_in_wishlist=models.Exists(
                    wishlist_model.objects.filter(
                        entity_id=models.OuterRef("id"),created_by=auth_user
                    )
                ),
                is_in_cart=models.Exists(
                    add_to_cart_model.objects.filter(
                        entity_id=models.OuterRef("id"),created_by=auth_user
                    )
                )
            )

        return qs

    def get_serializer_class(self):
        data_model = self.get_model_for_serializer()
        user = self.get_user()
        class _Serializer(get_read_serializer(data_model, "__all__")):
            def to_representation(self, instance):
                data = super().to_representation(instance=instance)
                data["is_in_cart"] = getattr(instance, "is_in_cart", False)
                data["is_in_wishlist"] = getattr(instance, "is_in_wishlist", False)

                # sale discount calcluations
                from datetime import datetime
                today = datetime.now().date()

                if data_model == 'Course':
                    sale_discount_data = SaleDiscount.objects.filter(courses=instance.id, start_date__lte=today, end_date__gte=today).first()
                    if sale_discount_data:
                        data["sale_discount"] = True
                        data["sale_discount_percentage"] = sale_discount_data.sale_discount_percentage
                        data["discount_price"] = instance.current_price_inr - ((instance.current_price_inr*sale_discount_data.sale_discount_percentage)/100)
                    else:
                        data["sale_discount"] = False
                        data["sale_discount_percentage"] = None
                        data["discount_price"] = None
                elif data_model == 'LearningPath':
                    sale_discount_data = SaleDiscount.objects.filter(learning_paths=instance.id, start_date__lte=today, end_date__gte=today).first()
                    if sale_discount_data:
                        data["sale_discount"] = True
                        data["sale_discount_percentage"] = sale_discount_data.sale_discount_percentage
                        data["discount_price"] = instance.current_price_inr - ((instance.current_price_inr*sale_discount_data.sale_discount_percentage)/100)
                    else:
                        data["sale_discount"] = False
                        data["sale_discount_percentage"] = None
                        data["discount_price"] = None
                elif data_model.__name__ == 'CertificationPath':
                    sale_discount_data = SaleDiscount.objects.filter(certification_paths=instance.id, start_date__lte=today, end_date__gte=today).first()
                    if sale_discount_data:
                        data["sale_discount"] = True
                        data["sale_discount_percentage"] = sale_discount_data.sale_discount_percentage
                        data["discount_price"] = instance.current_price_inr - ((instance.current_price_inr*sale_discount_data.sale_discount_percentage)/100)
                else:
                    data["sale_discount"] = False
                    data["sale_discount_percentage"] = None
                    data["discount_price"] = None

                if isinstance(user, AnonymousUser) or user == None:
                    data["is_in_buy"] = False
                else:
                    if data_model.__name__ == "Course":
                        is_in_buy = UserCourseTracker.objects.filter(entity_id=instance.id, created_by=user).exists()
                        data["is_in_buy"] = is_in_buy

                        if user.user_role and user.user_role.identity == "Student":
                            is_in_buy = StudentEnrolledCourseTracker.objects.filter(entity_id=instance.id, created_by=user).exists()
                            data["is_in_buy"] = is_in_buy
                        
                    if data_model.__name__ == 'LearningPath':
                        is_in_buy = UserLearningPathTracker.objects.filter(entity_id=instance.id, created_by=user).exists()
                        data["is_in_buy"] = is_in_buy
                            
                image_url = "https://b2cstagingv2.blob.core.windows.net/appuploads/media/"
                if instance.image:
                    image = str(instance.image.file)
                    data["image"] = image_url+image
                return data

        return _Serializer

    def post(self, request, *args, **kwargs):
        return self.get(request, *args, **kwargs)


class ExploreSearchAPIView(NonAuthenticatedAPIMixin, AppAPIView):
    """Provides API for Searching across the application based on the identity query"""
    def post(self, request, *args, **kwargs):
        serializer = ExploreSearchSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        limit = 20

        models_to_filter = {
            "courses": Course,
            "learning_paths": LearningPath,
            "certification_paths": CertificationPath,
            "blended_learning_paths": BlendedLearningPath,
        }

        query = {"identity__icontains": data["search"]}
        auth_user = self.get_authenticated_user()
        filtered_data = {}
        for k, v in models_to_filter.items():
            if k == "courses":
                meta_image_model = CourseImage
                meta_wishlist_model = CourseWishlist
                meta_cart_model = CourseAddToCart
            if k == "learning_paths":
                meta_image_model = LearningPathImage
                meta_wishlist_model = LearningPathWishlist
                meta_cart_model = LearningPathAddToCart
            if k == "certification_paths":
                meta_image_model = CertificationPathImage
                meta_wishlist_model = CertificationPathWishlist
                meta_cart_model = CertificationPathAddToCart
            if k == "blended_learning_paths":
                meta_image_model = BlendedLearningPathImage
                meta_wishlist_model = BlendedLearningPathWishlist
                meta_cart_model = BlendedLearningPathAddToCart
            serializer = get_read_serializer(
                v, meta_fields="__all__",
                init_fields_config={
                    "image_details": get_read_serializer(
                        meta_model= meta_image_model, meta_fields=['id', 'uuid','file']
                    )(source="image"),
                }
            )  
            queryset = v.objects.filter(**query).exclude(is_private_course=True)[:limit]
            if auth_user and auth_user.user_role and auth_user.user_role.identity == "Student":
                institution = InstitutionDetail.objects.filter(representative=auth_user.created_by).first()
                if institution:
                    user_group = InstitutionUserGroupDetail.objects.filter(institution=institution, user__id__icontains=auth_user.id)
                    if user_group:
                        user_group_content = InstitutionUserGroupContent.objects.filter(user_group__in=user_group)
                        course_ids = []
                        lp_ids = []
                        cp_ids = []
                        if user_group_content:
                            if k == "courses":
                                for content in user_group_content:
                                    course_ids.extend(list(content.courses.values_list('id', flat=True)))
                                queryset = v.objects.filter(id__in=course_ids, **query)[:limit]
                            elif k == "learning_paths":
                                for content in user_group_content:
                                    lp_ids.extend(list(content.learning_path.values_list('id', flat=True)))
                                queryset = v.objects.filter(id__in=lp_ids, **query)[:limit]
                            elif k == "certification_paths":
                                for content in user_group_content:
                                    cp_ids.extend(list(content.certification_path.values_list('id', flat=True)))
                                queryset = v.objects.filter(id__in=cp_ids, **query)[:limit]
                            else:
                                queryset = v.objects.none()
                        else:
                            queryset = v.objects.none()
                    else:
                        queryset = v.objects.none()
            serializer = serializer(data=queryset, many=True)
            serializer.is_valid()
            data = serializer.data
            
            # Add is_in_cart,is_in_wishlist,is_in_buy field to each serialized object
            for obj in data:
                obj_id = obj['id']
                is_in_cart = meta_cart_model.objects.filter(entity_id=obj_id, created_by=auth_user).exists()
                is_in_wishlist = meta_wishlist_model.objects.filter(entity_id=obj_id, created_by=auth_user).exists()
                is_in_buy = UserCourseTracker.objects.filter(entity_id=obj_id, created_by=auth_user).exists()
                obj['is_in_cart'] = is_in_cart
                obj['is_in_wishlist'] = is_in_wishlist
                obj['is_in_buy'] = is_in_buy
                today = datetime.now().date()
                sale_discount_data = SaleDiscount.objects.filter(courses=obj['id'], start_date__lte=today, end_date__gte=today).first()
                if sale_discount_data:
                    obj['sale_discount'] = True
                    obj['sale_discount_percentage'] = sale_discount_data.sale_discount_percentage
                    obj['discount_price'] = obj['current_price_inr'] - ((obj['current_price_inr']*sale_discount_data.sale_discount_percentage)/100)
                else:
                    obj['sale_discount'] = False
                    obj['sale_discount_percentage'] = None
                    obj['discount_price'] = None
            filtered_data[k] = data

        return self.send_response(data=filtered_data)


class CourseDetailView(
    NonAuthenticatedAPIMixin, AbstractLookUpFieldMixin, RetrieveAPIView, AppAPIView
):
    """
    This view provides endpoint to access Course in detail along with
    expanded related views.
    """

    serializer_class = CourseSerializer
    queryset = Course.objects.all()


class MMLCourseDetailView(
    NonAuthenticatedAPIMixin, AbstractLookUpFieldMixin, RetrieveAPIView, AppAPIView
):
    """
    This view provides endpoint to access Course in detail along with
    expanded related views.
    """

    serializer_class = MMLCourseSerializer
    queryset = MMLCourse.objects.all()


class LearningPathDetailView(
    NonAuthenticatedAPIMixin, AbstractLookUpFieldMixin, RetrieveAPIView, AppAPIView
):
    """
    This view provides endpoint to access LearningPath in detail along with
    expanded related views.
    """

    serializer_class = LeaningPathSerializer
    queryset = LearningPath.objects.all()

class LearningPathCourseListView(NonAuthenticatedAPIMixin, ListAPIView, AppAPIView):
    pagination_class = HomePageAppPagination
    serializer_class = LeaningPathCourseListSerializer
    def get_queryset(self):
        uuid = self.kwargs.get('uuid')       
        qs = LearningPathCourse.objects.filter(learning_path__uuid=uuid)
        return qs
    
class LearningPathCoursePreviewView(NonAuthenticatedAPIMixin, ListAPIView, AppAPIView):
    serializer_class = LeaningPathCoursePreviewSerializer
    def get_queryset(self):
        uuid = self.kwargs.get('uuid')       
        qs = LearningPathCourse.objects.filter(learning_path__uuid=uuid)[:1]
        return qs
    
class CertificationPathDetailView(
    NonAuthenticatedAPIMixin, AbstractLookUpFieldMixin, RetrieveAPIView, AppAPIView
):
    """
    This view provides endpoint to access CertificationPath in detail along with
    expanded related views.
    """

    serializer_class = CertificationPathSerializer
    queryset = CertificationPath.objects.all()

class ExploreSkillsMetaAPIView(NonAuthenticatedAPIMixin, AppAPIView):
    """Provides Meta Data for skills filtering"""

    def get(self, request):
        data = {
            "category": get_app_read_only_serializer(
                Category,  DEFAULT_IDENTITY_DISPLAY_FIELDS
            )(Category.objects.all(), many=True).data,
        }

        return self.send_response(data=data)

class SkillsPageAPIView(NonAuthenticatedAPIMixin, ListAPIView, AppAPIView):

    serializer_class = SkillListSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = "__all__"
    search_fields = ['identity']
    pagination_class = AppPagination

    def get_queryset(self):
        price_ranges = self.get_request().query_params.getlist('price_range')
        qs = Skill.objects.filter(is_archived=False)
        combined_filter = Q()  # Initialize an empty Q object for combining filters

        for price_range in price_ranges:
            if "above" in price_range:
                above_price = int(price_range.split(" ")[-1])
                combined_filter |= Q(current_price_inr__gt=above_price)
            elif "below" in price_range:
                below_price = int(price_range.split(" ")[-1])
                combined_filter |= Q(current_price_inr__lt=below_price)
            else:
                price_range_parts = price_range.split("-")
                from_price = int(price_range_parts[0].strip())
                to_price = int(price_range_parts[1].strip())
                combined_filter |= Q(current_price_inr__gte=from_price, current_price_inr__lte=to_price)
        qs = qs.filter(combined_filter)  # Apply the combined filter to the queryset
    
        return qs
    
class SkillsPageDetailsAPIView(NonAuthenticatedAPIMixin, AbstractLookUpFieldMixin, RetrieveAPIView, AppAPIView):
    """
    This view provides endpoint to access skills in detail along with
    expanded related views.
    """    
    serializer_class = SkillDetailSerializer
    queryset = Skill.objects.all()

class SkillsPageLearningDetailsAPIView(NonAuthenticatedAPIMixin, ListAPIView, AppAPIView):
    """
    This view provides endpoint to access skills in detail along with
    expanded related views.
    """   
    pagination_class = HomePageAppPagination
    def get_serializer_class(self):
        type = self.kwargs.get('type')
        if type == 'courses':
            return SkillCourseDetailsSerializer
        elif type == 'learning-paths':
            return SkillLeaningPathDetailsSerializer
        elif type == 'certificate-paths':
            return SkillCertificationPathDetailsSerializer
        elif type == 'webinars':
            return SkillWebinarDetailSerializer
        elif type == 'forums':
            return SkillZoneDetailsSerializer
        elif type == 'hackathons':
            return SkillHackathonDetailsSerializer
        else:
            return SkillCourseDetailsSerializer 
    queryset = Skill.objects.all()


class CourseBulkDetailView(NonAuthenticatedAPIMixin, AppAPIView):
    def post(self, request, format=None):
        serializer = CourseUUIDListSerializer(data=request.data)
        if serializer.is_valid():
            course_uuids = serializer.validated_data['course_uuids']
            courses = Course.objects.filter(uuid__in=course_uuids,is_private_course=False)
            course_serializer = CourseBulkDetailSerializer(courses, many=True)
            return self.send_response(data=course_serializer.data)
        return self.send_error_response()
    
class PrivateCourseBulkDetailView(NonAuthenticatedAPIMixin, AppAPIView):
    def post(self, request, format=None):
        serializer = CourseUUIDListSerializer(data=request.data)
        if serializer.is_valid():
            course_uuids = serializer.validated_data['course_uuids']
            courses = Course.objects.filter(uuid__in=course_uuids,is_private_course=True)
            course_serializer = CourseBulkDetailSerializer(courses, many=True)
            return self.send_response(data=course_serializer.data)
        return self.send_error_response()

class BlendedLearningPathDetailView(
    NonAuthenticatedAPIMixin, AbstractLookUpFieldMixin, RetrieveAPIView, AppAPIView
):
    """
    This view provides endpoint to access BlendedLearningPath in detail along with
    expanded related views.
    """

    serializer_class = BlendedLearningPathSerializer
    queryset = BlendedLearningPath.objects.all()

class BlendedLearningPathPriceDetailView(NonAuthenticatedAPIMixin, AppAPIView):
    """
    This view provides endpoint to access BlendedLearningPathPriceDetailView in detail along with
    expanded related views.
    """
    def get(self, request, *args, **kwargs):
        uuid = kwargs.get('uuid')
        if uuid:
            lp = LearningPath.objects.get(uuid=uuid)
            if lp:
                lp_name = lp.identity
                qs = BlendedLearningPathPriceDetails.objects.get_or_none(blended_learning__identity=lp_name)
                if qs:
                    modes = [mode.identity for mode in qs.mode.all()]  # Accessing identity attribute for each related mode
                    return self.send_response(data={
                            "blp_uuid": qs.blended_learning.uuid,
                            "blp_name":qs.blended_learning.identity,
                            "mode":modes,
                            # "self_paced_fee": qs.self_paced_fee,
                            "online_actual_fee": qs.online_actual_fee,
                            "online_discounted_fee": qs.online_discounted_fee,
                            "online_discount_rate": qs.online_discount_rate,
                            "classroom_actual_fee": qs.classroom_actual_fee,
                            "classroom_discounted_fee": qs.classroom_discounted_fee,
                            "classroom_discount_rate": qs.classroom_discount_rate,
                        })
                else:
                    return self.send_error_response()
            else:
                    return self.send_error_response()


class BlendedLearningPathBuyDetailView(AppAPIView):
    def get(self, request, *args, **kwargs):
        uuid = kwargs.get('uuid')
        if uuid:
            qs = UserBlendedLearningPathTracker.objects.filter(entity__uuid=uuid, created_by=self.get_user())
            response_data = []
            if qs:
                for data in qs:
                    response_data.append({"mode": data.blp_learning_mode,"schedule_id" :data.blp_schedule_id, "is_in_buy": True})
                    return self.send_response(response_data)
            else:
                return self.send_error_response("BLP not found.")
        else:
            return self.send_error_response("Missing 'blp_uuid' in request data.")

class BlendedLearningPathClassroomAndVirtualScheduleDetailView(NonAuthenticatedAPIMixin, AppAPIView):
     def get(self, request, *args, **kwargs):
        uuid = kwargs.get('uuid')
        mode = kwargs.get('mode')
        if uuid:
            blp = BlendedLearningPath.objects.get(uuid=uuid)
            if blp:
                blp_name = blp.identity
                qs = BlendedLearningClassroomAndVirtualDetails.objects.filter(blended_learning__identity=blp_name)
                price = BlendedLearningPath.objects.get_or_none(identity=blp_name)
                details_list = []
                if mode == "online":
                    for detail in qs:
                        if detail.online_details != {}:
                            detail_data = {
                                "blp_uuid": blp.uuid,
                                "blp_name": blp.identity,
                                "course_name": detail.course.identity,  
                                "online_number_of_sessions":detail.online_number_of_sessions,
                                "online_details":detail.online_details,
                                "virtual_session_link":detail.virtual_session_link,
                                "online_actual_price": price.online_actual_price,
                                "online_current_price": price.online_current_price,
                                "mode": "Online Training"
                            }
                            details_list.append(detail_data)
                    return self.send_response(data=details_list)
                if mode == "classroom":
                    for detail in qs:
                        if detail.classroom_details != {}:
                            detail_data = {
                                "blp_uuid": blp.uuid,
                                "blp_name": blp.identity,
                                "course_name": detail.course.identity,  
                                "classroom_number_of_sessions":detail.classroom_number_of_sessions,
                                "classroom_details":detail.classroom_details,
                                "classroom_actual_price": price.classroom_actual_price,
                                "classroom_current_price": price.classroom_current_price,
                                "mode": "Classroom Training"
                            }
                            details_list.append(detail_data)
                    return self.send_response(data=details_list)
        return self.send_error_response()
    
class BlendedLearningPathScheduleListView(NonAuthenticatedAPIMixin, ListAPIView, AppAPIView):
    """view for listing the schedules based on the BLP and the mode"""

    serializer_class = BlendedLearningPathScheduleDetailsSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["is_day_batch", "is_weekend_batch"]

    def get_queryset(self, *args, **kwargs):
        uuid = self.kwargs.get('uuid')
        mode = self.kwargs.get('mode')
        try:
            price_details = BlendedLearningPathPriceDetails.objects.get(blended_learning__uuid=uuid)
            blp_schedules = price_details.schedule_details.filter(mode__id=mode)
            return blp_schedules
        except BlendedLearningPathPriceDetails.DoesNotExist:
            raise serializers.ValidationError("Price details not found for the given UUID.")
        except Exception as err:
            raise serializers.ValidationError(str(err))
    
            