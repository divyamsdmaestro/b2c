from django.urls import path
from apps.cms.views.skills import BulkSkillArchiveAPIView
from apps.payments.models.subscription_plan import SubscriptionPlanCustomerEnquiry
from rest_framework.routers import SimpleRouter
from apps.cms.views.applicant import AdminStudentOneProfileAPIView, FresherPoolListAPIView, FresherPoolsMeta, UpdateApplicantListStatus, UpdateFresherPoolApplicantStatus
from apps.cms.views.forum import DeleteForumComment
from apps.cms.views.learning_content import LearningContentAPIView, AllLearningContentAPIView, LearningContentFeedbackAPIView, LearningContentFeedbackMeta
from apps.cms.views.skills import BulkSkillArchiveAPIView

from apps.meta.serializers import BLPAddressListModelSerializer

from apps.cms.views.subscription_plan import SubscriptionPlanListAPIView, SubscriptionPlanStatusUpdateAPIView
from apps.ecash.models import EcashMeta,Ecash
# from apps.badges.models import BadgesMeta,Badges,BadgeImage
from apps.learning.models.mml_course import MMLCourse
from ..webinars.models import *
from apps.learning.models import certificate as certificate_models
from apps.jobs.models import EducationQualification, JobInterviewSchedule, Job, JobFeedbackAttachment, JobFeedbackTemplate
from ..common.views.api import get_upload_api_view, get_upload_non_auth_api_view
from ..learning.models import (
    Accreditation,
    Author,
    Tutor,
    AuthorImage,
    Category,
    CategoryImage,
    CategoryPopularity,
    CertificationPath,
    CertificationPathImage,
    CertificationPathLearningPath,
    CertificationPathLevel,
    Course,
    CourseImage,
    ModuleTypeDocument,
    CourseResource,
    CourseLevel,
    CourseModule,
    CourseSubModule,
    Language,
    LearningPath,
    LearningPathCourse,
    LearningPathImage,
    LearningPathLevel,
    Proficiency,
    Skill,
    SkillImage,
    SkillPopularity,
    JobEligibleSkill,
    JobEligibleSkillImage,
    Tag,
    Vendor,
    VendorImage,
    LearningRoleImage,
    LearningRole,
    ModuleType,
    BlendedLearningPathImage,
    BlendedLearningPathLevel,
    BlendedLearningPath,
    BlendedLearningPathCourseMode,
    BlendedLearningPathCourseModesAndFee,
    BlendedLearningPathLearningType,
    BlendedLearningClassroomAndVirtualDetails,
    BlendedLearningPathCustomerEnquiry,
    BlendedLearningPathPriceDetails,
    BlendedLearningPathScheduleDetails
)
from ..meta.models import FrequentlyAskedQuestion, City, State, Country, BLPAddress
from ..payments.models import Discount, SaleDiscount
from ..forums.models import ForumImage, Forum, ZoneImage, Zone, ZoneType
from ..payments.models import Discount, SaleDiscount,SubscriptionPlanImage, SubscriptionPlan, SubscriptionPlanSaleDiscount
# from ..zones.models import ZoneImage, Zone, ZonePostType
from ..access.models import (
    User, 
    Permission, 
    UserRole, 
    RolePermission, 
    InstitutionBannerImage, 
    InstitutionDetail, 
    PermissionCategory, 
    InstitutionUserGroupDetail, 
    InstitutionUserGroupContent,
    EmployerLogoImage,
    EmployerDetail,
)
from ..service_idp.views import proxy_to_idp_view
from ..web_portal.models import Testimonial, TestimonialImage
from .views import (
    AdminCMSDynamicConfigAPIView,
    AdminHomeAPIView,
    AdminDetailHomeAPIView,
    CreateUserAPIView,
    VideoLinkAPIView,
    UpdateUserAPIView,
    EmployerDashboardAPIView,
    InstitutionAdminDashboardAPIView,
    InstitutionAdminDashboardTrendingAPIView,
    CreateInstitutionAPIView,
    UpdateInstitutionAPIView,
    CreateInstitutionUserGroupAPIView,
    UpdateInstitutionUserGroupAPIView,
    DetailInstitutionUserGroupAPIView,
    MetaInstitutionUserGroupAPIView,
    MetaInstitutionUserGroupContentAPIView,
    ReportGenerateAPIView,
    ReportGenerateMetaAPIView,
    ReportListAPIView,
    ReportDeleteAPIView,
    get_model_cud_api_viewset,
    get_model_list_api_viewset,
    get_student_list_api_viewset,
    get_staff_list_api_viewset,
    get_institution_user_group_list_api_viewset,
    get_institution_user_group_content_list_api_viewset,
    get_interview_panel_list_api_viewset,
    get_interview_schedule_list_api_viewset,
    get_schedule_list_for_interview_panel_api_viewset,
    get_job_feedback_template_list_api_viewset,
    StudentCreateAPIView,
    StudentEditAPIView,
    StudentDeleteAPIView,
    StudentDetailAPIView,
    StudentMyLearningsAPIView,
    StaffEditAPIView,
    StaffCreateAPIView,
    StaffDeleteAPIView,
    StaffDetailAPIView,
    CourseBulkUploadAPIView,
    SubscriptionPlanDetailView,
    CreateHackathonUpdate,
    CreateEmployerAPIView,
    UpdateEmployerAPIView,
    LearningContentMetaAPIView,
    LogoImageAPIView,
    CreateInterviewPanelAPIView,
    UpdateInterviewPanelAPIView,
    MetaInterviewScheduleAPIView,
    InterviewScheduleApplicantListAPIView,
    SendFeedbackInterviewPanelMetaAPIView,
    SendFeedbackInterviewPanelAPIView,
    JobFeedbackOption,
    FeedbackInterviewPanelAPIView,
    StudentsBulkUploadAPIView,
    LogoImageAPIView,
    BlogDetailAPIView,
    BlogLikeAPIView,
    BlogCommentListAPIView,
    BlogCommentReplyListAPIView,
    BlogArchieveAPIView,
    BlogApproveAPIView,
    BlogDeclineAPIView,
    DetailInstitutionUserGroupContentAPIView,
    UsersBulkUploadAPIView,
    WebinarRegistrationListAPIViewset,
    SubPlanBulkUploadAPIView,
    SubPlanModuleBulkUploadAPIView,
    SubPlanSubModuleBulkUploadAPIView,
    BlendedLearningPathCustomerOnlineListAPIViewset,
    BlendedLearningPathCustomerClassroomListAPIViewset,
)
from apps.meta.models import location as location_models
from apps.meta.models import profile as profile_models
from apps.learning.models import certificate as certificate_models
from apps.hackathons.models import hackathon as hackathon_models
from apps.hackathons.models import round_details as round_models
from apps.payments.models import sale_discount as salediscount_models
from apps.common.serializers import get_app_read_only_serializer as read_serializer, get_app_read_only_optimize_serializer
from apps.hackathons.models import prizes as prize_models
from apps.hackathons.models import industry as industry_models
from apps.cms.views import (
    ForumPostListAPIView,
    ForumPostLikeAPIView, 
    ForumPostCommentListAPIView, 
    ForumPostReplyListAPIView, 
    PostPollOptionClickAPIView, 
    HackathonDiscussionListAPIView, 
    HackathonDiscussionReplyListAPIView, 
    HackathonDiscussionCommentListAPIView,
    ZoneListAPIView,
    ZoneDetailAPIView,
    WebinarDiscussionListAPIView,
    WebinarDiscussionCommentListAPIView,
    WebinarDiscussionReplyListAPIView,
    CreateBlendedLearningAPIView,
    UpdateBlendedLearningAPIView,
    BlendedLearningModeAndFeeListAPIViewSet,
    BlendedLearningClassroomAndVirtualListAPIViewSet,
    BlendedLearningPathCustomerOnlineListTableMetaAPIViewset,
    BlendedLearningPathCustomerClassroomListTableMetaAPIViewset,
)
from apps.forums.models import Post, PostType, PostImage, PostComment, PostReply, SubjectivePostImage
from apps.access.models import User, StudentReportDetail, ReportFilterParameter
from apps.jobs.models import linkages as linkage_models
from apps.blogs.models import Blog,BlogComment,BlogCommentReply,BlogImage
from django.db.models import Q
from apps.jobs.models import NewsDetail, NewsThumbnailImage,BulkUploadTemplateData,BulkUploadTemplate
from apps.service_idp.views import CMSLoginAPIView, LogoutAPIView
from apps.my_learnings.models import UserBlendedLearningPathTracker

app_name = "cms"
API_URL_PREFIX = "api/cms/"
API_PROXY_URL_PREFIX = "api/cms/proxy/"

router = SimpleRouter()

# Identity Only Models
# --------------------------------------------------------------------------------------
identity_only_models_config = {
    # identity only models related to learning
    CourseLevel.DYNAMIC_KEY: CourseLevel,
    Accreditation.DYNAMIC_KEY: Accreditation,
    Tag.DYNAMIC_KEY: Tag,
    # Category.DYNAMIC_KEY: Category,
    CategoryPopularity.DYNAMIC_KEY: CategoryPopularity,
    LearningPathLevel.DYNAMIC_KEY: LearningPathLevel,
    CertificationPathLevel.DYNAMIC_KEY: CertificationPathLevel,
    Proficiency.DYNAMIC_KEY: Proficiency,
    SkillPopularity.DYNAMIC_KEY: SkillPopularity,
    linkage_models.EducationQualification.DYNAMIC_KEY: linkage_models.EducationQualification,
    linkage_models.JobCriteria.DYNAMIC_KEY: linkage_models.JobCriteria,
    certificate_models.CertificateLearningType.DYNAMIC_KEY: certificate_models.CertificateLearningType
}
for key, model in identity_only_models_config.items():
    router.register(
        f"{API_URL_PREFIX}{key}/cud",
        get_model_cud_api_viewset(meta_model=model, meta_fields=["identity"]),
    )
    router.register(
        f"{API_URL_PREFIX}{key}/list",
        get_model_list_api_viewset(
            meta_queryset=model.objects.all(),
            meta_all_table_columns={"identity": "Name"},
        ),
    )

# Identity + Image Models
# --------------------------------------------------------------------------------------
identity_image_models_config = {
    Vendor.DYNAMIC_KEY: Vendor,
    # Category.DYNAMIC_KEY: Category,
}
for key, model in identity_image_models_config.items():
    router.register(
        f"{API_URL_PREFIX}{key}/cud",
        get_model_cud_api_viewset(meta_model=model, meta_fields=["identity", "image"]),
    )
    router.register(
        f"{API_URL_PREFIX}{key}/list",
        get_model_list_api_viewset(
            meta_queryset=model.objects.all(),
            meta_all_table_columns={"identity": "Name"},
        ),
    )

# Access Control - Permission
# --------------------------------------------------------------------------------------
router.register(
    f"{API_URL_PREFIX}{Permission.DYNAMIC_KEY}/cud",
    get_model_cud_api_viewset(
        meta_model=Permission, meta_fields=["identity", "description"]
    ),
)
router.register(
    f"{API_URL_PREFIX}{Permission.DYNAMIC_KEY}/list",
    get_model_list_api_viewset(
        meta_queryset=Permission.objects.all(),
        meta_all_table_columns={"identity": "Name"},
    ),
)

# Access Control - Permission Category
# --------------------------------------------------------------------------------------
router.register(
    f"{API_URL_PREFIX}{PermissionCategory.DYNAMIC_KEY}/cud",
    get_model_cud_api_viewset(
        meta_model=PermissionCategory, meta_fields=["identity", "permissions"],
        get_serializer_meta=lambda x: {
            "permissions": x.serialize_for_meta(Permission.objects.all())
        },
    ),
)
router.register(
    f"{API_URL_PREFIX}{PermissionCategory.DYNAMIC_KEY}/list",
    get_model_list_api_viewset(
        meta_queryset=PermissionCategory.objects.all(),
        meta_all_table_columns={"identity": "Name"},
        meta_init_fields_config={
        "permission": read_serializer(
            meta_model=Permission, meta_fields=["id", "identity", "description"],
        )(many=True, source="permissions"),
        },
    ),
)

# Access Control - Role
# --------------------------------------------------------------------------------------
router.register(
    f"{API_URL_PREFIX}{UserRole.DYNAMIC_KEY}/cud",
    get_model_cud_api_viewset(
        meta_model=UserRole, meta_fields=["identity", "description", "role_permissions"],
    ),
)
router.register(
    f"{API_URL_PREFIX}{UserRole.DYNAMIC_KEY}/list",
    get_model_list_api_viewset(
        meta_queryset=UserRole.objects.all(),
        meta_all_table_columns={"identity": "Name", "description": "Description"},
        meta_init_fields_config={
        "role_permission": read_serializer(
            meta_model=RolePermission, meta_fields=['to_create', 'to_view', 'to_edit', 'to_delete'],
            init_fields_config={
                "permissions": read_serializer(
                    meta_model=Permission, meta_fields=['id', 'identity', 'category']
                )(source="permission"),
            }
        )(many=True, source="role_permissions"),
        },
    ),
)


# User
# --------------------------------------------------------------------------------------
router.register(
    f"{API_URL_PREFIX}user/cud",
    get_model_cud_api_viewset(
        meta_model=User, meta_fields=['user_role', 'first_name', 'middle_name', 'last_name', 'alternative_email', 'address', 'country', 'state', 'city', 'pincode'],
        meta_extra_kwargs={
            "user_role": {"allow_empty": False},
        },
        get_serializer_meta=lambda x: {
            "user_role": x.serialize_for_meta(UserRole.objects.all()),
            "country": x.serialize_for_meta(location_models.Country.objects.all()),
            "state": x.serialize_for_meta(location_models.State.objects.all(), fields=['id', 'uuid', 'identity','country']),
            "city": x.serialize_for_meta(location_models.City.objects.all(),  fields=['id', 'uuid', 'identity','state']),
        },
    ),
)
router.register(
    f"{API_URL_PREFIX}user/list",
    get_model_list_api_viewset(
        meta_queryset=User.objects.all(),
        meta_all_table_columns={
            "first_name": "Name",
            # "user_role": "User Role",
            "user_role__identity": "Role Identity",
            "status": "Status",
            # "created_by": "Created By"
        },
        meta_init_fields_config={
            "role": read_serializer(
                meta_model=UserRole, meta_fields=['id', 'identity'],
            )(source="user_role"),
        },
    ),
)

# User Group
# --------------------------------------------------------------------------------------
router.register(
    f"{API_URL_PREFIX}user-group/cud",
    get_model_cud_api_viewset(
        meta_model=InstitutionUserGroupDetail, meta_fields=["identity", "description", "user"],
        get_serializer_meta=lambda x: {
            "user": x.serialize_for_meta(User.objects.filter(Q(user_role__identity__icontains="Learner") | Q(user_role__identity__icontains="Student")),fields=['id','uuid', 'first_name', 'user_role', 'user_role__identity', 'alternative_email', 'idp_email']),
        },
    ),
)

router.register(
    f"{API_URL_PREFIX}user-group/list",
    get_model_list_api_viewset(
        meta_queryset=InstitutionUserGroupDetail.objects.filter(admin_created=True),
        meta_all_table_columns={
            "identity" : "Group Name",
            "description": "Group Description",
            "created": "Created On",
            "status": "Status"
        },
    ),
)

