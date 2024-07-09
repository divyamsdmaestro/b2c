from django.urls import path
from rest_framework.routers import SimpleRouter

from apps.meta.models import UserProfileResume
from apps.hackathons.models import round_details as round_models
from ..common.views.api import get_upload_api_view
from . import views
from apps.forums.models import PostImage, SubjectivePostImage
from apps.access.social_login import oauth_login, oauth_callback
from apps.cms.celery import webinar_reminder_email

app_name = "web_portal"
API_URL_PREFIX = "api/web-portal/"
API_PROXY_URL_PREFIX = "api/web-portal/proxy/"

router = SimpleRouter()

urlpatterns = [
                #   path(f"{API_URL_PREFIX}auth/meta-info/",
                #        views.AuthMetaInfoAPIView.as_view()),
                #   path(f"{API_URL_PREFIX}auth/sign-up/",
                #        views.UserSignUpAPIView.as_view()),
                #   path(
                #       f"{API_PROXY_URL_PREFIX}auth/refresh/",
                #       views.UserRefreshAPIView.as_view(),
                #   ),
                #   path(
                #       f"{API_PROXY_URL_PREFIX}auth/simple-login/",
                #       views.UserSignInAPIView.as_view(),
                #   ),
                #   path(
                #       f"{API_PROXY_URL_PREFIX}auth/logout/",
                #       proxy_to_idp_view(url_path="/api/access/v1/logout/").as_view(),
                #   ),
                #   Social oauth Login
                  path('auth/login/<str:provider>/', oauth_login, name='oauth-login'),
                  path('auth/complete/<str:provider>/', oauth_callback, name='oauth-callback'),
                  
                  path(f"{API_PROXY_URL_PREFIX}auth/simple-login/", views.SignInAPIView.as_view()),
                  path(f"{API_URL_PREFIX}auth/sign-up/", views.SignUpAPIView.as_view()),
                  path(f"{API_URL_PREFIX}auth/guest-user/create/", views.GenerateGuestUserIDAPIView.as_view()),
                  path(f"{API_URL_PREFIX}auth/guest-user/sign-up/", views.GuestUserSignUpAPIView.as_view()),
                  path(f"{API_URL_PREFIX}auth/forgot-password/", views.ForgotPasswordAPIView.as_view()),
                  path(f"{API_URL_PREFIX}auth/reset-password/<str:user_id>/<str:token>/", views.ForgotResetPasswordAPIView.as_view()),
                  path(f"{API_PROXY_URL_PREFIX}auth/logout/", views.LogoutAPIView.as_view()),
                  path(f"{API_PROXY_URL_PREFIX}auth/change-password/", views.ChangePasswordAPIView.as_view()),
                  path(f"{API_URL_PREFIX}home/", views.HomePageAPIView.as_view()),
                  path(f"{API_URL_PREFIX}home/recommendation/", views.HomePageRecommendationAPIView.as_view()),
                  path(f"{API_URL_PREFIX}home/support/", views.HomeSupportAPIView.as_view()),
                  path(f"{API_URL_PREFIX}home/category/", views.HomePageCategoryAPIView.as_view()),
                  path(f"{API_URL_PREFIX}home/courses/", views.HomePageCoursesAPIView.as_view()),
                  path(f"{API_URL_PREFIX}home/trending/", views.HomePageTrendingAPIView.as_view()),
                  path(f"{API_URL_PREFIX}home/career/", views.HomePageCareerAPIView.as_view()),
                  path(f"{API_URL_PREFIX}student/dashboard/", views.StudentDashboardAPIView.as_view()),
                  path(f"{API_URL_PREFIX}explore/", views.ExplorePageAPIView.as_view()),
                  path(f"{API_URL_PREFIX}explore/course/complete-in-a-day/", views.ExplorePageCourseCompleteInaDayAPIView.as_view()),
                  path(f"{API_URL_PREFIX}explore-recommentation/", views.ExplorePageRecommentationAPIView.as_view()),
                  path(f"{API_URL_PREFIX}explore/meta/",
                       views.ExploreMetaAPIView.as_view()),
                  path(
                      f"{API_URL_PREFIX}explore/certification-path/<uuid>/",
                      views.CertificationPathDetailView.as_view(),
                  ),
                  path(
                      f"{API_URL_PREFIX}explore/learning-path/<uuid>/",
                      views.LearningPathDetailView.as_view(),
                  ),
                  path(
                      f"{API_URL_PREFIX}explore/learning-path/<uuid>/course/list/",
                      views.LearningPathCourseListView.as_view(),
                  ),
                 path(
                      f"{API_URL_PREFIX}explore/learning-path/<uuid>/preview/",
                      views.LearningPathCoursePreviewView.as_view(),
                  ),
                  path(f"{API_URL_PREFIX}explore/courses/<uuid>/",
                       views.CourseDetailView.as_view()),
                  path(f"{API_URL_PREFIX}explore/mml-courses/<uuid>/",
                       views.MMLCourseDetailView.as_view()
                  ),
                  path(
                      f"{API_URL_PREFIX}explore/navigation/",
                      views.ExploreNavigationAPIView.as_view()
                  ),
                  path(f"{API_URL_PREFIX}explore/search/",
                       views.ExploreSearchAPIView.as_view()),
                  path(
                      f"{API_URL_PREFIX}purchase/entity/<uuid>/add-to-cart/",
                      views.EntityAddToCartAPIView.as_view(),
                  ),
                  path(
                      f"{API_URL_PREFIX}purchase/entity/<uuid>/add-to-wishlist/",
                      views.EntityAddToWishlistAPIView.as_view(),
                  ),
                  path(
                      f"{API_URL_PREFIX}purchase/my-wishlist/",
                      views.MyWishlistAPIView.as_view(),
                  ),
                #   path(f"{API_URL_PREFIX}purchase/my-cart/meta/",
                #        views.PincodeEditMetaAPIView.as_view()),
                  path(
                      f"{API_URL_PREFIX}purchase/my-cart/change-pincode/",
                      views.PincodeEditAPIView.as_view(),
                  ),
                  path(
                      f"{API_URL_PREFIX}purchase/my-cart/apply-coupon/",
                      views.ApplyOrRemoveCouponAPIView.as_view(),
                  ),
                  path(
                      f"{API_URL_PREFIX}purchase/my-cart/place-order/",
                      views.MakeOrderFromCartAPIView.as_view(),
                  ),
                  path(
                      f"{API_URL_PREFIX}purchase/order/<uuid>/make-payment/",
                      views.MakePaymentForOrderAPIView.as_view(),
                  ),
                  path(
                      f"{API_URL_PREFIX}purchase/order/<uuid>/verify-payment/",
                      views.VerifyPaymentForOrderAPIView.as_view(),
                  ),
                  path(
                      f"{API_URL_PREFIX}purchase/my-cart/",
                      views.MyCartAPIView.as_view(),
                  ),
                  path(
                      f"{API_URL_PREFIX}purchase/coupon-list/",
                      views.CouponListAPIView.as_view(),
                  ),
                  # Learner Free Course enroll url
                  path(f"{API_URL_PREFIX}course/<id>/enroll/", views.FreeCourseEnrollAPIView.as_view()),
                  # onboarding urls
                  path(f"{API_URL_PREFIX}onboarding/meta/",
                       views.OnboardingMetaAPIView.as_view()),
                  path(
                      f"{API_URL_PREFIX}onboarding/step-one/level/",
                      views.OnBoardingLevelStepOneAPIView.as_view(),
                  ),
                  path(
                      f"{API_URL_PREFIX}onboarding/step-two/technology/",
                      views.OnBoardingTechnologyStepTwoAPIView.as_view(),
                  ),
                  # help desk urls
                  path(f"{API_URL_PREFIX}help-desk/contact-us/meta/", views.ContactUsMetaAPIView.as_view()),
                  path(
                      f"{API_URL_PREFIX}help-desk/ask-a-questions/",
                      views.HelpDeskUserAskedQuestionAPIView.as_view(),
                  ),
                  path(
                      f"{API_URL_PREFIX}help-desk/faq/",
                      views.HelpDeskFaqAPIView.as_view(),
                  ),
                  path(
                      f"{API_URL_PREFIX}help-desk/contact-us/",
                      views.HelpDeskContactUsAPIView.as_view(),
                  ),
                  # user privacy & settings
                  path(
                      f"{API_URL_PREFIX}user/privacy/edit/meta/",
                      views.UserPrivacyEditMetaAPIView.as_view(),
                  ),
                  path(
                      f"{API_URL_PREFIX}user/privacy/edit/",
                      views.UserPrivacyEditAPIView.as_view(),
                  ),
                  path(
                      f"{API_URL_PREFIX}user/privacy/view/",
                      views.UserPrivacyDetailAPIView.as_view(),
                  ),
                #   # user profile & setting
                #   path(
                #       f"{API_URL_PREFIX}user/profile/edit/meta/",
                #       views.UserProfileEditMetaAPIView.as_view(),
                #   ),
                  # update user profile
                  path(
                      f"{API_URL_PREFIX}user/profile/edit/meta/",
                      views.UpdateUserProfileMetaAPIView.as_view(),
                  ),
                  # profile related uploads
                  path(
                      f"{API_URL_PREFIX}user/profile/resume/upload/",
                      get_upload_api_view(meta_model=UserProfileResume).as_view(),
                  ),
                  path(
                      f"{API_URL_PREFIX}user/profile/resume/<pk>/delete/",
                      views.UserProfileResumeDeleteAPIView.as_view(),
                  ),
                  path(
                      f"{API_URL_PREFIX}user/profile/image/upload/",
                      views.UserProfileImageUploadAPIView.as_view(),
                  ),
                #   path(
                #       f"{API_URL_PREFIX}user/profile/image/edit/",
                #       views.UserProfileImageEditAPIView.as_view(),
                #   ),
                  path(
                      f"{API_URL_PREFIX}user/profile/image/<pk>/delete/",
                      views.UserProfileImageDeleteAPIView.as_view(),
                  ),
                  path(
                      f"{API_URL_PREFIX}user/one-profile/download/",
                      views.UserOneProfileDownloadAPIView.as_view(),
                  ),
                  path(
                      f"{API_URL_PREFIX}user/one-profile/basic-information/",
                      views.UserOneProfileBasicInformationAPIView.as_view(),
                  ),
                  path(
                      f"{API_URL_PREFIX}user/one-profile/skill-achievement/",
                      views.UserOneProfilSkillAchievementAPIView.as_view(),
                  ),
                
                # zone urls
                path(f"{API_URL_PREFIX}zone/", views.ZonePageAPIView.as_view()),
                path(f"{API_URL_PREFIX}zone-recommentation/", views.ZonePageRecommentationAPIView.as_view()),
                path(f"{API_URL_PREFIX}zone/<uuid>/join/", views.ZoneJoinAPIView.as_view()),
                path(f"{API_URL_PREFIX}zone/joined-list/", views.ZoneJoinedListAPIView.as_view()),
                path(f"{API_URL_PREFIX}zone/<uuid>/detail/", views.ZoneDetailAPIView.as_view()),
                path(f"{API_URL_PREFIX}zone/<uuid>/retrieve/", views.ZoneRetrieveAPIView.as_view()), # common zone detail api without forum details
                path(f"{API_URL_PREFIX}zone/<uuid>/webinar/list/", views.ZoneWebinarListAPIView.as_view()), 
                path(f"{API_URL_PREFIX}zone/<uuid>/blog/list/", views.ZoneBlogListAPIView.as_view()),
                path(f"{API_URL_PREFIX}zone/<uuid>/hackathon/list/", views.ZoneHackathonListAPIView.as_view()),

                path(f"{API_URL_PREFIX}zone/<uuid>/forum/<forum_id>/post/list/", views.ForumPostListAPIView.as_view()),

                # create question/poll based post urls
                path(f"{API_URL_PREFIX}zone/<uuid>/forum/<forum_id>/post/create/", views.ForumPostCreateAPIView.as_view()),
                # forum post image upload url
                path(f"{API_URL_PREFIX}zone/forum/post/image/upload/",get_upload_api_view(meta_model=PostImage).as_view(),),
                path(f"{API_URL_PREFIX}zone/forum/post/subjective-image/upload/",get_upload_api_view(meta_model=SubjectivePostImage).as_view(),),
                # edit question/poll based post urls
                path(f"{API_URL_PREFIX}zone/<uuid>/forum/<forum_id>/post/<post_id>/edit/", views.ForumPostEditAPIView.as_view()),
                path(f"{API_URL_PREFIX}zone/<uuid>/forum/<forum_id>/post/<id>/edit/meta/", views.ForumPostEditMetaAPIView.as_view()),
                # Delete forum-post url
                path(f"{API_URL_PREFIX}zone/<uuid>/forum/<forum_id>/post/<post_id>/delete/", views.ForumPostDeleteAPIView.as_view()),
                # Like forum-post url
                path(f"{API_URL_PREFIX}zone/<uuid>/forum/<forum_id>/post/<post_id>/like/", views.ForumPostLikeAPIView.as_view()),
                # Forum post comments list
                path(f"{API_URL_PREFIX}zone/<uuid>/forum/<forum_id>/post/<post_id>/comment/", views.ForumPostCommentListAPIView.as_view()),
                # Forum post comments cud
                path(f"{API_URL_PREFIX}zone/<uuid>/forum/<forum_id>/post/<post_id>/comment/create/", views.ForumPostCommentCreateAPIView.as_view()),

                path(f"{API_URL_PREFIX}zone/<uuid>/forum/<forum_id>/post/<post_id>/comment/<comment_id>/edit/", views.ForumPostCommentEditAPIView.as_view()),

                path(f"{API_URL_PREFIX}zone/<uuid>/forum/<forum_id>/post/<post_id>/comment/<comment_id>/delete/", views.ForumPostCommentDeleteAPIView.as_view()),
                # Forum post comment replies list
                path(f"{API_URL_PREFIX}zone/<uuid>/forum/<forum_id>/post/<post_id>/comment/<comment_id>/reply/", views.ForumPostReplyListAPIView.as_view()),
                # Forum post comment reply cud
                path(f"{API_URL_PREFIX}zone/<uuid>/forum/<forum_id>/post/<post_id>/comment/<comment_id>/reply/create/", views.ForumPostReplyCreateAPIView.as_view()),

                path(f"{API_URL_PREFIX}zone/<uuid>/forum/<forum_id>/post/<post_id>/comment/<comment_id>/reply/<reply_id>/edit/", views.ForumPostReplyEditAPIView.as_view()),

                path(f"{API_URL_PREFIX}zone/<uuid>/forum/<forum_id>/post/<post_id>/comment/<comment_id>/reply/<reply_id>/delete/", views.ForumPostReplyDeleteAPIView.as_view()),
                # Forum post poll option click url
                path(f"{API_URL_PREFIX}zone/<uuid>/forum/<forum_id>/post/<post_id>/polloption/<poll_option_id>/", views.PostPollOptionClickAPIView.as_view()),
                # report forum-post url
                path(f"{API_URL_PREFIX}zone/<uuid>/forum/<forum_id>/post/<post_id>/report/", views.ForumPostReportAPIView.as_view()),
                # webinar urls
                path(f"{API_URL_PREFIX}webinar/list/", views.WebinarListAPIView.as_view(), ),
                path(f"{API_URL_PREFIX}webinar/filters/meta/", views.WebinarFilterMetaAPIView.as_view(), ),
                path(f"{API_URL_PREFIX}webinar/<uuid>/view/", views.WebinarDetailAPIView.as_view(), ),
                path(
                      f"{API_URL_PREFIX}webinar/register/",
                      views.WebinarRegistrationAPIView.as_view(), ),
                  path(
                      f"{API_URL_PREFIX}webinar/register/list/",
                      views.WebinarRegistrationListAPIView.as_view(), ),
                  path(
                      f"{API_URL_PREFIX}webinar/register/participation/",
                      views.MyWebinarListAPIView.as_view(), ),
                  path(
                      f"{API_URL_PREFIX}webinar/register/<uuid>/make-payment/",
                      views.MakePaymentForWebinarAPIView.as_view(), ),
                  path(
                      f"{API_URL_PREFIX}webinar/register/<uuid>/verify-payment/",
                      views.VerifyPaymentForWebinarAPIView.as_view(), ),
                # Webinar discussion list
                path(f"{API_URL_PREFIX}community/webinar/<uuid>/discussion/list/", views.WebinarDiscussionListAPIView.as_view()),
                # Webinar discussion comments cud
                path(f"{API_URL_PREFIX}community/webinar/<uuid>/discussion/<discussion_id>/comment/create/", views.WebinarDiscussionCommentCreateAPIView.as_view()),
                path(f"{API_URL_PREFIX}community/webinar/<uuid>/discussion/<discussion_id>/comment/<comment_id>/edit/", views.WebinarDiscussionCommentEditAPIView.as_view()),
                path(f"{API_URL_PREFIX}community/webinar/<uuid>/discussion/<discussion_id>/comment/<comment_id>/delete/", views.WebinarDiscussionCommentDeleteAPIView.as_view()),
                # Webinar discussion comments list
                path(f"{API_URL_PREFIX}community/webinar/<uuid>/discussion/<discussion_id>/comment/list/", views.WebinarDiscussionCommentListAPIView.as_view()),
                # Webinar discussion comment reply cud
                path(f"{API_URL_PREFIX}community/webinar/<uuid>/discussion/<discussion_id>/comment/<comment_id>/reply/create/", views.WebinarDiscussionReplyCreateAPIView.as_view()),
                path(f"{API_URL_PREFIX}community/webinar/<uuid>/discussion/<discussion_id>/comment/<comment_id>/reply/<reply_id>/edit/", views.WebinarDiscussionReplyEditAPIView.as_view()),
                path(f"{API_URL_PREFIX}community/webinar/<uuid>/discussion/<discussion_id>/comment/<comment_id>/reply/<reply_id>/delete/", views.WebinarDiscussionReplyDeleteAPIView.as_view()),
                # Webinar discussion comment replies list
                path(f"{API_URL_PREFIX}community/webinar/<uuid>/discussion/<discussion_id>/comment/<comment_id>/reply/list/", views.WebinarDiscussionReplyListAPIView.as_view()),

                # Hackathon urls
                path(
                    f"{API_URL_PREFIX}community/hackathon/",
                    views.HackathonPageAPIView.as_view(),
                ),
                path(
                    f"{API_URL_PREFIX}community/hackathon/meta/",
                    views.HackathonMetaAPIView.as_view(),
                ),
                path(f"{API_URL_PREFIX}community/hackathon/<uuid>/detail/", views.HackathonDetailAPIView.as_view()), 
                path(f"{API_URL_PREFIX}community/join/hackathon/meta/", views.HackathonJoinMetaAPIView.as_view()),
                path(f"{API_URL_PREFIX}community/hackathon/<uuid>/join/", views.HackathonJoinAPIView.as_view()),
                path(f"{API_URL_PREFIX}community/hackathon/<uuid>/submission/", views.HackathonSubmissionAPIView.as_view()),
                path(f"{API_URL_PREFIX}community/hackathon/<uuid>/updates/", views.HackathonUpdateListAPIView.as_view()),
                path(f"{API_URL_PREFIX}community/hackathon/<uuid>/participant/", views.HackathonParticipantsListAPIView.as_view()),
                # Hackathon discussion cud
                path(f"{API_URL_PREFIX}community/hackathon/<uuid>/discussion/create/", views.HackathonDiscussionCreateAPIView.as_view()),
                path(f"{API_URL_PREFIX}community/hackathon/<uuid>/discussion/<discussion_id>/edit/", views.HackathonDiscussionEditAPIView.as_view()),
                path(f"{API_URL_PREFIX}community/hackathon/<uuid>/discussion/<discussion_id>/delete/", views.HackathonDiscussionDeleteAPIView.as_view()),
                # Hackathon discussion list
                path(f"{API_URL_PREFIX}community/hackathon/<uuid>/discussion/list/", views.HackathonDiscussionListAPIView.as_view()),
                # Hackathon discussion comments cud
                path(f"{API_URL_PREFIX}community/hackathon/<uuid>/discussion/<discussion_id>/comment/create/", views.HackathonDiscussionCommentCreateAPIView.as_view()),
                path(f"{API_URL_PREFIX}community/hackathon/<uuid>/discussion/<discussion_id>/comment/<comment_id>/edit/", views.HackathonDiscussionCommentEditAPIView.as_view()),
                path(f"{API_URL_PREFIX}community/hackathon/<uuid>/discussion/<discussion_id>/comment/<comment_id>/delete/", views.HackathonDiscussionCommentDeleteAPIView.as_view()),
                # Hackathon discussion comments list
                path(f"{API_URL_PREFIX}community/hackathon/<uuid>/discussion/<discussion_id>/comment/list/", views.HackathonDiscussionCommentListAPIView.as_view()),
                # Hackathon discussion comment reply cud
                path(f"{API_URL_PREFIX}community/hackathon/<uuid>/discussion/<discussion_id>/comment/<comment_id>/reply/create/", views.HackathonDiscussionReplyCreateAPIView.as_view()),
                path(f"{API_URL_PREFIX}community/hackathon/<uuid>/discussion/<discussion_id>/comment/<comment_id>/reply/<reply_id>/edit/", views.HackathonDiscussionReplyEditAPIView.as_view()),
                path(f"{API_URL_PREFIX}community/hackathon/<uuid>/discussion/<discussion_id>/comment/<comment_id>/reply/<reply_id>/delete/", views.HackathonDiscussionReplyDeleteAPIView.as_view()),
                # Hackathon discussion comment replies list
                path(f"{API_URL_PREFIX}community/hackathon/<uuid>/discussion/<discussion_id>/comment/<comment_id>/reply/list/", views.HackathonDiscussionReplyListAPIView.as_view()),

                path(
                      f"{API_URL_PREFIX}community/join/hackathon/submission/image/upload/",
                      get_upload_api_view(meta_model=round_models.HackathonSubmissionMediaFiles).as_view(),
                  ),
                path(f"{API_URL_PREFIX}community/hackathon/enrolled/list/", views.EnrolledHackathonAPIView.as_view()),
                path(f"{API_URL_PREFIX}community/hackathon/completed/list/", views.CompletedHackathonAPIView.as_view()),
                # Job urls
                path(f"{API_URL_PREFIX}job/home", views.JobHomePageAPIView.as_view()),
                path(f"{API_URL_PREFIX}job/", views.JobPageAPIView.as_view()),
                path(f"{API_URL_PREFIX}job/meta", views.JobMetaAPIView.as_view()),
                path(f"{API_URL_PREFIX}job/<uuid>/", views.JobDetailPageAPIView.as_view()),
                path(f"{API_URL_PREFIX}job/<uuid>/apply", views.JobAppliedAPIView.as_view()),
                path(f"{API_URL_PREFIX}job/<uuid>/save", views.JobAddToSavedlistAPIView.as_view()),
                path(f"{API_URL_PREFIX}job/saved-list", views.MyJobSavedlistAPIView.as_view()),
                path(f"{API_URL_PREFIX}job/applied-list", views.MyJobAppliedlistAPIView.as_view()),
                path(f"{API_URL_PREFIX}job/applied-list/meta", views.MyJobAppliedMetaAPIView.as_view()),
                
                # Role Based Leraning
                path(f"{API_URL_PREFIX}explore/learning-role/",views.ExploreRolePageAPIView.as_view()),
                path(f"{API_URL_PREFIX}explore/learning-role/meta/", views.ExploreRoleMetaAPIView.as_view()),
                path(f"{API_URL_PREFIX}explore/learning-role/search/", views.ExploreRoleSearchAPIView.as_view()),

                # Skills urls
                path(f"{API_URL_PREFIX}explore/learning/skills/meta/", views.ExploreSkillsMetaAPIView.as_view(),),
                path(f"{API_URL_PREFIX}explore/learning/skills/", views.SkillsPageAPIView.as_view(),),
                path(f"{API_URL_PREFIX}explore/learning/skills/<uuid>/detail/", views.SkillsPageDetailsAPIView.as_view(),),
                path(f"{API_URL_PREFIX}explore/learning/skills-learning/<type>/<uuid>/list/", views.SkillsPageLearningDetailsAPIView.as_view(),),

                # Profile
                path(f"{API_URL_PREFIX}user/profile/edit/", views.UserProfileEditAPIView.as_view()),
                path(f"{API_URL_PREFIX}user/profile/view/", views.UserProfileDetailAPIView.as_view()),
                path(f"{API_URL_PREFIX}one/profile/view/", views.OneProfileDetailAPIView.as_view()),

                # Subscription
                path(f"{API_URL_PREFIX}subscription-plan/user-enquiry/", views.SubscriptionPlanEnquiryDetailsAPIView.as_view()),
                path(f"{API_URL_PREFIX}subscription-plan/list/", views.SubscriptionPlanListView.as_view()),
                path(f"{API_URL_PREFIX}subscription-plan/<uuid>/", views.SubscriptionPlanDetailView.as_view()),
                path(f"{API_URL_PREFIX}subscription-plan/courses/<uuid>/", views.SubscriptionCoursesView.as_view()),
                path(f"{API_URL_PREFIX}subscription-plan/learning-paths/<uuid>/", views.SubscriptionLearningPathView.as_view()),
                path(f"{API_URL_PREFIX}subscription-plan/certification-paths/<uuid>/", views.SubscriptionCertificationPathView.as_view()),
                path(f"{API_URL_PREFIX}subscription-plan/<uuid>/place-order/", views.MakeOrderForSubscriptionAPIView.as_view()),

                # JobEligibleSkill
                path(f"{API_URL_PREFIX}job-eligible-skill/list/", views.JobEligibleSkillListView.as_view()),
                path(f"{API_URL_PREFIX}job-eligible-skill/<uuid>/", views.JobEligibleSkillDetailView.as_view()),
                path(f"{API_URL_PREFIX}job-eligible-skill/courses/<uuid>/", views.JobSkillCourseView.as_view()),
                path(f"{API_URL_PREFIX}job-eligible-skill/learning-paths/<uuid>/", views.JobSkillLearningPathView.as_view()),
                path(f"{API_URL_PREFIX}job-eligible-skill/certification-paths/<uuid>/", views.JobSkillCertificationPathView.as_view()),
                
                # blog cud urls
                path(f"{API_URL_PREFIX}blog/create/", views.BlogCreateAPIView.as_view()),
                path(f"{API_URL_PREFIX}blog/<uuid>/edit/", views.BlogEditAPIView.as_view()),
                path(f"{API_URL_PREFIX}blog/<uuid>/delete/", views.BlogDeleteAPIView.as_view()),
                path(f"{API_URL_PREFIX}blog/<uuid>/edit/meta/", views.BlogEditMetaAPIView.as_view()),
                # blog list url
                path(f"{API_URL_PREFIX}blog/list/", views.BlogListAPIView.as_view()),
                path(f"{API_URL_PREFIX}blog/<uuid>/detail/", views.BlogDetailAPIView.as_view()),
                # Like blog url
                path(f"{API_URL_PREFIX}blog/<uuid>/like/", views.BlogLikeAPIView.as_view()),
                # blog comments list
                path(f"{API_URL_PREFIX}blog/<uuid>/comment/list/", views.BlogCommentListAPIView.as_view()),
                # blog comments cud
                path(f"{API_URL_PREFIX}blog/<uuid>/comment/create/", views.BlogCommentCreateAPIView.as_view()),

                path(f"{API_URL_PREFIX}blog/<uuid>/comment/<comment_id>/edit/", views.BlogCommentEditAPIView.as_view()),

                path(f"{API_URL_PREFIX}blog/<uuid>/comment/<comment_id>/delete/", views.BlogCommentDeleteAPIView.as_view()),
                # blog comment replies list
                path(f"{API_URL_PREFIX}blog/<uuid>/comment/<comment_id>/reply/list/", views.BlogCommentReplyListAPIView.as_view()),
                # blog comment reply cud
                path(f"{API_URL_PREFIX}blog/<uuid>/comment/<comment_id>/reply/create/", views.BlogCommentReplyCreateAPIView.as_view()),

                path(f"{API_URL_PREFIX}blog/<uuid>/comment/<comment_id>/reply/<reply_id>/edit/", views.BlogCommentReplyEditAPIView.as_view()),

                path(f"{API_URL_PREFIX}blog/<uuid>/comment/<comment_id>/reply/<reply_id>/delete/", views.BlogCommentReplyDeleteAPIView.as_view()),
                # news listing page
                path(f"{API_URL_PREFIX}news/list/", views.NewsListAPIView.as_view()),

                path(f"{API_URL_PREFIX}student-course/<id>/enroll/", views.StudentEnrollCourseAPIView.as_view()),

                path(f"{API_URL_PREFIX}student-learning-path/<id>/enroll/", views.StudentEnrollLearningPathAPIView.as_view()),

                path(f"{API_URL_PREFIX}student-certificate-path/<id>/enroll/", views.StudentEnrollCertificatePathAPIView.as_view()),
  
                path(f"{API_URL_PREFIX}transaction-history/", views.TransactionHistoryListAPIView.as_view()),
                path(f"{API_URL_PREFIX}invoice/<id>/print/", views.DownloadInvoiceAPIView.as_view()),

                # Bulk details of Course by uuids
                path(f"{API_URL_PREFIX}course/bulk/details/", views.CourseBulkDetailView.as_view()),
                path(f"{API_URL_PREFIX}private-course/bulk/details/", views.PrivateCourseBulkDetailView.as_view()),

                #yaksha urls
                path(f"{API_URL_PREFIX}yaksha-assessment/get-url/", views.GetAssessmentURLAsync.as_view()),
                path(f"{API_URL_PREFIX}yaksha-assessment/user-assessment-result/", views.GetUserAssessmentResult.as_view()),
                path(f"{API_URL_PREFIX}yaksha-assessment/get-result/<str:assessment_id>/", views.GetAssessmentResult.as_view()), 

                path(f"{API_URL_PREFIX}yaksha-assessment/job-assessment-result/", views.GetJobAssessmentResult.as_view()),
                path(f"{API_URL_PREFIX}yaksha-assessment/job-eligible-skill/assessment-result/", views.GetJobEligibleSkillAssessmentResult.as_view()),              
                #mml lab urls
                path(f"{API_URL_PREFIX}mml-lab/vm/provisioning/", views.GetVmProvisioningRequestAPIView.as_view()),                
                path(f"{API_URL_PREFIX}mml-lab/vm/provisioning/<id>/status/", views.GetVmStartAPIView.as_view()),
                #BLP
                path(
                      f"{API_URL_PREFIX}explore/blended-learning-path/<uuid>/",
                      views.BlendedLearningPathDetailView.as_view(),
                  ),
                #blp price details
                 path(
                      f"{API_URL_PREFIX}explore/blended-learning-path/price-detail/<uuid>/",
                      views.BlendedLearningPathPriceDetailView.as_view(),
                  ),
                   path(
                      f"{API_URL_PREFIX}explore/blended-learning-path/is-in-buy/<uuid>/",
                      views.BlendedLearningPathBuyDetailView.as_view(),
                  ),
                   path(
                      f"{API_URL_PREFIX}explore/blended-learning-path/schedule/<mode>/<uuid>/",
                      views.BlendedLearningPathClassroomAndVirtualScheduleDetailView.as_view(),
                   ),
                path(
                      f"{API_URL_PREFIX}explore/blended-learning-path/schedule-lists/<mode>/<uuid>/",
                      views.BlendedLearningPathScheduleListView.as_view(),
                   ),
                  # blp enroll urls
                path(f"{API_URL_PREFIX}blended-learning-path/enroll/meta/<id>/", views.GetBlendedLearningPathCoursesMeta.as_view()),
                path(f"{API_URL_PREFIX}blended-learning-path/user-enroll/", views.PostBlendedLearningUserEnroll.as_view()),
                path(f"{API_URL_PREFIX}blended-learning-path/user-enquiry/", views.PostBlendedLearningUserEnquiry.as_view()),
                path(f"{API_URL_PREFIX}blended-learning-path/auto-pop-up-user-information/", views.BlendedLearningPathAutoPopUpUserInformation.as_view()),

                #notification
                path(f"{API_URL_PREFIX}notifications/list/", views.UserNotificationListAPIView.as_view()),
                path(f"{API_URL_PREFIX}notification/update/<uuid>/", views.UserNotificationUpdateAPIView.as_view()),
                path(f"{API_URL_PREFIX}notifications/clear/", views.UserNotificationClearAPIView.as_view()),
                
                #wallet
                path(f"{API_URL_PREFIX}wallet/", views.WalletListAPIView.as_view()),
                path(f"{API_URL_PREFIX}enable-ecash/",views.ECashEnabledorDisabledAPIView.as_view()),
                
                #LeaderBoard
                # path(f"{API_URL_PREFIX}leaderboard/",views.LeaderBoardListAPIView.as_view()),
                path(f"{API_URL_PREFIX}reminder-email/", webinar_reminder_email, name='webinar-reminder-email'),
              ] + router.urls
