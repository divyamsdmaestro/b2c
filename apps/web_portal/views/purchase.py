from datetime import date
from apps.access.models import User, GuestUser
from django.conf import settings
from django.db import models
from rest_framework import serializers
from datetime import datetime
from apps.common.views.api import AppAPIView
from apps.learning.models.mml_course import MMLCourse
from apps.purchase.models.cart import EcashAddToCart, MMLCourseAddToCart
from apps.purchase.models.wishlist import MMLCourseWishlist
from apps.web_portal.models.notification import Notification
from ...common.serializers import AppSerializer, AppWriteOnlyModelSerializer
from ...learning.models import CertificationPath, Course, LearningPath, BlendedLearningPath, BlendedLearningUserEnroll, JobEligibleSkill, LearningRole
from ...payments.models import Discount, Order, SubscriptionPlan, SubscriptionPlanSaleDiscount
from ...purchase.helpers import get_cart_data_with_pricing_information, get_cart_data_with_pricing_information_list
from ...purchase.models import (
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
    JobEligibilitySkillWishlist,
    JobEligibilitySkillAddToCart,
)
from ..serializers import serialize_for_cart_and_wishlist, CouponListSerializer, TransactionHistoryListSerializer
from apps.my_learnings.helpers import get_one_year_datetime_from_now
from apps.my_learnings.models import StudentEnrolledCourseTracker, StudentEnrolledLearningPathTracker, StudentEnrolledCertificatePathTracker, UserCourseTracker
from apps.learning.models import Skill
from datetime import datetime
from rest_framework.generics import ListAPIView
from django_filters.rest_framework import DjangoFilterBackend
from ...common.pagination import AppPagination
from apps.common.helpers import send_welcome_email
from django.template.loader import get_template
from django.http import HttpResponse
from xhtml2pdf import pisa
from io import BytesIO
from rest_framework.response import Response
from ...common.serializers import get_read_serializer
from apps.meta.models import State
from apps.common.helpers import (
    number_to_words

)
from django.db import IntegrityError
from apps.common.views.api.base import NonAuthenticatedAPIMixin

today = datetime.now().date()

class EntityAddToWishlistAPIView(AppAPIView):
    """
    View used to add entities like Course, Learning Path, Certification Path
    into the users wishlist. This works in a toggle way(add & then delete).
    """

    def post(self, *args, **kwargs):
        """Handle on post."""

        uuid = kwargs["uuid"]
        user = self.get_user()
        config = [
            [Course, CourseWishlist],
            [LearningPath, LearningPathWishlist],
            [CertificationPath, CertificationPathWishlist],
            [Skill, SkillWishlist],
            [SubscriptionPlan,SubscriptionPlanWishlist],
            [BlendedLearningPath, BlendedLearningPathWishlist],
            [JobEligibleSkill, JobEligibilitySkillWishlist],
            [MMLCourse, MMLCourseWishlist]
        ]

        for _ in config:
            model = _[0]
            wishlist_model = _[1]

            entity = model.objects.get_or_none(uuid=uuid)
            if entity:
                wishlist_instance = wishlist_model.objects.get_or_none(
                    entity=entity, created_by=user
                )

                if wishlist_instance:
                    wishlist_instance.delete()
                else:
                    if model == SubscriptionPlan:
                        type = self.request.data.get('type')
                        if type == "monthly":
                            wishlist_model.objects.create(entity=entity,is_monthly_or_yearly=True, created_by=user)
                        else:
                            wishlist_model.objects.create(entity=entity,is_monthly_or_yearly=False, created_by=user)
                    elif model == BlendedLearningPath:
                        mode = self.request.data.get('mode')
                        if mode:
                            wishlist_model.objects.create(entity=entity,mode=mode,created_by=user)
                    else:
                        wishlist_model.objects.create(entity=entity, created_by=user)

                break

        return self.send_response()

