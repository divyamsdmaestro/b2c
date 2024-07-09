# flake8: noqa
from .auth import (
    AuthMetaInfoAPIView,
    # UserRefreshAPIView,
    # UserSignInAPIView,
    # UserSignUpAPIView,
)
from .explore import (
    CertificationPathDetailView,
    CourseDetailView,
    ExploreMetaAPIView,
    ExploreNavigationAPIView,
    ExplorePageAPIView,
    ExplorePageRecommentationAPIView,
    ExploreSearchAPIView,
    LearningPathDetailView,
    ExploreSkillsMetaAPIView,
    SkillsPageAPIView,
    StudentHomeAPIView,
    SkillsPageDetailsAPIView,
    StudentDashboardAPIView,
    CourseBulkDetailView,
    PrivateCourseBulkDetailView,
    BlendedLearningPathDetailView,
    MMLCourseDetailView,
    ExplorePageCourseCompleteInaDayAPIView,
    LearningPathCourseListView,
    LearningPathCoursePreviewView,
    SkillsPageLearningDetailsAPIView,
    BlendedLearningPathPriceDetailView,
    BlendedLearningPathBuyDetailView,
    BlendedLearningPathClassroomAndVirtualScheduleDetailView,
    BlendedLearningPathScheduleListView
)
from .help_desk import (
    HelpDeskContactUsAPIView,
    HelpDeskFaqAPIView,
    HelpDeskUserAskedQuestionAPIView,
    ContactUsMetaAPIView
)
from .home import (
    HomePageAPIView, 
    SignUpAPIView, 
    SignInAPIView, 
    ForgotPasswordAPIView,
    ForgotResetPasswordAPIView, 
    LogoutAPIView, 
    ChangePasswordAPIView,
    HomeSupportAPIView,
    HomePageCategoryAPIView,
    HomePageCoursesAPIView,
    HomePageTrendingAPIView,
    HomePageCareerAPIView,
    HomePageRecommendationAPIView,
    GenerateGuestUserIDAPIView,
    GuestUserSignUpAPIView,
)
from .onboarding import (
    OnBoardingLevelStepOneAPIView,
    OnboardingMetaAPIView,
    OnBoardingTechnologyStepTwoAPIView,
)
from .privacy import (
    UserPrivacyDetailAPIView,
    UserPrivacyEditAPIView,
    UserPrivacyEditMetaAPIView,
)
from .profile import (
    UserProfileEditAPIView,
    UserProfileResumeDeleteAPIView,
    UserProfileImageDeleteAPIView,
    UserOneProfileDownloadAPIView,
    UserProfileDetailAPIView,
    UpdateUserProfileMetaAPIView,
    OneProfileDetailAPIView,
    UserProfileImageUploadAPIView,
    UserOneProfileBasicInformationAPIView,
    UserOneProfilSkillAchievementAPIView,
)
from .purchase import (
    ApplyOrRemoveCouponAPIView,
    EntityAddToCartAPIView,
    EntityAddToWishlistAPIView,
    MakeOrderFromCartAPIView,
    MakePaymentForOrderAPIView,
    MyCartAPIView,
    MyWishlistAPIView,
    VerifyPaymentForOrderAPIView,
    PincodeEditAPIView,
    PincodeEditMetaAPIView,
    MakeOrderForSubscriptionAPIView,
    StudentEnrollCourseAPIView,
    StudentEnrollLearningPathAPIView,
    StudentEnrollCertificatePathAPIView,
    CouponListAPIView,
    TransactionHistoryListAPIView,
    FreeCourseEnrollAPIView,
    DownloadInvoiceAPIView,
)
from .forum import (
    ZonePageAPIView,
    ZonePageRecommentationAPIView,
    ZoneJoinAPIView,
    ZoneJoinedListAPIView,
    ForumPostCreateAPIView,
    ForumPostEditAPIView,
    ForumPostEditMetaAPIView,
    ZoneDetailAPIView,
    ForumPostListAPIView,
    ForumPostDeleteAPIView,
    ForumPostLikeAPIView,
    ForumPostCommentCreateAPIView,
    ForumPostCommentEditAPIView,
    ForumPostCommentDeleteAPIView,
    ForumPostReplyCreateAPIView,
    ForumPostReplyEditAPIView,
    ForumPostReplyDeleteAPIView,
    ForumPostCommentListAPIView,
    ForumPostReplyListAPIView,
    PostPollOptionClickAPIView,
    ForumPostReportAPIView,
    ZoneHackathonListAPIView,
    ZoneWebinarListAPIView,
    ZoneBlogListAPIView,
    ZoneRetrieveAPIView,
)

