from rest_framework import permissions
from apps.common.helpers import EmailNotification
from apps.common.serializers import (
    AppWriteOnlyModelSerializer,
    get_app_read_only_serializer,
)
from rest_framework import serializers
from apps.common.views.api import AppModelCUDAPIViewSet, AppModelListAPIViewSet
from apps.cms.serializers import HackathonPrizeDetailsSerializer, HackathonRoundDetailsSerializer, RolePermissionDetailSerializer
from apps.hackathons.models import hackathon as hackathon_models
from apps.access.models import UserRole, User, InstitutionUserGroupDetail, InstitutionDetail, InstitutionUserGroupContent, EmployerDetail
from apps.hackathons.models import hackathon as hackathon_models
from apps.cms.serializers import PollOptionsHandleSerializer, ForumCreateSerializer, ScheduleDetailsCreateSerializer
from apps.forums.models import Post, PostPollOption, PostReply, Zone, Forum, ZoneJoin
from apps.learning.models import BlendedLearningPathPriceDetails, BlendedLearningPathScheduleDetails

from apps.jobs.models import Job, JobAppliedList, JobInterviewSchedule, JobFeedbackTemplate
from apps.jobs.models.job import JobFeedbackOption
from apps.jobs.serializers import JobCriteriaSerializer, JobRoundDetailSerializer, JobFeedbackQuestionSerializer
from apps.blogs.models import BlogCommentReply
from apps.webinars.models import Webinar, WebinarDiscussionReply, WebinarRegistration
from config import settings

class AllowedToAccessAdminCMSMixin:
    """Checks if the user is allowed to access the Admin CMS."""

    # TODO: handle the permissions later
    permission_classes = [permissions.IsAuthenticated]


