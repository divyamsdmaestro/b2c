from apps.common.views.api import AppAPIView
from apps.learning import models
from apps.payments.models import Discount, SaleDiscount
from apps.web_portal.models import Testimonial
from apps.meta.models import location as location_models
from apps.meta.models import mics as mics_models
from apps.meta.models import profile as profile_models
from apps.hackathons.models import hackathon as hackathon_models
from apps.learning.models import certificate as certificate_models
from apps.access.models import UserRole, InstitutionDetail, Permission, PermissionCategory, EmployerDetail
from apps.webinars.models import Webinar, PaymentMode, WebinarRegistration
from apps.jobs.models import  EducationQualification, FunctionalArea, JobCriteria
from apps.payments.models import SubscriptionPlan, SubscriptionPlanCustomerEnquiry
from apps.forums.models import Zone, ZoneType, PostType
from apps.jobs.models import NewsDetail
from apps.blogs.models import Blog
from apps.hackathons.models import industry as industry_models
from apps.ecash.models import Ecash,EcashMeta
# from apps.badges.models import Badges,BadgesMeta
from apps.my_learnings.models import UserBlendedLearningPathTracker

class AdminCMSDynamicConfigAPIView(AppAPIView):
    """Sends out a dynamic config for the front-end to render the navigation bar."""

    def get(self, *args, **kwargs):
        return self.send_response(
            data={
                "navigation_render_config": [
                    {
                        "display": "Dashboard", "key": "dashboard",
                    },
                    {
                        "display": "Manage",
                        "key": None,
                        "sub_links": [
                            {"display": "User Management", "key":"user-management",
                                 "sub_sub_links": [
                                    {"display": "Users", "key":"user"},
                                    {"display": "User Roles", "key":UserRole.DYNAMIC_KEY},
                                    {
                                        "display": "Certificate",
                                        "key": certificate_models.Certificate.DYNAMIC_KEY,
                                    },
                                ],
                            },
                            {"display": "Plans", "key": SubscriptionPlan.DYNAMIC_KEY},
                            {
                                "display": "Learning Type",
                                "key": certificate_models.CertificateLearningType.DYNAMIC_KEY,
                            },
                            {
                                "display": "Campaign Leads",
                                "key": models.BlendedLearningPathCustomerEnquiry.DYNAMIC_KEY,
                            },
                            {
                                "display": "Webinar Leads",
                                "key": WebinarRegistration.DYNAMIC_KEY,
                            },
                            {
                                "display": "BLP - Online Training Leads",
                                "key": "online-user-blended-learning-path-tracker",
                            },
                            {
                                "display": "BLP - Classroom Learning Leads",
                                "key": "classroom-user-blended-learning-path-tracker",
                            },
                            {
                                "display": "Subscription Plan Leads",
                                "key": SubscriptionPlanCustomerEnquiry.DYNAMIC_KEY,
                            },
                        ],
                        
                    },
                    {
                        "display": "Learning",
                        "key": None,
                        "sub_links": [
                            {"display": "Skill", "key": models.Skill.DYNAMIC_KEY},
                            {"display": "Category", "key": models.Category.DYNAMIC_KEY},
                            {"display": "Job Eligibility Skill", "key": models.JobEligibleSkill.DYNAMIC_KEY},
                            {"display": "Course", "key": models.Course.DYNAMIC_KEY},
                            {
                                "display": "Learning Path",
                                "key": models.LearningPath.DYNAMIC_KEY,
                            },
                            {
                                "display": "Advanced Learning Path",
                                "key": models.CertificationPath.DYNAMIC_KEY,
                            },
                            {
                                "display": "Blended Learning Path",
                                "key": models.BlendedLearningPath.DYNAMIC_KEY,
                            },
                            {
                                "display": "BLP V2",
                                "key": models.BlendedLearningPathPriceDetails.DYNAMIC_KEY,
                            },
                            {
                                "display": "MML Course",
                                "key": models.MMLCourse.DYNAMIC_KEY,
                            },
                            {
                                "display": "Learning Content Feedback",
                                "key": models.LearningContentFeedback.DYNAMIC_KEY,
                            },
                            {
                                "display": "ECash",
                                "key": Ecash.DYNAMIC_KEY,
                            },
                            # {
                            #     "display": "Badges",
                            #     "key": Badges.DYNAMIC_KEY,
                            # },     
                        ],
                    },
                    {
                        "display": "Community",
                        "key": None,
                        "sub_links": [
                            {"display": "Community zones", "key": Zone.DYNAMIC_KEY},
                            {"display": "Hackathon", "key": hackathon_models.Hackathon.DYNAMIC_KEY},
                            {"display": "Webinars", "key": Webinar.DYNAMIC_KEY},
                            {"display": "Blogs", "key": Blog.DYNAMIC_KEY},
                        ],
                    },
                    {
                        "display": "Tenants",
                        "key": None,
                        "sub_links": [
                            {"display": "Institution", "key": InstitutionDetail.DYNAMIC_KEY},
                            {"display": "Corporates", "key": EmployerDetail.DYNAMIC_KEY},
                        ],
                    },
                    {
                        "display": "Learning Meta",
                        "key": None,
                        "sub_links": [
                            {"display": "Author", "key": models.Author.DYNAMIC_KEY},
                            {
                                "display": "Category Popularity",
                                "key": models.CategoryPopularity.DYNAMIC_KEY,
                            },
                            {"display": "Level", "key": models.CourseLevel.DYNAMIC_KEY},
                            {
                                "display": "Skill Popularity",
                                "key": models.SkillPopularity.DYNAMIC_KEY,
                            },
                            {"display": "Vendor", "key": models.Vendor.DYNAMIC_KEY},
                            {"display": "Tag", "key": models.Tag.DYNAMIC_KEY},
                            {
                                "display": "Accreditation",
                                "key": models.Accreditation.DYNAMIC_KEY,
                            },
                            {"display": "University", "key": profile_models.EducationUniversity.DYNAMIC_KEY},
                            {"display": "Learning Role", "key": models.LearningRole.DYNAMIC_KEY},
                            {"display": "Payment Mode", "key": PaymentMode.DYNAMIC_KEY},
                            {"display": "User Role Policy  Category", "key":PermissionCategory.DYNAMIC_KEY},
                            {"display": "User Role Policy Sub-Category", "key": Permission.DYNAMIC_KEY},
                            {"display": "Zone Type", "key": ZoneType.DYNAMIC_KEY},
                            {"display": "Module Type", "key": models.ModuleType.DYNAMIC_KEY},
                            {"display": "Course Modes", "key": models.BlendedLearningPathCourseMode.DYNAMIC_KEY},
                            {"display": "BLP Learning Type", "key": models.BlendedLearningPathLearningType.DYNAMIC_KEY},
                            {
                                "display": "Ecash-Meta",
                                "key": EcashMeta.DYNAMIC_KEY,   
                            },
                            # {
                            #     "display": "Badges-Meta",
                            #     "key": BadgesMeta.DYNAMIC_KEY,   
                            # },

                        ],
                    },
                    {
                        "display": "Website Meta",
                        "key": None,
                        "sub_links": [
                            {"display": "Testimonials", "key": Testimonial.DYNAMIC_KEY},
                            {"display": "Language","key": models.Language.DYNAMIC_KEY},
                            {"display": "Country","key": location_models.Country.DYNAMIC_KEY},
                            {"display": "State","key": location_models.State.DYNAMIC_KEY},
                            {"display": "City","key": location_models.City.DYNAMIC_KEY},
                            {"display": "BLP Address","key": location_models.BLPAddress.DYNAMIC_KEY},
                            {"display": "Gender","key": profile_models.UserGender.DYNAMIC_KEY},
                            {"display": "Identification Type","key": profile_models.UserIdentificationType.DYNAMIC_KEY},
                            {"display": "Marital Status","key": profile_models.UserMartialStatus.DYNAMIC_KEY},
                            {"display": "Onboarding Level", "key": profile_models.OnboardingLevel.DYNAMIC_KEY},
                            {"display": "Onboarding Highest Education","key": profile_models.OnboardingHighestEducation.DYNAMIC_KEY},
                            {"display": "Onboarding Area Of Interest","key": profile_models.OnboardingAreaOfInterest.DYNAMIC_KEY},
                            {"display": "FAQ", "key": mics_models.FrequentlyAskedQuestion.DYNAMIC_KEY},
                            # {"display": "Sales Discount", "key": SaleDiscount.DYNAMIC_KEY},
                            {"display": "Employment Type", "key": profile_models.EmploymentType.DYNAMIC_KEY},
                            # {"display": "Job Title", "key": JobTitle.DYNAMIC_KEY},
                            {"display": "Education Qualification", "key": EducationQualification.DYNAMIC_KEY},
                            {"display": "Industry", "key": industry_models.IndustryType.DYNAMIC_KEY},
                            {"display": "Job Functional Area", "key": FunctionalArea.DYNAMIC_KEY},
                            {"display": "Job Criteria", "key": JobCriteria.DYNAMIC_KEY},
                            {"display": "News", "key": NewsDetail.DYNAMIC_KEY},
                            {"display": "Post Type", "key": PostType.DYNAMIC_KEY},
                        ],
                    },
                    {
                        "display": "Discounts", "key": Discount.DYNAMIC_KEY,
                    },
                   
                ]
            }
        )