# Employer
# --------------------------------------------------------------------------------------
router.register(
    f"{API_URL_PREFIX}corporate/cud",
    get_model_cud_api_viewset(
        meta_model=EmployerDetail,
        meta_fields=[
            "identity",
            "description",
            "logo_image",
            "contact_email_id",
            "alternative_conatct_email_id",
            "contact_number",
            "locality_street_address",
            "country",
            "state",
            "city",
            "pincode",
            "representative",
        ],
        meta_extra_kwargs={
            "user_role": {"allow_empty": False},
        },
        get_serializer_meta=lambda x: {
            "city": x.serialize_for_meta(City.objects.all(), fields=['id', 'uuid', 'identity','state']),
            "state": x.serialize_for_meta(State.objects.all(), fields=['id', 'uuid', 'identity','country']),
            "country": x.serialize_for_meta(Country.objects.all()),
            "user_role": x.serialize_for_meta(UserRole.objects.all()),
        },
    ),
)

router.register(
    f"{API_URL_PREFIX}corporate/list",
    get_model_list_api_viewset(
        meta_queryset=EmployerDetail.objects.all(),
        meta_all_table_columns={
            "identity" : "Company Name",
            "locality_street_address": "Company Address",
            "contact_email_id": "Email",
            "contact_number": "Contact Number"
        },
        meta_init_fields_config={
        "representatives": read_serializer(
            meta_model=User, meta_fields=['id', 'first_name', 'middle_name', 'last_name', ],
        )(source="representative"),
        }
    ),
)

# Interview Pannel
# --------------------------------------------------------------------------------------
router.register(
    f"{API_URL_PREFIX}interview-panel/cud",
    get_model_cud_api_viewset(
        meta_model=User, 
        meta_fields=[
            'user_role',
            'first_name', 
            'middle_name', 
            'last_name', 
            'alternative_email', 
            'job_role', 
            'experience_years', 
            'industry_type', 
            'address', 
            'country', 
            'state', 
            'city', 
            'pincode'
        ],
        meta_extra_kwargs={
            "user_role": {"allow_empty": False},
        },
        get_serializer_meta=lambda x: {
            "user_role": x.serialize_for_meta(UserRole.objects.all()),
            "industry_type": x.serialize_for_meta(industry_models.IndustryType.objects.all(), fields=['id', 'uuid', 'identity']),
            "country": x.serialize_for_meta(location_models.Country.objects.all()),
            "state": x.serialize_for_meta(location_models.State.objects.all(), fields=['id', 'uuid', 'identity','country']),
            "city": x.serialize_for_meta(location_models.City.objects.all(), fields=['id', 'uuid', 'identity','state']),
        },
    ),
)
router.register(
    f"{API_URL_PREFIX}interview-panel/list",
    get_interview_panel_list_api_viewset(
        meta_queryset=User.objects.all(),
        meta_all_table_columns={
            "first_name": "Name",
            "job_role": "Job Role",
            "experience_years": "Experience Years",
            "created": "Created On"
        },
        meta_init_fields_config={
            "role": read_serializer(
                meta_model=UserRole, meta_fields=['id', 'identity'],
            )(source="user_role"),
        },
        fields_to_filter=["first_name"],
    ),
)

# Interview Schedule
router.register(
    f"{API_URL_PREFIX}interview-schedule/cud",
    get_model_cud_api_viewset(
        meta_model=JobInterviewSchedule, 
        meta_fields=[
            'identity',
            'description',
            'applicant', 
            'job', 
            'job_round', 
            'schedule_date', 
            'start_time', 
            'end_time', 
            'interview_link', 
            'interview_panel',
            'interview_feedback_template',
        ],
    ),
)
router.register(
    f"{API_URL_PREFIX}interview-schedule/list",
    get_interview_schedule_list_api_viewset(
        meta_queryset=JobInterviewSchedule.objects.all(),
        meta_all_table_columns={
            "identity": "Title",
            "schedule_date": "Schedule Date",
            "start_time": "Schedule Time",
            "user__identity": "Applicant Name",
            "job_detail__identity": "Applied For Job",
        },
        meta_init_fields_config={
            "user": read_serializer(
                meta_model=User, meta_fields=['id', 'first_name'],
            )(source="applicant"),
            "job_detail": read_serializer(
                meta_model=Job, meta_fields=['id', 'identity'],
            )(source="job"),
        },
        fields_to_filter=["identity"],
    ),
)

# Interview Feedback Template
router.register(
    f"{API_URL_PREFIX}{JobFeedbackTemplate.DYNAMIC_KEY}/cud",
    get_model_cud_api_viewset(
        meta_model=JobFeedbackTemplate, 
        meta_fields=[
            'identity',
            'description',
            'industry_type', 
            'comment_box_enable', 
            'attachment_enable',
            'feedback_question',
        ],
        get_serializer_meta=lambda x: {
            "industry_type": x.serialize_for_meta(industry_models.IndustryType.objects.all()),
        },
    ),
)
router.register(
    f"{API_URL_PREFIX}{JobFeedbackTemplate.DYNAMIC_KEY}/list",
    get_job_feedback_template_list_api_viewset(
        meta_queryset=JobFeedbackTemplate.objects.all(),
        meta_all_table_columns={
            "identity": "Title",
            "description": "Description",
            "industry_type": "Industry Type",
            "created": "Created On",
        },
        fields_to_filter=["identity"],
    ),
)

# Interview Scheduled List
# --------------------------------------------------------------------------------------
router.register(
    f"{API_URL_PREFIX}scheduled-interview/list",
    get_schedule_list_for_interview_panel_api_viewset(
        meta_queryset=JobInterviewSchedule.objects.all(),
        meta_all_table_columns={
            "uuid": "UUID",
            "identity" : "Schedule Title",
            "schedule_date": "Schedule Date",
            "start_time": "Schedule Time",
            "end_time": "End Time",
            "applicant__first_name": "Applicant Name",
            "job__identity": "Applied For Job"
        },
    ),
)

# Interview Scheduled Applicant List
# --------------------------------------------------------------------------------------
router.register(
    f"{API_URL_PREFIX}scheduled-interview-applicant/list",
    get_schedule_list_for_interview_panel_api_viewset(
        meta_queryset=JobInterviewSchedule.objects.all(),
        meta_all_table_columns={
            "uuid": "UUID",
            "applicant__first_name": "Applicant Name",
            "job__identity": "Applied For Job",
            "applicant__idp_email": "Contact Email"
        },
    ),
)

# Institution
# --------------------------------------------------------------------------------------
router.register(
    f"{API_URL_PREFIX}institution/cud",
    get_model_cud_api_viewset(
        meta_model=InstitutionDetail,
        meta_fields=[
            "identity",
            "banner_image",
            "contact_email_id",
            "alternative_conatct_email_id",
            "contact_number",
            "accreditation",
            "locality_street_address",
            "country",
            "state",
            "city",
            "pincode",
            "courses",
            "learning_paths",
            "certification_paths",
            "representative",
        ],
        meta_extra_kwargs={
            "user_role": {"allow_empty": False},
        },
        get_serializer_meta=lambda x: {
            "accreditation": x.serialize_for_meta(Accreditation.objects.all()),
            "city": x.serialize_for_meta(City.objects.all(), fields=['id', 'uuid', 'identity','state']),
            "state": x.serialize_for_meta(State.objects.all(), fields=['id', 'uuid', 'identity','country']),
            "country": x.serialize_for_meta(Country.objects.all()),
            "user_role": x.serialize_for_meta(UserRole.objects.all()),
            "courses": x.serialize_for_meta(Course.objects.all(), fields=['id', 'uuid', 'identity', 'description', 'code', 'image__file', 'level__identity', 'duration', 'author__identity', 'rating']),
            "learning_paths": x.serialize_for_meta(LearningPath.objects.all(), fields=['id', 'uuid', 'identity', 'description', 'code', 'image__file', 'level__identity', 'duration', 'rating']),
            "certification_paths": x.serialize_for_meta(CertificationPath.objects.all(), fields=['id', 'uuid', 'identity', 'description', 'code', 'image__file', 'level__identity', 'duration', 'rating']),
        },
    ),
)

router.register(
    f"{API_URL_PREFIX}institution/list",
    get_model_list_api_viewset(
        meta_queryset=InstitutionDetail.objects.all(),
        meta_all_table_columns={
            "identity" : "Institution Name",
            "locality_street_address": "Institution Address",
            "contact_email_id": "Email",
            "contact_number": "Contact Number"
        },
        meta_init_fields_config={
        "representatives": read_serializer(
            meta_model=User, meta_fields=['id', 'first_name', 'middle_name', 'last_name', ],
        )(source="representative"),
        }
    ),
)

# Institution User Group
# --------------------------------------------------------------------------------------
router.register(
    f"{API_URL_PREFIX}{InstitutionUserGroupDetail.DYNAMIC_KEY}/cud",
    get_model_cud_api_viewset(
        meta_model=InstitutionUserGroupDetail, meta_fields=["identity", "description", "user"],
    ),
)

router.register(
    f"{API_URL_PREFIX}{InstitutionUserGroupDetail.DYNAMIC_KEY}/list",
    get_institution_user_group_list_api_viewset(
        meta_queryset=InstitutionUserGroupDetail.objects.all(),
        meta_all_table_columns={
            # "id": "ID",
            "uuid": "UUID",
            "identity" : "Group Name",
            "description": "Group Description",
            "created": "Created On",
            "status": "Status"
        },
    ),
)

# Institution User Group Content
# --------------------------------------------------------------------------------------
router.register(
    f"{API_URL_PREFIX}{InstitutionUserGroupContent.DYNAMIC_KEY}/cud",
    get_model_cud_api_viewset(
        meta_model=InstitutionUserGroupContent, meta_fields=["identity", "description", "user_group", "courses", "learning_path", "certification_path"],
    ),
)

router.register(
    f"{API_URL_PREFIX}{InstitutionUserGroupContent.DYNAMIC_KEY}/list",
    get_institution_user_group_content_list_api_viewset(
        meta_queryset=InstitutionUserGroupContent.objects.all(),
        meta_all_table_columns={
            # "id": "ID",
            "uuid": "UUID",
            "identity" : "Group Name",
            "description": "Group Description",
            "created": "Created On",
            "status": "Status"
        },
    ),
)

# Learning Meta - Author/Tutor
# --------------------------------------------------------------------------------------
router.register(
    f"{API_URL_PREFIX}{Author.DYNAMIC_KEY}/cud",
    get_model_cud_api_viewset(
        meta_model=Author, meta_fields=["identity", "image", "designation", "rating","vendor"],
        get_serializer_meta=lambda x: {"vendor": x.serialize_for_meta(Vendor.objects.all())},
    ),
)
router.register(
    f"{API_URL_PREFIX}{Author.DYNAMIC_KEY}/list",
    get_model_list_api_viewset(
        meta_queryset=Author.objects.all(),
        meta_all_table_columns={"identity": "Name", "designation": "Designation"},
    ),
)

# Degree
# --------------------------------------------------------------------------------------
router.register(
    f"{API_URL_PREFIX}{Tutor.DYNAMIC_KEY}/cud",
    get_model_cud_api_viewset(
        meta_model=Tutor,
        meta_fields=["identity"],
        get_serializer_meta=lambda x: {},
    ),
)
router.register(
    f"{API_URL_PREFIX}{Tutor.DYNAMIC_KEY}/list",
    get_model_list_api_viewset(
        meta_queryset=Tutor.objects.all(),
        meta_all_table_columns={
            # "id": "ID",
            "identity": "Industry",
        },
    ),
)
# Learning Meta - FunctionalArea
router.register(
    f"{API_URL_PREFIX}{linkage_models.FunctionalArea.DYNAMIC_KEY}/cud",
    get_model_cud_api_viewset(
        meta_model=linkage_models.FunctionalArea, meta_fields=["identity", "image", "is_this_functional_area_popular"]
    ),
)
router.register(
    f"{API_URL_PREFIX}{linkage_models.FunctionalArea.DYNAMIC_KEY}/list",
    get_model_list_api_viewset(
        meta_queryset=linkage_models.FunctionalArea.objects.all(),
        meta_all_table_columns={"identity": "Name"},
    ),
)

# Learning Meta - Skill
# --------------------------------------------------------------------------------------
router.register(
    f"{API_URL_PREFIX}{Skill.DYNAMIC_KEY}/cud",
    get_model_cud_api_viewset(
        meta_model=Skill, meta_fields=["identity", "image", "description", "category", "make_this_skill_popular", "is_archived","current_price_inr", "assessmentID", "vm_name", "mml_sku_id"],
        meta_extra_kwargs={
            "category": {"allow_empty": False},
        },
        get_serializer_meta=lambda x: {
            "category": x.serialize_for_meta(Category.objects.all()),
        },
    ),
)
router.register(
    f"{API_URL_PREFIX}{Skill.DYNAMIC_KEY}/list",
    get_model_list_api_viewset(
        meta_queryset=Skill.objects.filter(is_archived=False),
        meta_all_table_columns={
            "identity": "Skill Name",
            "category__identity":"Category",
            "description": "description"
        },
        meta_init_fields_config={
            "category_details": read_serializer(
                meta_model=Category, meta_fields=['id', 'uuid', 'identity']
            )(many=True, source="category"),
            "skill_image": read_serializer(
                meta_model=SkillImage, meta_fields=['id','uuid','file']
            )(source="image"),
        },
        fields_to_filter=["identity"],
    ),
)

# Learning Meta - JobEligibleSkill
# --------------------------------------------------------------------------------------
router.register(
    f"{API_URL_PREFIX}{JobEligibleSkill.DYNAMIC_KEY}/cud",
    get_model_cud_api_viewset(
        meta_model = JobEligibleSkill,
        meta_fields = [
            "identity",
            "description",
            "image",
            "category",
            "make_this_skill_popular",
            "assessment_id",
            "courses",
            "learning_paths",
            "certification_paths",
            "current_price_inr",
        ],
        get_serializer_meta = lambda x:{
            "category": x.serialize_for_meta(Category.objects.all(), fields = ['id', 'uuid', 'identity']),
            "courses": x.serialize_for_meta(Course.objects.all(), fields=['id', 'uuid', 'identity', 'description', 'code', 'image__file', 'level__identity', 'duration', 'author__identity', 'rating']),
            "learning_paths": x.serialize_for_meta(LearningPath.objects.all(), fields=['id', 'uuid', 'identity', 'description', 'code', 'image__file', 'level__identity', 'duration', 'rating']),
            "certification_paths": x.serialize_for_meta(CertificationPath.objects.all(), fields=['id', 'uuid', 'identity', 'description', 'code', 'image__file', 'level__identity', 'duration', 'rating']),
        },
    )
)

router.register(
    f"{API_URL_PREFIX}{JobEligibleSkill.DYNAMIC_KEY}/list",
    get_model_list_api_viewset(
        meta_queryset = JobEligibleSkill.objects.all(),
        meta_all_table_columns = {
            "identity": "Title",
            "description": "Description",
        }
    )
)

