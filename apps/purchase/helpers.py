from django.db import models
from apps.access.models import User
from apps.common.serializers import get_app_read_only_serializer
from apps.my_learnings.models.trackers import UserCourseTracker
from apps.payments.models import Discount
from apps.purchase.models import (
    CertificationPathAddToCart,
    CertificationPathWishlist,
    CourseAddToCart,
    CourseWishlist,
    DiscountAddToCart,
    LearningPathAddToCart,
    LearningPathWishlist,
    SkillAddToCart,
    SkillWishlist,
    SubscriptionPlanAddToCart,
    SubscriptionPlanWishlist,
    BlendedLearningPathWishlist,
    BlendedLearningPathAddToCart,
    JobEligibilitySkillAddToCart,
    JobEligibilitySkillWishlist
)
from apps.purchase.models.cart import  EcashAddToCart,MMLCourseAddToCart
from apps.purchase.models.wishlist import MMLCourseWishlist
from apps.web_portal.serializers import serialize_for_cart_and_wishlist


def get_cart_data_with_pricing_information(user, guest_id=None):
    # Determine the user filter condition
    if guest_id:
        user_filter = {'guest_id': guest_id}
    else:
        user_filter = {'created_by': user}
    qs = [
        *CourseAddToCart.objects.filter(created_by=user).annotate(
            is_in_wishlist=models.Exists(
                CourseWishlist.objects.filter(entity_id=models.OuterRef("entity_id"),created_by=user)
            ),
            is_in_cart=models.Exists(
                CourseAddToCart.objects.filter(
                    id=models.OuterRef("id"), created_by=user
                )
            ),
        ),
        *MMLCourseAddToCart.objects.filter(created_by=user).annotate(
            is_in_wishlist=models.Exists(
                MMLCourseWishlist.objects.filter(entity_id=models.OuterRef("entity_id"),created_by=user)
            ),
            is_in_cart=models.Exists(
                MMLCourseAddToCart.objects.filter(
                    id=models.OuterRef("id"), created_by=user
                )
            ),
        ),
        *LearningPathAddToCart.objects.filter(created_by=user).annotate(
            is_in_wishlist=models.Exists(
                LearningPathWishlist.objects.filter(
                    entity_id=models.OuterRef("entity_id"), created_by=user
                )
            ),
            is_in_cart=models.Exists(
                LearningPathAddToCart.objects.filter(
                    id=models.OuterRef("id"), created_by=user
                )
            ),
        ),
        *CertificationPathAddToCart.objects.filter(created_by=user).annotate(
            is_in_wishlist=models.Exists(
                CertificationPathWishlist.objects.filter(
                    entity_id=models.OuterRef("entity_id"), created_by=user
                )
            ),
            is_in_cart=models.Exists(
                CertificationPathAddToCart.objects.filter(
                    id=models.OuterRef("id"), created_by=user
                )
            ),
        ),
        *SkillAddToCart.objects.filter(created_by=user).annotate(
            is_in_wishlist=models.Exists(
                SkillWishlist.objects.filter(
                    entity_id=models.OuterRef("entity_id"), created_by=user
                )
            ),
            is_in_cart=models.Exists(
                SkillAddToCart.objects.filter(
                    id=models.OuterRef("id"), created_by=user
                )
            ),
        ),
        *SubscriptionPlanAddToCart.objects.filter(**user_filter).annotate(
            is_in_wishlist=models.Exists(
                SubscriptionPlanWishlist.objects.filter(entity_id=models.OuterRef("entity_id"))
            ),
            is_in_cart=models.Exists(
                SubscriptionPlanAddToCart.objects.filter(
                    id=models.OuterRef("id"), **user_filter
                )
            ),
        ),
        *BlendedLearningPathAddToCart.objects.filter(created_by=user).annotate(
            is_in_wishlist=models.Exists(
                BlendedLearningPathWishlist.objects.filter(
                    entity_id=models.OuterRef("entity_id"), created_by=user
                )
            ),
            is_in_cart=models.Exists(
                BlendedLearningPathAddToCart.objects.filter(
                    id=models.OuterRef("id"), created_by=user
                )
            ),
        ),
        *JobEligibilitySkillAddToCart.objects.filter(created_by=user).annotate(
            is_in_wishlist=models.Exists(
                JobEligibilitySkillWishlist.objects.filter(
                    entity_id=models.OuterRef("entity_id"),created_by=user
                )
            ),
            is_in_cart=models.Exists(
                JobEligibilitySkillAddToCart.objects.filter(
                    id=models.OuterRef("id"), created_by=user
                )
            ),
        ),
    ]
   
    discount_applied = DiscountAddToCart.objects.get_or_none(created_by=user)

    coupon_applied = None
    total_amount = 0.0 
    discount_amount = 0.0
    amount_without_discount = 0.0
    wallet = 0
    total_wallet = 0
    ecash_applied = EcashAddToCart.objects.get_or_none(created_by=user)
    #wallet calculation
    # Check if the user has purchased any non-free courses
    ecash = True if ecash_applied else False #set ecash as TRUE if ecash is applied or else FALSE
    # if ecash_applied:
    try:
        # Retrieve the user instance from the database
        user_instance = User.objects.get(id=user.id)
        points = user_instance.current_reward_points
        wallet = points
        total_wallet = user_instance.total_reward_points
        
    except User.DoesNotExist:
        # Handle case where user does not exist
        pass
    except Exception as e:
        # Handle other exceptions if necessary
        print(f"An error occurred: {e}")

    entity_data = [serialize_for_cart_and_wishlist(_) for _ in qs]
    discount_list = []
    for _ in entity_data:
        price_in_inr = _.get("entity", {}).get("price_in_inr", 0)
        if price_in_inr:
            total_amount += price_in_inr
            amount_without_discount += price_in_inr
        sales_dis_amount = _.get("entity", {}).get("sale_discount", {}).get("total_discount_price", 0)
        if sales_dis_amount:
            total_amount = 0
            total_amount += sales_dis_amount
        sda_val = _.get("entity", {}).get("sale_discount", {}).get("sale_discount_amount", 0)
        if sda_val is not None:
            discount_list.append(sda_val)
    if discount_list:
        sale_discount_total = sum(discount_list)
    else:
        sale_discount_total = 0

    if discount_applied:
        discount = discount_applied.discount
        coupon_applied = get_app_read_only_serializer(Discount, meta_fields="__all__")(
            discount
        ).data

        if discount.is_flat_rate_discount:
            if discount.discount_in_amount:
                if total_amount <= discount.discount_in_amount:
                    discount_amount = total_amount
                else:
                    discount_amount = discount.discount_in_amount
        else:
            if discount.discount_in_percentage:
                discount_amount = (discount.discount_in_percentage / 100) * total_amount
                if discount.discount_in_percentage_amount_cap:
                    if discount.discount_in_percentage_amount_cap > 0:  # noqa
                        if discount_amount > discount.discount_in_percentage_amount_cap:
                            discount_amount = discount.discount_in_percentage_amount_cap
    #deduct the wallet amount from the total amount
    if ecash == True:
        final_amount = (total_amount - discount_amount) - wallet
    else:
        final_amount = (total_amount - discount_amount)
    # get Pincode
    if user and user.pincode:
        pincode = user.pincode
    else:
        pincode=None
    if final_amount > 1 and ecash == True:
        trigger_razorypay = True
    elif final_amount > 1 and ecash == False:
        trigger_razorypay = True
    else:
        trigger_razorypay = False
    cart_data = {
        "entities": entity_data,
        "discount_percentage": (discount_amount / 100),
        "coupon_applied": coupon_applied,
        "total_amount": amount_without_discount,
        "discount": sale_discount_total,
        "coupon_discount_amount": discount_amount,
        "ecash_applied":ecash,
        "wallet":wallet,
        "total_wallet": wallet,
        "gst_value": (final_amount * 0.18),
        "grand_amount": (final_amount + (final_amount * 0.18)),
        "pincode": pincode,
        "trigger_razorypay": trigger_razorypay
    }
    # print(cart_data)
    # breakpoint()

    return cart_data

