from django.db import models
from apps.common.views.api.base import NonAuthenticatedAPIMixin
from rest_framework.filters import SearchFilter
from ...common.pagination import AppPagination
from rest_framework.generics import ListAPIView
from apps.common.views.api import AppAPIView
from django_filters.rest_framework import DjangoFilterBackend
from apps.web_portal.serializers import ExploreRoleSerializer
from ...learning.models import CertificationPath, Course, LearningPath, LearningRole, BlendedLearningPath, CourseImage, LearningPathImage, CertificationPathImage, BlendedLearningPathImage
from apps.access.models import InstitutionDetail, InstitutionUserGroupDetail, InstitutionUserGroupContent
from ...purchase.models import CourseWishlist, LearningPathWishlist, CertificationPathWishlist, CourseAddToCart, LearningPathAddToCart, CertificationPathAddToCart, BlendedLearningPathWishlist, BlendedLearningPathAddToCart
from ...common.serializers import get_read_serializer
from ...payments.models import SaleDiscount
from django.contrib.auth.models import AnonymousUser
from apps.my_learnings.models import UserCourseTracker, StudentEnrolledCourseTracker, UserLearningPathTracker, UserCertificatePathTracker, UserBlendedLearningPathTracker
from apps.common.views.api.generic import (
    DEFAULT_IDENTITY_DISPLAY_FIELDS,
)
from ..serializers import ExploreSearchSerializer
from datetime import datetime
from rest_framework import filters

class MultipleValueFilterBackend(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        learning_roles = request.query_params.getlist('learning_role')
        if learning_roles:
            queryset = queryset.filter(learning_role__in=learning_roles)
        return queryset

class ExploreRolePageAPIView(NonAuthenticatedAPIMixin, ListAPIView, AppAPIView):
    """Sends out data for the website Explore page."""

    filter_backends = [MultipleValueFilterBackend, SearchFilter]
    filterset_fields = "__all__"
    search_fields = ["identity"]
    pagination_class = AppPagination

    def get_validated_serialized_data(self):
        serializer = ExploreRoleSerializer(data=self.request.data)
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

    def get_queryset(self):
        
        model = self.get_model_for_serializer()
        
        qs = model.objects.exclude(learning_role=None).exclude(is_private_course=True)
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
                                qs = Course.objects.filter(id__in=course_ids)
                            elif model.__name__ == "LearningPath":
                                qs=model.objects.none()
                            else:
                                qs=model.objects.none()
                        else:
                            qs=model.objects.none()
                    else:
                        qs=model.objects.none()
                else:
                    qs=model.objects.none()

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
                else:
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
                        is_in_buy = StudentEnrolledCourseTracker.objects.filter(entity_id=instance.id, created_by=user).exists()
                        data["is_in_buy"] = is_in_buy

                else:
                    if data_model.__name__ == 'Course':
                        is_in_buy = UserCourseTracker.objects.filter(entity_id=instance.id, created_by=user).exists()
                        data["is_in_buy"] = is_in_buy
                    elif data_model.__name__ == 'LearningPath':
                        is_in_buy = UserLearningPathTracker.objects.filter(entity_id=instance.id, created_by=user).exists()
                        data["is_in_buy"] = is_in_buy
                    elif data_model.__name__ == 'BlendedLearningPath':
                        is_in_buy = UserBlendedLearningPathTracker.objects.filter(entity_id=instance.id, created_by=user).exists()
                        data["is_in_buy"] = is_in_buy
                    else:
                        is_in_buy = UserCertificatePathTracker.objects.filter(entity_id=instance.id, created_by=user).exists()
                        data["is_in_buy"] = is_in_buy

                image_url = "https://b2cstagingv2.blob.core.windows.net/appuploads/media/"
                if instance.image:
                    image = str(instance.image.file)
                    data["image"] = image_url+image
                return data

        return _Serializer

    def post(self, request, *args, **kwargs):
        return self.get(request, *args, **kwargs)
    
class ExploreRoleMetaAPIView(NonAuthenticatedAPIMixin, AppAPIView):
    """Provides Meta Data for filtering"""

    def get(self, request):
        data = {
            "learning_role": get_read_serializer(
                LearningRole, DEFAULT_IDENTITY_DISPLAY_FIELDS
            )(LearningRole.objects.all(), many=True).data,
        }

        return self.send_response(data=data)
    
class ExploreRoleSearchAPIView(NonAuthenticatedAPIMixin, AppAPIView):
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
            "blended_learning_paths": BlendedLearningPath
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
                v, meta_fields=['id','uuid', 'identity', 'description', 'duration', 'rating', 'actual_price_inr', 'current_price_inr'],
                init_fields_config={
                "image_details": get_read_serializer(
                    meta_model= meta_image_model, meta_fields=['uuid','file']
                )(source="image"),
                }
            )  

            serializer = serializer(data=v.objects.filter(**query).exclude(learning_role=None).exclude(is_private_course=True)[:limit], many=True)
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