# Learning Meta - Category
# --------------------------------------------------------------------------------------
router.register(
    f"{API_URL_PREFIX}{Category.DYNAMIC_KEY}/cud",
    get_model_cud_api_viewset(
        meta_model=Category, meta_fields=["identity", "image"]
    ),
)
router.register(
    f"{API_URL_PREFIX}{Category.DYNAMIC_KEY}/list",
    get_model_list_api_viewset(
        meta_queryset=Category.objects.all(),
        meta_all_table_columns={"identity": "Name"},
        meta_init_fields_config={
        "category_image": read_serializer(
            meta_model=CategoryImage, meta_fields=['id','uuid','file']
        )(source="image"),
        },
        fields_to_filter=["identity"],

    ),
)
# Learning  - EcashMeta
# --------------------------------------------------------------------------------------
router.register(
    f"{API_URL_PREFIX}{EcashMeta.DYNAMIC_KEY}/cud",
    get_model_cud_api_viewset(
        meta_model=EcashMeta, meta_fields=["identity"],
    ),
)
router.register(
    f"{API_URL_PREFIX}{EcashMeta.DYNAMIC_KEY}/list",
    get_model_list_api_viewset(
        meta_queryset=EcashMeta.objects.all(),
        meta_all_table_columns={"identity": "identity"},
    ),
)
# Learning  - Ecash
# --------------------------------------------------------------------------------------
router.register(
    f"{API_URL_PREFIX}{Ecash.DYNAMIC_KEY}/cud",
    get_model_cud_api_viewset(
        meta_model=Ecash, meta_fields=["name","points","ecashmeta","description"],
        get_serializer_meta=lambda x: {
            "ecashmeta": x.serialize_for_meta(EcashMeta.objects.all()),
        },
    ),
)
router.register(
    f"{API_URL_PREFIX}{Ecash.DYNAMIC_KEY}/list",
    get_model_list_api_viewset(
        meta_queryset=Ecash.objects.all(),
        meta_all_table_columns={"name":"Name","description":"Description","points":"Points"},
        meta_init_fields_config={
        "ecashmeta_details": read_serializer(
            meta_model=EcashMeta, meta_fields=['id','uuid','identity']
        )(source="ecashmeta"),
        },
        fields_to_filter=["ecashmeta"],
    )
)


# Learning  - BadgesMeta
# --------------------------------------------------------------------------------------
# router.register(
#     f"{API_URL_PREFIX}{BadgesMeta.DYNAMIC_KEY}/cud",
#     get_model_cud_api_viewset(
#         meta_model=BadgesMeta, meta_fields=["identity"],
#     ),
# )
# router.register(
#     f"{API_URL_PREFIX}{BadgesMeta.DYNAMIC_KEY}/list",
#     get_model_list_api_viewset(
#         meta_queryset=BadgesMeta.objects.all(),
#         meta_all_table_columns={"identity": "identity"},
#     ),
# )
# Learning  - Badges
# --------------------------------------------------------------------------------------
# router.register(
#     f"{API_URL_PREFIX}{Badges.DYNAMIC_KEY}/cud",
#     get_model_cud_api_viewset(
#         meta_model=Badges, meta_fields=["name","points","badgesmeta","image","description"],
#         get_serializer_meta=lambda x: {
#             "badgesmeta": x.serialize_for_meta(BadgesMeta.objects.all()),
#         },
#     ),
# )
# router.register(
#     f"{API_URL_PREFIX}{Badges.DYNAMIC_KEY}/list",
#     get_model_list_api_viewset(
#         meta_queryset=Badges.objects.all(),
#         meta_all_table_columns={"name":"Name","description":"Description","points":"Points"},
#         meta_init_fields_config={
#         "badgesmeta_details": read_serializer(
#             meta_model=BadgesMeta, meta_fields=['id','uuid','identity']
#         )(source="badgesmeta"),
#         "badge-image": read_serializer(
#                 meta_model=BadgeImage, meta_fields=['id', 'uuid', 'file']
#             )(source="image"),
#         },
#         fields_to_filter=["badgesmeta"],
#     )
# )

# Learning - Course
# --------------------------------------------------------------------------------------
router.register(
    f"{API_URL_PREFIX}{Course.DYNAMIC_KEY}/cud",
    get_model_cud_api_viewset(
        meta_model=Course,
        meta_fields=[
            "identity",
            "description",
            "is_certification_enabled",
            "image",
            "vendor",
            "author",
            "skills",
            "categories",
            "code",
            "level",
            "language",
            "duration",
            "start_date",
            "end_date",
            "enable_ratings",
            "rating",
            "enable_feedback_comments",
            "sequential_course_flow",
            "accreditation",
            "is_free",
            "requirements",
            "highlights",
            # "actual_price_inr",
            "current_price_inr",
            "complete_in_a_day",
            "make_this_course_popular",
            "make_this_course_best_selling",
            "make_this_course_trending",
            "editors_pick",
            "learning_role",
            "mml_sku_id",
            "vm_name",
            "is_private_course",
            "resource_title",
            "resource_type",
            "resource",
            "virtual_lab"
        ],
        meta_extra_kwargs={
            "skills": {"allow_empty": False},
            "categories": {"allow_empty": False},
        },
        get_serializer_meta=lambda x: {
            "author": x.serialize_for_meta(Author.objects.all(), fields=['id', 'identity', 'vendor']),
            "vendor": x.serialize_for_meta(Vendor.objects.all()),
            "skills": x.serialize_for_meta(Skill.objects.filter(is_archived=False), fields=['id', 'identity', 'category']),
            "categories": x.serialize_for_meta(Category.objects.all()),
            "language": x.serialize_for_meta(Language.objects.all()),
            "accreditation": x.serialize_for_meta(Accreditation.objects.all()),
            "level": x.serialize_for_meta(CourseLevel.objects.all()),
            "learning_role": x.serialize_for_meta(LearningRole.objects.all()),
        },
    ),
)
router.register(
    f"{API_URL_PREFIX}{Course.DYNAMIC_KEY}/list",
    get_model_list_api_viewset(
        meta_queryset=Course.objects.all(),
        meta_all_table_columns={"code": "Code", "identity": "Name",
                                "duration": "Duration",
                                "rating": "Rating", "description": "Description",},
        meta_init_fields_config={
            "level_details": read_serializer(
                meta_model=CourseLevel, meta_fields=['id', 'uuid', 'identity']
            )(source="level"),
            "author_details": read_serializer(
                meta_model=Author, meta_fields=['id','uuid','identity'],
            )(source="author"),
            "category": read_serializer(
                meta_model=Category, meta_fields=['id', 'identity']
            )(many=True, source="categories"),
            "course_image": read_serializer(
                meta_model=CourseImage, meta_fields=['id', 'uuid', 'file']
            )(source="image"),
        },
        fields_to_filter=["level", "categories", "skills", "author"],
    ),
)

# Learning - CourseModule
# --------------------------------------------------------------------------------------
router.register(
    f"{API_URL_PREFIX}{CourseModule.DYNAMIC_KEY}/cud",
    get_model_cud_api_viewset(
        meta_model=CourseModule,
        meta_fields=[
            "course",
            "identity",
            "description",
            "position",
        ],
        get_serializer_meta=lambda x: {},
    ),
)
router.register(
    f"{API_URL_PREFIX}{CourseModule.DYNAMIC_KEY}/list",
    get_model_list_api_viewset(
        meta_queryset=CourseModule.objects.all(),
        meta_all_table_columns={
            "identity": "Identity",
            "description": "Description",
            "position": "Position",
        },
        fields_to_filter=["course"],
    ),
)

# Learning - CourseSubModule
# --------------------------------------------------------------------------------------
router.register(
    f"{API_URL_PREFIX}{CourseSubModule.DYNAMIC_KEY}/cud",
    get_model_cud_api_viewset(
        meta_model=CourseSubModule,
        meta_fields=[
            "module",
            "identity",
            "duration",
            "position",
            "description",
            "video_url",
            "module_type",
            "assessmentID",
            "document"
        ],
        get_serializer_meta=lambda x: {
            "module_type": x.serialize_for_meta(ModuleType.objects.all()),
        },
    ),
)
router.register(
    f"{API_URL_PREFIX}{CourseSubModule.DYNAMIC_KEY}/list",
    get_model_list_api_viewset(
        meta_queryset=CourseSubModule.objects.all(),
        meta_all_table_columns={
            "identity": "Identity",
            "duration": "Duration",
            "position": "Position",
        },
        fields_to_filter=["module"],
    ),
)
# Learning Meta - Module Type
# --------------------------------------------------------------------------------------
router.register(
    f"{API_URL_PREFIX}{ModuleType.DYNAMIC_KEY}/cud",
    get_model_cud_api_viewset(
        meta_model=ModuleType,
        meta_fields=["identity"],
        get_serializer_meta=lambda x: {},
    ),
)
router.register(
    f"{API_URL_PREFIX}{ModuleType.DYNAMIC_KEY}/list",
    get_model_list_api_viewset(
        meta_queryset=ModuleType.objects.all(),
        meta_all_table_columns={
            "identity": "Name",
        },
    ),
)
# Website Meta - Testimonial
# --------------------------------------------------------------------------------------
router.register(
    f"{API_URL_PREFIX}{Testimonial.DYNAMIC_KEY}/cud",
    get_model_cud_api_viewset(
        meta_model=Testimonial,
        meta_fields=[
            "name",
            "designation",
            "image",
            "message",
            "video_url",
        ],
        get_serializer_meta=lambda x: {},
    ),
)
router.register(
    f"{API_URL_PREFIX}{Testimonial.DYNAMIC_KEY}/list",
    get_model_list_api_viewset(
        meta_queryset=Testimonial.objects.all(),
        meta_all_table_columns={
            "name": "Name",
            "designation": "Designation",
            "message": "Message",
        },
    ),
)
# Learning - MML Course
# ----------------------------------------------------------------------------------------
router.register(
    f"{API_URL_PREFIX}{MMLCourse.DYNAMIC_KEY}/cud",
    get_model_cud_api_viewset(
        meta_model=MMLCourse,
        meta_fields=[
            "identity",
            "description",
            "image",
            "is_certification_enabled",
            "vendor",
            "author",
            "skills",
            "categories",
            "code",
            "level",
            "language",
            "duration",
            "start_date",
            "end_date",
            "enable_ratings",
            "rating",
            "enable_feedback_comments",
            "sequential_course_flow",
            "accreditation",
            "is_free",
            "requirements",
            "highlights",
            # "actual_price_inr",
            "current_price_inr",
            "complete_in_a_day",
            "make_this_course_popular",
            "make_this_course_best_selling",
            "make_this_course_trending",
            "editors_pick",
            "learning_role",
            "mml_sku_id",
            "vm_name",
            "is_private_course",
            "resource_title",
            "resource_type",
            "resource",
            "virtual_lab"
        ],
        meta_extra_kwargs={
            "skills": {"allow_empty": False},
            "categories": {"allow_empty": False},
        },
        get_serializer_meta=lambda x: {
            "author": x.serialize_for_meta(Author.objects.all(), fields=['id', 'identity', 'vendor']),
            "vendor": x.serialize_for_meta(Vendor.objects.all()),
            "skills": x.serialize_for_meta(Skill.objects.filter(is_archived=False), fields=['id', 'identity', 'category']),
            "categories": x.serialize_for_meta(Category.objects.all()),
            "language": x.serialize_for_meta(Language.objects.all()),
            "accreditation": x.serialize_for_meta(Accreditation.objects.all()),
            "level": x.serialize_for_meta(CourseLevel.objects.all()),
            "learning_role": x.serialize_for_meta(LearningRole.objects.all()),
        },
    ),
)
router.register(
    f"{API_URL_PREFIX}{MMLCourse.DYNAMIC_KEY}/list",
    get_model_list_api_viewset(
        meta_queryset=MMLCourse.objects.all(),
        meta_all_table_columns={"code": "Code", "identity": "Name",
                                "duration": "Duration",
                                "rating": "Rating"},
        meta_init_fields_config={
            "level_details": read_serializer(
                meta_model=CourseLevel, meta_fields=['id', 'uuid', 'identity']
            )(source="level"),
            "author_details": read_serializer(
                meta_model=Author, meta_fields=['id','uuid','identity'],
            )(source="author"),
            "category": read_serializer(
                meta_model=Category, meta_fields=['id', 'identity']
            )(many=True, source="categories"),
            "course_image": read_serializer(
                meta_model=CourseImage, meta_fields=['id', 'uuid', 'file']
            )(source="image"),
        },
        fields_to_filter=["level", "categories", "skills", "author"],
    ),
)
# Learning - Learning Path
# --------------------------------------------------------------------------------------
router.register(
    f"{API_URL_PREFIX}{LearningPath.DYNAMIC_KEY}/cud",
    get_model_cud_api_viewset(
        meta_model=LearningPath,
        meta_fields=[
            "identity",
            "description",
            "image",
            "is_certification_enabled",
            "skills",
            "categories",
            "code",
            "level",
            "language",
            "duration",
            "start_date",
            "end_date",
            "enable_ratings",
            "rating",
            "enable_feedback_comments",
            "sequential_course_flow",
            "accreditation",
            "requirements",
            "highlights",
            "make_this_lp_popular",
            "make_this_lp_best_selling",
            "make_this_lp_trending",
            # "actual_price_inr",
            "current_price_inr",
            "learning_role",
            "is_private_course",
            "mml_sku_id",
            "vm_name",
            "virtual_lab",
        ],
        meta_extra_kwargs={
            "author": {"allow_empty": False},
        },
        get_serializer_meta=lambda x: {
            "author": x.serialize_for_meta(Author.objects.all()),
            "skills": x.serialize_for_meta(Skill.objects.filter(is_archived=False), fields=['id', 'identity', 'category']),
            "categories": x.serialize_for_meta(Category.objects.all()),
            "language": x.serialize_for_meta(Language.objects.all()),
            "accreditation": x.serialize_for_meta(Accreditation.objects.all()),
            "level": x.serialize_for_meta(CourseLevel.objects.all()),
            "learning_role": x.serialize_for_meta(LearningRole.objects.all()),
        },
    ),
)
router.register(
    f"{API_URL_PREFIX}{LearningPath.DYNAMIC_KEY}/list",
    get_model_list_api_viewset(
        meta_queryset=LearningPath.objects.all(),
        meta_all_table_columns={
            # "uuid": "UUID",
            "identity": "Identity",
            "code": "Code",
            "description": "Description",
            "duration": "Duration",
            "rating": "Rating",
            "is_certification_enabled": "Certificate Enabled",
        },
        meta_init_fields_config={
            "level_details": read_serializer(
                meta_model=CourseLevel, meta_fields=['id', 'uuid', 'identity']
            )(source="level"),
            "category": read_serializer(
                meta_model=Category, meta_fields=['identity']
            )(many=True, source="categories"),
            "lp_image": read_serializer(
                meta_model=LearningPathImage, meta_fields=['id', 'uuid', 'file']
            )(source="image"),
        },
        fields_to_filter=["identity"],
    ),
)

# Learning - LearningPathCourse
# --------------------------------------------------------------------------------------
router.register(
    f"{API_URL_PREFIX}{LearningPathCourse.DYNAMIC_KEY}/cud",
    get_model_cud_api_viewset(
        meta_model=LearningPathCourse,
        meta_fields=[
            "uuid",
            "learning_path",
            "course",
            "position",
            # "is_mandatory_to_complete",
        ],
        get_serializer_meta=lambda x: {},
    ),
)
router.register(
    f"{API_URL_PREFIX}{LearningPathCourse.DYNAMIC_KEY}/list",
    get_model_list_api_viewset(
        meta_queryset=LearningPathCourse.objects.all(),
        meta_all_table_columns={
            # "learning_path": "Learning Path",
            # "position": "Position",
            # "section": "Section",
            "course_details__identity": 'Identity',
            "course_details__description": 'Description',
            "course_details__code": 'Code',
            # "course_details__categories" : 'Category',
            "course_details__duration": 'Duration',
            "course_details__level_details__identity": "Level",
            "course_details__author_details__identity": "Author",

        },
        meta_init_fields_config={
            "course_details": read_serializer(
                meta_model=Course,
                meta_fields=['id', 'uuid','identity', 'description', 'code', 'duration'],
                init_fields_config={
                    "author_details": read_serializer(
                        meta_model=Author, meta_fields=['identity']
                    )(source="author"),
                    "level_details": read_serializer(
                        meta_model=CourseLevel,
                        meta_fields=['uuid', 'identity']
                    )(source="level"),
                    # "category": read_serializer(
                    #     meta_model=Category, meta_fields=['identity']
                    # )(many=True, source="categories"),
                    "image": read_serializer(
                        meta_model=CourseImage, meta_fields=['id', 'uuid', 'file']
                    )(),
                },
            )(source="course")
        },
        fields_to_filter=["learning_path"],
    ),
)

