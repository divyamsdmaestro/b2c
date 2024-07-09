from apps.learning.models.linkages import Skill
from apps.my_learnings.models import UserSubscriptionPlanTracker
from apps.purchase.models import SubscriptionPlanWishlist
from rest_framework import serializers
from apps.common.views.api.base import NonAuthenticatedAPIMixin
from rest_framework.generics import ListAPIView, RetrieveAPIView
from apps.payments.models import SubscriptionPlan, SubscriptionPlanSaleDiscount, SubscriptionPlanImage, SubscriptionPlanCustomerEnquiry
from apps.common.views.api import AppAPIView
from apps.common.serializers import AppReadOnlyModelSerializer, AppWriteOnlyModelSerializer, get_app_read_only_serializer
from datetime import datetime
from apps.common.views.api.generic import AbstractLookUpFieldMixin
from django.contrib.auth.models import AnonymousUser
from apps.purchase.models import SubscriptionPlanAddToCart
from apps.learning.models import Course, CourseImage, LearningPath, LearningPathImage, CertificationPath, CertificationPathImage
from ...common.pagination import HomePageAppPagination, SubscriptionPlanAppPagination

class SubscriptionPlanSerializer(AppReadOnlyModelSerializer):
    image = get_app_read_only_serializer(SubscriptionPlanImage, meta_fields="__all__")()
    sale_discount_for_yearly = serializers.SerializerMethodField()
    sale_discount_for_monthly = serializers.SerializerMethodField()
    is_in_cart = serializers.SerializerMethodField()
    is_in_wishlist = serializers.SerializerMethodField()
    is_in_buy = serializers.SerializerMethodField()
    learning_content_count = serializers.SerializerMethodField()

    class Meta(AppReadOnlyModelSerializer.Meta):
        model = SubscriptionPlan
        fields = [
            "id",
            "uuid",
            "identity",
            "description",
            "image",
            "rating",
            "what_will_you_learn",
            "start_date",
            "end_date",
            "make_this_subscription_plan_popular",
            # Feature
            "skill_level_assesment",
            "interactive_practices",
            "certification",
            "virtual_labs",
            "basic_to_advance_level",
            "is_duration",
            "duration",
            # Pricing Yearly
            "is_yearly_subscription_plan_active",
            "yearly_price_in_inr",
            "is_gst_inclusive_for_yearly",
            # Pricing Monthly
            "is_monthly_subscription_plan_active",
            "monthly_price_in_inr",
            "is_gst_inclusive_for_monthly",
            "sale_discount_for_yearly",
            "sale_discount_for_monthly",
            "is_in_cart",
            "is_in_wishlist",
            "is_in_buy",
            "learning_content_count",
        ]

    def get_is_in_cart(self, obj):
        """This function used to get subscription plan is already in cart or not"""
        user = self.get_user()
        if isinstance(user, AnonymousUser) or user == None:
            return False
        else:
            is_in_cart = SubscriptionPlanAddToCart.objects.filter(
                entity_id=obj.id, created_by=user
            ).exists()
            return is_in_cart

    def get_is_in_wishlist(self, obj):
        """This function used to get subscriptionplan is already in wishlist or not"""
        user = self.get_user()
        if isinstance(user, AnonymousUser) or user == None:
            return False
        else:
            is_in_wishlist = SubscriptionPlanWishlist.objects.filter(
                entity_id=obj.id, created_by=user
            ).exists()
            return is_in_wishlist
    
    def get_is_in_buy(self,obj):
        """This function used to get subscriptionplan is already in buy or not"""
        user = self.get_user()
        if isinstance(user, AnonymousUser) or user == None:
            return False
        else:
            is_buy = UserSubscriptionPlanTracker.objects.filter(entity_id=obj.id, created_by=user).exists()
            return is_buy

    def get_sale_discount_for_yearly(self,obj):
        """This function used to get sale discount"""
        today = datetime.now().date()
        sale_discount_data = SubscriptionPlanSaleDiscount.objects.filter(subscription_plan=obj.id, start_date__lte=today, end_date__gte=today).first()
        if sale_discount_data:
            if obj.is_yearly_subscription_plan_active:
                if sale_discount_data.is_yearly_subscription_plan_offer:
                    if sale_discount_data.is_yearly_discount_percentage:
                        if sale_discount_data.yearly_discount_percentage:
                            yearly_sale_discount = True
                            yearly_sale_discount_ammount = None
                            yearly_sale_discount_percentage = sale_discount_data.yearly_discount_percentage
                            yearly_discount_price = obj.yearly_price_in_inr - ((obj.yearly_price_in_inr*sale_discount_data.yearly_discount_percentage)/100)
                    elif sale_discount_data.is_yearly_discount_amount:
                        if sale_discount_data.yearly_discount_amount:
                            yearly_sale_discount = True
                            yearly_sale_discount_ammount = sale_discount_data.yearly_discount_amount
                            yearly_sale_discount_percentage = None
                            yearly_discount_price = obj.yearly_price_in_inr - yearly_sale_discount_ammount
                else:
                    yearly_sale_discount = False
                    yearly_sale_discount_ammount = None
                    yearly_sale_discount_percentage = None
                    yearly_discount_price = None
            else:
                yearly_sale_discount = False
                yearly_sale_discount_ammount = None
                yearly_sale_discount_percentage = None
                yearly_discount_price = None
            return {"yearly_sale_discount":yearly_sale_discount, 'yearly_sale_discount_ammount':yearly_sale_discount_ammount, "yearly_sale_discount_percentage":yearly_sale_discount_percentage, "yearly_discount_price":yearly_discount_price}
    
    def get_sale_discount_for_monthly(self,obj):
        """This function used to get sale discount"""
        today = datetime.now().date()
        sale_discount_data = SubscriptionPlanSaleDiscount.objects.filter(subscription_plan=obj.id, start_date__lte=today, end_date__gte=today).first()
        if sale_discount_data:
            if obj.is_monthly_subscription_plan_active:
                if sale_discount_data.is_monthly_subscription_plan_offer:
                    if sale_discount_data.is_monthly_discount_percentage:
                        if sale_discount_data.monthly_discount_percentage:
                            monthly_sale_discount = True
                            monthly_sale_discount_ammount = None
                            monthly_sale_discount_percentage = sale_discount_data.monthly_discount_percentage
                            monthly_discount_price = obj.monthly_price_in_inr - ((obj.monthly_price_in_inr*sale_discount_data.monthly_discount_percentage)/100)
                    elif sale_discount_data.is_monthly_discount_amount:
                        if sale_discount_data.monthly_discount_amount:
                            monthly_sale_discount = True
                            monthly_sale_discount_ammount = sale_discount_data.monthly_discount_amount
                            monthly_sale_discount_percentage = None
                            monthly_discount_price = obj.monthly_price_in_inr - monthly_sale_discount_ammount
                else:
                    monthly_sale_discount = False
                    monthly_sale_discount_ammount = None
                    monthly_sale_discount_percentage = None
                    monthly_discount_price = None
            else:
                monthly_sale_discount = False
                monthly_sale_discount_ammount = None
                monthly_sale_discount_percentage = None
                monthly_discount_price = None
            return {"monthly_sale_discount":monthly_sale_discount, 'monthly_sale_discount_ammount':monthly_sale_discount_ammount, "monthly_sale_discount_percentage":monthly_sale_discount_percentage, "monthly_discount_price":monthly_discount_price}
        
    def get_learning_content_count(self, obj):
        return{
            "courses_count": obj.courses.count(),
            "learning_paths_count": obj.learning_paths.count(),
            "certification_paths_count": obj.certification_paths.count()
        }