class CouponListAPIView(ListAPIView, AppAPIView):
    
    queryset = Discount.objects.all()
    serializer_class = CouponListSerializer

class EntityAddToCartAPIView(NonAuthenticatedAPIMixin,AppAPIView):
    """
    View used to add entities like Course, Learning Path, Certification Path
    into the users cart for buying later. This works in a toggle way.
    """

    def post(self, *args, **kwargs):
        """Handle on post."""

        uuid = kwargs["uuid"]
        user = self.get_user()
        config = [
            [Course, CourseAddToCart],
            [LearningPath, LearningPathAddToCart],
            [CertificationPath, CertificationPathAddToCart],
            [Skill, SkillAddToCart],
            [SubscriptionPlan, SubscriptionPlanAddToCart],
            [BlendedLearningPath, BlendedLearningPathAddToCart],
            # [BlendedLearningUserEnroll, BlendedLearningPathAddToCart],
            [JobEligibleSkill, JobEligibilitySkillAddToCart],
            [MMLCourse, MMLCourseAddToCart]
        ]

        for _ in config:
            model = _[0]
            cart_model = _[1]

            entity = model.objects.get_or_none(uuid=uuid)
            if entity:
                type = self.request.data.get('type')
                if self.request.data.get('guest_id'):
                    guest_id = GuestUser.objects.get_or_none(uuid=self.request.data.get('guest_id'))
                else:
                    guest_id = None
                if guest_id is not None:
                    cart_instance = cart_model.objects.get_or_none(
                    entity=entity, guest_id=guest_id)
                else:
                    cart_instance = cart_model.objects.get_or_none(
                    entity=entity, created_by=user)

                if cart_instance:
                    cart_instance.delete()
                else:
                    if model == SubscriptionPlan:
                        if type == "monthly":
                            if user is None and guest_id.id:
                                cart_model.objects.create(entity=entity,is_monthly_or_yearly=True,guest_id=guest_id.id)
                            else:
                                cart_model.objects.create(entity=entity,is_monthly_or_yearly=True, created_by=user)
                        else:
                            if user is None and guest_id.id:
                                cart_model.objects.create(entity=entity,is_monthly_or_yearly=False,guest_id=guest_id.id)
                            else:
                                cart_model.objects.create(entity=entity,is_monthly_or_yearly=False, created_by=user)
                    elif model == BlendedLearningPath:
                        mode = self.request.data.get('mode')
                        course = self.request.data.get('course') 
                        session_details = self.request.data.get('session_details') 
                        schedule_details = self.request.data.get('schedule_details')
                        if mode:
                            cart_model.objects.create(entity=entity,mode=mode,course_id=course,session_details=[], created_by=user, schedule_details_id=schedule_details)
                    else:
                        cart_model.objects.create(entity=entity, created_by=user)

                   
                break

        return self.send_response()

class PincodeEditAPIView(AppAPIView):
    class _Serializer(AppWriteOnlyModelSerializer):
        class Meta(AppWriteOnlyModelSerializer.Meta):
            model = User
            fields = [
                "pincode"
            ]

        def update(self, instance, validated_data):
            instance = super().update(validated_data=validated_data, instance=instance)
            return instance

    serializer_class = _Serializer
    
    def post(self, *args, **kwargs):
        serializer = self.get_valid_serializer(instance=self.get_authenticated_user())
        serializer.save()
        return self.send_response()

class PincodeEditMetaAPIView(ListAPIView, AppAPIView):
    """Provides meta-data for highest education and area of interest."""

    def get(self, request, *args, **kwargs):
        data = {
            "state": get_read_serializer(
                State, meta_fields=['id', 'uuid', 'identity']
            )(State.objects.all(), many=True).data,
        }
        return self.send_response(data=data)