# Learning - CertificationPath
# --------------------------------------------------------------------------------------
router.register(
    f"{API_URL_PREFIX}{CertificationPath.DYNAMIC_KEY}/cud",
    get_model_cud_api_viewset(
        meta_model=CertificationPath,
        meta_fields=[
            "identity",
            "description",
            "image",
            "is_certification_enabled",
            "skills",
            "categories",
            "code",
            "level",
            "language",
            "duration",
            "start_date",
            "end_date",
            "enable_ratings",
            "rating",
            "enable_feedback_comments",
            "sequential_course_flow",
            "accreditation",
            "requirements",
            "highlights",
            "make_this_alp_popular",
            "make_this_alp_trending",
            "make_this_alp_best_selling",
            # "actual_price_inr",
            "current_price_inr",
            "learning_role",
            "is_private_course",
            "mml_sku_id",
            "vm_name",
            "virtual_lab"
        ],
        meta_extra_kwargs={
            "author": {"allow_empty": False},
        },
        get_serializer_meta=lambda x: {
            "author": x.serialize_for_meta(Author.objects.all()),
            "skills": x.serialize_for_meta(Skill.objects.filter(is_archived=False), fields=['id', 'identity', 'category']),
            "categories": x.serialize_for_meta(Category.objects.all()),
            "language": x.serialize_for_meta(Language.objects.all()),
            "accreditation": x.serialize_for_meta(Accreditation.objects.all()),
            "level": x.serialize_for_meta(CourseLevel.objects.all()),
            "learning_role": x.serialize_for_meta(LearningRole.objects.all()),
        },
        
    ),
)
router.register(
    f"{API_URL_PREFIX}{CertificationPath.DYNAMIC_KEY}/list",
    get_model_list_api_viewset(
        meta_queryset=CertificationPath.objects.all(),
        meta_all_table_columns={
            # "uuid": "UUID",
            "identity": "Identity",
            "code": "Code",
            "duration": "Duration",
            "rating": "Rating",
            "is_certification_enabled": "Certificate Enabled",
        },
        meta_init_fields_config={
            "category": read_serializer(
                meta_model=Category, meta_fields=['identity']
            )(many=True, source="categories"),
            "cp_image": read_serializer(
                meta_model=CertificationPathImage, meta_fields=['id', 'uuid', 'file']
            )(source="image"),
        },
        fields_to_filter=["identity"],
    ),
)

# Learning - Certification Path Learning Path
# --------------------------------------------------------------------------------------
router.register(
    f"{API_URL_PREFIX}{CertificationPathLearningPath.DYNAMIC_KEY}/cud",
    get_model_cud_api_viewset(
        meta_model=CertificationPathLearningPath,
        meta_fields=[
            "learning_path",
            "position",
            "certification_path",
            # "is_mandatory_to_complete",
        ],
        get_serializer_meta=lambda x: {},
    ),
)
router.register(
    f"{API_URL_PREFIX}{CertificationPathLearningPath.DYNAMIC_KEY}/list",
    get_model_list_api_viewset(
        meta_queryset=CertificationPathLearningPath.objects.all(),
        meta_all_table_columns={
            "learning_path": "Learning Path",
            "certification_path": "Certificate Path",
            "position": "Position",
            "lp_details__identity": "LP Identity",
            "lp_details__duration": "LP Duration",
            "lp_details__level_details__identity": "LP Level Identity",
            "lp_details__code": "LP Code"
        },
        meta_init_fields_config={
            "lp_details": read_serializer(
                meta_model=LearningPath,
                meta_fields=['id', 'identity', 'description', 'code', 'duration'],
                init_fields_config={
                    "level_details": read_serializer(
                        meta_model=CourseLevel, meta_fields=['uuid', 'identity']
                    )(source="level"),
                    "image": read_serializer(
                        meta_model=LearningPathImage, meta_fields=['id', 'uuid', 'file']
                    )(),
                },
            )(source="learning_path")
        },
        fields_to_filter=["certification_path"],
    ),
)

# Learning - BlendedLearningPath
# --------------------------------------------------------------------------------------
router.register(
    f"{API_URL_PREFIX}{BlendedLearningPath.DYNAMIC_KEY}/cud",
    get_model_cud_api_viewset(
        meta_model=BlendedLearningPath,
        meta_fields=[
            "identity",
            "accreditation",
            "description",
            "image",
            "learning_path_category",
            "skills",
            "learning_path_code",
            "learning_path_level",
            "language",
            "duration",
            "start_date",
            "end_date",
            "learning_type",
            "cutoff_time_for_mode_changes",
            "self_paced",
            "virtual",
            "classroom",
            "learning_points",
            "is_this_paid_learning_path",
            "ratings",
            "feedback_comments",
            "make_course_in_learning_path_sequential",
            "requirements",
            "highlights",
            "is_private_course",
            "learning_role",
            "mml_sku_id",
            "vm_name",
            "virtual_lab",
        ],
        meta_extra_kwargs={
        },
        get_serializer_meta=lambda x: {
            "learning_path_category": x.serialize_for_meta(Category.objects.all()),
            "skills": x.serialize_for_meta(Skill.objects.filter(is_archived=False)),
            "language": x.serialize_for_meta(Language.objects.all()),
            "accreditation": x.serialize_for_meta(Accreditation.objects.all()),
            "learning_path_level": x.serialize_for_meta(CourseLevel.objects.all()),
            "mode_details": x.serialize_for_meta(BlendedLearningPathCourseMode.objects.all()),
            "learning_type": x.serialize_for_meta(BlendedLearningPathLearningType.objects.all()),
            "learning_role": x.serialize_for_meta(LearningRole.objects.all()),
            "city": x.serialize_for_meta(City.objects.all()),
        },
    ),
)

# Learning - BlendedLearningPathCustomerEnquiry
# --------------------------------------------------------------------------------------
router.register(
    f"{API_URL_PREFIX}{BlendedLearningPathCustomerEnquiry.DYNAMIC_KEY}/list",
    get_model_list_api_viewset(
        meta_queryset=BlendedLearningPathCustomerEnquiry.objects.all(),
        meta_all_table_columns={
            # "uuid": "UUID",
            "blp_name": "BLP Name",
            "name": "Name",
            "email": "Email",
            "phone_number": "Phone Number",
            "is_customer": "Is Customer",
            "mode_details__identity": "Learning Mode",
            "created": "Created At",
        },
        meta_init_fields_config={
            "mode_details": get_app_read_only_optimize_serializer(
                meta_model=BlendedLearningPathCourseMode, meta_fields=['uuid', 'identity']
            )(source="mode"),
        },
        fields_to_filter=["blp_name", "name", "email"],
    ),
)

# router.register(
#     f"{API_URL_PREFIX}{BlendedLearningClassroomAndVirtualDetails.DYNAMIC_KEY}/list",
#     get_model_list_api_viewset(
#         meta_queryset=BlendedLearningClassroomAndVirtualDetails.objects.all(),
#         meta_all_table_columns={
#             "blended_learning": "Blended Learning",
#             "course": "Course",
#             "number_of_sessions": "No.of.sessions",
#             "address_details": "Address_details",
#             "virtual_session_link": "Virtual Session Link",
#             "virtual_session_start_time": "Virtual Session Start Time",
#             "virtual_session_end_time": "Virtual Session End Time",
#         },
#         fields_to_filter=["blended_learning"],
#     ),
# )


# router.register(
#     f"{API_URL_PREFIX}{BlendedLearningPathCourseModesAndFee.DYNAMIC_KEY}/list",
#     get_model_list_api_viewset(
#         meta_queryset=BlendedLearningPathCourseModesAndFee.objects.all(),
#         meta_all_table_columns={
#             "blended_learning": "Blended Learning",
#             "course": "Course",
#             "self_paced_fee": "Self Paced Fee",
#             "online_fee": "Online Fee",
#             "classroom_fee": "Classroom Fee",
#             "mode_details": "Mode Details",
#         },
#         fields_to_filter=["blended_learning"],
#     ),
# )

router.register(
    f"{API_URL_PREFIX}{BlendedLearningPath.DYNAMIC_KEY}/list",
    get_model_list_api_viewset(
        meta_queryset=BlendedLearningPath.objects.all(),
        meta_all_table_columns={
            # "uuid": "UUID",
            "identity": "BLP Name",
            "learning_path_code": "BLP Code",
            "duration": "Duration (Hrs)",
            "learning_path_level": "Proficiency",
            "learning_path_category": "Category",
            "self_paced": "Learning Mode",
            "virtual": "Learning Mode",
            "classroom": "Learning Mode"
        },
        meta_init_fields_config={
            "level_details": read_serializer(
                meta_model=CourseLevel, meta_fields=['id', 'uuid', 'identity']
            )(source="learning_path_level"),
            "category_details": read_serializer(
                meta_model=Category, meta_fields=['identity']
            )(many=True, source="learning_path_category"),
            "blp_image": read_serializer(
                meta_model=BlendedLearningPathImage, meta_fields=['id', 'uuid', 'file']
            )(source="image"),
        },
        fields_to_filter=["learning_path_category", "skills", "learning_path_level"],
    ),
)

# Learning - BlendedLearningPathPriceDetails
# --------------------------------------------------------------------------------------
router.register(
    f"{API_URL_PREFIX}{BlendedLearningPathPriceDetails.DYNAMIC_KEY}/cud",
    get_model_cud_api_viewset(
        meta_model=BlendedLearningPathPriceDetails,
        meta_fields=[
            "blended_learning",
            "mode",
            # "self_paced_fee",
            "online_actual_fee",
            "online_discount_rate",
            
            "classroom_actual_fee",
            "classroom_discount_rate",
            "schedule_details"
        ],
        meta_extra_kwargs={
        },
        get_serializer_meta=lambda x: {
            "blended_learning": x.serialize_for_meta(BlendedLearningPath.objects.all()),
            "mode": x.serialize_for_meta(BlendedLearningPathCourseMode.objects.all()),
            "address": BLPAddressListModelSerializer(BLPAddress.objects.all(), many=True).data
        },
    ),
)

router.register(
    f"{API_URL_PREFIX}{BlendedLearningPathPriceDetails.DYNAMIC_KEY}/list",
    get_model_list_api_viewset(
        meta_queryset=BlendedLearningPathPriceDetails.objects.all(),
        meta_all_table_columns={
            "blended_learning_details__identity": "BLP Name",
            "mode_details__identity": "Mode",
            # "self_paced_fee": "Self-paced Fee",
            "online_actual_fee": "Online Fee",
            "online_discounted_fee": "Online Discounted Fee",
            "classroom_actual_fee": "Classroom Fee",
            "classroom_discounted_fee": "Classroom Discounted Fee",
        },
        meta_init_fields_config={
            "blended_learning_details": read_serializer(
                meta_model=BlendedLearningPath, meta_fields=['id', 'uuid', 'identity']
            )(source="blended_learning"),
            "mode_details": read_serializer(
                meta_model=BlendedLearningPathCourseMode, meta_fields=['identity']
            )(many=True,source="mode"),
        },
        fields_to_filter=["blended_learning", "mode"],
    ),
)
# Blended Learning Path - Course Mode
# --------------------------------------------------------------------------------------
router.register(
    f"{API_URL_PREFIX}{BlendedLearningPathCourseMode.DYNAMIC_KEY}/cud",
    get_model_cud_api_viewset(
        meta_model=BlendedLearningPathCourseMode,
        meta_fields=["identity"],
        get_serializer_meta=lambda x: {
            "modes": x.serialize_for_meta(BlendedLearningPathCourseMode.objects.all()),
        },
    ),
)
router.register(
    f"{API_URL_PREFIX}{BlendedLearningPathCourseMode.DYNAMIC_KEY}/list",
    get_model_list_api_viewset(
        meta_queryset=BlendedLearningPathCourseMode.objects.all(),
        meta_all_table_columns={
            "identity": "Name",
        },
    ),
)


# Blended Learning Path - Learning Type
# --------------------------------------------------------------------------------------
router.register(
    f"{API_URL_PREFIX}{BlendedLearningPathLearningType.DYNAMIC_KEY}/cud",
    get_model_cud_api_viewset(
        meta_model=BlendedLearningPathLearningType,
        meta_fields=["identity"],
        get_serializer_meta=lambda x: {
            "learning_type": x.serialize_for_meta(BlendedLearningPathLearningType.objects.all()),
        },
    ),
)
router.register(
    f"{API_URL_PREFIX}{BlendedLearningPathLearningType.DYNAMIC_KEY}/list",
    get_model_list_api_viewset(
        meta_queryset=BlendedLearningPathLearningType.objects.all(),
        meta_all_table_columns={
            "identity": "Name",
        },
    ),
)

# Learning Role
# --------------------------------------------------------------------------------------
router.register(
    f"{API_URL_PREFIX}{LearningRole.DYNAMIC_KEY}/cud",
    get_model_cud_api_viewset(
        meta_model=LearningRole, meta_fields=["identity", "image", "description", "skills", "make_this_role_popular", "duration", "enable_ratings", "rating", "make_this_role_trending", "make_this_role_best_selling"],
        meta_extra_kwargs={
            "skills": {"allow_empty": False},
        },
        get_serializer_meta=lambda x: {
            "skills": x.serialize_for_meta(Skill.objects.filter(is_archived=False)),
        },
    ),
)
router.register(
    f"{API_URL_PREFIX}{LearningRole.DYNAMIC_KEY}/list",
    get_model_list_api_viewset(
        meta_queryset=LearningRole.objects.all(),
        meta_all_table_columns={"identity": "Role Name", "description": "Description"},
        meta_init_fields_config={
            "role_image": read_serializer(
                meta_model=LearningRoleImage, meta_fields=['id','uuid','file']
            )(source="image"),
            "Skill_details": read_serializer(
                meta_model=Skill, meta_fields=['id', 'identity']
            )(many=True, source="skills"),
        },
    ),
)

# Learning Meta - Language
# --------------------------------------------------------------------------------------
router.register(
    f"{API_URL_PREFIX}{Language.DYNAMIC_KEY}/cud",
    get_model_cud_api_viewset(
        meta_model=Language,
        meta_fields=["identity", "code"],
        get_serializer_meta=lambda x: {},
    ),
)
router.register(
    f"{API_URL_PREFIX}{Language.DYNAMIC_KEY}/list",
    get_model_list_api_viewset(
        meta_queryset=Language.objects.all(),
        meta_all_table_columns={
            # "id": "ID",
            "identity": "Name",
            "code": "Code",
        },
    ),
)

# Payments - Coupon Code
# --------------------------------------------------------------------------------------
router.register(
    f"{API_URL_PREFIX}{Discount.DYNAMIC_KEY}/cud",
    get_model_cud_api_viewset(
        meta_model=Discount,
        meta_fields=[
            "identity",
            "coupon_code",
            "is_flat_rate_discount",
            "discount_in_percentage",
            "discount_in_percentage_amount_cap",
            "discount_in_amount",
            "enable_usage_limit",
            "maximum_number_of_usages",
            "per_user_usage_limit",
            "start_date",
            "end_date",
        ],
        get_serializer_meta=lambda x: {},
    ),
)
router.register(
    f"{API_URL_PREFIX}{Discount.DYNAMIC_KEY}/list",
    get_model_list_api_viewset(
        meta_queryset=Discount.objects.all(),
        meta_all_table_columns={
            "identity": "Name",
            "coupon_code": "Code",
        },
    ),
)