class SubscriptionCourseSerializer(serializers.ModelSerializer):
    """This serializer contains configuration for Course."""

    image = get_app_read_only_serializer(CourseImage, meta_fields="__all__")()
    skills = get_app_read_only_serializer(Skill, meta_fields=['id','uuid','identity'])(many=True)
    
    class Meta:
        fields = ['id', 'uuid', 'identity', 'description', 'skills', 'rating', 'duration', 'make_this_course_popular', 'make_this_course_trending', 'make_this_course_best_selling', 'image']
        model = Course

class SubscriptionLearningPathSerializer(serializers.ModelSerializer):
    """This serializer contains configuration for Course."""

    image = get_app_read_only_serializer(LearningPathImage, meta_fields="__all__")()
    
    class Meta:
        fields = ['id', 'uuid', 'identity', 'description', 'rating', 'duration', 'make_this_lp_popular', 'make_this_lp_best_selling', 'make_this_lp_trending', 'image']
        model = LearningPath

class SubscriptionCertificationPathSerializer(serializers.ModelSerializer):
    """This serializer contains configuration for Course."""

    image = get_app_read_only_serializer(CertificationPathImage, meta_fields="__all__")()
    
    class Meta:
        fields = ['id', 'uuid', 'identity', 'description', 'rating', 'duration', 'make_this_alp_popular', 'make_this_alp_trending', 'make_this_alp_best_selling', 'image']
        model = CertificationPath