def get_model_cud_api_viewset(
    meta_fields,
    meta_model=None,
    meta_queryset=None,
    meta_extra_kwargs={},  # noqa
    get_serializer_meta=lambda self: {},
    parent_view=AllowedToAccessAdminCMSMixin,
):
    """
    Returns a dynamic instance of `AppModelCUDAPIViewSet` for the Admin CMS.
    This can also be used in other places based on use cases.
    """

    # either one must be present
    assert meta_model or meta_queryset

    # qs
    if not meta_queryset:
        meta_queryset = meta_model.objects.all()

    # model
    if not meta_model:
        meta_model = meta_queryset.model
   
    class _ViewSet(parent_view, AppModelCUDAPIViewSet):
        """CUD Viewset."""

        class _Serializer(AppWriteOnlyModelSerializer):
            """Write Serializer"""
            if meta_model is hackathon_models.Hackathon:
                prizes_details = HackathonPrizeDetailsSerializer(many=True)
                round_details = HackathonRoundDetailsSerializer(many=True)

            if meta_model is Job:
                # eligibility_criteria = JobCriteriaSerializer(many=True)
                job_round_details = JobRoundDetailSerializer(many=True)

            if meta_model is UserRole:
                role_permissions = RolePermissionDetailSerializer(many=True)

            if meta_model is Post:
                poll_options = PollOptionsHandleSerializer(many=True)
            
            if meta_model is JobFeedbackTemplate:
                feedback_question = JobFeedbackQuestionSerializer(many=True)

            if meta_model is Zone:
                forums = ForumCreateSerializer(many=True)
                
            if meta_model is BlendedLearningPathPriceDetails:
                schedule_details = ScheduleDetailsCreateSerializer(many=True)

            class Meta(AppWriteOnlyModelSerializer.Meta):
                model = meta_model
                fields = meta_fields
                extra_kwargs = meta_extra_kwargs

            if meta_model is InstitutionUserGroupDetail:
                get_serializer_meta=lambda x: {
                    "user": x.serialize_for_meta(User.objects.all()),
                },
            
            def get_meta(self) -> dict:
                return get_serializer_meta(self)
            
            if meta_model is Webinar:
                def create(self, validated_data):
                    instance = super().create(validated_data)

                    user_group_ids = instance.user_group.all().values_list('id', flat=True)
                    user_groups = InstitutionUserGroupDetail.objects.filter(id__in=user_group_ids)
                    users = User.objects.filter(institutionusergroupdetail__in=user_groups).distinct()
                    enrolled_user_ids = WebinarRegistration.objects.filter(webinar=instance).values_list('user', flat=True)
                    users_to_enroll = users.exclude(id__in=enrolled_user_ids)
                    participants_to_create = [WebinarRegistration(user=user, webinar=instance, status="success") for user in users_to_enroll]
                    WebinarRegistration.objects.bulk_create(participants_to_create)

                    return instance
                
                def update(self, instance, validated_data):
                    instance = super().update(instance, validated_data)

                    user_group_ids = instance.user_group.all().values_list('id', flat=True)
                    user_groups = InstitutionUserGroupDetail.objects.filter(id__in=user_group_ids)
                    users = User.objects.filter(institutionusergroupdetail__in=user_groups).distinct()
                    enrolled_user_ids = WebinarRegistration.objects.filter(webinar=instance).values_list('user', flat=True)
                    users_to_enroll = users.exclude(id__in=enrolled_user_ids)
                    participants_to_create = [WebinarRegistration(user=user, webinar=instance, status="success") for user in users_to_enroll]
                    WebinarRegistration.objects.bulk_create(participants_to_create)

                    return instance
            
            if meta_model is hackathon_models.Hackathon:
                def create(self, validated_data):
                    prizes_data = validated_data.pop('prizes_details', [])
                    rounds_data = validated_data.pop('round_details', [])
                    instance = super().create(validated_data)
                    
                    for prize_data in prizes_data:
                        instance.prizes_details.create(**prize_data)

                    for round_data in rounds_data:
                        instance.round_details.create(**round_data)
                    
                    user_group_ids = instance.user_group.all().values_list('id', flat=True)
                    user_groups = InstitutionUserGroupDetail.objects.filter(id__in=user_group_ids)
                    users = User.objects.filter(institutionusergroupdetail__in=user_groups).distinct()
                    enrolled_user_ids = hackathon_models.HackathonParticipant.objects.filter(entity=instance).values_list('created_by', flat=True)
                    users_to_enroll = users.exclude(id__in=enrolled_user_ids)
                    participants_to_create = [hackathon_models.HackathonParticipant(created_by=user, entity=instance) for user in users_to_enroll]
                    hackathon_models.HackathonParticipant.objects.bulk_create(participants_to_create)
    
                    return instance

                def update(self, instance, validated_data):
                    prizes_data = validated_data.pop('prizes_details', [])
                    rounds_data = validated_data.pop('round_details', [])
                    instance = super().update(instance, validated_data)
                    
                    instance.prizes_details.all().delete()
                    instance.round_details.all().delete()

                    for prize_data in prizes_data:
                        instance.prizes_details.create(**prize_data)

                    for round_data in rounds_data:
                        instance.round_details.create(**round_data)
                    
                    user_group_ids = instance.user_group.all().values_list('id', flat=True)
                    user_groups = InstitutionUserGroupDetail.objects.filter(id__in=user_group_ids)
                    users = User.objects.filter(institutionusergroupdetail__in=user_groups).distinct()
                    enrolled_user_ids = hackathon_models.HackathonParticipant.objects.filter(entity=instance).values_list('created_by', flat=True)
                    users_to_enroll = users.exclude(id__in=enrolled_user_ids)
                    participants_to_create = [hackathon_models.HackathonParticipant(created_by=user, entity=instance) for user in users_to_enroll]
                    hackathon_models.HackathonParticipant.objects.bulk_create(participants_to_create)

                    return instance
                
            if meta_model is Job:
                def create(self, validated_data):
                    # eligibility_criteria = validated_data.pop('eligibility_criteria', [])
                    job_round_details = validated_data.pop('job_round_details', [])
                    instance = super().create(validated_data)
                    
                    # for eligibility_criteria in eligibility_criteria:
                    #     instance.eligibility_criteria.create(**eligibility_criteria)

                    for job_round_details in job_round_details:
                        instance.job_round_details.create(**job_round_details)

                    rep = self.get_user()
                    data = EmployerDetail.objects.get_or_none(representative=rep)
                    instance.company = data
                    instance.save()

                    return instance

                def update(self, instance, validated_data):
                    # eligibility_criteria = validated_data.pop('eligibility_criteria', [])
                    job_round_details = validated_data.pop('job_round_details', [])
                    instance = super().update(instance, validated_data)
                    
                    # instance.eligibility_criteria.all().delete()
                    instance.job_round_details.all().delete()

                    # for eligibility_criteria in eligibility_criteria:
                    #     instance.eligibility_criteria.create(**eligibility_criteria)

                    for job_round_details in job_round_details:
                        instance.job_round_details.create(**job_round_details)

                    rep = self.get_user()
                    data = EmployerDetail.objects.get_or_none(representative=rep)
                    instance.company = data
                    instance.save()

                    return instance
                
            if meta_model is UserRole:
                def create(self, validated_data):
                    role_permissions = validated_data.pop('role_permissions', [])
                    instance = super().create(validated_data)
                   
                    for role_permissions in role_permissions:
                        instance.role_permissions.create(**role_permissions)

                    return instance
                
                def update(self, instance, validated_data):
                    role_permissions = validated_data.pop('role_permissions', [])
                    instance = super().update(instance, validated_data)
                    
                    instance.role_permissions.all().delete()

                    for role_permissions in role_permissions:
                        instance.role_permissions.create(**role_permissions)

                    return instance

            if meta_model is Post:
                def create(self, validated_data):
                    poll_options = validated_data.pop('poll_options', [])
                    instance = super().create(validated_data)
                    for poll_option in poll_options:
                        instance.poll_options.create(**poll_option)
                    return instance

                def update(self, instance, validated_data):
                    poll_options_data = validated_data.pop('poll_options', [])
                    instance = super().update(instance, validated_data)
                    # M2M fields
                    if poll_options_data:
                        instance.poll_options.clear()
                        for data in poll_options_data:
                            poll_options = PostPollOption.objects.filter(**data)
                            if poll_options.exists():
                                poll_option = poll_options.first()
                            else:
                                poll_option = PostPollOption.objects.create(**data)
                            instance.poll_options.add(poll_option)

                    return instance

            if meta_model is PostReply or meta_model is hackathon_models.HackathonDiscussionReply or meta_model is BlogCommentReply or meta_model is WebinarDiscussionReply:
                def create(self, validated_data):
                    instance = super().create(validated_data)
                    instance.comment.replies.add(instance)

                    return instance
                
            if meta_model is JobFeedbackTemplate:
                def create(self, validated_data):
                    feedback_question = validated_data.pop('feedback_question', [])
                    instance = super().create(validated_data)
                   
                    for feedback_question in feedback_question:
                        instance.feedback_question.create(**feedback_question)

                    return instance
                
                def update(self, instance, validated_data):
                    feedback_question = validated_data.pop('feedback_question', [])
                    instance = super().update(instance, validated_data)
                    
                    instance.feedback_question.all().delete()

                    for feedback_question in feedback_question:
                        instance.feedback_question.create(**feedback_question)

                    return instance
                
            if meta_model is JobInterviewSchedule:
                def create(self, validated_data):
                    instance = super().create(validated_data)
                    job = JobAppliedList.objects.filter(created_by=validated_data.pop("applicant"), job=validated_data.pop('job')).first()
 
                    if job:
                        job.status = "interview_scheduled"
                        job.save()

                        EmailNotification(
                            email_to=instance.applicant.idp_email,
                            template_code='interview_scheduled_learner',
                            kwargs={
                                "job_title": instance.job.job_role,  
                                "interview_round": instance.job_round.title,
                                'schedule_date': instance.schedule_date,
                                'start_time': instance.start_time,
                                'end_time': instance.end_time,
                                'interview_link': instance.interview_link
                            }
                        )
                        EmailNotification(
                            email_to=instance.interview_panel.idp_email,  
                            template_code="interview_scheduled_interviewer",
                            kwargs={
                                "applicant": instance.applicant.full_name,  
                                "job_title": instance.job.job_role,
                                "interview_round": instance.job_round.title,
                                'schedule_date': instance.schedule_date,
                                'start_time': instance.start_time,
                                'end_time': instance.end_time,
                                'interview_link': instance.interview_link,
                                'interview_feedback_template': f"{settings.FRONTEND_CMS_URL}interview-panel/scheduled-interview-applicant/detail/{instance.id}"
                            }
                        )
        
                    return instance


            if meta_model is Zone:
                def create(self, validated_data):
                    forums = validated_data.pop('forums', [])
                    instance = super().create(validated_data)
                    # for user in instance.assign_members.all():
                    #     ZoneJoin.objects.create(zone=instance,created_by=user)
                    for forum in forums:
                        instance.forums.create(**forum)
                    return instance

                def update(self, instance, validated_data):
                    forums_data = validated_data.pop('forums', [])
                    instance = super().update(instance, validated_data)
                    # M2M fields
                    if forums_data:
                        instance.forums.clear()
                        for data in forums_data:
                            forums = Forum.objects.filter(**data)
                            if forums.exists():
                                forum = forums.first()
                            else:
                                forum = Forum.objects.create(**data)
                            instance.forums.add(forum)

                    return instance
                
            if meta_model is BlendedLearningPathPriceDetails:
                def create(self, validated_data):
                    schedule_details = validated_data.pop('schedule_details', [])
                    instance = super().create(validated_data)
                    for schedule_detail in schedule_details:
                        instance.schedule_details.create(**schedule_detail)
                    return instance

                def update(self, instance, validated_data):
                    schedule_data = validated_data.pop('schedule_details', [])
                    instance = super().update(instance, validated_data)
                    # M2M fields
                    if schedule_data:
                        instance.schedule_details.clear()
                        for data in schedule_data:
                            schedule_details = BlendedLearningPathScheduleDetails.objects.filter(**data)
                            if schedule_details.exists():
                                schedule_detail = schedule_details.first()
                            else:
                                schedule_detail = BlendedLearningPathScheduleDetails.objects.create(**data)
                            instance.schedule_details.add(schedule_detail)

                    return instance

        queryset = meta_queryset
        serializer_class = _Serializer

    return _ViewSet