# Payments - Subscription Plan
# --------------------------------------------------------------------------------------
router.register(
    f"{API_URL_PREFIX}{SubscriptionPlan.DYNAMIC_KEY}/cud",
    get_model_cud_api_viewset(
        meta_model=SubscriptionPlan,
        meta_fields=[
            "identity",
            "description",
            "start_date",
            "end_date",
            "rating",
            "what_will_you_learn",
            "make_this_subscription_plan_popular",

            # Plan Feature
            "skill_level_assesment",
            "interactive_practices",
            "certification",
            "virtual_labs",
            "basic_to_advance_level",
            "is_duration",
            "duration",
            "image",

            # Pricing
            "is_yearly_subscription_plan_active",
            "is_monthly_subscription_plan_active",

            "yearly_price_in_inr",
            "is_gst_inclusive_for_yearly",

            "monthly_price_in_inr",
            "is_gst_inclusive_for_monthly",

            # Contents
            "courses",
            "learning_paths",
            "certification_paths",
            "status",
        ],
        get_serializer_meta=lambda x: {
            "categories": x.serialize_for_meta(Category.objects.all(), fields=['id', 'uuid', 'identity']),
            "skills": x.serialize_for_meta(Skill.objects.filter(is_archived=False), fields=['id', 'uuid', 'identity']),
            "courses": x.serialize_for_meta(Course.objects.all(), fields=['id', 'uuid', 'identity', 'description', 'code', 'image__file', 'level__identity', 'duration', 'author__identity', 'rating']),
            "learning_paths": x.serialize_for_meta(LearningPath.objects.all(), fields=['id', 'uuid', 'identity', 'description', 'code', 'image__file', 'level__identity', 'duration', 'rating']),
            "certification_paths": x.serialize_for_meta(CertificationPath.objects.all(), fields=['id', 'uuid', 'identity', 'description', 'code', 'image__file', 'level__identity', 'duration', 'rating']),
        },
    ),
)
router.register(
    f"{API_URL_PREFIX}{SubscriptionPlan.DYNAMIC_KEY}/list",
    get_model_list_api_viewset(
        meta_queryset=SubscriptionPlan.objects.all(),
        meta_all_table_columns={
            # "uuid": "UUID",
            "identity": "Title",
            "description": "Description",
            # "sale_discount_percentage": "Sale Discount Percentage",
            "start_date": "Start From",
            "end_date": "Valid Till",
            "yearly_price_in_inr": "Yearly Plan Rate",
            "monthly_price_in_inr": "Monthly Plan Rate",
            "status": "Status",
        },
        meta_init_fields_config={
            "subscription_plan_image": read_serializer(
                meta_model=SubscriptionPlanImage, meta_fields=['id','uuid','file']
            )(source="image"),
        },
        fields_to_filter=["identity"],
    ),
)
# Learning - SubscriptionPlanCustomerEnquiry
# --------------------------------------------------------------------------------------
router.register(
    f"{API_URL_PREFIX}{SubscriptionPlanCustomerEnquiry.DYNAMIC_KEY}/list",
    get_model_list_api_viewset(
        meta_queryset=SubscriptionPlanCustomerEnquiry.objects.all(),
        meta_all_table_columns={
            "subscription_plans__identity": "Subscription",
            "name": "Name",
            "email": "Email",
            "phone_number": "Phone Number",
            "is_customer": "Is Customer",
            "created": "Created At",
        },
        meta_init_fields_config={
            "subscription_plans": read_serializer(
                meta_model=SubscriptionPlan, meta_fields=['id','uuid','identity']
            )(source="subscription_plan"),
        },
        fields_to_filter=["phone_number", "name", "email"],
    ),
)
# Payments - Sale Discount Subscription Plan
# --------------------------------------------------------------------------------------
router.register(
    f"{API_URL_PREFIX}{SubscriptionPlanSaleDiscount.DYNAMIC_KEY}/cud",
    get_model_cud_api_viewset(
        meta_model=SubscriptionPlanSaleDiscount,
        meta_fields=[
            "subscription_plan",
            "sale_code",
            "start_date",
            "end_date",
            # Yearly Subscription Plan Offer
            "is_yearly_subscription_plan_offer",
            "is_yearly_discount_percentage",
            "yearly_discount_percentage",
            "is_yearly_discount_amount",
            "yearly_discount_amount",
            # Monthly Subscription Plan Offer
            "is_monthly_subscription_plan_offer",
            "is_monthly_discount_percentage",
            "monthly_discount_percentage",
            "is_monthly_discount_amount",
            "monthly_discount_amount",
            
            "sale_for",
        ],
        get_serializer_meta=lambda x: {
            "subscription_plan": x.serialize_for_meta(SubscriptionPlan.objects.all()),
        },
    ),
)

router.register(
    f"{API_URL_PREFIX}{SubscriptionPlanSaleDiscount.DYNAMIC_KEY}/list",
    get_model_list_api_viewset(
        meta_queryset=SubscriptionPlanSaleDiscount.objects.all(),
        meta_all_table_columns={
            "sale_code": "Sale Code",
            "start_date": "Start From",
            "end_date": "Valid Till",
            "sale_for": "Sale For",
        },
        meta_init_fields_config={
            "subscription_plans": read_serializer(
                meta_model=SubscriptionPlan, meta_fields=['id','uuid','identity']
            )(source="subscription_plan"),
        },
    ),
)

# Payments - Sale Discount Learning Content
# --------------------------------------------------------------------------------------
router.register(
    f"{API_URL_PREFIX}{SaleDiscount.DYNAMIC_KEY}/cud",
    get_model_cud_api_viewset(
        meta_model=SaleDiscount,
        meta_fields=[
            "identity",
            "sale_code",
            "description",
            "start_date",
            "end_date",
            "sale_discount_percentage",
            "image",
            "courses",
            "learning_paths",
            "certification_paths",
            # "role_based_learnings",
            "sale_for"
        ],
        get_serializer_meta=lambda x: {
            "courses": x.serialize_for_meta(Course.objects.all(), fields=['id', 'uuid', 'identity', 'description', 'code', 'image__file', 'level__identity', 'duration', 'author__identity', 'rating']),
            "learning_paths": x.serialize_for_meta(LearningPath.objects.all(), fields=['id', 'uuid', 'identity', 'description', 'code', 'image__file', 'level__identity', 'duration', 'rating']),
            "certification_paths": x.serialize_for_meta(CertificationPath.objects.all(), fields=['id', 'uuid', 'identity', 'description', 'code', 'image__file', 'level__identity', 'duration', 'rating']),
            "skills": x.serialize_for_meta(Skill.objects.filter(is_archived=False), fields=['id', 'uuid', 'identity']),
            "categories": x.serialize_for_meta(Category.objects.all(), fields=['id', 'uuid', 'identity'])
            # "role_based_learning": x.serialize_for_meta(LearningRole.objects.all(), fields=['id', 'uuid', 'identity', 'image__file', 'duration', 'rating']),
        },
    ),
)

router.register(
    f"{API_URL_PREFIX}{SaleDiscount.DYNAMIC_KEY}/list",
    get_model_list_api_viewset(
        meta_queryset=SaleDiscount.objects.all(),
        meta_all_table_columns={
            "sale_code": "Sale Code",
            "identity": "Sale Title",
            "start_date": "Start From",
            "end_date": "Valid Till",
            "sale_for": "Sale For",
        },
        fields_to_filter=["identity"],
    ),
)

# Zone
# --------------------------------------------------------------------------------------
router.register(
    f"{API_URL_PREFIX}{Zone.DYNAMIC_KEY}/cud",
    get_model_cud_api_viewset(
        meta_model=Zone,
        meta_fields=[
            "identity",
            "description",
            "hash_tags",
            "image",
            "zone_type",
            "assign_members",
            "forums",
            "categories",
            "skills",
        ],
        meta_extra_kwargs={},
        get_serializer_meta=lambda x: {
            "zone_type": x.serialize_for_meta(ZoneType.objects.all(),fields=["id","uuid","identity"]),
            "assign_members": x.serialize_for_meta(InstitutionUserGroupDetail.objects.all(),fields=["id","uuid","identity"]),
            "categories": x.serialize_for_meta(Category.objects.all()),
            "skills": x.serialize_for_meta(Skill.objects.filter(is_archived=False),fields=["id", "identity", "category"]),
        },
    ),
)
# community zone list is only for table-meta
router.register(
    f"{API_URL_PREFIX}{Zone.DYNAMIC_KEY}/list",
    get_model_list_api_viewset(
        meta_queryset=Zone.objects.all(),
        meta_all_table_columns={
            "identity": "Community Name",
            "created":"Creation date",
            "no_of_forums": "No. Of Forums",
            "members_count": "Members",
            "no_of_posts":"No. Of Posts",
            "status":"Status"
        },
        fields_to_filter=["identity"],
    ),
)
# Zone Type
# --------------------------------------------------------------------------------------
router.register(
    f"{API_URL_PREFIX}{ZoneType.DYNAMIC_KEY}/cud",
    get_model_cud_api_viewset(
        meta_model=ZoneType,
        meta_fields=[
            "identity"
        ],
        meta_extra_kwargs={},
        get_serializer_meta=lambda x: {},
    ),
)
router.register(
    f"{API_URL_PREFIX}{ZoneType.DYNAMIC_KEY}/list",
    get_model_list_api_viewset(
        meta_queryset=ZoneType.objects.all(),
        meta_all_table_columns={
            "identity": "Zone Type",
        },
    ),
)
# Frequently Asked Questions
# --------------------------------------------------------------------------------------
router.register(
    f"{API_URL_PREFIX}{FrequentlyAskedQuestion.DYNAMIC_KEY}/cud",
    get_model_cud_api_viewset(
        meta_model=FrequentlyAskedQuestion,
        meta_fields=["question", "answer"],
        get_serializer_meta=lambda x: {},
    ),
)
router.register(
    f"{API_URL_PREFIX}{FrequentlyAskedQuestion.DYNAMIC_KEY}/list",
    get_model_list_api_viewset(
        meta_queryset=FrequentlyAskedQuestion.objects.all(),
        meta_all_table_columns={
            "question": "Question",
            "answer": "Answer",
        },
    ),
)

# Country
# --------------------------------------------------------------------------------------
router.register(
    f"{API_URL_PREFIX}{location_models.Country.DYNAMIC_KEY}/cud",
    get_model_cud_api_viewset(
        meta_model=location_models.Country,
        meta_fields=["identity"],
        get_serializer_meta=lambda x: {},
    ),
)
router.register(
    f"{API_URL_PREFIX}{location_models.Country.DYNAMIC_KEY}/list",
    get_model_list_api_viewset(
        meta_queryset=location_models.Country.objects.all(),
        meta_all_table_columns={
            "identity": "Country",
        },
    ),
)

# State
# --------------------------------------------------------------------------------------
router.register(
    f"{API_URL_PREFIX}{location_models.State.DYNAMIC_KEY}/cud",
    get_model_cud_api_viewset(
        meta_model=location_models.State,
        meta_fields=["identity", "country"],
        get_serializer_meta=lambda x: {
            "country": x.serialize_for_meta(location_models.Country.objects.all()),
        },
    ),
)
router.register(
    f"{API_URL_PREFIX}{location_models.State.DYNAMIC_KEY}/list",
    get_model_list_api_viewset(
        meta_queryset=location_models.State.objects.all(),
        meta_all_table_columns={
            "identity": "State",
            "country__identity": "Country"
        },
        meta_init_fields_config={
            "country_detail": read_serializer(
                meta_model=Country, meta_fields=['id','identity']
            )(source="country"),
        },
    ),
)

# City
# --------------------------------------------------------------------------------------
router.register(
    f"{API_URL_PREFIX}{location_models.City.DYNAMIC_KEY}/cud",
    get_model_cud_api_viewset(
        meta_model=location_models.City,
        meta_fields=["identity", "state"],
        get_serializer_meta=lambda x: {
            "state": x.serialize_for_meta(location_models.State.objects.all()),
        },
    ),
)
router.register(
    f"{API_URL_PREFIX}{location_models.City.DYNAMIC_KEY}/list",
    get_model_list_api_viewset(
        meta_queryset=location_models.City.objects.all(),
        meta_all_table_columns={
            "identity": "City",
            "state__identity": "State"
        },
        meta_init_fields_config={
            "state_detail": read_serializer(
                meta_model=State, meta_fields=['id','identity']
            )(source="state"),
        },
    ),
)

#BLP Address
# --------------------------------------------------------------------------------------
router.register(
    f"{API_URL_PREFIX}{location_models.BLPAddress.DYNAMIC_KEY}/cud",
    get_model_cud_api_viewset(
        meta_model=location_models.BLPAddress,
        meta_fields=["identity", "city"],
        get_serializer_meta=lambda x: {
            "city": x.serialize_for_meta(location_models.City.objects.all()),
        },
    ),
)

router.register(
    f"{API_URL_PREFIX}{location_models.BLPAddress.DYNAMIC_KEY}/list",
    get_model_list_api_viewset(
        meta_queryset=location_models.BLPAddress.objects.all(),
        meta_all_table_columns={
            "identity": "Address",
            "city__identity": "City"
        },
        meta_init_fields_config={
            "city_detail": read_serializer(
                meta_model=City, meta_fields=['id','identity']
            )(source="city"),
        },
    ),
)

# Onboarding Level
# --------------------------------------------------------------------------------------
router.register(
    f"{API_URL_PREFIX}{profile_models.OnboardingLevel.DYNAMIC_KEY}/cud",
    get_model_cud_api_viewset(
        meta_model=profile_models.OnboardingLevel,
        meta_fields=["identity"],
        get_serializer_meta=lambda x: {},
    ),
)
router.register(
    f"{API_URL_PREFIX}{profile_models.OnboardingLevel.DYNAMIC_KEY}/list",
    get_model_list_api_viewset(
        meta_queryset=profile_models.OnboardingLevel.objects.all(),
        meta_all_table_columns={
            "identity": "Onboarding Level",
        },
    ),
)

# Onboarding Highest Education
# --------------------------------------------------------------------------------------
router.register(
    f"{API_URL_PREFIX}{profile_models.OnboardingHighestEducation.DYNAMIC_KEY}/cud",
    get_model_cud_api_viewset(
        meta_model=profile_models.OnboardingHighestEducation,
        meta_fields=["identity"],
        get_serializer_meta=lambda x: {},
    ),
)
router.register(
    f"{API_URL_PREFIX}{profile_models.OnboardingHighestEducation.DYNAMIC_KEY}/list",
    get_model_list_api_viewset(
        meta_queryset=profile_models.OnboardingHighestEducation.objects.all(),
        meta_all_table_columns={
            "identity": "Onboarding Highest Education",
        },
    ),
)

# Onboarding Area of Interest
# --------------------------------------------------------------------------------------
router.register(
    f"{API_URL_PREFIX}{profile_models.OnboardingAreaOfInterest.DYNAMIC_KEY}/cud",
    get_model_cud_api_viewset(
        meta_model=profile_models.OnboardingAreaOfInterest,
        meta_fields=["identity"],
        get_serializer_meta=lambda x: {},
    ),
)
router.register(
    f"{API_URL_PREFIX}{profile_models.OnboardingAreaOfInterest.DYNAMIC_KEY}/list",
    get_model_list_api_viewset(
        meta_queryset=profile_models.OnboardingAreaOfInterest.objects.all(),
        meta_all_table_columns={
            "identity": "Onboarding Area of Interest",
        },
    ),
)