class SubscriptionPlanDetailSerializer(AppReadOnlyModelSerializer):
    image = get_app_read_only_serializer(SubscriptionPlanImage, meta_fields="__all__")()
    sale_discount_for_yearly = serializers.SerializerMethodField()
    sale_discount_for_monthly = serializers.SerializerMethodField()
    is_in_cart = serializers.SerializerMethodField()
    is_in_wishlist = serializers.SerializerMethodField()
    is_in_buy = serializers.SerializerMethodField()
    learning_content_count = serializers.SerializerMethodField()

    class Meta(AppReadOnlyModelSerializer.Meta):
        model = SubscriptionPlan
        fields = [
            "id",
            "uuid",
            "identity",
            "description",
            "rating",
            "what_will_you_learn",
            "image",
            "start_date",
            "end_date",
            "make_this_subscription_plan_popular",
            # Feature
            "skill_level_assesment",
            "interactive_practices",
            "certification",
            "virtual_labs",
            "basic_to_advance_level",
            "is_duration",
            "duration",
            # Pricing Yearly
            "is_yearly_subscription_plan_active",
            "yearly_price_in_inr",
            "is_gst_inclusive_for_yearly",
            # Pricing Monthly
            "is_monthly_subscription_plan_active",
            "monthly_price_in_inr",
            "is_gst_inclusive_for_monthly",
            "sale_discount_for_yearly",
            "sale_discount_for_monthly",
            "is_in_cart",
            "is_in_wishlist",
            "is_in_buy",
            "learning_content_count",
        ]

    def get_is_in_cart(self, obj):
        """This function used to get subscription plan is already in cart or not"""
        user = self.get_user()
        if isinstance(user, AnonymousUser) or user == None:
            return False
        else:
            is_in_cart = SubscriptionPlanAddToCart.objects.filter(
                entity_id=obj.id, created_by=user
            ).exists()
            return is_in_cart

    def get_is_in_wishlist(self, obj):
        """This function used to get subscriptionplan is already in wishlist or not"""
        user = self.get_user()
        if isinstance(user, AnonymousUser) or user == None:
            return False
        else:
            is_in_wishlist = SubscriptionPlanWishlist.objects.filter(
                entity_id=obj.id, created_by=user
            ).exists()
            return is_in_wishlist
    
    def get_is_in_buy(self,obj):
        """This function used to get subscriptionplan is already in buy or not"""
        user = self.get_user()
        if isinstance(user, AnonymousUser) or user == None:
            return False
        else:
            is_buy = UserSubscriptionPlanTracker.objects.filter(entity_id=obj.id, created_by=user).exists()
            return is_buy

    def get_sale_discount_for_yearly(self,obj):
        """This function used to get sale discount"""
        today = datetime.now().date()
        sale_discount_data = SubscriptionPlanSaleDiscount.objects.filter(subscription_plan=obj.id, start_date__lte=today, end_date__gte=today).first()
        if sale_discount_data:
            if obj.is_yearly_subscription_plan_active:
                if sale_discount_data.is_yearly_subscription_plan_offer:
                    if sale_discount_data.is_yearly_discount_percentage:
                        if sale_discount_data.yearly_discount_percentage:
                            yearly_sale_discount = True
                            yearly_sale_discount_ammount = None
                            yearly_sale_discount_percentage = sale_discount_data.yearly_discount_percentage
                            yearly_discount_price = obj.yearly_price_in_inr - ((obj.yearly_price_in_inr*sale_discount_data.yearly_discount_percentage)/100)
                    elif sale_discount_data.is_yearly_discount_amount:
                        if sale_discount_data.yearly_discount_amount:
                            yearly_sale_discount = True
                            yearly_sale_discount_ammount = sale_discount_data.yearly_discount_amount
                            yearly_sale_discount_percentage = None
                            yearly_discount_price = obj.yearly_price_in_inr - yearly_sale_discount_ammount
                else:
                    yearly_sale_discount = False
                    yearly_sale_discount_ammount = None
                    yearly_sale_discount_percentage = None
                    yearly_discount_price = None
            else:
                yearly_sale_discount = False
                yearly_sale_discount_ammount = None
                yearly_sale_discount_percentage = None
                yearly_discount_price = None
            return {"yearly_sale_discount":yearly_sale_discount, 'yearly_sale_discount_ammount':yearly_sale_discount_ammount, "yearly_sale_discount_percentage":yearly_sale_discount_percentage, "yearly_discount_price":yearly_discount_price}
    
    def get_sale_discount_for_monthly(self,obj):
        """This function used to get sale discount"""
        today = datetime.now().date()
        sale_discount_data = SubscriptionPlanSaleDiscount.objects.filter(subscription_plan=obj.id, start_date__lte=today, end_date__gte=today).first()
        if sale_discount_data:
            if obj.is_monthly_subscription_plan_active:
                if sale_discount_data.is_monthly_subscription_plan_offer:
                    if sale_discount_data.is_monthly_discount_percentage:
                        if sale_discount_data.monthly_discount_percentage:
                            monthly_sale_discount = True
                            monthly_sale_discount_ammount = None
                            monthly_sale_discount_percentage = sale_discount_data.monthly_discount_percentage
                            monthly_discount_price = obj.monthly_price_in_inr - ((obj.monthly_price_in_inr*sale_discount_data.monthly_discount_percentage)/100)
                    elif sale_discount_data.is_monthly_discount_amount:
                        if sale_discount_data.monthly_discount_amount:
                            monthly_sale_discount = True
                            monthly_sale_discount_ammount = sale_discount_data.monthly_discount_amount
                            monthly_sale_discount_percentage = None
                            monthly_discount_price = obj.monthly_price_in_inr - monthly_sale_discount_ammount
                else:
                    monthly_sale_discount = False
                    monthly_sale_discount_ammount = None
                    monthly_sale_discount_percentage = None
                    monthly_discount_price = None
            else:
                monthly_sale_discount = False
                monthly_sale_discount_ammount = None
                monthly_sale_discount_percentage = None
                monthly_discount_price = None
            return {"monthly_sale_discount":monthly_sale_discount, 'monthly_sale_discount_ammount':monthly_sale_discount_ammount, "monthly_sale_discount_percentage":monthly_sale_discount_percentage, "monthly_discount_price":monthly_discount_price} 
        
    def get_learning_content_count(self, obj):
        return{
            "courses_count": obj.courses.count(),
            "learning_paths_count": obj.learning_paths.count(),
            "certification_paths_count": obj.certification_paths.count()
        }