def get_model_list_api_viewset(
    
    meta_queryset,
    meta_all_table_columns: dict,
    meta_init_fields_config={},  # noqa
    parent_view=AllowedToAccessAdminCMSMixin,
    fields_to_filter=None,
    # meta_model = None,
):
    """
    Returns a dynamic `AppModelListAPIViewSet` for the Admin CMS.
    This can also be used in other places based on use cases.
    """
    fields_to_filter = fields_to_filter if fields_to_filter is not None else []

    class _ListAPIViewSet(parent_view, AppModelListAPIViewSet):
        """List ViewSet"""

        queryset = meta_queryset
        filterset_fields = [*fields_to_filter]
        search_fields = [
            "id",
            *meta_all_table_columns.keys(),
        ]
        all_table_columns = {
            # "id": "ID",
            "serial_number": "S.No",
            **meta_all_table_columns,
        }

        def get_serializer_class(self):
            """Read Serializer."""

            return get_app_read_only_serializer(
                meta_model=meta_queryset.model,
                meta_fields=["id", *meta_all_table_columns.keys()],
                init_fields_config={**meta_init_fields_config},
            )
    return _ListAPIViewSet

def get_student_list_api_viewset(
    
    meta_queryset,
    meta_all_table_columns: dict,
    meta_init_fields_config={},  # noqa
    parent_view=AllowedToAccessAdminCMSMixin,
    fields_to_filter=None,
    # meta_model = None,
):
    """
    Returns a dynamic `AppModelListAPIViewSet` for the Admin CMS.
    This can also be used in other places based on use cases.
    """
    fields_to_filter = fields_to_filter if fields_to_filter is not None else []

    class _ListAPIViewSet(parent_view, AppModelListAPIViewSet):
        """List ViewSet"""

        queryset = meta_queryset
        filterset_fields = [*fields_to_filter]
        search_fields = [
            "id",
            *meta_all_table_columns.keys(),
        ]
        all_table_columns = {
            # "id": "ID",
            "serial_number": "S.No",
            **meta_all_table_columns,
        }

        def get_queryset(self):
            user=self.get_user()
            if user.user_role.identity == 'Staff':
                return User.objects.filter(created_by=user.created_by, user_role__identity="Student")
            else:
                return User.objects.filter(created_by=self.get_user(), user_role__identity="Student")
    
        def get_serializer_class(self):
            """Read Serializer."""

            return get_app_read_only_serializer(
                meta_model=meta_queryset.model,
                meta_fields=["id", *meta_all_table_columns.keys()],
                init_fields_config={**meta_init_fields_config},
                queryset=self.get_queryset()
            )
    return _ListAPIViewSet