# User Gender
# --------------------------------------------------------------------------------------
router.register(
    f"{API_URL_PREFIX}{profile_models.UserGender.DYNAMIC_KEY}/cud",
    get_model_cud_api_viewset(
        meta_model=profile_models.UserGender,
        meta_fields=["identity"],
        get_serializer_meta=lambda x: {},
    ),
)
router.register(
    f"{API_URL_PREFIX}{profile_models.UserGender.DYNAMIC_KEY}/list",
    get_model_list_api_viewset(
        meta_queryset=profile_models.UserGender.objects.all(),
        meta_all_table_columns={
            "identity": "Gender",
        },
    ),
)

# User Identification Type
# --------------------------------------------------------------------------------------
router.register(
    f"{API_URL_PREFIX}{profile_models.UserIdentificationType.DYNAMIC_KEY}/cud",
    get_model_cud_api_viewset(
        meta_model=profile_models.UserIdentificationType,
        meta_fields=["identity"],
        get_serializer_meta=lambda x: {},
    ),
)
router.register(
    f"{API_URL_PREFIX}{profile_models.UserIdentificationType.DYNAMIC_KEY}/list",
    get_model_list_api_viewset(
        meta_queryset=profile_models.UserIdentificationType.objects.all(),
        meta_all_table_columns={
            "identity": "Identification Type",
        },
    ),
)

# User Martial Status
# --------------------------------------------------------------------------------------
router.register(
    f"{API_URL_PREFIX}{profile_models.UserMartialStatus.DYNAMIC_KEY}/cud",
    get_model_cud_api_viewset(
        meta_model=profile_models.UserMartialStatus,
        meta_fields=["identity"],
        get_serializer_meta=lambda x: {},
    ),
)
router.register(
    f"{API_URL_PREFIX}{profile_models.UserMartialStatus.DYNAMIC_KEY}/list",
    get_model_list_api_viewset(
        meta_queryset=profile_models.UserMartialStatus.objects.all(),
        meta_all_table_columns={
            "identity": "Martial Status",
        },
    ),
)

# Webinar
# --------------------------------------------------------------------------------------
router.register(
    f"{API_URL_PREFIX}{Webinar.DYNAMIC_KEY}/cud",
    get_model_cud_api_viewset(
        meta_model=Webinar,
        meta_fields=[
            "identity",
            "language",
            "image",
            "description",
            "webinar_link",
            "participant_limit",
            "user_group",
            "skills",
            # "webinar_type",
            "is_paid_webinar",
            "webinar_fee",
            # "payment_mode",
            "start_date",
            "end_date",
            "session_detail",
            "payment_mode_details",
            "zone",
        ],
        get_serializer_meta=lambda x: {
            "language": x.serialize_for_meta(Language.objects.all()),
            "user_group": x.serialize_for_meta(InstitutionUserGroupDetail.objects.all(),fields=["id","uuid","identity"]),
            "skills": x.serialize_for_meta(Skill.objects.filter(is_archived=False)),
            # "payment_mode": x.serialize_for_meta(PaymentMode.objects.all()),
            "zone": x.serialize_for_meta(Zone.objects.all()),
        },
    ),
)
router.register(
    f"{API_URL_PREFIX}{Webinar.DYNAMIC_KEY}/list",
    get_model_list_api_viewset(
        meta_queryset=Webinar.objects.all(),
        meta_all_table_columns={
            "identity": "Webinar Name",
            "participant_limit": "Participants",
            "status": "status",
            "start_date": "Start Date",
            "end_date": "End Date"
        },
    ),
)
# Webinar Discussion 
# --------------------------------------------------------------------------------------
router.register(
    f"{API_URL_PREFIX}{WebinarDiscussion.DYNAMIC_KEY}/cud",
    get_model_cud_api_viewset(
        meta_model=WebinarDiscussion,
        meta_fields=[
                    "webinar",
                    "title",
                    "message",
                    ],
        meta_extra_kwargs={},
        get_serializer_meta=lambda x: {
            "webinar": x.serialize_for_meta(Webinar.objects.all()),
        },
    ),
)
# Webinar Discussion Comment
# --------------------------------------------------------------------------------------
router.register(
    f"{API_URL_PREFIX}{WebinarDiscussionComment.DYNAMIC_KEY}/cud",
    get_model_cud_api_viewset(
        meta_model=WebinarDiscussionComment,
        meta_fields=["webinar_discussion","identity"],
        get_serializer_meta=lambda x: {
            "webinar_discussion": x.serialize_for_meta(WebinarDiscussion.objects.all()),
        },
    ),
)
# Webinar Discussion Reply
# --------------------------------------------------------------------------------------
router.register(
    f"{API_URL_PREFIX}{WebinarDiscussionReply.DYNAMIC_KEY}/cud",
    get_model_cud_api_viewset(
        meta_model=WebinarDiscussionReply,
        meta_fields=["comment","identity"],
        get_serializer_meta=lambda x: {},
    ),
)
# Webinar Registration List
# --------------------------------------------------------------------------------------
router.register(
    f"{API_URL_PREFIX}{WebinarRegistration.DYNAMIC_KEY}/list",
    get_model_list_api_viewset(
        meta_queryset=WebinarRegistration.objects.all(),
        meta_all_table_columns={
            "webinar__identity": "Webinar Name",
            "webinar__is_paid_webinar": "Webinar Type",
            "user__full_name": "User Name",
            "user__idp_email": "Email ID",
            "user__phone_number": "Phone Number",
            "created": "Registration Date",
        },
    ),
)
# Certificate for course,LP,ALP
# --------------------------------------------------------------------------------------
router.register(
    f"{API_URL_PREFIX}{certificate_models.Certificate.DYNAMIC_KEY}/cud",
    get_model_cud_api_viewset(
        meta_model=certificate_models.Certificate,
        meta_fields=["learning_type", "sponsor_logo", "keep_techademy_logo",
                     "orientation", "headline_text", "body_text", "image"],
        get_serializer_meta=lambda x: {
            "learning_type": x.serialize_for_meta(
                certificate_models.CertificateLearningType.objects.all()),
        },
    ),
)
router.register(
    f"{API_URL_PREFIX}{certificate_models.Certificate.DYNAMIC_KEY}/list",
    get_model_list_api_viewset(
        meta_queryset=certificate_models.Certificate.objects.all(),
        meta_all_table_columns={
            "learning_type_details__identity": "Learning Type",
        },
        meta_init_fields_config={
            "learning_type_details": read_serializer(
                meta_model=certificate_models.CertificateLearningType,
                meta_fields=['id', 'uuid', 'identity']
            )(source="learning_type"),
        },
    ),
)
# Hackathon
# --------------------------------------------------------------------------------------
router.register(
    f"{API_URL_PREFIX}{hackathon_models.Hackathon.DYNAMIC_KEY}/cud",
    get_model_cud_api_viewset(
        meta_model=hackathon_models.Hackathon,
        meta_fields=["identity", "language", "image", "description",
                     "no_of_attempts_allowed", "no_of_participants_limit",
                     "user_group", "skills", "hackathon_fees", "start_date",
                     "end_date", "prizes_details", "problem_statement",
                     "expected_solution", "round_details", "general_rules",
                     "eligibility", "how_to_enter", "submission_required",
                     "terms_and_conditions","is_free","zone"],
        get_serializer_meta=lambda x: {
            "language": x.serialize_for_meta(Language.objects.all()),
            "skills": x.serialize_for_meta(Skill.objects.filter(is_archived=False)),
            "judge_id": x.serialize_for_meta(round_models.HackathonJudge.objects.all()),
            "user_group": x.serialize_for_meta(InstitutionUserGroupDetail.objects.all(),fields=["id","uuid","identity"]),
            "zone": x.serialize_for_meta(Zone.objects.all()),
        },
    ),
)
router.register(
    f"{API_URL_PREFIX}{hackathon_models.Hackathon.DYNAMIC_KEY}/list",
    get_model_list_api_viewset(
        meta_queryset=hackathon_models.Hackathon.objects.all(),
        meta_all_table_columns={
            "identity": "Hackathon Name",
            # "duration": "Duration",
            # "period": "Period",
            # "created_by_details__full_name": "Created By",
            "no_of_participants_limit": "Participants",
            # "prizes": "Prizes",
            "start_date": "Start Date",
            "end_date": "End Date",
        },
        meta_init_fields_config={
        "prizes_data": read_serializer(
            meta_model=prize_models.HackathonPrizeDetails, meta_fields=['id','uuid','rank', 'prize_amount']
        )(many=True, source="prizes_details"),
        "rounds_data": read_serializer(
            meta_model=round_models.HackathonRoundDetails, meta_fields=['id','uuid', 'round_no','desc', 'prize_amount', 'round_start_date', 'round_start_time', 'round_end_date', 'round_end_time', 'passing_points', 'judging_criteria', 'judging_start_date', 'judging_end_date', 'judging_announcement_date'],
            init_fields_config={
                "judge_data": read_serializer(
                    meta_model=round_models.HackathonJudge, meta_fields=['id','uuid','identity', 'designation']
                )(source='judge')
             },
        )(many=True, source="round_details"),
        "created_by_details": read_serializer(
            meta_model=User, meta_fields=['id','uuid','full_name']
        )(source="created_by"),
        },
        fields_to_filter=["identity"],
    ),
)

# Hackathon Judge
# --------------------------------------------------------------------------------------
router.register(
    f"{API_URL_PREFIX}{round_models.HackathonJudge.DYNAMIC_KEY}/cud",
    get_model_cud_api_viewset(
        meta_model=round_models.HackathonJudge,
        meta_fields=["identity"],
        get_serializer_meta=lambda x: {},
    ),
)
router.register(
    f"{API_URL_PREFIX}{round_models.HackathonJudge.DYNAMIC_KEY}/list",
    get_model_list_api_viewset(
        meta_queryset=round_models.HackathonJudge.objects.all(),
        meta_all_table_columns={
            "identity": "Judge",
        },
        fields_to_filter=["identity"],
    ),
)

# Hackathon Updates
# --------------------------------------------------------------------------------------
router.register(
    f"{API_URL_PREFIX}{hackathon_models.HackathonUpdates.DYNAMIC_KEY}/cud",
    get_model_cud_api_viewset(
        meta_model=hackathon_models.HackathonUpdates,
        meta_fields=["hackathon","desc"],
        get_serializer_meta=lambda x: {},
    ),
)
router.register(
    f"{API_URL_PREFIX}{hackathon_models.HackathonUpdates.DYNAMIC_KEY}/list",
    get_model_list_api_viewset(
        meta_queryset=hackathon_models.HackathonUpdates.objects.all(),
        meta_all_table_columns={
            "desc": "Description",
            "created": "Created At"
        },
        fields_to_filter=["id"],
    ),
)
# Hackathon Discussion 
# --------------------------------------------------------------------------------------
router.register(
    f"{API_URL_PREFIX}{hackathon_models.HackathonDiscussion.DYNAMIC_KEY}/cud",
    get_model_cud_api_viewset(
        meta_model=hackathon_models.HackathonDiscussion,
        meta_fields=[
                    "hackathon",
                    "title",
                    "message",
                    ],
        meta_extra_kwargs={},
        get_serializer_meta=lambda x: {
            "hackathon": x.serialize_for_meta(hackathon_models.Hackathon.objects.all()),
        },
    ),
)
# Hackathon Discussion Comment
# --------------------------------------------------------------------------------------
router.register(
    f"{API_URL_PREFIX}{hackathon_models.HackathonDiscussionComment.DYNAMIC_KEY}/cud",
    get_model_cud_api_viewset(
        meta_model=hackathon_models.HackathonDiscussionComment,
        meta_fields=["hackathon_discussion","identity"],
        get_serializer_meta=lambda x: {
            "hackathon_discussion": x.serialize_for_meta(hackathon_models.HackathonDiscussion.objects.all()),
        },
    ),
)
# Hackathon Discussion Comment Reply
# --------------------------------------------------------------------------------------
router.register(
    f"{API_URL_PREFIX}{hackathon_models.HackathonDiscussionReply.DYNAMIC_KEY}/cud",
    get_model_cud_api_viewset(
        meta_model=hackathon_models.HackathonDiscussionReply,
        meta_fields=["comment","identity"],
        get_serializer_meta=lambda x: {},
    ),
)

#payment-mode
router.register(
    f"{API_URL_PREFIX}{PaymentMode.DYNAMIC_KEY}/cud",
    get_model_cud_api_viewset(
        meta_model=PaymentMode,
        meta_fields=["identity"],
        get_serializer_meta=lambda x: {},
    ),
)
router.register(
    f"{API_URL_PREFIX}{PaymentMode.DYNAMIC_KEY}/list",
    get_model_list_api_viewset(
        meta_queryset=PaymentMode.objects.all(),
        meta_all_table_columns={
            "identity": "Payment Mode",
        },
        fields_to_filter=["id"],
    ),
)


# Industry
# --------------------------------------------------------------------------------------
router.register(
    f"{API_URL_PREFIX}{industry_models.IndustryType.DYNAMIC_KEY}/cud",
    get_model_cud_api_viewset(
        meta_model=industry_models.IndustryType,
        meta_fields=["identity"],
        get_serializer_meta=lambda x: {},
    ),
)
router.register(
    f"{API_URL_PREFIX}{industry_models.IndustryType.DYNAMIC_KEY}/list",
    get_model_list_api_viewset( 
        meta_queryset=industry_models.IndustryType.objects.all(),
        meta_all_table_columns={
            "identity": "Industry",
        },
    ),
)

# University
# --------------------------------------------------------------------------------------
router.register(
    f"{API_URL_PREFIX}{profile_models.EducationUniversity.DYNAMIC_KEY}/cud",
    get_model_cud_api_viewset(
        meta_model=profile_models.EducationUniversity,
        meta_fields=["identity"],
        get_serializer_meta=lambda x: {},
    ),
)
router.register(
    f"{API_URL_PREFIX}{profile_models.EducationUniversity.DYNAMIC_KEY}/list",
    get_model_list_api_viewset(
        meta_queryset=profile_models.EducationUniversity.objects.all(),
        meta_all_table_columns={
            "identity": "Industry",
        },
    ),
)

# Student
# --------------------------------------------------------------------------------------
router.register(
    f"{API_URL_PREFIX}student/cud",
    get_model_cud_api_viewset(
        meta_model=User,
        meta_fields=[
            "first_name",
            "middle_name",
            "last_name",
            "gender",
            "user_role",
            # "martial_status",
            "birth_date",
            "identification_type",
            "identification_number",
            "address",
            "country",
            "state",
            "city",
            "pincode",
            "admission_id",
            "alternative_email",
            "education_details"
        ],
        get_serializer_meta=lambda x: {
            "gender": x.serialize_for_meta(profile_models.UserGender.objects.all()),
            # "martial_status": x.serialize_for_meta(profile_models.UserMartialStatus.objects.all()),
            "identification_type": x.serialize_for_meta(profile_models.UserIdentificationType.objects.all()),
            "state": x.serialize_for_meta(location_models.State.objects.all(), fields=['id', 'uuid', 'identity','country']),
            "city": x.serialize_for_meta(location_models.City.objects.all(), fields=['id', 'uuid', 'identity','state']),
            "country": x.serialize_for_meta(location_models.Country.objects.all()),
            "qualification": x.serialize_for_meta(EducationQualification.objects.all()),
            "university_name": x.serialize_for_meta(profile_models.EducationUniversity.objects.all()),
            "degree": x.serialize_for_meta(profile_models.OnboardingHighestEducation.objects.all()),
            "user_role": x.serialize_for_meta(UserRole.objects.all()),
        },
    ),
)
router.register(
    f"{API_URL_PREFIX}student/list",
    get_student_list_api_viewset(
        meta_queryset=User.objects.all(),
        meta_all_table_columns={
            "uuid": "ID",
            "first_name": "Student Name",
            "admission_id": "ID No",
            "idp_email": "Email",
            "status": "Status"
        },
    ),
)
# Staff
# --------------------------------------------------------------------------------------
router.register(
    f"{API_URL_PREFIX}staff/cud",
    get_model_cud_api_viewset(
        meta_model=User,
        meta_fields=[
            "first_name",
            "middle_name",
            "last_name",
            "user_role",
            "alternative_email"
        ],
        get_serializer_meta=lambda x: {
            "user_role": x.serialize_for_meta(UserRole.objects.all()),
        },
    ),
)
router.register(
    f"{API_URL_PREFIX}staff/list",
    get_staff_list_api_viewset(
        meta_queryset=User.objects.all(),
        meta_all_table_columns={
            "first_name": "Staff Name",
            "idp_email": "Email"
        },
    ),
)
# Employment type
# --------------------------------------------------------------------------------------
router.register(
    f"{API_URL_PREFIX}{profile_models.EmploymentType.DYNAMIC_KEY}/cud",
    get_model_cud_api_viewset(
        meta_model=profile_models.EmploymentType,
        meta_fields=["identity"],
        get_serializer_meta=lambda x: {},
    ),
)
router.register(
    f"{API_URL_PREFIX}{profile_models.EmploymentType.DYNAMIC_KEY}/list",
    get_model_list_api_viewset(
        meta_queryset=profile_models.EmploymentType.objects.all(),
        meta_all_table_columns={
            "identity": "Employment Type",
        },
    ),
)