class ApplyOrRemoveCouponAPIView(AppAPIView):
    """
    View to apply coupon for the cart.
    """

    def post(self, request, *args, **kwargs):
        class Serializer(AppSerializer):
            coupon_code = serializers.CharField(max_length=512)

            class Meta:
                fields = ["coupon_code"]

        serializer = Serializer(data=request.data)

        serializer.is_valid(raise_exception=True)
        discount = Discount.get_discount(serializer.data["coupon_code"])

        user = request.user

        discount_data = self.validate_coupon(discount, user)

        if discount_data[0]:
            DiscountAddToCart.objects.filter(created_by=user).exclude(
                discount=discount
            ).delete()
            discount_added_in_cart, created = DiscountAddToCart.objects.get_or_create(
                discount=discount, created_by=user
            )

            if created:
                return self.send_response(data={"coupon": "COUPON_APPLIED"})
            else:
                DiscountAddToCart.objects.filter(
                    created_by=user, discount=discount
                ).delete()
                return self.send_response(data={"coupon": "COUPON_REMOVED"})
        else:
            return self.send_error_response(data={"error": discount_data[1]})

    def validate_coupon(self, discount, user):
        if discount:
            if discount.enable_usage_limit:  # noqa
                if discount.discount_usage == discount.maximum_number_of_usages:
                    return [False, "COUPON_EXPIRED"]

            if discount.per_user_usage_limit > 0:  # noqa
                if (
                    len(
                        Order.objects.filter(
                            created_by=user, status="success", discount_applied=discount
                        )
                    )
                    >= discount.per_user_usage_limit
                ):
                    return [False, "USER_LIMIT_REACHED_FOR_THIS_COUPON"]

            if not (discount.start_date <= date.today() <= discount.end_date):
                return [False, "COUPON_EXPIRED"]

            return [True, discount]
        else:
            return [False, "INVALID_COUPON"]


class MyWishlistAPIView(AppAPIView):
    """View to list out entities in the user's wishlist trackers."""

    def get(self, request, *args, **kwargs):
        """Handle on get."""

        user = self.get_user()
        identity = request.GET.get('search')
      
        qs = [
            *CourseWishlist.objects.filter(created_by=user).annotate(
                is_in_wishlist=models.Exists(
                    CourseWishlist.objects.filter(
                        id=models.OuterRef("id"), created_by=user
                    )
                ),
                is_in_cart=models.Exists(
                    CourseAddToCart.objects.filter(
                        entity_id=models.OuterRef("entity_id"), created_by=user
                    )
                ),
            ),
            *MMLCourseWishlist.objects.filter(created_by=user).annotate(
                is_in_wishlist=models.Exists(
                    MMLCourseWishlist.objects.filter(
                        id=models.OuterRef("id"), created_by=user
                    )
                ),
                is_in_cart=models.Exists(
                    MMLCourseAddToCart.objects.filter(
                        entity_id=models.OuterRef("entity_id"), created_by=user
                    )
                ),
            ),
            *LearningPathWishlist.objects.filter(created_by=user).annotate(
                is_in_wishlist=models.Exists(
                    LearningPathWishlist.objects.filter(
                        id=models.OuterRef("id"), created_by=user
                    )
                ),
                is_in_cart=models.Exists(
                    LearningPathAddToCart.objects.filter(
                        entity_id=models.OuterRef("entity_id"), created_by=user
                    )
                ),
            ),
            *CertificationPathWishlist.objects.filter(created_by=user).annotate(
                is_in_wishlist=models.Exists(
                    CertificationPathWishlist.objects.filter(
                        id=models.OuterRef("id"), created_by=user
                    )
                ),
                is_in_cart=models.Exists(
                    CertificationPathAddToCart.objects.filter(
                        entity_id=models.OuterRef("entity_id"), created_by=user
                    )
                ),
            ),
            *SkillWishlist.objects.filter(created_by=user).annotate(
                is_in_wishlist=models.Exists(
                    SkillWishlist.objects.filter(
                        id=models.OuterRef("id"), created_by=user
                    )
                ),
                is_in_cart=models.Exists(
                    SkillAddToCart.objects.filter(
                        entity_id=models.OuterRef("entity_id"), created_by=user
                    )
                ),
            ),
            *SubscriptionPlanWishlist.objects.filter(created_by=user).annotate(
                is_in_wishlist=models.Exists(
                    SubscriptionPlanWishlist.objects.filter(
                        id=models.OuterRef("id"), created_by=user
                    )
                ),
                is_in_cart=models.Exists(
                    SubscriptionPlanAddToCart.objects.filter(
                        entity_id=models.OuterRef("entity_id"), created_by=user
                    )
                ),
            ),
            *BlendedLearningPathWishlist.objects.filter(created_by=user).annotate(
                is_in_wishlist=models.Exists(
                    BlendedLearningPathWishlist.objects.filter(
                        id=models.OuterRef("id"), created_by=user
                    )
                ),
                is_in_cart=models.Exists(
                    BlendedLearningPathAddToCart.objects.filter(
                        entity_id=models.OuterRef("id"), created_by=user
                    )
                ),
                # is_in_cart=models.Exists(
                #     BlendedLearningPathAddToCart.objects.filter(
                #         entity__blended_learning_id=models.OuterRef("id"), created_by=user
                #     )
                # ),
            ),
            *JobEligibilitySkillWishlist.objects.filter(created_by=user).annotate(
                is_in_wishlist=models.Exists(
                    JobEligibleSkill.objects.filter(
                        id=models.OuterRef("id"), created_by=user
                    )
                ),
                is_in_cart=models.Exists(
                    JobEligibilitySkillAddToCart.objects.filter(
                        entity_id=models.OuterRef("entity_id"), created_by=user
                    )
                ),
            ),
        ]
        if identity:
            qs = [
                tracker
                for tracker in qs
                if tracker.entity.identity == identity
            ]
            
        return self.send_response([serialize_for_cart_and_wishlist(_) for _ in qs])