def get_interview_panel_list_api_viewset(
    meta_queryset,
    meta_all_table_columns: dict,
    meta_init_fields_config={},  # noqa
    parent_view=AllowedToAccessAdminCMSMixin,
    fields_to_filter=None,
    # meta_model = None,
):
    """
    Returns a dynamic `AppModelListAPIViewSet` for the Admin CMS.
    This can also be used in other places based on use cases.
    """
    fields_to_filter = fields_to_filter if fields_to_filter is not None else []

    class _ListAPIViewSet(parent_view, AppModelListAPIViewSet):
        """List ViewSet"""

        queryset = meta_queryset
        filterset_fields = [*fields_to_filter]
        search_fields = [
            "id",
            *meta_all_table_columns.keys(),
        ]
        all_table_columns = {
            # "id": "ID",
            "serial_number": "S.No",
            **meta_all_table_columns,
        }

        def get_queryset(self):
            corporate = EmployerDetail.objects.get(representative=self.get_user())
            return User.objects.filter(corporate=corporate,user_role__identity__icontains="Interview Panel Member")
    
        def get_serializer_class(self):
            """Read Serializer."""

            return get_app_read_only_serializer(
                meta_model=meta_queryset.model,
                meta_fields=["id", *meta_all_table_columns.keys()],
                init_fields_config={**meta_init_fields_config},
                queryset=self.get_queryset()
            )
    return _ListAPIViewSet