# Education Qualification
# --------------------------------------------------------------------------------------
router.register(
    f"{API_URL_PREFIX}{EducationQualification.DYNAMIC_KEY}/cud",
    get_model_cud_api_viewset(
        meta_model=EducationQualification,
        meta_fields=["identity"],
        get_serializer_meta=lambda x: {},
    ),
)
router.register(
    f"{API_URL_PREFIX}{EducationQualification.DYNAMIC_KEY}/list",
    get_model_list_api_viewset(
        meta_queryset=EducationQualification.objects.all(),
        meta_all_table_columns={
            "identity": "Education Qualification",
        },
    ),
)
# Post 
# --------------------------------------------------------------------------------------
router.register(
    f"{API_URL_PREFIX}{Post.DYNAMIC_KEY}/cud",
    get_model_cud_api_viewset(
        meta_model=Post,
        meta_fields=[
                    "forum",
                    "post_type",
                    "identity",
                    "description",
                    "image",
                    "poll_options",
                    "post_attachment",
                    "tags",     
                    "enable_end_time",
                    "start_date",
                    "end_date",
                    "enable_hide_discussion"
                    ],
        meta_extra_kwargs={},
        get_serializer_meta=lambda x: {
            "post_type": x.serialize_for_meta(PostType.objects.all()),
        },
    ),
)
# Post - Type
# --------------------------------------------------------------------------------------
router.register(
    f"{API_URL_PREFIX}{PostType.DYNAMIC_KEY}/cud",
    get_model_cud_api_viewset(
        meta_model=PostType,
        meta_fields=["identity"],
        meta_extra_kwargs={},
        get_serializer_meta=lambda x: {},
    ),
)
router.register(
    f"{API_URL_PREFIX}{PostType.DYNAMIC_KEY}/list",
    get_model_list_api_viewset(
        meta_queryset=PostType.objects.all(),
        meta_all_table_columns={
            "identity": "Post Type",
        },
    ),
)
# Report List meta only
# -----------------------------------------------------------------------------------------
router.register(
    f"{API_URL_PREFIX}{StudentReportDetail.DYNAMIC_KEY}/list",
    get_model_list_api_viewset(
        meta_queryset=StudentReportDetail.objects.all(),
        meta_all_table_columns={
            "identity": "Report Name",
            "created": "generated On",
            "report": "Report Link",
            "period": "Period",
            "status": "Report Status",
        },
    ),
)
# Report Filter Parameter
# --------------------------------------------------------------------------------------
router.register(
    f"{API_URL_PREFIX}{ReportFilterParameter.DYNAMIC_KEY}/cud",
    get_model_cud_api_viewset(
        meta_model=ReportFilterParameter,
        meta_fields=["identity"],
        get_serializer_meta=lambda x: {},
    ),
)
router.register(
    f"{API_URL_PREFIX}{ReportFilterParameter.DYNAMIC_KEY}/list",
    get_model_list_api_viewset(
        meta_queryset=ReportFilterParameter.objects.all(),
        meta_all_table_columns={
            "identity": "Parameter",
        },
    ),
)
# Post Comment
# --------------------------------------------------------------------------------------
router.register(
    f"{API_URL_PREFIX}{PostComment.DYNAMIC_KEY}/cud",
    get_model_cud_api_viewset(
        meta_model=PostComment,
        meta_fields=["post","identity"],
        get_serializer_meta=lambda x: {
            "post": x.serialize_for_meta(Post.objects.all()),
        },
    ),
)
# Post Comment Reply
# --------------------------------------------------------------------------------------
router.register(
    f"{API_URL_PREFIX}{PostReply.DYNAMIC_KEY}/cud",
    get_model_cud_api_viewset(
        meta_model=PostReply,
        meta_fields=["comment","identity"],
        get_serializer_meta=lambda x: {},
    ),
)
# News
# --------------------------------------------------------------------------------------
router.register(
    f"{API_URL_PREFIX}{NewsDetail.DYNAMIC_KEY}/cud",
    get_model_cud_api_viewset(
        meta_model=NewsDetail,
        meta_fields=["title", "news_link", "image", "published_by",
                     "published_on","tags","skills"],
        get_serializer_meta=lambda x: {
            "skills": x.serialize_for_meta(Skill.objects.filter(is_archived=False)),
        },
    ),
)
router.register(
    f"{API_URL_PREFIX}{NewsDetail.DYNAMIC_KEY}/list",
    get_model_list_api_viewset(
        meta_queryset=NewsDetail.objects.all(),
        meta_all_table_columns={
            "title": "Title",
            "published_by": "Published By",
            "published_on": "Published On",
        },
        meta_init_fields_config={},
        fields_to_filter=["title"],
    ),
)

# Blog
# --------------------------------------------------------------------------------------
router.register(
    f"{API_URL_PREFIX}{Blog.DYNAMIC_KEY}/cud",
    get_model_cud_api_viewset(
        meta_model=Blog,
        meta_fields=[
            "identity",
            "description",
            "hash_tags",
            "image",
            "category",
            "zone",
        ],
        meta_extra_kwargs={},
        get_serializer_meta=lambda x: {
            "category": x.serialize_for_meta(Category.objects.all()),
            "zone": x.serialize_for_meta(Zone.objects.all()),
        },
    ),
)
router.register(
    f"{API_URL_PREFIX}{Blog.DYNAMIC_KEY}/list",
    get_model_list_api_viewset(
        meta_queryset=Blog.objects.all(),
        meta_all_table_columns={
            "identity": "Blog Name",
            "created":"Creation date",
            "status": "Status",
        },
        meta_init_fields_config={
            "Created_by": read_serializer(
                meta_model=User, meta_fields=['id','uuid','first_name']
            )(source="created_by"),
            "Category": read_serializer(
                meta_model=Category, meta_fields=['id','uuid', 'identity']
            )(source="category"),
        },
        fields_to_filter=["identity"],
    ),
)
# Blog Comment
# --------------------------------------------------------------------------------------
router.register(
    f"{API_URL_PREFIX}{BlogComment.DYNAMIC_KEY}/cud",
    get_model_cud_api_viewset(
        meta_model=BlogComment,
        meta_fields=["blog","identity"],
        get_serializer_meta=lambda x: {},
    ),
)
# Blog Comment Reply
# --------------------------------------------------------------------------------------
router.register(
    f"{API_URL_PREFIX}{BlogCommentReply.DYNAMIC_KEY}/cud",
    get_model_cud_api_viewset(
        meta_model=BlogCommentReply,
        meta_fields=["comment","identity"],
        get_serializer_meta=lambda x: {},
    ),
)

# Bulk Upload Template Data CUD
# --------------------------------------------------------------------------------------
router.register(
    f"{API_URL_PREFIX}{BulkUploadTemplateData.DYNAMIC_KEY}/cud",
    get_model_cud_api_viewset(
        meta_model=BulkUploadTemplateData,
        meta_fields=["identity","image"],
        get_serializer_meta=lambda x: {},
    ),
)
# Bulk Upload Template Data List
# --------------------------------------------------------------------------------------
router.register(
    f"{API_URL_PREFIX}{BulkUploadTemplateData.DYNAMIC_KEY}/list",
    get_model_list_api_viewset(
        meta_queryset=BulkUploadTemplateData.objects.all(),
        meta_all_table_columns={
            "id":"ID",
            "identity": "Template Name",

        },
        meta_init_fields_config={
            "image_details": read_serializer(
                meta_model=BulkUploadTemplate, meta_fields=['id','uuid','file']
            )(source="image"),
        },
    ),
)

