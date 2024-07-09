# flake8: noqa
from .certification_path import (
    CertificationPath,
    CertificationPathImage,
    CertificationPathLearningPath,
    CertificationPathLevel,
)
from .course import Course, CourseImage, CourseResource, CourseLevel, CourseModule, CourseSubModule, MyLearningsNotes, ModuleType, CourseRating, LearningContentFeedback, ModuleTypeDocument
from .learning_path import (
    LearningPath,
    LearningPathCourse,
    LearningPathImage,
    LearningPathLevel,
)
from .linkages import (
    Category,
    CategoryImage,
    CategoryPopularity,
    Proficiency,
    Skill,
    SkillImage,
    SkillPopularity,
    JobEligibleSkill,
    JobEligibleSkillImage,
    Tag,
    LearningRoleImage,
    LearningRole,
)
from .providers import (
    Accreditation,
    Author,
    AuthorImage,
    Language,
    Tutor,
    Vendor,
    VendorImage,
    CourseWhatWillYouLearn,
)
from .certificate import (
    CertificateSponsorImage,
    CertificateImage,
    Certificate,
    CertificateLearningType,
)

from .blended_learning_path import (
    BlendedLearningPathImage,
    BlendedLearningPathLevel,
    BlendedLearningPath,
    # BlendedLearningPathCourse,
    BlendedLearningPathCourseMode,
    # BlendedLearningPathCourseDetails,
    BlendedLearningClassroomAndVirtualDetails,
    BlendedLearningPathCourseModesAndFee,
    BlendedLearningPathLearningType,
    BlendedLearningUserEnroll,
    BlendedLearningUserEnrollCourseDetails,
    BlendedLearningPathCustomerEnquiry,
    BlendedLearningPathPriceDetails,
    BlendedLearningPathScheduleDetails,
)

from .mml_course import (
    MMLCourse,
    MMLCourseLevel,
    MMLCourseImage
)
# TODO: Thumbnail images (smaller images)?
