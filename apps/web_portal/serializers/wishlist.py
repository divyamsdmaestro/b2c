from apps.learning.models.blended_learning_path import BlendedLearningPathCourseMode
from ...payments.models import SaleDiscount, SubscriptionPlan, Discount
from datetime import datetime
from ...common.helpers import get_file_field_url
from apps.common.serializers import (
    AppReadOnlyModelSerializer,
)
from ...purchase.models import DiscountAddToCart
from rest_framework import serializers
from apps.learning.models import BlendedLearningUserEnrollCourseDetails, BlendedLearningPath, BlendedLearningPathPriceDetails

def serialize_for_cart_and_wishlist(tracker):
    """Serializer the `Wishlist` or `AddToCart` tracker for front end."""
    entity = tracker.entity

    """This function used to get sale discount"""
    today = datetime.now().date()
    blp_mode =  None
    blp_course = None
    blp_session_details = None
    sale_discount_data = SaleDiscount.objects.filter(courses=entity.id, start_date__lte=today, end_date__gte=today).first()
    if sale_discount_data and not isinstance(entity, (SubscriptionPlan, BlendedLearningPath)):
        sale_discount = True
        sale_discount_percentage = sale_discount_data.sale_discount_percentage
        discount_price = entity.current_price_inr - ((entity.current_price_inr*sale_discount_data.sale_discount_percentage)/100)
        sale_discount_amount = entity.current_price_inr - discount_price
    elif sale_discount_data and isinstance(entity, SubscriptionPlan) and not isinstance(entity, BlendedLearningPath):
        if tracker.is_monthly_or_yearly:
            current_price_inr = getattr(entity, "monthly_price_in_inr", 10)
        else:
            current_price_inr = getattr(entity, "yearly_price_in_inr", 10)
        sale_discount = True
        sale_discount_percentage = sale_discount_data.sale_discount_percentage
        discount_price = current_price_inr - ((current_price_inr*sale_discount_data.sale_discount_percentage)/100)
        sale_discount_amount = current_price_inr - discount_price
    else:
        sale_discount_amount = None
        sale_discount = False
        sale_discount_percentage = None
        discount_price = None

    if isinstance(entity, SubscriptionPlan):
        if tracker.is_monthly_or_yearly:
            subscription_plan_price = getattr(entity, "monthly_price_in_inr", 10)
        else:
            subscription_plan_price = getattr(entity, "yearly_price_in_inr", 10)
    elif isinstance(entity, BlendedLearningPath):
        if tracker.mode == "Self Paced":
            blp = BlendedLearningPath.objects.filter(id=entity.id, mode_details__identity=tracker.mode).first()
            blp_model_price = blp.self_paced_current_price
            blp_mode = "Self Paced"
        elif tracker.mode == "Online instructor led training":
            mode = BlendedLearningPathCourseMode.objects.get(identity=tracker.mode)
            blp_price= BlendedLearningPathPriceDetails.objects.filter(blended_learning=entity, mode__in=[mode.id]).first()
            blp_model_price = blp_price.online_discounted_fee if blp_price.online_discounted_fee else blp_price.online_actual_fee
            blp_course = tracker.course.id if tracker.course else None
            blp_mode = "Online instructor led training"
            blp_session_details = tracker.schedule_details_id
        else:
            mode = BlendedLearningPathCourseMode.objects.get(identity=tracker.mode)
            blp_price= BlendedLearningPathPriceDetails.objects.filter(blended_learning=entity, mode__in=[mode]).first()
            blp_model_price = blp_price.classroom_discounted_fee if blp_price.classroom_discounted_fee else blp_price.classroom_actual_fee
            blp_course = tracker.course.id if tracker.course else None
            blp_mode = "Classroom training"
            blp_session_details = tracker.schedule_details_id

    if isinstance(entity, SubscriptionPlan):
        prince_in_inr = subscription_plan_price
    elif isinstance(entity, BlendedLearningPath):
        prince_in_inr = blp_model_price
    else:
        prince_in_inr = getattr(entity, "current_price_inr", 10)
    return {
        "entity": {
            "uuid": str(entity.uuid),
            "identity": entity.identity,
            "price_in_inr": prince_in_inr,
            "blp_mode": blp_mode if blp_mode else None,
            # "price_actual": getattr(entity, "actual_price_inr", 100),
            # "tutor": str(entity.author.identity),
            "duration": getattr(entity, "duration", 6000),
            "tag": "Testing",
            "type": entity.__class__.__name__,
            "sale_discount": {
                "sale_discount": sale_discount,
                "sale_discount_amount" :  sale_discount_amount,
                "sale_discount_percentage": sale_discount_percentage,
                "total_discount_price": discount_price
            },
            "image": get_file_field_url(entity, "image"),
            "blp_course":blp_course if blp_course else None,
            "session_details": blp_session_details if blp_session_details else None
        },
        "is_in_wishlist": tracker.is_in_wishlist,
        "is_in_cart": tracker.is_in_cart,
        "uuid": str(tracker.uuid),
        "created": str(tracker.created),
    }


def serialize_for_bookmark_list(tracker):
    """Serializer the `Wishlist` or `AddToCart` tracker for front end."""
    entity = tracker.entity
    return {
        "entity": {
            "uuid": str(entity.uuid),
            "identity": entity.identity,
        },
        "is_in_bookmark": tracker.is_in_bookmark,
        "uuid": str(tracker.uuid),
        "created": str(tracker.created),
    }

class CouponListSerializer(AppReadOnlyModelSerializer):
    is_applied = serializers.SerializerMethodField()

    class Meta:
        model = Discount
        fields = "__all__"

    def get_is_applied(self, obj):
        user = self.get_user()
        if user==None:
            return False
        else:
            is_applied = DiscountAddToCart.objects.filter(discount=obj.id, created_by=user).exists()
            return is_applied