class MyCartAPIView(NonAuthenticatedAPIMixin, AppAPIView):
    """View to list out entities in the user's add to cart trackers."""

    def get(self, *args, **kwargs):
        """Handle on get."""

        user = self.get_user()
        guest_id = self.request.query_params.get('guest_id', None)  # primary key
        # guest_id = self.request.data.get('guest_id', None) # primary key
        return self.send_response(get_cart_data_with_pricing_information(user, guest_id))


class MakeOrderFromCartAPIView(AppAPIView):
    """Create Order from Cart"""

    def get(self, request, *args, **kwargs):
        user = self.get_user()

        cart_data = get_cart_data_with_pricing_information_list(user)
        discount = cart_data.get("coupon_applied")
        if discount:
            discount = Discount.objects.get(uuid=discount["uuid"])

        order = Order(
            cart_data=cart_data,
            discount_applied=discount,
            total_price=cart_data["total_amount"],
            discount_price=cart_data["coupon_discount_amount"],
            total_price_after_discount=cart_data["grand_amount"],
            created_by=user,
            created=datetime.now()
        )
        
        # if cart_data["ecash_applied"]:
        #     user_instance = User.objects.get(id=user.id)
        #     user_instance.used_reward_points += cart_data["wallet"]
        #     user_instance.current_reward_points = 0
        #     user_instance.save()

        # models_to_clear = [
        #     # EcashAddToCart,
        #     DiscountAddToCart,
        #     CourseAddToCart,
        #     LearningPathAddToCart,
        #     SkillAddToCart,
        #     SubscriptionPlanAddToCart,
        #     BlendedLearningPathAddToCart,
        #     JobEligibilitySkillAddToCart,
        # ]

        # for _ in models_to_clear:
        #     _.objects.filter(created_by=user).delete()

        order.save()

        return self.send_response(data={"uuid": order.uuid})


