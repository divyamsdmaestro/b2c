from django.db import models
from apps.common.models import (
    COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG,
    COMMON_CHAR_FIELD_MAX_LENGTH,
    BaseModel,
)
from apps.learning.models import CertificationPath, Course, LearningPath, BlendedLearningUserEnroll, JobEligibleSkill, LearningRole, BlendedLearningPath
from apps.learning.models.mml_course import MMLCourse
from apps.ecash.reward_points import trigger_reward_points
# from apps.badges.reward_badges import trigger_reward_badges

from apps.my_learnings.actions import (
    handle_user_enrolled_to_certification_path,
    handle_user_enrolled_to_course,
    handle_user_enrolled_to_learning_path,
    handle_user_enrolled_to_mml_course,
    # handle_user_enrolled_to_subscription_plan,
    handle_user_enrolled_to_hackathon,
    handle_user_enrolled_to_skill_learning_path,
    handle_user_enrolled_to_blended_learning_path,
    handle_user_enrolled_to_job_eligible_Skill
)
from apps.cms.celery import handle_user_enrolled_to_subscription_plan
from apps.payments.helpers import (
    get_razorpay_payment_order,
    verify_razorpay_payment_completion,
)
from apps.hackathons.models.hackathon import Hackathon
from .payments import Payment
from .subscription_plan import SubscriptionPlan
from apps.learning.models import Skill
from apps.my_learnings.models.trackers import UserCourseTracker
from apps.access.models import User
from apps.purchase.models.cart import EcashAddToCart

class Order(BaseModel):
    # Saving as JSON snapsentity_namehot as the data may change in future
    cart_data = models.JSONField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)

    discount_applied = models.ForeignKey(
        to="payments.Discount",
        on_delete=models.SET_NULL,
        **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG
    )

    payment = models.ForeignKey(
        to="payments.Payment",
        on_delete=models.SET_NULL,
        **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG
    )

    ORDER_STATUS_CHOICES = (
        ("on_process", "on_process"),
        ("success", "success"),
        ("failed", "failed"),
    )

    total_price = models.FloatField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    discount_price = models.FloatField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    total_price_after_discount = models.FloatField(
        **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG
    )

    status = models.CharField(
        choices=ORDER_STATUS_CHOICES,
        default="on_process",
        max_length=COMMON_CHAR_FIELD_MAX_LENGTH,
    )
    

    def get_razor_pay_order_id(self):
        razorpay_order_data = get_razorpay_payment_order(
            self.total_price_after_discount, "INR", str(self.uuid)
        )

        payment = Payment(
            razorpay_order_id=razorpay_order_data["id"],
            razorpay_order_data=razorpay_order_data,
        )
        payment.save()

        self.payment = payment
        self.save()

        return razorpay_order_data

    def verify_payment_completion(self, data):
        # print(self.created_by)
        if data["razorpay_order_id"] != self.payment.razorpay_order_id:
            raise Exception("Order ID does not match with the provided one.")

        verify_razorpay_payment_completion(**data)

        payment = self.payment

        payment.verification_signature = data
        payment.status = "success"
        payment.save()

        entities = self.cart_data["entities"]

        self.status = "success"
        self.save()
        
        type_actions = {
            "Course": handle_user_enrolled_to_course,
            "LearningPath": handle_user_enrolled_to_learning_path,
            "CertificationPath": handle_user_enrolled_to_certification_path,
            "MMLCourse": handle_user_enrolled_to_mml_course,
            "SubscriptionPlan": handle_user_enrolled_to_subscription_plan,
            "Hackathon": handle_user_enrolled_to_hackathon,
            "Skill": handle_user_enrolled_to_skill_learning_path,
            "BlendedLearningPath": handle_user_enrolled_to_blended_learning_path,
            "JobEligibleSkill" : handle_user_enrolled_to_job_eligible_Skill,
        }

        type_models = {
            "Course": Course,
            "LearningPath": LearningPath,
            "CertificationPath": CertificationPath,
            "MMLCourse": MMLCourse,
            "SubscriptionPlan": SubscriptionPlan,
            "Hackathon": Hackathon,
            "Skill": Skill,
            "BlendedLearningPath": BlendedLearningPath,
            "JobEligibleSkill": JobEligibleSkill
        }
        #add points on first purchase
        try:
            if data_type == "Course":
                user_courses_count = UserCourseTracker.objects.filter(created_by=self.created_by, entity__is_free=False).count()
                if user_courses_count ==  0:
                    #add reward points on first purchase
                    trigger_reward_points(self.created_by, action="purchased")
                    #add badge on first purchase
                    #  trigger_reward_badges(self.created_by,action="New Learner")
            else:
                pass
        except Exception as e:
            # Handle other exceptions if necessary
            print(f"An error occurred: {e}")
        for _ in entities:
            entity_name = _.get("entity")
            data_type = entity_name.get("type")
            uuid = entity_name.get("uuid")

            entity = type_models[data_type].objects.get(uuid=uuid)
            if data_type == "BlendedLearningPath":
                type_actions[data_type](self.created_by, entity, entity_name.get("blp_mode"), entity_name.get("session_details"))
            else:
                type_actions[data_type](self.created_by, entity)