def get_interview_schedule_list_api_viewset(
    meta_queryset,
    meta_all_table_columns: dict,
    meta_init_fields_config={},  # noqa
    parent_view=AllowedToAccessAdminCMSMixin,
    fields_to_filter=None,
    # meta_model = None,
):
    """
    Returns a dynamic `AppModelListAPIViewSet` for the Admin CMS.
    This can also be used in other places based on use cases.
    """
    fields_to_filter = fields_to_filter if fields_to_filter is not None else []

    class _ListAPIViewSet(parent_view, AppModelListAPIViewSet):
        """List ViewSet"""

        queryset = meta_queryset
        filterset_fields = [*fields_to_filter]
        search_fields = [
            "id",
            *meta_all_table_columns.keys(),
        ]
        all_table_columns = {
            # "id": "ID",
            "serial_number": "S.No",
            **meta_all_table_columns,
        }

        def get_queryset(self):
            return JobInterviewSchedule.objects.filter(created_by=self.get_user())
    
        def get_serializer_class(self):
            """Read Serializer."""

            return get_app_read_only_serializer(
                meta_model=meta_queryset.model,
                meta_fields=["id", *meta_all_table_columns.keys()],
                init_fields_config={**meta_init_fields_config},
                queryset=self.get_queryset()
            )
    return _ListAPIViewSet