from .webinar import (
    WebinarListAPIView,
    WebinarFilterMetaAPIView,
    WebinarDetailAPIView,
    WebinarRegistrationAPIView,
    MakePaymentForWebinarAPIView,
    VerifyPaymentForWebinarAPIView,
    MyWebinarListAPIView,
    WebinarRegistrationListAPIView,
    WebinarDiscussionListAPIView,
    WebinarDiscussionCommentListAPIView,
    WebinarDiscussionCommentCreateAPIView,
    WebinarDiscussionCommentEditAPIView,
    WebinarDiscussionCommentDeleteAPIView,
    WebinarDiscussionReplyListAPIView,
    WebinarDiscussionReplyCreateAPIView,
    WebinarDiscussionReplyEditAPIView,
    WebinarDiscussionReplyDeleteAPIView,
)
from .hackathon import (
    HackathonPageAPIView,
    HackathonDetailAPIView,
    HackathonJoinAPIView,
    HackathonSubmissionAPIView,
    HackathonJoinMetaAPIView,
    HackathonUpdateListAPIView,
    HackathonDiscussionCreateAPIView,
    HackathonDiscussionEditAPIView,
    HackathonDiscussionDeleteAPIView,
    HackathonDiscussionListAPIView,
    HackathonDiscussionCommentCreateAPIView,
    HackathonDiscussionCommentEditAPIView,
    HackathonDiscussionCommentDeleteAPIView,
    HackathonDiscussionCommentListAPIView,
    HackathonDiscussionReplyCreateAPIView,
    HackathonDiscussionReplyEditAPIView,
    HackathonDiscussionReplyDeleteAPIView,
    HackathonDiscussionReplyListAPIView,
    HackathonMetaAPIView,
    EnrolledHackathonAPIView,
    CompletedHackathonAPIView,
    HackathonParticipantsListAPIView,
)

from .role_based_learning import (
    ExploreRolePageAPIView,
    ExploreRoleMetaAPIView,
    ExploreRoleSearchAPIView
)

from .subscription_plan import (
    SubscriptionPlanListView,
    SubscriptionPlanDetailView,
    SubscriptionCoursesView,
    SubscriptionLearningPathView,
    SubscriptionCertificationPathView,
    SubscriptionPlanEnquiryDetailsAPIView
)
from .job import (
    JobPageAPIView,
    JobDetailPageAPIView,
    JobAddToSavedlistAPIView,
    MyJobSavedlistAPIView,
    JobAppliedAPIView,
    MyJobAppliedlistAPIView,
    MyJobAppliedMetaAPIView,
    JobHomePageAPIView,
    JobMetaAPIView
)
from .blog import (
    BlogCreateAPIView,
    BlogDeleteAPIView,
    BlogEditAPIView,
    BlogEditMetaAPIView,
    BlogListAPIView,
    BlogDetailAPIView,
    BlogCommentCreateAPIView,
    BlogCommentEditAPIView,
    BlogCommentDeleteAPIView,
    BlogCommentListAPIView,
    BlogCommentReplyListAPIView,
    BlogCommentReplyCreateAPIView,
    BlogCommentReplyEditAPIView,
    BlogCommentReplyDeleteAPIView,
    BlogLikeAPIView
)
from .news import NewsListAPIView

from .yaksha import (
    GetAssessmentURLAsync,
    GetUserAssessmentResult,
    GetAssessmentResult,
    GetJobAssessmentResult,
    GetJobEligibleSkillAssessmentResult,
)
from .mml import (
    GetVmProvisioningRequestAPIView,
    GetVmStartAPIView
)
from .blended_learning import (
    GetBlendedLearningPathCoursesMeta,
    PostBlendedLearningUserEnroll,
    _CourseDetailsSerializer,
    PostBlendedLearningUserEnquiry,
    BlendedLearningPathAutoPopUpUserInformation,
)
from .notification import (
    UserNotificationListAPIView,
    UserNotificationUpdateAPIView,
    UserNotificationClearAPIView,
)

from .jobeligibleskill import (
    JobEligibleSkillListView,
    JobEligibleSkillDetailView,
    JobSkillCourseView,
    JobSkillLearningPathView,
    JobSkillCertificationPathView
    )

from .wallet import (
    WalletListAPIView,
    ECashEnabledorDisabledAPIView
)

# from .badges import (
#     LeaderBoardListAPIView
# )