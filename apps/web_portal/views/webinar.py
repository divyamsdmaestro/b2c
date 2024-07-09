from django.shortcuts import render
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.generics import ListAPIView, RetrieveAPIView
from apps.common.pagination import AppPagination
from apps.common.serializers import get_app_read_only_serializer
from apps.common.views.api.base import AppAPIView, NonAuthenticatedAPIMixin
from apps.common.views.api.generic import (
    DEFAULT_IDENTITY_DISPLAY_FIELDS,
    AbstractLookUpFieldMixin,
)
from apps.web_portal.serializers.webinar import WebinarSerializer, \
    WebinarRegistrationSerializer, WebinarFilter

from apps.webinars.models import (Webinar, WebinarRegistration,WebinarDiscussion, WebinarDiscussionComment,WebinarDiscussionReply)

from apps.learning.models import Skill, Language
from django.conf import settings
from rest_framework import serializers
from ...common.serializers import get_app_read_only_serializer as read_serializer
from rest_framework.filters import SearchFilter
from datetime import datetime
from apps.access.models import User, InstitutionUserGroupDetail
from ...common.serializers import (
    AppWriteOnlyModelSerializer,
    AppReadOnlyModelSerializer
)
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter
from apps.cms.serializers import UserProfileSerializer
from django.contrib.auth.models import AnonymousUser
from apps.common.helpers import EmailNotification

today = datetime.now().date()

# Create your views here.
class WebinarListAPIView(NonAuthenticatedAPIMixin, ListAPIView, AppAPIView):
    """Sends out data for the Jobs Listing Page."""

    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_class = WebinarFilter
    search_fields = ["identity"]
    pagination_class = AppPagination
    serializer_class = WebinarSerializer
    queryset = Webinar.objects.filter(start_date__gte=today)


class WebinarDetailAPIView(
    NonAuthenticatedAPIMixin, AbstractLookUpFieldMixin, RetrieveAPIView, AppAPIView
):
    """Sends out data for the Jobs Detail Page."""

    serializer_class = WebinarSerializer
    queryset = Webinar.objects.all()


class WebinarFilterMetaAPIView(NonAuthenticatedAPIMixin, AppAPIView):
    """This API returns the metadata for Jobs filter in listing page."""

    def get(self, request, *args, **kwargs):
        filter_meta_data = {
            "skills": get_app_read_only_serializer(
                Skill, meta_fields=DEFAULT_IDENTITY_DISPLAY_FIELDS
            )(Skill.objects.filter(is_archived=False), many=True).data,
            "languages": get_app_read_only_serializer(
                Language, meta_fields=DEFAULT_IDENTITY_DISPLAY_FIELDS
            )(Language.objects.all(), many=True).data,
            "user_group": get_app_read_only_serializer(
                InstitutionUserGroupDetail, meta_fields=['id', 'uuid','identity'])
            (User.objects.all(), many=True).data,
        }

        return self.send_response(data=filter_meta_data)


class WebinarRegistrationAPIView(AppAPIView):
    """Register Webinar"""

    def post(self, request, *args, **kwargs):
        user = self.get_user()
        # print(self.request.data)
        web_reg = WebinarRegistration.objects.get_or_none(webinar_id=self.request.data.get("webinar_id"),created_by=user)
        if web_reg:
            if web_reg.status == "success":
                return self.send_response(data={"status": "Already Registered"})
            else:
                return self.send_response(data={"uuid": web_reg.uuid})
        else:
            if self.request.data.get("is_paid_webinar") == False:
                registration = WebinarRegistration(
                webinar_id=self.request.data.get("webinar_id"),
                payment_amount=self.request.data.get("payment_amount"),
                created_by=user, user=user, status="success"
            )
            #email verification
                EmailNotification(
                                email_to=registration.user.idp_email,
                                template_code='webinar_registration',
                                kwargs={
                                    "username": registration.user.full_name,
                                    "webinar_title": registration.webinar.identity,
                                    "webinar_link": registration.webinar.webinar_link,
                                    "start_date": registration.webinar.start_date,
                                    "end_date": registration.webinar.end_date,
                                }
                            )
            else:
               registration = WebinarRegistration(
                webinar_id=self.request.data.get("webinar_id"),
                payment_amount=self.request.data.get("payment_amount"),
                created_by=user, user=user
            )
            
            registration.save()
            return self.send_response(data={"uuid": registration.uuid})


class MakePaymentForWebinarAPIView(AppAPIView):
    """
    Make payment for the Webinar Registration that created.
    """

    def get(self, request, *args, **kwargs):
        uuid = kwargs["uuid"]
        registration = WebinarRegistration.objects.get_or_none(uuid=uuid)
        if registration:
            if registration.status == "success":
                return self.send_error_response(
                    data={"Registration": "PAYMENT_ALREADY_PROCESSED"}
                )

            order_data = registration.get_razor_pay_order_id()
            order_data["razor_pay_key"] = settings.RAZORPAY_KEY_ID
            return self.send_response(data=order_data)

        return self.send_error_response(data={"order": "INVALID_UUID"})