def get_interview_schedule_interview_panel_list_api_viewset(
    meta_queryset,
    meta_all_table_columns: dict,
    meta_init_fields_config={},  # noqa
    parent_view=AllowedToAccessAdminCMSMixin,
    fields_to_filter=None,
    # meta_model = None,
):
    """
    Returns a dynamic `AppModelListAPIViewSet` for the Admin CMS.
    This can also be used in other places based on use cases.
    """
    fields_to_filter = fields_to_filter if fields_to_filter is not None else []

    class _ListAPIViewSet(parent_view, AppModelListAPIViewSet):
        """List ViewSet"""

        queryset = meta_queryset
        filterset_fields = [*fields_to_filter]
        search_fields = [
            "id",
            *meta_all_table_columns.keys(),
        ]
        all_table_columns = {
            # "id": "ID",
            "serial_number": "S.No",
            **meta_all_table_columns,
        }

        def get_queryset(self):
            return JobInterviewSchedule.objects.filter(interview_panel=self.get_user())
    
        def get_serializer_class(self):
            """Read Serializer."""

            return get_app_read_only_serializer(
                meta_model=meta_queryset.model,
                meta_fields=["id", *meta_all_table_columns.keys()],
                init_fields_config={**meta_init_fields_config},
                queryset=self.get_queryset()
            )
    return _ListAPIViewSet

def get_schedule_list_for_interview_panel_api_viewset(
    meta_queryset,
    meta_all_table_columns: dict,
    meta_init_fields_config={},  # noqa
    parent_view=AllowedToAccessAdminCMSMixin,
    fields_to_filter=None,
    # meta_model = None,
):
    """
    Returns a dynamic `AppModelListAPIViewSet` for the Admin CMS.
    This can also be used in other places based on use cases.
    """
    fields_to_filter = fields_to_filter if fields_to_filter is not None else []

    class _ListAPIViewSet(parent_view, AppModelListAPIViewSet):
        """List ViewSet"""

        queryset = meta_queryset
        filterset_fields = [*fields_to_filter]
        search_fields = [
            "id",
            *meta_all_table_columns.keys(),
        ]
        all_table_columns = {
            # "id": "ID",
            "serial_number": "S.No",
            **meta_all_table_columns,
        }

        def get_queryset(self):
            return JobInterviewSchedule.objects.filter(interview_panel=self.get_user())
    
        def get_serializer_class(self):
            """Read Serializer."""

            return get_app_read_only_serializer(
                meta_model=meta_queryset.model,
                meta_fields=["id", *meta_all_table_columns.keys()],
                init_fields_config={**meta_init_fields_config},
                queryset=self.get_queryset()
            )
    return _ListAPIViewSet

def get_staff_list_api_viewset(
    
    meta_queryset,
    meta_all_table_columns: dict,
    meta_init_fields_config={},  # noqa
    parent_view=AllowedToAccessAdminCMSMixin,
    fields_to_filter=None,
    # meta_model = None,
):
    """
    Returns a dynamic `AppModelListAPIViewSet` for the Admin CMS.
    This can also be used in other places based on use cases.
    """
    fields_to_filter = fields_to_filter if fields_to_filter is not None else []

    class _ListAPIViewSet(parent_view, AppModelListAPIViewSet):
        """List ViewSet"""

        queryset = meta_queryset
        filterset_fields = [*fields_to_filter]
        search_fields = [
            "id",
            *meta_all_table_columns.keys(),
        ]
        all_table_columns = {
            # "id": "ID",
            "serial_number": "S.No",
            **meta_all_table_columns,
        }

        def get_queryset(self):
            
            return User.objects.filter(created_by=self.get_user(),user_role__identity="Staff")
    
        def get_serializer_class(self):
            """Read Serializer."""

            return get_app_read_only_serializer(
                meta_model=meta_queryset.model,
                meta_fields=["id", *meta_all_table_columns.keys()],
                init_fields_config={**meta_init_fields_config},
                queryset=self.get_queryset()
            )
    return _ListAPIViewSet

