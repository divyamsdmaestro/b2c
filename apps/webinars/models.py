from django.db import models

# Create your models here.
from django.db.models import JSONField
from apps.common import model_fields
from apps.common.models import BaseModel
from apps.learning.models.linkages import Skill
from apps.common.models import (
    COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG,
    COMMON_CHAR_FIELD_MAX_LENGTH,
    BaseModel,
    FileOnlyModel,
)
from apps.payments.models import Payment
from apps.access.models import InstitutionUserGroupDetail
from apps.payments.helpers import (
    get_razorpay_payment_order,
    verify_razorpay_payment_completion,
)
from django.db import IntegrityError
import datetime


class WebinarImage(FileOnlyModel):
    """Image data for a `Webinar`."""
    DYNAMIC_KEY = "webinar-image"
    file = model_fields.AppSingleFileField(
        upload_to="files/webinar/image/",
    )


class PaymentMode(BaseModel):
    """Holds the `Payment method` data for webinar."""

    DYNAMIC_KEY = "payment-mode"

    identity = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH, unique=True)
    description = models.TextField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)


class Webinar(BaseModel):
    DYNAMIC_KEY = "webinar"

    # WEBINAR_TYPES = (
    #     ('one_day', 'One Day'),
    #     ('multi_day', 'Multi Day'),
    # )
    STATUS_CHOICES = (
        ('published', 'Published'),
        ('pending_approval', 'Pending for Approval'),
        ('draft', 'Draft'),
        ('upcoming', 'Upcoming'),
    )

    identity = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH)
    language = models.ForeignKey(
        to="learning.Language",
        on_delete=models.SET_NULL,
        **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG,
    )

    image = models.ForeignKey(
        to=WebinarImage,
        on_delete=models.SET_NULL,
        **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG,
    )
    description = models.TextField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    webinar_link = models.URLField()
    participant_limit = models.PositiveIntegerField(
        **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    user_group = models.ManyToManyField(InstitutionUserGroupDetail, **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    skills = models.ManyToManyField(to="learning.Skill", blank=True)
    # webinar_type = models.CharField(max_length=20, choices=WEBINAR_TYPES)
    is_paid_webinar = models.BooleanField(default=False)
    webinar_fee = models.DecimalField(max_digits=10, decimal_places=2)
    payment_mode = models.ForeignKey(to=PaymentMode, on_delete=models.SET_NULL,
                                     **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG,
                                     )
    payment_mode_details = models.TextField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    start_date = models.DateField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    end_date = models.DateField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    session_detail = JSONField()
    status = models.CharField(max_length=20,
                              choices=STATUS_CHOICES, default="published")
    zone = models.ForeignKey(
        to="forums.Zone",
        on_delete=models.SET_NULL,
        **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG,
    )

    def __str__(self):
        return self.identity


class Participant(BaseModel):
    user = models.ForeignKey(
        to="access.User",
        on_delete=models.SET_NULL,
        **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG
    )

    def __str__(self):
        return self.user.name


class WebinarRegistration(BaseModel):
    DYNAMIC_KEY = "webinar-registration"

    REGISTRATION_STATUS_CHOICES = (
        ("on_process", "on_process"),
        ("success", "success"),
        ("failed", "failed"),
    )

    webinar = models.ForeignKey(Webinar, on_delete=models.CASCADE,
                                related_name='registrations')
    user = models.ForeignKey(
        to="access.User",
        on_delete=models.SET_NULL,
        **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG
    )
    registration_date = models.DateTimeField(auto_now_add=True)
    is_attended = models.BooleanField(default=False)
    payment = models.ForeignKey(
        to="payments.Payment",
        on_delete=models.SET_NULL,
        **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG
    )
    payment_amount = models.FloatField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)

    status = models.CharField(
        choices=REGISTRATION_STATUS_CHOICES,
        default="on_process",
        max_length=COMMON_CHAR_FIELD_MAX_LENGTH,
    )

    def __str__(self):
        return f"Registration for {self.webinar.identity}"

    def save(self, *args, **kwargs):
        # Check if the user has already registered for the webinar
        if self.pk is None and self.user is not None and self.webinar is not None:
            if WebinarRegistration.objects.filter(webinar=self.webinar,
                                                  user=self.user).exists():
                raise Exception("User has already registered for this webinar.")
        super().save(*args, **kwargs)

    def total_registrations(self, user):
        queryset = WebinarRegistration.objects.filter(user=user,
                                                      status='success').select_related(
            'webinar').distinct()
        registrations = queryset.values(
            "registration_date",
            'webinar__identity',
            'webinar__uuid',
            "uuid",
            "status",
            'webinar__language__identity',
            'webinar__image',
            'webinar__description',
            'webinar__webinar_link',
            'webinar__participant_limit',
            'webinar__skills__identity',
            'webinar__is_paid_webinar',
            'webinar__webinar_fee',
            'webinar__payment_mode_details',
            'webinar__start_date',
            'webinar__end_date',
            'webinar__session_detail',
            'webinar__status'
        )
        return registrations

    def total_attendees(self, user):
        current_date = datetime.datetime.now()

        return WebinarRegistration.objects.filter(
            user=user,
            is_attended=True,
            webinar__start_date__gt=current_date
        ).values(
            "registration_date",
            'webinar__identity',
            'webinar__uuid',
            "status",
            "uuid",
            'webinar__language__identity',
            'webinar__image',
            'webinar__description',
            'webinar__webinar_link',
            'webinar__participant_limit',
            'webinar__skills__identity',
            'webinar__is_paid_webinar',
            'webinar__webinar_fee',
            'webinar__payment_mode_details',
            'webinar__start_date',
            'webinar__end_date',
            'webinar__session_detail',
            'webinar__status'
        )

    def get_razor_pay_order_id(self):
        razorpay_order_data = get_razorpay_payment_order(
            self.payment_amount, "INR", str(self.uuid)
        )

        payment = Payment(
            razorpay_order_id=razorpay_order_data["id"],
            razorpay_order_data=razorpay_order_data,
        )
        payment.save()
        self.payment = payment
        self.save()

        return razorpay_order_data

    def verify_payment_completion_registration(self, data):
        if data["razorpay_order_id"] != self.payment.razorpay_order_id:
            raise Exception("Order ID does not match with the provided one.")

        verify_razorpay_payment_completion(**data)

        payment = self.payment

        payment.verification_signature = data
        payment.status = "success"
        payment.save()

        self.status = "success"
        self.save()

class WebinarDiscussion(BaseModel):
    """
    This model holds information about the Webinar discussion details.
    """

    DYNAMIC_KEY = "webinar-discussion"

    webinar = models.ForeignKey(Webinar,
        on_delete=models.SET_NULL,
        **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG,)
    title = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH)
    message = models.TextField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)

    def get_comments_count(self):
        comments = WebinarDiscussionComment.objects.filter(webinar_discussion=self)
        return comments.count()

class WebinarDiscussionReply(BaseModel):
    """Holds the Webinar Discussion comments replies data."""

    DYNAMIC_KEY = "webinar-discussion-reply"

    comment = models.ForeignKey(
        to = "webinars.WebinarDiscussionComment",
        on_delete=models.SET_NULL,
        **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG
    )
    identity = models.TextField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)


class WebinarDiscussionComment(BaseModel):
    """Holds the Webinar Discussion comments data."""

    DYNAMIC_KEY = "webinar-discussion-comment"
     
    webinar_discussion = models.ForeignKey(
        to="webinars.WebinarDiscussion",
        related_name="comments",
        on_delete=models.SET_NULL,
        **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG
    )
    identity = models.TextField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    replies = models.ManyToManyField(to="webinars.WebinarDiscussionReply", blank=True)

    def replies_count(self):
        return self.replies.all().count()