def get_cart_data_with_pricing_information_list(user):
    qs = [
        *CourseAddToCart.objects.filter(created_by=user).annotate(
            is_in_wishlist=models.Exists(
                CourseWishlist.objects.filter(entity_id=models.OuterRef("entity_id"),created_by=user)
            ),
            is_in_cart=models.Exists(
                CourseAddToCart.objects.filter(
                    id=models.OuterRef("id"), created_by=user
                )
            ),
        ),
        *MMLCourseAddToCart.objects.filter(created_by=user).annotate(
            is_in_wishlist=models.Exists(
                MMLCourseWishlist.objects.filter(entity_id=models.OuterRef("entity_id"),created_by=user)
            ),
            is_in_cart=models.Exists(
                MMLCourseAddToCart.objects.filter(
                    id=models.OuterRef("id"), created_by=user
                )
            ),
        ),
        *LearningPathAddToCart.objects.filter(created_by=user).annotate(
            is_in_wishlist=models.Exists(
                LearningPathWishlist.objects.filter(
                    entity_id=models.OuterRef("entity_id"), created_by=user
                )
            ),
            is_in_cart=models.Exists(
                LearningPathAddToCart.objects.filter(
                    id=models.OuterRef("id"), created_by=user
                )
            ),
        ),
        *CertificationPathAddToCart.objects.filter(created_by=user).annotate(
            is_in_wishlist=models.Exists(
                CertificationPathWishlist.objects.filter(
                    entity_id=models.OuterRef("entity_id"), created_by=user
                )
            ),
            is_in_cart=models.Exists(
                CertificationPathAddToCart.objects.filter(
                    id=models.OuterRef("id"), created_by=user
                )
            ),
        ),
        *SkillAddToCart.objects.filter(created_by=user).annotate(
            is_in_wishlist=models.Exists(
                SkillWishlist.objects.filter(
                    entity_id=models.OuterRef("entity_id"), created_by=user
                )
            ),
            is_in_cart=models.Exists(
                SkillAddToCart.objects.filter(
                    id=models.OuterRef("id"), created_by=user
                )
            ),
        ),
        *SubscriptionPlanAddToCart.objects.filter(created_by=user).annotate(
            is_in_wishlist=models.Exists(
                SubscriptionPlanWishlist.objects.filter(entity_id=models.OuterRef("entity_id"),created_by=user)
            ),
            is_in_cart=models.Exists(
                SubscriptionPlanAddToCart.objects.filter(
                    id=models.OuterRef("id"), created_by=user
                )
            ), #guest id is primary key
        ),
        *BlendedLearningPathAddToCart.objects.filter(created_by=user).annotate(
            is_in_wishlist=models.Exists(
                BlendedLearningPathWishlist.objects.filter(
                    entity_id=models.OuterRef("entity_id"), created_by=user
                )
            ),
            is_in_cart=models.Exists(
                BlendedLearningPathAddToCart.objects.filter(
                    id=models.OuterRef("id"), created_by=user
                )
            ),
        ),
        *JobEligibilitySkillAddToCart.objects.filter(created_by=user).annotate(
            is_in_wishlist=models.Exists(
                JobEligibilitySkillWishlist.objects.filter(
                    entity_id=models.OuterRef("entity_id"),created_by=user
                )
            ),
            is_in_cart=models.Exists(
                JobEligibilitySkillAddToCart.objects.filter(
                    id=models.OuterRef("id"), created_by=user
                )
            ),
        ),
    ]
   
    discount_applied = DiscountAddToCart.objects.get_or_none(created_by=user)

    coupon_applied = None
    total_amount = 0.0 
    discount_amount = 0.0
    amount_without_discount = 0.0
    wallet = 0
    total_wallet = 0
    ecash_applied = EcashAddToCart.objects.get_or_none(created_by=user)
    #wallet calculation
    # Check if the user has purchased any non-free courses
    ecash = True if ecash_applied else False #set ecash as TRUE if ecash is applied or else FALSE
    # if ecash_applied:
    try:
        # Retrieve the user instance from the database
        user_instance = User.objects.get(id=user.id)
        points = user_instance.current_reward_points
        wallet = points
        total_wallet = user_instance.total_reward_points
        
    except User.DoesNotExist:
        # Handle case where user does not exist
        pass
    except Exception as e:
        # Handle other exceptions if necessary
        print(f"An error occurred: {e}")

    entity_data = [serialize_for_cart_and_wishlist(_) for _ in qs]
    discount_list = []
    for _ in entity_data:
        price_in_inr = _.get("entity", {}).get("price_in_inr", 0)
        if price_in_inr:
            total_amount += price_in_inr
            amount_without_discount += price_in_inr
        sales_dis_amount = _.get("entity", {}).get("sale_discount", {}).get("total_discount_price", 0)
        if sales_dis_amount:
            total_amount = 0
            total_amount += sales_dis_amount
        sda_val = _.get("entity", {}).get("sale_discount", {}).get("sale_discount_amount", 0)
        if sda_val is not None:
            discount_list.append(sda_val)
    if discount_list:
        sale_discount_total = sum(discount_list)
    else:
        sale_discount_total = 0

    if discount_applied:
        discount = discount_applied.discount
        coupon_applied = get_app_read_only_serializer(Discount, meta_fields="__all__")(
            discount
        ).data

        if discount.is_flat_rate_discount:
            if discount.discount_in_amount:
                if total_amount <= discount.discount_in_amount:
                    discount_amount = total_amount
                else:
                    discount_amount = discount.discount_in_amount
        else:
            if discount.discount_in_percentage:
                discount_amount = (discount.discount_in_percentage / 100) * total_amount
                if discount.discount_in_percentage_amount_cap:
                    if discount.discount_in_percentage_amount_cap > 0:  # noqa
                        if discount_amount > discount.discount_in_percentage_amount_cap:
                            discount_amount = discount.discount_in_percentage_amount_cap
    #deduct the wallet amount from the total amount
    if ecash == True:
        final_amount = (total_amount - discount_amount) - wallet
    else:
        final_amount = (total_amount - discount_amount)
    # get Pincode
    if user and user.pincode:
        pincode = user.pincode
    else:
        pincode=None
    if final_amount > 1 and ecash == True:
        trigger_razorypay = True
    elif final_amount > 1 and ecash == False:
        trigger_razorypay = True
    else:
        trigger_razorypay = False
    cart_data = {
        "entities": entity_data,
        "discount_percentage": (discount_amount / 100),
        "coupon_applied": coupon_applied,
        "total_amount": amount_without_discount,
        "discount": sale_discount_total,
        "coupon_discount_amount": discount_amount,
        "ecash_applied":ecash,
        "wallet":wallet,
        "total_wallet": wallet,
        "gst_value": (final_amount * 0.18),
        "grand_amount": (final_amount + (final_amount * 0.18)),
        "pincode": pincode,
        "trigger_razorypay": trigger_razorypay
    }
    # print(cart_data)
    # breakpoint()

    return cart_data