def get_institution_user_group_list_api_viewset(
    
    meta_queryset,
    meta_all_table_columns: dict,
    meta_init_fields_config={},  # noqa
    parent_view=AllowedToAccessAdminCMSMixin,
    fields_to_filter=None,
    # meta_model = None,
):
    """
    Returns a dynamic `AppModelListAPIViewSet` for the Admin CMS.
    This can also be used in other places based on use cases.
    """
    fields_to_filter = fields_to_filter if fields_to_filter is not None else []

    class _ListAPIViewSet(parent_view, AppModelListAPIViewSet):
        """List ViewSet"""

        queryset = meta_queryset
        filterset_fields = [*fields_to_filter]
        search_fields = [
            "id",
            *meta_all_table_columns.keys(),
        ]
        all_table_columns = {
            # "id": "ID",
            "serial_number": "S.No",
            **meta_all_table_columns,
        }

        def get_queryset(self):
            user = self.get_user()
            if user.user_role.identity == "Staff":
                institution = InstitutionDetail.objects.get_or_none(representative=user.created_by)
            else:
                institution = InstitutionDetail.objects.get_or_none(representative=user)
            if institution:
                return InstitutionUserGroupDetail.objects.filter(institution=institution)
            else:
                return InstitutionUserGroupDetail.objects.none()

    
        def get_serializer_class(self):
            """Read Serializer."""

            return get_app_read_only_serializer(
                meta_model=meta_queryset.model,
                meta_fields=["id", *meta_all_table_columns.keys()],
                init_fields_config={**meta_init_fields_config},
                queryset=self.get_queryset()
            )
    return _ListAPIViewSet

def get_institution_user_group_content_list_api_viewset(
    
    meta_queryset,
    meta_all_table_columns: dict,
    meta_init_fields_config={},  # noqa
    parent_view=AllowedToAccessAdminCMSMixin,
    fields_to_filter=None,
    # meta_model = None,
):
    """
    Returns a dynamic `AppModelListAPIViewSet` for the Admin CMS.
    This can also be used in other places based on use cases.
    """
    fields_to_filter = fields_to_filter if fields_to_filter is not None else []

    class _ListAPIViewSet(parent_view, AppModelListAPIViewSet):
        """List ViewSet"""

        queryset = meta_queryset
        filterset_fields = [*fields_to_filter]
        search_fields = [
            "id",
            *meta_all_table_columns.keys(),
        ]
        all_table_columns = {
            # "id": "ID",
            "serial_number": "S.No",
            **meta_all_table_columns,
        }

        def get_queryset(self):
            user = self.get_user()
            if user.user_role.identity == "Staff":
                institution = InstitutionDetail.objects.get_or_none(representative=user.created_by)
            else:
                institution = InstitutionDetail.objects.get_or_none(representative=user)
            if institution:
                user_group = InstitutionUserGroupDetail.objects.filter(institution=institution)
            else:
                user_group = InstitutionUserGroupDetail.objects.none()
            return InstitutionUserGroupContent.objects.filter(user_group__in=user_group).distinct()
    
        def get_serializer_class(self):
            """Read Serializer."""

            return get_app_read_only_serializer(
                meta_model=meta_queryset.model,
                meta_fields=["id", *meta_all_table_columns.keys()],
                init_fields_config={**meta_init_fields_config},
                queryset=self.get_queryset()
            )
    return _ListAPIViewSet