class VerifyPaymentForWebinarAPIView(AppAPIView):
    """Verify Payment for the Webinar Registration."""

    def post(self, request, *args, **kwargs):
        registration_id = kwargs["uuid"]
        registration = WebinarRegistration.objects.get_or_none(uuid=registration_id)
        if registration:
            if registration.status == "success":
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
                registration.verify_payment_completion_registration(data)
                #email verification
                EmailNotification(
                                email_to=registration.user.idp_email,
                                template_code='webinar_registration',
                                kwargs={
                                   "username": registration.user.full_name,
                                   "webinar_title": registration.webinar.identity,
                                   "webinar_link": registration.webinar.webinar_link,
                                   "start_date": registration.webinar.start_date,
                                   "end_date": registration.webinar.end_date,
                                }
                            )
                return self.send_response(
                    data={"payment": "PAYMENT_VERIFIED_SUCCESSFULLY"}
                )
            except:  # noqa
                return self.send_error_response(
                    data={"payment": "PAYMENT_VERIFICATION_FAILED"}
                )

        return self.send_error_response(data={"order": "INVALID_UUID"})


class MyWebinarListAPIView(AppAPIView):
    """View to list out entities in the user's wishlist trackers."""

    def get(self, request, *args, **kwargs):
        """Handle on get."""
        user = self.get_user()
        current_date = datetime.now()
        search_keyword = request.GET.get('search', '')
        total_registrations = WebinarRegistration.objects.filter(user=user,
                                                                 status='success',
                                                                 webinar__start_date__gte=
                                                                 current_date,
                                                                 webinar__identity__icontains=search_keyword) \
            .values(
            "registration_date",
            'webinar__identity',
            'webinar__uuid',
            "uuid",
            "status",
            'webinar__language__identity',
            'webinar__image__file',
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
            'webinar__status').distinct()
        total_attendees = WebinarRegistration.objects.filter(user=user,
                                                             webinar__start_date__lt=
                                                             current_date).values(
            "registration_date",
            'webinar__identity',
            'webinar__uuid',
            "status",
            "uuid",
            'webinar__language__identity',
            'webinar__image__file',
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
        ).distinct()
        return self.send_response({
            "total_registrations": total_registrations,
            "total_attendees": total_attendees,
        })


class WebinarRegistrationListAPIView(NonAuthenticatedAPIMixin, ListAPIView, AppAPIView):
    """Sends out data for the webinar Registered Listing Page."""

    filter_backends = [DjangoFilterBackend]
    filterset_fields = "__all__"
    pagination_class = AppPagination
    serializer_class = WebinarRegistrationSerializer
    queryset = WebinarRegistration.objects.all()

class WebinarDiscussionListAPIView(ListAPIView, AppAPIView):
    """Sends out data for the webinar discussion Listing Page."""

    class _Serializer(AppReadOnlyModelSerializer):
        """This serializer contains configuration for Blog."""
        webinar = get_app_read_only_serializer(Webinar, meta_fields=["id","uuid","identity"])(
            Webinar.objects.all()
        )
        comments_count = serializers.SerializerMethodField()
        is_my_discussion = serializers.SerializerMethodField()
        class Meta(AppReadOnlyModelSerializer.Meta):
            model = WebinarDiscussion
            fields = [
                "id",
                "uuid",
                "webinar",
                "title",
                "message",
                "comments_count",
                "created",
                "modified",
                "is_my_discussion"
            ]

        def get_comments_count(self, obj):
            return obj.get_comments_count()

        def get_is_my_discussion(self, obj):
            user = self.get_user()
            if isinstance(user, AnonymousUser) or user == None:
                return False
            else:
                return True if obj.created_by == user else False

    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = "__all__"
    search_fields = ["title"]
    pagination_class = AppPagination
    serializer_class = _Serializer

    def get_queryset(self, *args, **kwargs):
        return WebinarDiscussion.objects.filter(webinar__uuid=self.kwargs['uuid'])
    
class WebinarDiscussionCommentCreateAPIView(AppAPIView):
    """view used to create Webinar Discussion comment by user"""

    class _Serializer(AppWriteOnlyModelSerializer):
        """Handle input data."""

        class Meta(AppWriteOnlyModelSerializer.Meta):
            fields = [ "identity" ]
            model = WebinarDiscussionComment

    serializer_class = _Serializer

    def post(self, request, *args, **kwargs):
        webinar_discussion = WebinarDiscussion.objects.get(id=kwargs['discussion_id'])
        serializer = self.get_valid_serializer()
        serializer.is_valid(raise_exception=True)
        serializer.save(webinar_discussion=webinar_discussion)  # set webinar discussion here
        return self.send_response()

