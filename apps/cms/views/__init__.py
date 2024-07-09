# flake8: noqa
from .base import (
    get_model_cud_api_viewset, 
    get_model_list_api_viewset, 
    get_staff_list_api_viewset, 
    get_student_list_api_viewset, 
    get_institution_user_group_list_api_viewset, 
    get_institution_user_group_content_list_api_viewset,
    get_employer_job_list_api_viewset,
    get_job_applied_list_api_viewset,
    get_interview_panel_list_api_viewset,
    get_interview_schedule_list_api_viewset,
    get_interview_schedule_interview_panel_list_api_viewset,
    get_schedule_list_for_interview_panel_api_viewset,
    get_job_feedback_template_list_api_viewset,

)
from .dashboard import AdminCMSDynamicConfigAPIView
from .user import (
    CreateUserAPIView,
    VideoLinkAPIView,
    UpdateUserAPIView,
    StudentCreateAPIView,
    StudentDeleteAPIView,
    StudentEditAPIView,
    StudentDetailAPIView,
    StudentMyLearningsAPIView,
    # StudentListAPIView,
    StaffCreateAPIView,
    StaffDeleteAPIView,
    StaffDetailAPIView,
    StaffEditAPIView,
    # StaffListAPIView
    CourseBulkUploadAPIView,
    SubPlanBulkUploadAPIView,
    SubPlanModuleBulkUploadAPIView,
    SubPlanSubModuleBulkUploadAPIView,
) 
from .forum import (
    ForumPostListAPIView,
    ForumPostLikeAPIView,
    ForumPostCommentListAPIView,
    ForumPostReplyListAPIView,
    PostPollOptionClickAPIView,
    ZoneListAPIView,
    ZoneDetailAPIView,
    DeleteForumComment,
    ) 
from .institution import (
    CreateInstitutionAPIView,
    UpdateInstitutionAPIView, 
    CreateInstitutionUserGroupAPIView,
    UpdateInstitutionUserGroupAPIView, 
    MetaInstitutionUserGroupAPIView,
    MetaInstitutionUserGroupContentAPIView,
    DetailInstitutionUserGroupAPIView, 
    ReportGenerateAPIView,
    ReportListAPIView,
    StudentsBulkUploadAPIView,
    ReportGenerateMetaAPIView,
    ReportDeleteAPIView,
    InstitutionAdminDashboardAPIView,
    InstitutionAdminDashboardTrendingAPIView,
    AdminHomeAPIView,
    AdminDetailHomeAPIView,
    LogoImageAPIView,
    DetailInstitutionUserGroupContentAPIView,
    UsersBulkUploadAPIView
)
from .subscription_plan import SubscriptionPlanDetailView, LearningContentMetaAPIView, SubscriptionPlanListAPIView, SubscriptionPlanStatusUpdateAPIView
from .hackathon import (
    CreateHackathonUpdate, 
    HackathonDiscussionListAPIView, 
    HackathonDiscussionCommentListAPIView, 
    HackathonDiscussionReplyListAPIView
)
from .employer import (
    CreateEmployerAPIView, 
    UpdateEmployerAPIView, 
    CreateInterviewPanelAPIView,
    UpdateInterviewPanelAPIView,
    MetaInterviewScheduleAPIView,
    EmployerDashboardAPIView
)
from .interview_panel import(
    InterviewScheduleListAPIView,
    InterviewScheduleApplicantListAPIView,
    SendFeedbackInterviewPanelMetaAPIView,
    SendFeedbackInterviewPanelAPIView,
    JobFeedbackOption,
    FeedbackInterviewPanelAPIView
)
from .employer import CreateEmployerAPIView, UpdateEmployerAPIView
from .blog import (
    BlogApproveAPIView,
    BlogArchieveAPIView,
    BlogDeclineAPIView,
    BlogCommentListAPIView,
    BlogCommentReplyListAPIView,
    BlogLikeAPIView,
    BlogDetailAPIView,
)
from .news import NewsListAPIView
from .webinar import WebinarDiscussionListAPIView, WebinarDiscussionReplyListAPIView, WebinarDiscussionCommentListAPIView, WebinarRegistrationListAPIViewset
from .blended_learning import CreateBlendedLearningAPIView, UpdateBlendedLearningAPIView, BlendedLearningModeAndFeeListAPIViewSet, BlendedLearningClassroomAndVirtualListAPIViewSet, BlendedLearningPathCustomerOnlineListAPIViewset, BlendedLearningPathCustomerClassroomListAPIViewset,BlendedLearningPathCustomerOnlineListTableMetaAPIViewset,BlendedLearningPathCustomerClassroomListTableMetaAPIViewset
from .learning_content import LearningContentAPIView, AllLearningContentAPIView, LearningContentFeedbackAPIView, LearningContentFeedbackMeta
from .applicant import FresherPoolListAPIView, AdminStudentOneProfileAPIView, UpdateFresherPoolApplicantStatus, UpdateApplicantListStatus, FresherPoolsMeta
from .skills import BulkSkillArchiveAPIView