class MakePaymentForOrderAPIView(AppAPIView):
    """
    Make payment for the new order that created.
    """

    def get(self, request, *args, **kwargs):
        uuid = kwargs["uuid"]
        order = Order.objects.get_or_none(uuid=uuid)
        if order:
            if order.status == "success":
                return self.send_error_response(
                    data={"order": "PAYMENT_ALREADY_PROCESSED"}
                )
            order_data = order.get_razor_pay_order_id()
            order_data["razor_pay_key"] = settings.RAZORPAY_KEY_ID
            # models_to_clear = [
            #     # EcashAddToCart,
            #     DiscountAddToCart,
            #     CourseAddToCart,
            #     LearningPathAddToCart,
            #     SkillAddToCart,
            #     SubscriptionPlanAddToCart,
            #     BlendedLearningPathAddToCart,
            #     JobEligibilitySkillAddToCart,
            # ]

            # for _ in models_to_clear:
            #     _.objects.filter(created_by=order.created_by.id).delete()
            return self.send_response(data=order_data)
        

        return self.send_error_response(data={"order": "INVALID_UUID"})


class VerifyPaymentForOrderAPIView(AppAPIView):
    """Verify Payment for the order placed."""

    def post(self, request, *args, **kwargs):
        user = self.get_user()
        order_id = kwargs["uuid"]
        # print(order_id)
        order = Order.objects.get_or_none(uuid=order_id)
        if order:
            if order.status == "success":
                return self.send_error_response(
                    data={"order": "PAYMENT_ALREADY_VERIFIED"}
                )

            class Serializer(serializers.Serializer): 
                razorpay_payment_id = serializers.CharField(max_length=512)
                razorpay_order_id = serializers.CharField(max_length=512)
                razorpay_signature = serializers.CharField(max_length=512)

                class Meta:
                    fields = (
                        "razorpay_payment_id",
                        "razorpay_order_id",
                        "razorpay_signature",
                    )

            serializer = Serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            data = serializer.data

            try:
                order.verify_payment_completion(data)
                ecash_applied = EcashAddToCart.objects.get_or_none(created_by=user)
                if ecash_applied:
                    user_instance = User.objects.get(id=user.id)
                    user_instance.used_reward_points +=  order.cart_data["wallet"]
                    user_instance.current_reward_points -= order.cart_data["wallet"]
                    user_instance.save()
                    ecash_applied.delete()
                models_to_clear = [
                    # EcashAddToCart,
                    DiscountAddToCart,
                    CourseAddToCart,
                    LearningPathAddToCart,
                    SkillAddToCart,
                    SubscriptionPlanAddToCart,
                    BlendedLearningPathAddToCart,
                    JobEligibilitySkillAddToCart,
                ]

                for _ in models_to_clear:
                    _.objects.filter(created_by=order.created_by.id).delete()
                return self.send_response(
                    data={"payment": "PAYMENT_VERIFIED_SUCCESSFULLY"}
                )
            except IntegrityError as e:
                # Handle integrity error (e.g., duplicate key, foreign key constraint violation)
                print(f"IntegrityError occurred: {e}")
                # breakpoint()
            except Exception as e:
                # Handle other types of exceptions
                print(f"An unexpected error occurred: {e}")
                print(e)
                # breakpoint()
                return self.send_error_response(
                    data={"payment": "PAYMENT_VERIFICATION_FAILED"}
                )

        return self.send_error_response(data={"order": "INVALID_UUID"})
    