urlpatterns = [
    # Add user view from admin
    path(f"{API_URL_PREFIX}create-user/", CreateUserAPIView.as_view()),
    path(f"{API_URL_PREFIX}video/upload/", VideoLinkAPIView.as_view()),
    # Edit user view from admin
    path(f"{API_URL_PREFIX}update-user/<int:pk>/", UpdateUserAPIView.as_view()),

    path(f"{API_URL_PREFIX}create-institution/", CreateInstitutionAPIView.as_view()),
    path(f"{API_URL_PREFIX}update-institution/<id>/", UpdateInstitutionAPIView.as_view()),

    # Employer
    path(f"{API_URL_PREFIX}employer/dashboard/", EmployerDashboardAPIView.as_view()),
    path(f"{API_URL_PREFIX}create-corporate/", CreateEmployerAPIView.as_view()),
    path(f"{API_URL_PREFIX}update-corporate/<id>/", UpdateEmployerAPIView.as_view()),

    # Interview Panel User Creation
    path(f"{API_URL_PREFIX}create-interview-panel/", CreateInterviewPanelAPIView.as_view()),
    path(f"{API_URL_PREFIX}update-interview-panel/<id>/", UpdateInterviewPanelAPIView.as_view()),

    # Interview Panel Schedule Interview 
    path(f"{API_URL_PREFIX}interview-schedule/meta/", MetaInterviewScheduleAPIView.as_view()),

    # Interview Panel Schedule Interview List
    # path(f"{API_URL_PREFIX}scheduled-interview/", InterviewScheduleListAPIView.as_view()),
    path(f"{API_URL_PREFIX}scheduled-interview-applicant/", InterviewScheduleApplicantListAPIView.as_view()),
    path(f"{API_URL_PREFIX}interview-feedback/<id>/meta/", SendFeedbackInterviewPanelMetaAPIView.as_view()),
    path(f"{API_URL_PREFIX}send-interview-feedback/<id>/", SendFeedbackInterviewPanelAPIView.as_view()),
    path(f"{API_URL_PREFIX}interview-feedback/<id>/", FeedbackInterviewPanelAPIView.as_view()),

    path(f"{API_URL_PREFIX}dynamic-config/", AdminCMSDynamicConfigAPIView.as_view()),
    path(
        f"{API_URL_PREFIX}{Vendor.DYNAMIC_KEY}/image/upload/",
        get_upload_api_view(meta_model=VendorImage).as_view(),
    ),
    path(
        f"{API_URL_PREFIX}{Author.DYNAMIC_KEY}/image/upload/",
        get_upload_api_view(meta_model=AuthorImage).as_view(),
    ),
    path(
        f"{API_URL_PREFIX}{Skill.DYNAMIC_KEY}/image/upload/",
        get_upload_api_view(meta_model=SkillImage).as_view(),
    ),
    path(
        f"{API_URL_PREFIX}{JobEligibleSkill.DYNAMIC_KEY}/image/upload/",
        get_upload_api_view(meta_model=JobEligibleSkillImage).as_view(),
    ),
    path(
        f"{API_URL_PREFIX}{Category.DYNAMIC_KEY}/image/upload/",
        get_upload_api_view(meta_model=CategoryImage).as_view(),
    ),
    path(
        f"{API_URL_PREFIX}{Course.DYNAMIC_KEY}/image/upload/",
        get_upload_api_view(meta_model=CourseImage).as_view(),
    ),
    path(
        f"{API_URL_PREFIX}{Course.DYNAMIC_KEY}/resource/upload/",
        get_upload_api_view(meta_model=CourseResource).as_view(),
    ),
    path(
        f"{API_URL_PREFIX}{CourseSubModule.DYNAMIC_KEY}/document/upload/",
        get_upload_api_view(meta_model=ModuleTypeDocument).as_view(),
    ),
    path(
        f"{API_URL_PREFIX}{Testimonial.DYNAMIC_KEY}/image/upload/",
        get_upload_api_view(meta_model=TestimonialImage).as_view(),
    ),
    path(
        f"{API_URL_PREFIX}{LearningPath.DYNAMIC_KEY}/image/upload/",
        get_upload_api_view(meta_model=LearningPathImage).as_view(),
    ),
    path(
        f"{API_URL_PREFIX}{CertificationPath.DYNAMIC_KEY}/image/upload/",
        get_upload_api_view(meta_model=CertificationPathImage).as_view(),
    ),
    # Learning Role
    path(
        f"{API_URL_PREFIX}{LearningRole.DYNAMIC_KEY}/image/upload/",
        get_upload_api_view(meta_model=LearningRoleImage).as_view(),
    ),
    # Zone urls
    path(
        f"{API_URL_PREFIX}{Zone.DYNAMIC_KEY}/image/upload/",
        get_upload_api_view(meta_model=ZoneImage).as_view(),
    ),
    # Forum urls
    path(
        f"{API_URL_PREFIX}{Forum.DYNAMIC_KEY}/image/upload/",
        get_upload_api_view(meta_model=ForumImage).as_view(),
    ),
    # Forum post urls
    path(
        f"{API_URL_PREFIX}{Post.DYNAMIC_KEY}/image/upload/",
        get_upload_api_view(meta_model=PostImage).as_view(),
    ),
    path(
        f"{API_URL_PREFIX}{Post.DYNAMIC_KEY}/subjective-image/upload/",
        get_upload_api_view(meta_model=SubjectivePostImage).as_view(),
    ),
    # webinar/speaker image urls
    path(
        f"{API_URL_PREFIX}{Webinar.DYNAMIC_KEY}/image/upload/",
        get_upload_api_view(meta_model=WebinarImage).as_view(),
    ),
    # path(
    #     f"{API_URL_PREFIX}{Webinar.DYNAMIC_KEY}/speaker-image/upload/",
    #     get_upload_api_view(meta_model=SpeakerImage).as_view(),
    # ),
    path(
        f"{API_URL_PREFIX}{certificate_models.Certificate.DYNAMIC_KEY}/sponsor_logo/upload/",
        get_upload_api_view(meta_model=certificate_models.CertificateSponsorImage).as_view(),
    ),
    path(
        f"{API_URL_PREFIX}{certificate_models.Certificate.DYNAMIC_KEY}/image/upload/",
        get_upload_api_view(meta_model=certificate_models.CertificateImage).as_view(),
    ),
    # hackathon urls
    path(
        f"{API_URL_PREFIX}{hackathon_models.Hackathon.DYNAMIC_KEY}/image/upload/",
        get_upload_api_view(meta_model=hackathon_models.HackathonImage).as_view(),
    ),
    path(
        f"{API_URL_PREFIX}{round_models.HackathonJudge.DYNAMIC_KEY}/image/upload/",
        get_upload_api_view(meta_model=round_models.JudgeImage).as_view(),
    ),
    # Sale Discount image upload urls
    path(
        f"{API_URL_PREFIX}{salediscount_models.SaleDiscount.DYNAMIC_KEY}/image/upload/",
        get_upload_api_view(meta_model=salediscount_models.SaleDiscountImage).as_view(),
    ),
    # Subscription Plan Upload Image
    path(
        f"{API_URL_PREFIX}{SubscriptionPlan.DYNAMIC_KEY}/image/upload/",
        get_upload_api_view(meta_model=SubscriptionPlanImage).as_view(),
    ),
    # Functional Area
    path(
        f"{API_URL_PREFIX}{linkage_models.FunctionalArea.DYNAMIC_KEY}/image/upload/",
        get_upload_api_view(meta_model=linkage_models.FunctionalAreaImage).as_view(),
    ),
    # Institution Banner Image
    path(
        f"{API_URL_PREFIX}{InstitutionDetail.DYNAMIC_KEY}/banner_image/upload/",
        get_upload_api_view(meta_model=InstitutionBannerImage).as_view(),
    ),
    # Institution Logo Image
    path(
        f"{API_URL_PREFIX}{EmployerDetail.DYNAMIC_KEY}/logo_image/upload/",
        get_upload_api_view(meta_model=EmployerLogoImage).as_view(),
    ),
    # Interview Feedback Attachment 
    path(
        f"{API_URL_PREFIX}{JobFeedbackOption.DYNAMIC_KEY}/image/upload/",
        get_upload_non_auth_api_view(meta_model=JobFeedbackAttachment).as_view(),
    ),
    # News thumbnail image
    path(
        f"{API_URL_PREFIX}{NewsDetail.DYNAMIC_KEY}/image/upload/",
        get_upload_api_view(meta_model=NewsThumbnailImage).as_view(),
    ),
    path(
        f"{API_URL_PREFIX}{BulkUploadTemplateData.DYNAMIC_KEY}/upload/",
        get_upload_api_view(meta_model=BulkUploadTemplate).as_view(),
    ),
    # IDP Auth
    # path(
    #     f"{API_PROXY_URL_PREFIX}v1/refresh/",
    #     proxy_to_idp_view(url_path="/api/access/v1/refresh/").as_view(),
    # ),
    # path(
    #     f"{API_PROXY_URL_PREFIX}v1/simple-login/",
    #     proxy_to_idp_view(url_path="/api/access/v1/simple-login/").as_view(),
    # ),
    # path(
    #     f"{API_PROXY_URL_PREFIX}v1/logout/",
    #     proxy_to_idp_view(url_path="/api/access/v1/logout/").as_view(),
    # ),
    path(
        f"{API_PROXY_URL_PREFIX}v1/simple-login/",CMSLoginAPIView.as_view(),
    ),
    path(
        f"{API_PROXY_URL_PREFIX}v1/logout/",LogoutAPIView.as_view(),
    ),

    # CRUD API for student in which his email, password, phone_number will be saved in IDP
    # and other details will be saved in the User model
    path(f"{API_URL_PREFIX}create-student/", StudentCreateAPIView.as_view()),
    path(f"{API_URL_PREFIX}edit-student/<id>/", StudentEditAPIView.as_view()),
    path(f"{API_URL_PREFIX}delete-student/<id>/", StudentDeleteAPIView.as_view()),
    path(f"{API_URL_PREFIX}detail-student/<uuid>/", StudentDetailAPIView.as_view()),

    # path(f"{API_URL_PREFIX}student/list/", StudentListAPIView.as_view()),
    # CRUD API for staff in which his email, password, phone_number will be saved in IDP
    # and other details will be saved in the User model
    path(f"{API_URL_PREFIX}create-staff/", StaffCreateAPIView.as_view()),
    path(f"{API_URL_PREFIX}edit-staff/<id>/", StaffEditAPIView.as_view()),
    path(f"{API_URL_PREFIX}delete-staff/<id>/", StaffDeleteAPIView.as_view()),
    path(f"{API_URL_PREFIX}detail-staff/<uuid>/", StaffDetailAPIView.as_view()),

    # SUbscription Detail View 
    path(f"{API_URL_PREFIX}detail-subscription-plan/<uuid>/", SubscriptionPlanDetailView.as_view()),
    path(f"{API_URL_PREFIX}subscription-plan/status/update/<id>/", SubscriptionPlanStatusUpdateAPIView.as_view()),

    # Hackathon
    path(f"{API_URL_PREFIX}create-hackathon-updates/<uuid>/", CreateHackathonUpdate.as_view()),

    # path(f"{API_URL_PREFIX}staff/list/", StaffListAPIView.as_view()),

    # Institution User Group
    path(f"{API_URL_PREFIX}admin/dashboard/", AdminHomeAPIView.as_view()),
    path(f"{API_URL_PREFIX}admin/dashboard/details/", AdminDetailHomeAPIView.as_view()),

    path(f"{API_URL_PREFIX}institution/dashboard/", InstitutionAdminDashboardAPIView.as_view()),
    path(f"{API_URL_PREFIX}institution/content-dashboard/", InstitutionAdminDashboardTrendingAPIView.as_view()),
    path(f"{API_URL_PREFIX}create-institution-user-group/", CreateInstitutionUserGroupAPIView.as_view()),
    path(f"{API_URL_PREFIX}edit-institution-user-group/<id>/", UpdateInstitutionUserGroupAPIView.as_view()),
    path(f"{API_URL_PREFIX}detail-institution-user-group/<uuid>/", DetailInstitutionUserGroupAPIView.as_view()),
    path(f"{API_URL_PREFIX}institution-user-group/meta/", MetaInstitutionUserGroupAPIView.as_view()),

    # Institution User Content Group
    path(f"{API_URL_PREFIX}detail-institution-user-group-content/<uuid>/", DetailInstitutionUserGroupContentAPIView.as_view()),
    path(f"{API_URL_PREFIX}institution-user-group-content/meta/", MetaInstitutionUserGroupContentAPIView.as_view()),

    # Student Learning Trackers
    path(f"{API_URL_PREFIX}student/my-learnings/home/<uuid>/", StudentMyLearningsAPIView.as_view()),

    #Course bulk upload
    path(f"{API_URL_PREFIX}course/my-learnings/bulk-upload/", CourseBulkUploadAPIView.as_view()),

    #Course bulk upload
    path(f"{API_URL_PREFIX}sub-plan/my-learnings/bulk-upload/", SubPlanBulkUploadAPIView.as_view()),
    path(f"{API_URL_PREFIX}sub-plan-module/my-learnings/bulk-upload/", SubPlanModuleBulkUploadAPIView.as_view()),
    path(f"{API_URL_PREFIX}sub-plan-sub-module/my-learnings/bulk-upload/", SubPlanSubModuleBulkUploadAPIView.as_view()),

    # Logo For Employer, Institute and Student
    path(f"{API_URL_PREFIX}logo/", LogoImageAPIView.as_view()),

    # Zone urls
    path(f"{API_URL_PREFIX}{Zone.DYNAMIC_KEY}/", ZoneListAPIView.as_view()),

    path(f"{API_URL_PREFIX}{Zone.DYNAMIC_KEY}/<id>/detail/", ZoneDetailAPIView.as_view()),

    path(f"{API_URL_PREFIX}{Zone.DYNAMIC_KEY}/<id>/forum/<forum_id>/post/list/", ForumPostListAPIView.as_view()),

    # Like forum-post url
    path(f"{API_URL_PREFIX}{Zone.DYNAMIC_KEY}/<id>/forum/<forum_id>/post/<post_id>/like/", ForumPostLikeAPIView.as_view()),
    # Forum post comments list
    path(f"{API_URL_PREFIX}{Zone.DYNAMIC_KEY}/<id>/forum/<forum_id>/post/<post_id>/comment/list/", ForumPostCommentListAPIView.as_view()),
    # Forum post comment replies list
    path(f"{API_URL_PREFIX}{Zone.DYNAMIC_KEY}/<id>/forum/<forum_id>/post/<post_id>/comment/<comment_id>/reply/list/", ForumPostReplyListAPIView.as_view()),
    # Forum post poll option click url
    path(f"{API_URL_PREFIX}{Zone.DYNAMIC_KEY}/<id>/forum/<forum_id>/post/<post_id>/polloption/<poll_option_id>/", PostPollOptionClickAPIView.as_view()),
    #Report Generate API
    path(f"{API_URL_PREFIX}generate-report/", ReportGenerateAPIView.as_view()),

    path(f"{API_URL_PREFIX}generate-report/list/", ReportListAPIView.as_view()),

    path(f"{API_URL_PREFIX}generate-report/meta/", ReportGenerateMetaAPIView.as_view()),

    path(f"{API_URL_PREFIX}generate-report/delete/<pk>/", ReportDeleteAPIView.as_view()),

    path(f"{API_URL_PREFIX}learning-content/meta/", LearningContentMetaAPIView.as_view()),
    # blog urls
    path(f"{API_URL_PREFIX}{Blog.DYNAMIC_KEY}/<id>/detail/", BlogDetailAPIView.as_view()),
    # Like blog url
    path(f"{API_URL_PREFIX}{Blog.DYNAMIC_KEY}/<id>/like/", BlogLikeAPIView.as_view()),
    # Blog Upload Image
    path(
        f"{API_URL_PREFIX}{Blog.DYNAMIC_KEY}/image/upload/",
        get_upload_api_view(meta_model=BlogImage).as_view(),
    ),
    # Blog comments list
    path(f"{API_URL_PREFIX}{Blog.DYNAMIC_KEY}/<id>/comment/list/", BlogCommentListAPIView.as_view()),
    # Blog comment replies list
    path(f"{API_URL_PREFIX}{Blog.DYNAMIC_KEY}/<id>/comment/<comment_id>/reply/list/", BlogCommentReplyListAPIView.as_view()),
    # archieve blog url
    path(f"{API_URL_PREFIX}{Blog.DYNAMIC_KEY}/<id>/archieve/", BlogArchieveAPIView.as_view()),
    # approve blog url
    path(f"{API_URL_PREFIX}{Blog.DYNAMIC_KEY}/<id>/approve/", BlogApproveAPIView.as_view()),
    # decline blog url
    path(f"{API_URL_PREFIX}{Blog.DYNAMIC_KEY}/<id>/decline/", BlogDeclineAPIView.as_view()),
    # Hackathon discussion list
    path(f"{API_URL_PREFIX}{hackathon_models.Hackathon.DYNAMIC_KEY}/<id>/discussion/list/", HackathonDiscussionListAPIView.as_view()),
    # Hackathon discussion comments list
    path(f"{API_URL_PREFIX}{hackathon_models.Hackathon.DYNAMIC_KEY}/<id>/discussion/<discussion_id>/comment/list/", HackathonDiscussionCommentListAPIView.as_view()),
    # Hackathon discussion comment replies list
    path(f"{API_URL_PREFIX}{hackathon_models.Hackathon.DYNAMIC_KEY}/<id>/discussion/<discussion_id>/comment/<comment_id>/reply/list/", HackathonDiscussionReplyListAPIView.as_view()),
    #Student bulk upload
    path(f"{API_URL_PREFIX}student/bulk-upload/", StudentsBulkUploadAPIView.as_view()),
    # Webinar discussion list
    path(f"{API_URL_PREFIX}{Webinar.DYNAMIC_KEY}/<id>/discussion/list/", WebinarDiscussionListAPIView.as_view()),
    path(f"{API_URL_PREFIX}{WebinarRegistration.DYNAMIC_KEY}/list/", WebinarRegistrationListAPIViewset.as_view()),
    # Webinar discussion comments list
    path(f"{API_URL_PREFIX}{Webinar.DYNAMIC_KEY}/<id>/discussion/<discussion_id>/comment/list/", WebinarDiscussionCommentListAPIView.as_view()),
    # Webinar discussion comment replies list
    path(f"{API_URL_PREFIX}{Webinar.DYNAMIC_KEY}/<id>/discussion/<discussion_id>/comment/<comment_id>/reply/list/", WebinarDiscussionReplyListAPIView.as_view()),
    path(
        f"{API_URL_PREFIX}{BlendedLearningPath.DYNAMIC_KEY}/image/upload/",
        get_upload_api_view(meta_model=BlendedLearningPathImage).as_view(),
    ),
    path(f"{API_URL_PREFIX}create-blended-learning-path/", CreateBlendedLearningAPIView.as_view()),
    path(f"{API_URL_PREFIX}update-blended-learning-path/<id>/", UpdateBlendedLearningAPIView.as_view()),
    path(
        f"{API_URL_PREFIX}{BlendedLearningPathCourseModesAndFee.DYNAMIC_KEY}/list/",
        BlendedLearningModeAndFeeListAPIViewSet.as_view({'get': 'list'}),
        name="blended_learning_list",
    ),
    path(
        f"{API_URL_PREFIX}{BlendedLearningClassroomAndVirtualDetails.DYNAMIC_KEY}/list/",
        BlendedLearningClassroomAndVirtualListAPIViewSet.as_view({'get': 'list'}),
        name="blended_learning_classroom_virtual_list",
    ),

    path(f"{API_URL_PREFIX}subscription_plan_list/list/", SubscriptionPlanListAPIView.as_view()),
    path(f"{API_URL_PREFIX}learning-content/", LearningContentAPIView.as_view()),
    path(f"{API_URL_PREFIX}all-learning-content/", AllLearningContentAPIView.as_view()),
    path(f"{API_URL_PREFIX}learning-content-feedback/list/", LearningContentFeedbackAPIView.as_view()),
    path(f"{API_URL_PREFIX}learning-content-feedback/list/table-meta/", LearningContentFeedbackMeta.as_view()),

    path(f"{API_URL_PREFIX}fresher-pool/list/", FresherPoolListAPIView.as_view()),
    path(f"{API_URL_PREFIX}fresher-pool/table-meta/", FresherPoolsMeta.as_view()),
    path(f"{API_URL_PREFIX}student/one-profile/view/<uuid>/", AdminStudentOneProfileAPIView.as_view()),
    path(f"{API_URL_PREFIX}fresher-pool/applicant-status/update/<id>/", UpdateFresherPoolApplicantStatus.as_view()),
    path(f"{API_URL_PREFIX}applicant-list/status/<user_id>/<job_id>/", UpdateApplicantListStatus.as_view()),

    path(f"{API_URL_PREFIX}forum-comment/delete/<uuid>/", DeleteForumComment.as_view()),
    # NOTE: this is not a valid method
    path(f"{API_URL_PREFIX}online-user-blended-learning-path-tracker/list/", BlendedLearningPathCustomerOnlineListAPIViewset.as_view()),
    path(f"{API_URL_PREFIX}classroom-user-blended-learning-path-tracker/list/", BlendedLearningPathCustomerClassroomListAPIViewset.as_view()),
    path(f"{API_URL_PREFIX}online-user-blended-learning-path-tracker/list/table-meta/", BlendedLearningPathCustomerOnlineListTableMetaAPIViewset.as_view()),
    path(f"{API_URL_PREFIX}classroom-user-blended-learning-path-tracker/list/table-meta/", BlendedLearningPathCustomerClassroomListTableMetaAPIViewset.as_view()),

    # Badge Image
    # path(
    #     f"{API_URL_PREFIX}{Badges.DYNAMIC_KEY}/image/upload/",
    #     get_upload_api_view(meta_model=BadgeImage).as_view(),
    # ),

    #Bulk Skil Archive
    path(f"{API_URL_PREFIX}skill/archive/", BulkSkillArchiveAPIView.as_view()),

    path(f"{API_URL_PREFIX}user/bulk-upload/", UsersBulkUploadAPIView.as_view()),
   
] + router.urls

# TODO: `handle_performance_chain` in Course & Other Models