def get_employer_job_list_api_viewset(
    
    meta_queryset,
    meta_all_table_columns: dict,
    meta_init_fields_config={},  # noqa
    parent_view=AllowedToAccessAdminCMSMixin,
    fields_to_filter=None,
    # meta_model = None,
):
    """
    Returns a dynamic `AppModelListAPIViewSet` for the Admin CMS.
    This can also be used in other places based on use cases.
    """
    fields_to_filter = fields_to_filter if fields_to_filter is not None else []

    class _ListAPIViewSet(parent_view, AppModelListAPIViewSet):
        """List ViewSet"""

        queryset = meta_queryset
        filterset_fields = [*fields_to_filter]
        search_fields = [
            "id",
            *meta_all_table_columns.keys(),
        ]
        all_table_columns = {
            # "id": "ID",
            "serial_number": "S.No",
            **meta_all_table_columns,
        }

        def get_queryset(self):
            user = self.get_user()
            return Job.objects.filter(created_by=user)
    
        def get_serializer_class(self):
            """Read Serializer."""

            return get_app_read_only_serializer(
                meta_model=meta_queryset.model,
                meta_fields=["id", *meta_all_table_columns.keys()],
                init_fields_config={**meta_init_fields_config},
                queryset=self.get_queryset()
            )
    return _ListAPIViewSet

def get_job_applied_list_api_viewset(
    
    meta_queryset,
    meta_all_table_columns: dict,
    meta_init_fields_config={},  # noqa
    parent_view=AllowedToAccessAdminCMSMixin,
    fields_to_filter=None,
    # meta_model = None,
):
    """
    Returns a dynamic `AppModelListAPIViewSet` for the Admin CMS.
    This can also be used in other places based on use cases.
    """
    fields_to_filter = fields_to_filter if fields_to_filter is not None else []

    class _ListAPIViewSet(parent_view, AppModelListAPIViewSet):
        """List ViewSet"""

        queryset = meta_queryset
        filterset_fields = [*fields_to_filter]
        search_fields = [
            "id",
            *meta_all_table_columns.keys(),
        ]
        all_table_columns = {
            # "id": "ID",
            "serial_number": "S.No",
            **meta_all_table_columns,
        }

        def get_queryset(self):
            user = self.get_user()
            return JobAppliedList.objects.filter(job__created_by=user).exclude(status="pending_assessment")
    
        def get_serializer_class(self):
            """Read Serializer."""

            return get_app_read_only_serializer(
                meta_model=meta_queryset.model,
                meta_fields=["id", *meta_all_table_columns.keys()],
                init_fields_config={**meta_init_fields_config},
                queryset=self.get_queryset()
            )
    return _ListAPIViewSet

def get_job_feedback_template_list_api_viewset(
    
    meta_queryset,
    meta_all_table_columns: dict,
    meta_init_fields_config={},  # noqa
    parent_view=AllowedToAccessAdminCMSMixin,
    fields_to_filter=None,
    # meta_model = None,
):
    """
    Returns a dynamic `AppModelListAPIViewSet` for the Admin CMS.
    This can also be used in other places based on use cases.
    """
    fields_to_filter = fields_to_filter if fields_to_filter is not None else []

    class _ListAPIViewSet(parent_view, AppModelListAPIViewSet):
        """List ViewSet"""

        queryset = meta_queryset
        filterset_fields = [*fields_to_filter]
        search_fields = [
            "id",
            *meta_all_table_columns.keys(),
        ]
        all_table_columns = {
            # "id": "ID",
            "serial_number": "S.No",
            **meta_all_table_columns,
        }

        def get_queryset(self):
            user = self.get_user()
            return JobFeedbackTemplate.objects.filter(created_by=user)
    
        def get_serializer_class(self):
            """Read Serializer."""

            return get_app_read_only_serializer(
                meta_model=meta_queryset.model,
                meta_fields=["id", *meta_all_table_columns.keys()],
                init_fields_config={**meta_init_fields_config},
                queryset=self.get_queryset()
            )
    return _ListAPIViewSet