# Subscription Make Order
class MakeOrderForSubscriptionAPIView(AppAPIView):
    """
    This view helps to choose the subscription type along with the
    validity period based on the availability.
    """

    VALID_SUBSCRIPTION_VALIDITY = ["monthly", "yearly"]

    def post(self, request, *args, **kwargs):
        user = self.get_user()
        uuid = kwargs.get("uuid")
        today = datetime.now().date()
        subscription_plan = SubscriptionPlan.objects.get_or_none(uuid=uuid)
        subscription_plan_sale_discount = SubscriptionPlanSaleDiscount.objects.filter(subscription_plan=subscription_plan, start_date__lte=today, end_date__gte=today).first()

        if subscription_plan:
            plan_validity = request.data.get("plan")

            if plan_validity not in self.VALID_SUBSCRIPTION_VALIDITY:
                return self.send_error_response(
                    data={
                        "plan": f"Please choose valid plan {' or '.join(self.VALID_SUBSCRIPTION_VALIDITY)}"
                    }
                )

            is_validity_available = getattr(
                subscription_plan, f"is_{plan_validity}_subscription_plan_active"
            )
            if subscription_plan_sale_discount:
                is_discount_type = getattr(
                    subscription_plan_sale_discount, f"is_{plan_validity}_subscription_plan_offer"
                )

                is_discount_percentage = getattr(
                    subscription_plan_sale_discount, f"is_{plan_validity}_discount_percentage"
                )

                is_discount_amount = getattr(
                    subscription_plan_sale_discount, f"is_{plan_validity}_discount_amount"
                )

            if is_validity_available:
                price_in_inr = getattr(
                    subscription_plan, f"{plan_validity}_price_in_inr"
                )
                is_gst_inclusive = getattr(
                    subscription_plan, f"is_gst_inclusive_for_{plan_validity}"
                )

                if subscription_plan_sale_discount:
                    if is_discount_type:
                        if is_discount_percentage:
                            discount_percentage = getattr(
                                subscription_plan_sale_discount, f"{plan_validity}_discount_percentage"
                            )
                            discount_amount_inr = (price_in_inr*discount_percentage)/100

                        elif is_discount_amount:
                            discount_amount = getattr(
                                discount_amount = getattr(
                                    subscription_plan_sale_discount, f"{plan_validity}_discount_amount"
                                )
                            )
                            discount_amount_inr = discount_amount
                        else:
                            discount_amount_inr = 0
                    else:
                        discount_amount_inr = 0
                else:
                    discount_amount_inr = 0

            else:
                return self.send_error_response(
                    data={
                        "plan": f"{str(plan_validity).capitalize()} plan does not available for this subscription type."
                    }
                )


            cart_data = {
                "entities": [
                    {
                        "entity": {
                            "uuid": str(subscription_plan.uuid),
                            "identity": subscription_plan.identity,
                            "price_in_inr": price_in_inr,
                            "validity": plan_validity,
                            "is_gst_inclusive": is_gst_inclusive,
                            "type": subscription_plan.__class__.__name__,
                        }
                    }
                ],
                "coupon_applied": None,
                "total_amount": price_in_inr,
                "discount_amount": discount_amount_inr,
                "final_amount": price_in_inr - discount_amount_inr,
            }

            order = Order(
                cart_data=cart_data,
                discount_applied=None,
                total_price=cart_data["total_amount"],
                discount_price=cart_data["discount_amount"],
                total_price_after_discount=cart_data["final_amount"],
                created_by=user,
            )

            order.save()

            return self.send_response(data={"uuid": order.uuid})

        else:
            return self.send_error_response(data={"subscription": "INVALID_UUID"})


class StudentEnrollCourseAPIView(AppAPIView):
    def post(self, request, *args, **kwargs):
        user = self.get_user()
        course_id = kwargs.get("id")
        entity = Course.objects.get(id=course_id)
        tracker=StudentEnrolledCourseTracker.objects.create(entity=entity,created_by=user,valid_till=get_one_year_datetime_from_now())
        tracker.handle_user_enrolled()
        html_content=f'Hi, you have successfully enroll course {entity.identity}'
        success, message = send_welcome_email(user.idp_email, 'Successfull Enrolled', html_content)
        notification = Notification(user=user, course=entity, purpose="enrolled", message=f'Successfully enrolled in the course {entity.identity}')
        notification.save()
        if success:
            return self.send_response(data={'detail': message})
        else:
            return self.send_error_response(data={'detail': message})
    
