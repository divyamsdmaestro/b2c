from rest_framework import serializers
from apps.common.pagination import AppPagination
from apps.common.views.api import AppAPIView
from apps.common.views.api.generic import (
    AbstractLookUpFieldMixin,
)
from rest_framework.generics import RetrieveAPIView
from apps.common.serializers import AppReadOnlyModelSerializer, get_app_read_only_serializer
from apps.payments.models import SubscriptionPlan, SubscriptionPlanSaleDiscount
from datetime import datetime
from apps.payments.models.subscription_plan import SubscriptionPlanImage
from apps.web_portal.serializers import CourseSerializer, LeaningPathSerializer, CertificationPathSerializer
from apps.learning.models import Course, LearningPath, CertificationPath
from rest_framework.generics import ListAPIView

class SubscriptionPlanDetailView(AbstractLookUpFieldMixin, RetrieveAPIView, AppAPIView
):
    """
    This view staff details.
    """
    class _Serializer(AppReadOnlyModelSerializer):
        sale_discount_for_yearly = serializers.SerializerMethodField()
        sale_discount_for_monthly = serializers.SerializerMethodField()

        class Meta(AppReadOnlyModelSerializer.Meta):
            model = SubscriptionPlan
            fields = [
                "identity",
                "description",
                "start_date",
                "end_date",
                "rating",
                "what_will_you_learn",
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
            ]

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


    serializer_class = _Serializer
    queryset = SubscriptionPlan.objects.filter(status="active")

class LearningContentMetaAPIView(AppAPIView):

    def get(self, request, *args, **kwargs):
        course_data = CourseSerializer(Course.objects.all(), many=True, context={"request": request}).data
        learning_path_data = LeaningPathSerializer(LearningPath.objects.all(), many=True, context={"request": request}).data
        advance_learning_path_data = CertificationPathSerializer(CertificationPath.objects.all(), many=True, context={"request": request}).data

        course_data_with_type = self.add_type(course_data, "course")
        learning_path_data_with_type = self.add_type(learning_path_data, "learning_path")
        advance_learning_path_data_with_type = self.add_type(advance_learning_path_data, "adv_learning_path")

        data = {
            "courses": course_data_with_type,
            "learning_paths": learning_path_data_with_type,
            "advance_learning_paths": advance_learning_path_data_with_type,
        }
        return self.send_response(data=data)

    def add_type(self, data, type):
        for item in data:
            item["type"] = type
        return data 
    

class SubscriptionPlanListAPIView(AppAPIView, ListAPIView):
    # class _Serializer(AppReadOnlyModelSerializer):
    #     class Meta:
    #         model = SubscriptionPlan
    #         fields = [
    #             "id",
    #             "uuid",
    #             "identity",
    #             "description",
    #             "start_date",
    #             "end_date",
    #             "yearly_price_in_inr",
    #             "monthly_price_in_inr",
    #         ]
    
    pagination_class = AppPagination
    queryset = SubscriptionPlan.objects.filter(status="active")
    # serializer_class = _Serializer

    def get_serializer_class(self):
        return get_app_read_only_serializer(
            meta_model=SubscriptionPlan,
            meta_fields=[
                "id",
                "uuid",
                "identity",
                "description",
                "start_date",
                "end_date",
                "yearly_price_in_inr",
                "monthly_price_in_inr",
            ],
            init_fields_config={
            #     "subscription_plan_image": get_app_read_only_serializer(
            #     meta_model=SubscriptionPlanImage, meta_fields=['id','uuid','file']
            # )(source="image"),
            "course":get_app_read_only_serializer(
                meta_model=Course, meta_fields=['id','identity', 'description', 'code', 'duration'],
            )(many=True, source="courses"),
    #         "learning_path":get_app_read_only_serializer(
    #             meta_model=LearningPath, meta_fields=['id','identity', 'description', 'duration'],
    #         )(many=True, source="learning_paths"),
    #         "certification_path":get_app_read_only_serializer(
    #             meta_model=CertificationPath, meta_fields=['id','identity', 'description', 'duration'],
    #         )(many=True, source="certification_paths")
            },
        )
    
class SubscriptionPlanStatusUpdateAPIView(AppAPIView):
    def post(self, request, *args, **kwargs):
        try:
            subscription_plan = SubscriptionPlan.objects.get(pk=kwargs["id"])
            new_status = request.data.get("status")
            subscription_plan.status = new_status
            subscription_plan.save()
            return self.send_response()
        except SubscriptionPlan.DoesNotExist:
            return self.send_error_response()