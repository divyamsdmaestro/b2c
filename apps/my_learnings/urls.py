from django.urls import path

from . import views

app_name = "my_learnings"
API_URL_PREFIX = "api/one-profile/"

urlpatterns = [
    #---------------------Course , module, sub module trackers----------------------#

    path(f"{API_URL_PREFIX}my-learnings/home/", views.MyCourseLearningsHomeAPIView.as_view()),
    path(
        f"{API_URL_PREFIX}my-learnings/learning-interface/tracker/course-module/<uuid>/viewed/",
        views.UserVisitedCourseModuleTrackerAPIView.as_view(),
    ),
    path(
        f"{API_URL_PREFIX}my-learnings/learning-interface/tracker/course-sub-module/<uuid>/viewed/",
        views.UserVisitedCourseSubModuleTrackerAPIView.as_view(),
    ),

    #----------------------------------MML Course---------------------------------------------#
     path(f"{API_URL_PREFIX}my-learnings/mml-course/home/", views.MyMMLCourseLearningsHomeAPIView.as_view()),
     path(
        f"{API_URL_PREFIX}my-learnings/learning-interface/tracker/mml-course/<uuid>/viewed/",
        views.UserVisitedMMLCourseTrackerAPIView.as_view(),
    ),

    #---------------------Learning Path, Course , module, sub module trackers----------------------#

    path(f"{API_URL_PREFIX}my-learnings/learning-path/home/", views.MyLearningPathHomeAPIView.as_view()),
    path(
        f"{API_URL_PREFIX}my-learnings/learning-interface/tracker/learning-path-course/<uuid>/viewed/",
        views.UserVisitedLearningPathCourseTrackerAPIView.as_view(),
    ),
    path(
        f"{API_URL_PREFIX}my-learnings/learning-interface/tracker/learning-path-course-module/<uuid>/viewed/",
        views.UserVisitedLearningPathCourseModuleTrackerAPIView.as_view(),
    ),
    path(
        f"{API_URL_PREFIX}my-learnings/learning-interface/tracker/learning-path-course-sub-module/<uuid>/viewed/",
        views.UserVisitedLearningPathCourseSubModuleTrackerAPIView.as_view(),
    ),

    #---------------------Advanced Learning path, Course , module, sub module trackers----------------------#

    path(f"{API_URL_PREFIX}my-learnings/certificate-path/home/", views.MyCertificatePathHomeAPIView.as_view()),
    path(
        f"{API_URL_PREFIX}my-learnings/learning-interface/tracker/certificate-path-learning-path/<uuid>/viewed/",
        views.UserVisitedCertificatePathLearningPathTrackerAPIView.as_view(),
    ),
    path(
        f"{API_URL_PREFIX}my-learnings/learning-interface/tracker/certificate-path-course/<uuid>/viewed/",
        views.UserVisitedCertificatePathLearningPathCourseTrackerAPIView.as_view(),
    ),
    path(
        f"{API_URL_PREFIX}my-learnings/learning-interface/tracker/certificate-path-course-module/<uuid>/viewed/",
        views.UserVisitedCertificatePathLearningPathCourseModuleTrackerAPIView.as_view(),
    ),
    path(
        f"{API_URL_PREFIX}my-learnings/learning-interface/tracker/certificate-path-course-sub-module/<uuid>/viewed/",
        views.UserVisitedCertificatePathLearningPathCourseSubModuleTrackerAPIView.as_view(),
    ),

    #---------------------Learning Role----------------------#
    path(f"{API_URL_PREFIX}my-learnings/learning-role/home/", views.MyLearningRoleHomeAPIView.as_view()),
    path(f"{API_URL_PREFIX}my-learnings/learning-role/<uuid>/start/", views.LearningRoleStartAPIView.as_view()),

    # path(
    #     f"{API_URL_PREFIX}my-learnings/learning-interface/tracker/sub-module/<uuid>/viewed/",
    #     views.UserVisitedSubModuleTrackerAPIView.as_view(),
    # ),
    # mml course process start api
    path(
        f"{API_URL_PREFIX}my-learnings/mml-course/tracker/<uuid>/start/",
        views.UserMMLCourseLearningTrackerStartAPIView.as_view(),
    ),
    # course module process start
    path(
        f"{API_URL_PREFIX}my-learnings/tracker/<uuid>/start/",
        views.UserLearningTrackerStartAPIView.as_view(),
    ),
    # Learning Path module process start api
    path(
        f"{API_URL_PREFIX}my-learnings/learning-path/tracker/<uuid>/start/",
        views.UserLearningPathTrackerStartAPIView.as_view(),
    ),
    # Certificate Learning Path module process start api
    path(
        f"{API_URL_PREFIX}my-learnings/certificate-path/tracker/<uuid>/start/",
        views.UserCertificatePathTrackerStartAPIView.as_view(),
    ),
    # Blended Learning Path module process start api
    path(
        f"{API_URL_PREFIX}my-learnings/blended-learning-path/tracker/<uuid>/start/",
        views.UserBlendedLearningPathTrackerStartAPIView.as_view(),
    ),
    path(
        f"{API_URL_PREFIX}my-learnings/blended-learning-path/tracker/details/",
        views.UserBlendedLearningPathTrackerDetailsAPIView.as_view(),
    ),
    #------------Subscription Plan-------------#
    path(f"{API_URL_PREFIX}my-learnings/subscription-plan/home/", views.MySubscriptionPlanHomeAPIView.as_view()),
    path(
        f"{API_URL_PREFIX}subscription-my-learnings/tracker/<uuid>/start/",
        views.SubscriptionLearningTrackerStartAPIView.as_view(),
    ),
    # Course viewed
    path(
        f"{API_URL_PREFIX}subscription-my-learnings/learning-interface/tracker/course-module/<uuid>/viewed/",
        views.SubscriptionVisitedCourseModuleTrackerAPIView.as_view(),
    ),
    path(
        f"{API_URL_PREFIX}subscription-my-learnings/learning-interface/tracker/course-sub-module/<uuid>/viewed/",
        views.SubscriptionVisitedCourseSubModuleTrackerAPIView.as_view(),
    ),
    # Learning Path Viewed
    path(
        f"{API_URL_PREFIX}subscription-my-learnings/learning-interface/tracker/learning-path-course/<uuid>/viewed/",
        views.SubscriptionVisitedLearningPathCourseTrackerAPIView.as_view(),
    ),
    path(
        f"{API_URL_PREFIX}subscription-my-learnings/learning-interface/tracker/learning-path-course-module/<uuid>/viewed/",
        views.SubscriptionVisitedLearningPathCourseModuleTrackerAPIView.as_view(),
    ),
    path(
        f"{API_URL_PREFIX}subscription-my-learnings/learning-interface/tracker/learning-path-course-sub-module/<uuid>/viewed/",
        views.SubscriptionVisitedLearningPathCourseSubModuleTrackerAPIView.as_view(),
    ),
    # Certification Path Viewed
    path(
        f"{API_URL_PREFIX}my-learnings/learning-interface/tracker/certificate-path-learning-path/<uuid>/viewed/",
        views.SubscriptionVisitedCertificatePathLearningPathTrackerAPIView.as_view(),
    ),
    path(
        f"{API_URL_PREFIX}my-learnings/learning-interface/tracker/certificate-path-course/<uuid>/viewed/",
        views.SubscriptionVisitedCertificatePathLearningPathCourseTrackerAPIView.as_view(),
    ),
    path(
        f"{API_URL_PREFIX}my-learnings/learning-interface/tracker/certificate-path-course-module/<uuid>/viewed/",
        views.SubscriptionVisitedCertificatePathLearningPathCourseModuleTrackerAPIView.as_view(),
    ),
    path(
        f"{API_URL_PREFIX}my-learnings/learning-interface/tracker/certificate-path-course-sub-module/<uuid>/viewed/",
        views.SubscriptionVisitedCertificatePathLearningPathCourseSubModuleTrackerAPIView.as_view(),
    ),


    #------------Skill Based Learning Tracker-------------#
    path(f"{API_URL_PREFIX}my-learnings/skill-based-learning/home/", views.MySkillHomeAPIView.as_view()),
    path(f"{API_URL_PREFIX}my-learnings/skill-based-learning/<uuid>/start/", views.SkillStartAPIView.as_view()),

    # Course viewed
    path(
        f"{API_URL_PREFIX}skill-my-learnings/learning-interface/tracker/course-module/<uuid>/viewed/",
        views.SkillVisitedCourseModuleTrackerAPIView.as_view(),
    ),
    path(
        f"{API_URL_PREFIX}skill-my-learnings/learning-interface/tracker/course-sub-module/<uuid>/viewed/",
        views.SkillVisitedCourseSubModuleTrackerAPIView.as_view(),
    ),
    # Learning Path Viewed
    path(
        f"{API_URL_PREFIX}skill-my-learnings/learning-interface/tracker/learning-path-course/<uuid>/viewed/",
        views.SkillVisitedLearningPathCourseTrackerAPIView.as_view(),
    ),
    path(
        f"{API_URL_PREFIX}skill-my-learnings/learning-interface/tracker/learning-path-course-module/<uuid>/viewed/",
        views.SkillVisitedLearningPathCourseModuleTrackerAPIView.as_view(),
    ),
    path(
        f"{API_URL_PREFIX}skill-my-learnings/learning-interface/tracker/learning-path-course-sub-module/<uuid>/viewed/",
        views.SkillVisitedLearningPathCourseSubModuleTrackerAPIView.as_view(),
    ),
    # Certification Path Viewed
    path(
        f"{API_URL_PREFIX}skill-my-learnings/learning-interface/tracker/certificate-path-learning-path/<uuid>/viewed/",
        views.SkillVisitedCertificatePathLearningPathTrackerAPIView.as_view(),
    ),
    path(
        f"{API_URL_PREFIX}skill-my-learnings/learning-interface/tracker/certificate-path-course/<uuid>/viewed/",
        views.SkillVisitedCertificatePathLearningPathCourseTrackerAPIView.as_view(),
    ),
    path(
        f"{API_URL_PREFIX}skill-my-learnings/learning-interface/tracker/certificate-path-course-module/<uuid>/viewed/",
        views.SkillVisitedCertificatePathLearningPathCourseModuleTrackerAPIView.as_view(),
    ),
    path(
        f"{API_URL_PREFIX}skill-my-learnings/learning-interface/tracker/certificate-path-course-sub-module/<uuid>/viewed/",
        views.SkillVisitedCertificatePathLearningPathCourseSubModuleTrackerAPIView.as_view(),
    ),


    # my certification urls
    path(f"{API_URL_PREFIX}my-learnings/certificate/list/", views.MyLearningsCertificateListAPIView.as_view()),

    path(f"{API_URL_PREFIX}my-learnings/certificate/<uuid>/download/", views.MyLearningsCertificateDownloadAPIView.as_view()),

    # my learnings notes urls
    path(f"{API_URL_PREFIX}my-learnings/notes/", views.MyLearningsNotesAPIView.as_view(), name='mylearningsnotes'),
    path(f"{API_URL_PREFIX}my-learnings/notes/<int:pk>/", views.MyLearningsNotesAPIView.as_view(), name='mylearningsnotes-detail'),
    path(f"{API_URL_PREFIX}my-learnings/notes/<uuid>/list/", views.MyLearningsNotesListAPIView.as_view()),
    path(f"{API_URL_PREFIX}my-learnings/<uuid>/overallnotes/list/", views.MyLearningsOverallNotesListAPIView.as_view()),
    path(f"{API_URL_PREFIX}my-learnings/<uuid>/overallnotes/meta/",views.MyLearningsNotesFilterMetaAPIView.as_view()),

    #my learnings video bookmark urls
    path(
            f"{API_URL_PREFIX}purchase/sub-module/<uuid>/add-to-bookmark/",
            views.EntityAddToBookMarkAPIView.as_view(),
        ),
    path(
        f"{API_URL_PREFIX}purchase/my-bookmarklist/",
        views.MySubModulesVideoBookMarkAPIView.as_view(),
    ),
    # Student My learning
    path(f"{API_URL_PREFIX}student-my-learnings/home/", views.StudentMyCourseLearningsHomeAPIView.as_view()),

    # Student My learning Learning Path
    path(f"{API_URL_PREFIX}student-my-learnings/learning-path/home/", views.StudentMyLearningPathHomeAPIView.as_view()),
    # Student My learning Certification Path
    path(f"{API_URL_PREFIX}student-my-learnings/certification-path/home/", views.StudentMyCertificatePathHomeAPIView.as_view()),
    path(
        f"{API_URL_PREFIX}student-my-learnings/learning-path/tracker/<uuid>/start/",
        views.StudentLearningPathTrackerStartAPIView.as_view(),
    ),
    path(
        f"{API_URL_PREFIX}student-my-learnings/certification-path/tracker/<uuid>/start/",
        views.StudentCertificatePathTrackerStartAPIView.as_view(),
    ),
    path(
        f"{API_URL_PREFIX}student-my-learnings/tracker/<uuid>/start/",
        views.StudentLearningTrackerStartAPIView.as_view(),
    ),
    path(
        f"{API_URL_PREFIX}student-my-learnings/learning-interface/tracker/course-module/<uuid>/viewed/",
        views.StudentVisitedCourseModuleTrackerAPIView.as_view(),
    ),
    path(
        f"{API_URL_PREFIX}student-my-learnings/learning-interface/tracker/course-sub-module/<uuid>/viewed/",
        views.StudentVisitedCourseSubModuleTrackerAPIView.as_view(),
    ),
    path(
        f"{API_URL_PREFIX}student-my-learnings/learning-interface/tracker/learning-path-course/<uuid>/viewed/",
        views.StudentVisitedLearningPathCourseTrackerAPIView.as_view(),
    ),
    path(
        f"{API_URL_PREFIX}student-my-learnings/learning-interface/tracker/learning-path-course-module/<uuid>/viewed/",
        views.StudentVisitedLearningPathCourseModuleTrackerAPIView.as_view(),
    ),
    path(
        f"{API_URL_PREFIX}student-my-learnings/learning-interface/tracker/learning-path-course-sub-module/<uuid>/viewed/",
        views.StudentVisitedLearningPathCourseSubModuleTrackerAPIView.as_view(),
    ),
    path(
        f"{API_URL_PREFIX}course/<uuid>/rating/",
        views.CourseRatingAPIView.as_view(),
    ),
    path(
        f"{API_URL_PREFIX}learning-content/<uuid>/feedback/",
        views.LearningContentFeedbackAPIView.as_view(),
    ),
    path(
        f"{API_URL_PREFIX}course/<uuid>/completed/page/",
        views.CourseCompletedPageAPIView.as_view(),
    ),
    #---------------------Blended Learning Path, Course , module, sub module trackers----------------------#

    path(f"{API_URL_PREFIX}my-learnings/blended-learning-path/home/", views.MyBlendedLearningPathHomeAPIView.as_view()),
    path(
        f"{API_URL_PREFIX}my-learnings/learning-interface/tracker/blended-learning-path-course/<uuid>/viewed/",
        views.UserVisitedBlendedLearningPathCourseTrackerAPIView.as_view(),
    ),
    path(
        f"{API_URL_PREFIX}my-learnings/learning-interface/tracker/blended-learning-path-course-module/<uuid>/viewed/",
        views.UserVisitedBlendedLearningPathCourseModuleTrackerAPIView.as_view(),
    ),
    path(
        f"{API_URL_PREFIX}my-learnings/learning-interface/tracker/blended-learning-path-course-sub-module/<uuid>/viewed/",
        views.UserVisitedBlendedLearningPathCourseSubModuleTrackerAPIView.as_view(),
    ),

    #------------Job Eligible Skill-------------#
    path(f"{API_URL_PREFIX}my-learnings/job-eligible-skill/home/", views.MyJobEligibleSkillHomeAPIView.as_view()),
    path(
        f"{API_URL_PREFIX}job-skill-my-learnings/tracker/<uuid>/start/",
        views.JobEligibleSkillLearningTrackerStartAPIView.as_view(),
    ),
    # Course viewed
    path(
        f"{API_URL_PREFIX}job-skill-my-learnings/learning-interface/tracker/course-module/<uuid>/viewed/",
        views.JobEligibleSkillVisitedCourseModuleTrackerAPIView.as_view(),
    ),
    path(
        f"{API_URL_PREFIX}job-skill-my-learnings/learning-interface/tracker/course-sub-module/<uuid>/viewed/",
        views.JobEligibleSkillVisitedCourseSubModuleTrackerAPIView.as_view(),
    ),
    # Learning Path Viewed
    path(
        f"{API_URL_PREFIX}job-skill-my-learnings/learning-interface/tracker/learning-path-course/<uuid>/viewed/",
        views.JobEligibleSkillVisitedLearningPathCourseTrackerAPIView.as_view(),
    ),
    path(
        f"{API_URL_PREFIX}job-skill-my-learnings/learning-interface/tracker/learning-path-course-module/<uuid>/viewed/",
        views.JobEligibleSkillVisitedLearningPathCourseModuleTrackerAPIView.as_view(),
    ),
    path(
        f"{API_URL_PREFIX}job-skill-my-learnings/learning-interface/tracker/learning-path-course-sub-module/<uuid>/viewed/",
        views.JobEligibleSkillVisitedLearningPathCourseSubModuleTrackerAPIView.as_view(),
    ),
    # Certification Path Viewed
    path(
        f"{API_URL_PREFIX}job-skill-my-learnings/learning-interface/tracker/certificate-path-learning-path/<uuid>/viewed/",
        views.JobEligibleSkillVisitedCertificatePathLearningPathTrackerAPIView.as_view(),
    ),
    path(
        f"{API_URL_PREFIX}job-skill-my-learnings/learning-interface/tracker/certificate-path-course/<uuid>/viewed/",
        views.JobEligibleSkillVisitedCertificatePathLearningPathCourseTrackerAPIView.as_view(),
    ),
    path(
        f"{API_URL_PREFIX}job-skill-my-learnings/learning-interface/tracker/certificate-path-course-module/<uuid>/viewed/",
        views.JobEligibleSkillVisitedCertificatePathLearningPathCourseModuleTrackerAPIView.as_view(),
    ),
    path(
        f"{API_URL_PREFIX}job-skill-my-learnings/learning-interface/tracker/certificate-path-course-sub-module/<uuid>/viewed/",
        views.JobEligibleSkillVisitedCertificatePathLearningPathCourseSubModuleTrackerAPIView.as_view(),
    ),
]