class WebinarDiscussionCommentEditAPIView(AppAPIView):
    """view used to Edit Webinar Discussion comment by user"""

    class _Serializer(AppWriteOnlyModelSerializer):
        """Handle input data."""

        class Meta(AppWriteOnlyModelSerializer.Meta):
            fields = [ "identity" ]
            model = WebinarDiscussionComment

    serializer_class = _Serializer

    def post(self, request, *args, **kwargs):
        webinar_discussion_comment = WebinarDiscussionComment.objects.get(id=kwargs['comment_id'])
        if webinar_discussion_comment.created_by == self.get_user():
            serializer = self.get_valid_serializer(instance=webinar_discussion_comment)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return self.send_response()
        return self.send_error_response()

class WebinarDiscussionCommentDeleteAPIView(AppAPIView):
    """View to delete the Webinar Discussion comments"""

    def delete(self, request, *args, **kwargs):
        user = self.get_user()
        webinar_discussion_comment = WebinarDiscussionComment.objects.get(id=kwargs['comment_id'])
        if webinar_discussion_comment.created_by == user:
            webinar_discussion_comment.replies.all().delete()
            webinar_discussion_comment.delete()
            return self.send_response()
        return self.send_error_response()

class WebinarDiscussionCommentListAPIView(ListAPIView, AppAPIView):
    """List down Webinar Discussion comments to the admin. This is a read only view."""

    class _Serializer(AppReadOnlyModelSerializer):
        """Handle input data."""
        replies_count = serializers.SerializerMethodField()
        created_by = UserProfileSerializer()
        is_my_comment = serializers.SerializerMethodField()

        class Meta(AppReadOnlyModelSerializer.Meta):
            fields = ["id","uuid","identity","modified","replies_count","created_by","is_my_comment" ]
            model = WebinarDiscussionComment

        def get_replies_count(self, obj):
            return obj.replies_count()
        
        def get_is_my_comment(self, obj):
            user = self.get_user()
            if isinstance(user, AnonymousUser) or user == None:
                return False
            else:
                return True if obj.created_by == user else False

    serializer_class = _Serializer

    def get_queryset(self):
        return WebinarDiscussionComment.objects.filter(webinar_discussion__id=self.kwargs['discussion_id'])
    
class WebinarDiscussionReplyCreateAPIView(AppAPIView):
    """view used to create Webinar Discussion reply by user"""

    class _Serializer(AppWriteOnlyModelSerializer):
        """Handle input data."""

        class Meta(AppWriteOnlyModelSerializer.Meta):
            fields = [ "identity" ]
            model = WebinarDiscussionReply

    serializer_class = _Serializer

    def post(self, request, *args, **kwargs):
        webinar_discussion_comment = WebinarDiscussionComment.objects.get(id=kwargs['comment_id'])
        serializer = self.get_valid_serializer()
        serializer.is_valid(raise_exception=True)
        comment_reply = serializer.save(comment=webinar_discussion_comment)
        webinar_discussion_comment.replies.add(comment_reply)
        webinar_discussion_comment.save()
        return self.send_response()

class WebinarDiscussionReplyEditAPIView(AppAPIView):
    """view used to Edit Webinar Discussion reply by user"""

    class _Serializer(AppWriteOnlyModelSerializer):
        """Handle input data."""

        class Meta(AppWriteOnlyModelSerializer.Meta):
            fields = [ "identity" ]
            model = WebinarDiscussionReply

    serializer_class = _Serializer

    def post(self, request, *args, **kwargs):
        webinar_discussion_reply = WebinarDiscussionReply.objects.get(id=kwargs['reply_id'])
        if webinar_discussion_reply.created_by == self.get_user():
            serializer = self.get_valid_serializer(instance=webinar_discussion_reply)
            serializer.is_valid(raise_exception=True)
            serializer.save()
        return self.send_response()

class WebinarDiscussionReplyDeleteAPIView(AppAPIView):
    """View to delete the Webinar Discussion replies"""

    def delete(self, request, *args, **kwargs):
        user = self.get_user()
        webinar_discussion_comment = WebinarDiscussionComment.objects.get(id=kwargs['comment_id'])
        reply = WebinarDiscussionReply.objects.get(id=kwargs['reply_id'])
        if reply.created_by == user:
            webinar_discussion_comment.replies.remove(reply)
            reply.delete()
            return self.send_response()
        return self.send_error_response()

class WebinarDiscussionReplyListAPIView(ListAPIView, AppAPIView):
    """List down forums Webinar Discussion comments reply to the admin. This is a read only view."""

    class _Serializer(AppReadOnlyModelSerializer):
        """Handle input data."""
        created_by = UserProfileSerializer()
        is_my_reply = serializers.SerializerMethodField()
        class Meta(AppReadOnlyModelSerializer.Meta):
            fields = ["id","uuid","identity","modified","created_by","is_my_reply" ]
            model = WebinarDiscussionReply

        def get_is_my_reply(self, obj):
            user = self.get_user()
            if isinstance(user, AnonymousUser) or user == None:
                return False
            else:
                return True if obj.created_by == user else False

    serializer_class = _Serializer

    def get_queryset(self):
        return WebinarDiscussionReply.objects.filter(comment_id=self.kwargs["comment_id"])