class StudentEnrollLearningPathAPIView(AppAPIView):
    def post(self, request, *args, **kwargs):
        user = self.get_user()
        learning_path_id = kwargs.get("id")
        entity = LearningPath.objects.get(id=learning_path_id)
        tracker=StudentEnrolledLearningPathTracker.objects.create(entity=entity,created_by=user,valid_till=get_one_year_datetime_from_now())
        notification = Notification(user=user, learning_path=entity, purpose="enrolled", message=f'Successfully enrolled in the course {entity.identity}')
        notification.save()
        tracker.handle_user_enrolled()
        return self.send_response()
    
class StudentEnrollCertificatePathAPIView(AppAPIView):
    def post(self, request, *args, **kwargs):
        user = self.get_user()
        certificate_path_id = kwargs.get("id")
        entity = CertificationPath.objects.get(id=certificate_path_id)
        tracker=StudentEnrolledCertificatePathTracker.objects.create(entity=entity,created_by=user,valid_till=get_one_year_datetime_from_now())
        notification = Notification(user=user, certification_path=entity, purpose="enrolled", message=f'Successfully enrolled in the course {entity.identity}')
        notification.save()
        tracker.handle_user_enrolled()
        return self.send_response()
    

# Transation History
class TransactionHistoryListAPIView(ListAPIView, AppAPIView):

    filter_backends = [DjangoFilterBackend]
    pagination_class = AppPagination
    serializer_class = TransactionHistoryListSerializer

    def get_queryset(self, *args, **kwargs):
        return Order.objects.filter(created_by=self.get_user(), status="success").order_by('-created')
    
class DownloadInvoiceAPIView(AppAPIView):
    def get(self, request, *args, **kwargs):
        user=self.get_user()
        order = Order.objects.get_or_none(id=kwargs.get('id'))
        if order:
            template = get_template("invoice.html")
            sgst = order.total_price * 0.09
            cgst = order.total_price * 0.09
            igst = order.total_price * 0.18
            pincode_str = str(order.created_by.pincode)
            if pincode_str[:2] in ['56', '57', '58', '59']:
                pincode = "KA"
                total_price = igst + order.total_price
                total_price_in_words = number_to_words(int(total_price))
            else:
                pincode = "others"
                total_price = sgst + cgst + order.total_price
                total_price_in_words = number_to_words(int(total_price))
            # Formatting the invoice number
            invoice_number = "{:03d}/{:02d}/{:04d}-{:02d}".format(
                order.id, order.created.month, order.created.year, (order.created.year + 1) % 100
            )
            html = template.render({"user": user, "order": order, "sgst": sgst, "cgst": cgst, "igst": igst, "total_price_in_words":total_price_in_words, "pincode": pincode, "total_price": total_price, "invoice_number":invoice_number})
            # Create a PDF response
            response = HttpResponse(content_type="application/pdf")
            response["Content-Disposition"] = 'attachment; filename="invoice.pdf"'

            # Generate the PDF and attach it to the response
            pdf = pisa.CreatePDF(BytesIO(html.encode("UTF-8")), response, encoding="utf-8")
            
            if not pdf.err:
                return response
        return Response({"error": "Invoice not found or an error occurred."}, status=404)

# Free Courses Enroll API View
class FreeCourseEnrollAPIView(AppAPIView):
    def post(self, request, *args, **kwargs):
        user = self.get_user()
        course_id = kwargs.get("id")
        entity = Course.objects.get(id=course_id)
        tracker=UserCourseTracker.objects.create(entity=entity,created_by=user,valid_till=get_one_year_datetime_from_now())
        notification = Notification(user=user, course=entity, purpose="enrolled", message=f'Successfully enrolled in the course {entity.identity}')
        notification.save()
        tracker.handle_user_enrolled()
        return self.send_response()
