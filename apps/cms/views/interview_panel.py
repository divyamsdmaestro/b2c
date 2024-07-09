from rest_framework.generics import ListAPIView
from apps.common.views.api import AppAPIView
from apps.common.views.api.base import NonAuthenticatedAPIMixin
from django_filters.rest_framework import DjangoFilterBackend
from apps.common.pagination import AppPagination
from rest_framework.filters import SearchFilter
from apps.common.serializers import AppReadOnlyModelSerializer, AppWriteOnlyModelSerializer
from apps.jobs.models import (
    JobInterviewSchedule, 
    Job, 
    JobFeedbackOption, 
    JobFeedbackAttachment, 
    JobFeedbackQuestionAnswer, 
    JobFeedbackQuestion, 
    JobFeedbackTemplate,
    JobAppliedList
)
from apps.common.serializers import get_app_read_only_serializer as read_serializer
from apps.access.models import User

class InterviewScheduleListAPIView(ListAPIView, AppAPIView):
    """
    Interview Schedule List
    """
    
    class _Serializer(AppReadOnlyModelSerializer):
        """Handle input data."""

        applicant = read_serializer(User, meta_fields=["id","uuid","first_name"])()
        job = read_serializer(Job, meta_fields=["id","uuid","identity"])()

        class Meta(AppReadOnlyModelSerializer.Meta):
            fields = ["id", "uuid", "identity", "description", "schedule_date", "start_time", "end_time", "interview_link", "applicant", "job"]
            model = JobInterviewSchedule
        
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = "__all__"
    search_fields = ["identity"]
    pagination_class = AppPagination
    serializer_class = _Serializer

    def get_queryset(self, *args, **kwargs):
        return JobInterviewSchedule.objects.filter(interview_panel=self.get_user())

class InterviewScheduleApplicantListAPIView(ListAPIView, AppAPIView):
    """
    Sends out data for the Interview Schedule Applicant Listing Page.
    """

    class _Serializer(AppReadOnlyModelSerializer):
        """Handle input data."""

        applicant = read_serializer(User, meta_fields=["id","uuid","first_name", "alternative_email"])()
        job = read_serializer(Job, meta_fields=["id","uuid","identity"])()
        

        class Meta(AppReadOnlyModelSerializer.Meta):
            fields = ["id", "uuid", "identity", "schedule_date", "applicant", "job", "is_feedback_send"]
            model = JobInterviewSchedule
        
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = "__all__"
    search_fields = ["identity"]
    pagination_class = AppPagination
    serializer_class = _Serializer

    def get_queryset(self, *args, **kwargs):
        return JobInterviewSchedule.objects.filter(interview_panel=self.get_user())
    
class SendFeedbackInterviewPanelMetaAPIView(NonAuthenticatedAPIMixin, ListAPIView, AppAPIView):
    """
    Meta Data For Feedback Interview Panel
    """

    class _Serializer(AppReadOnlyModelSerializer):

        feedback_question = read_serializer(JobFeedbackQuestion, meta_fields=["id", "uuid", "question", "answer_type", "choice1", "choice2", "choice3", "choice4"])(many=True)

        class Meta(AppReadOnlyModelSerializer):
            model = JobFeedbackTemplate
            fields = ["id", "uuid", "identity", "description", "industry_type", "comment_box_enable", "attachment_enable", "feedback_question"]

    serializer_class = _Serializer
    queryset = JobFeedbackTemplate.objects.all()

    def get_queryset(self):
        interview_schedule = JobInterviewSchedule.objects.get(id=self.kwargs['id'])
        return JobFeedbackTemplate.objects.filter(id=interview_schedule.interview_feedback_template.id)
    
class SendFeedbackInterviewPanelAPIView(NonAuthenticatedAPIMixin, AppAPIView):
    """
    API View to create Feedback For Interview Schedule.
    """

    class _Serializer(AppWriteOnlyModelSerializer):
        """Handle input data."""

        class _FeedbackAnswerSerializer(AppWriteOnlyModelSerializer):

            class Meta(AppWriteOnlyModelSerializer.Meta):
                model = JobFeedbackQuestionAnswer
                fields = ["feedback_question", "text_area", "choice1", "choice2", "choice3", "choice4"]

        feedback_question_answer = _FeedbackAnswerSerializer(many=True)

        class Meta(AppWriteOnlyModelSerializer.Meta):
            fields = ["comment", "attachment", "feedback_question_answer", "is_shortlisted"]
            model = JobFeedbackOption

    serializer_class = _Serializer

    def post(self, request, *args, **kwargs):
        interview_schedule = JobInterviewSchedule.objects.get(id=kwargs['id'])
        serializer = self.get_valid_serializer()
        if interview_schedule.is_feedback_send == False:
            if serializer.is_valid():
                feedback_question_answers = serializer.validated_data.pop('feedback_question_answer', [])
                feedback = serializer.save(interview_schedule=interview_schedule) 
                
                for feedback_question_answers in feedback_question_answers:
                    feedback.feedback_question_answer.create(**feedback_question_answers)

                interview_schedule.is_feedback_send = True
                interview_schedule.save()
                is_shortlisted = serializer.validated_data.pop('is_shortlisted')
                job = JobAppliedList.objects.filter(created_by=interview_schedule.applicant, job=interview_schedule.job).first()
                if is_shortlisted:
                    job.status = "recommended"
                    job.save()
                else:
                    job.status = "rejected"
                    job.save()
                return self.send_response(serializer.data)
        else:
            return self.send_response({"detail": "Already send the Feedback."})
        return self.send_error_response(serializer.errors)
    
class FeedbackInterviewPanelAPIView(NonAuthenticatedAPIMixin, ListAPIView, AppAPIView):
    """
    Send out the data of Feedback send.
    """

    class _Serializer(AppReadOnlyModelSerializer):
        """Handle input data."""

        attachment = read_serializer(JobFeedbackAttachment, meta_fields=["id", "uuid", "file"])(
            JobFeedbackAttachment.objects.all(), many=True
        )
        feedback_question_answer = read_serializer(JobFeedbackQuestionAnswer, meta_fields=["id", "uuid", "feedback_question", "text_area", "choice1", "choice2", "choice3", "choice4"])(
            JobFeedbackQuestionAnswer.objects.all(), many=True
        )

        class Meta(AppReadOnlyModelSerializer.Meta):
            fields = ["comment", "attachment", "feedback_question_answer", "is_shortlisted"]
            model = JobFeedbackOption

    serializer_class = _Serializer
    queryset = JobFeedbackOption.objects.all()

    def get_queryset(self):
        interview_schedule = JobInterviewSchedule.objects.get(id=self.kwargs['id'])
        return JobFeedbackOption.objects.filter(interview_schedule=interview_schedule)
    