class SubscriptionPlanListView(NonAuthenticatedAPIMixin, ListAPIView, AppAPIView):

    serializer_class = SubscriptionPlanSerializer
    queryset = SubscriptionPlan.objects.filter(status="active")

class SubscriptionPlanDetailView(NonAuthenticatedAPIMixin, AbstractLookUpFieldMixin, RetrieveAPIView, AppAPIView):

    queryset = SubscriptionPlan.objects.filter(status="active")
    serializer_class = SubscriptionPlanDetailSerializer

class SubscriptionCoursesView(NonAuthenticatedAPIMixin, ListAPIView):
    serializer_class = SubscriptionCourseSerializer
    pagination_class = SubscriptionPlanAppPagination

    def get_queryset(self):
        # Retrieve the subscription based on the identifier in the URL
        subscription = SubscriptionPlan.objects.get(uuid=self.kwargs['uuid'])

        # Return the courses associated with the subscription
        return subscription.courses.all()
    
class SubscriptionLearningPathView(NonAuthenticatedAPIMixin, ListAPIView):
    serializer_class = SubscriptionLearningPathSerializer
    pagination_class = SubscriptionPlanAppPagination

    def get_queryset(self):
        # Retrieve the subscription based on the identifier in the URL
        subscription = SubscriptionPlan.objects.get(uuid=self.kwargs['uuid'])

        # Return the courses associated with the subscription
        return subscription.learning_paths.all()
    
class SubscriptionCertificationPathView(NonAuthenticatedAPIMixin, ListAPIView):
    serializer_class = SubscriptionCertificationPathSerializer
    pagination_class = SubscriptionPlanAppPagination

    def get_queryset(self):
        # Retrieve the subscription based on the identifier in the URL
        subscription = SubscriptionPlan.objects.get(uuid=self.kwargs['uuid'])

        # Return the courses associated with the subscription
        return subscription.certification_paths.all()

class SubscriptionPlanEnquiryDetailsAPIView(NonAuthenticatedAPIMixin, AppAPIView):    
    class _Serializer(AppWriteOnlyModelSerializer):
        """Handle input data."""
        class Meta(AppWriteOnlyModelSerializer.Meta):
            fields = [
                "name",
                "email",
                "subscription_plan",
                "phone_number",
                "is_customer"]
            model = SubscriptionPlanCustomerEnquiry
    serializer_class = _Serializer

    def get_serializer(self, *args, **kwargs):
        kwargs['context'] = self.get_serializer_context()
        return self.serializer_class(*args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            email = data.get('email')
            subscription_plan = data.get('subscription_plan')
            phone_number = data.get('phone_number')
            name = data.get('name')
            is_customer = data.get('is_customer')

        subscription_reg = SubscriptionPlanCustomerEnquiry.objects.get_or_none(email=email,subscription_plan=subscription_plan,phone_number=phone_number,)
        if subscription_reg:
            if subscription_reg.created_by == self.request.user:
                return self.send_response(data={"status": "Already Registered"})
            else:
                return self.send_error_response()
        else:
            registration = SubscriptionPlanCustomerEnquiry(
                subscription_plan=subscription_plan,
                name=name,
                email=email,
                phone_number=phone_number,
                is_customer=is_customer,
                created_by=self.request.user
            )
            registration.save()
            return self.send_response(data={"status":"Successfully Registered"})