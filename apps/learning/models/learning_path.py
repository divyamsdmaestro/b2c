from django.db import models

from apps.common import model_fields
from apps.common.models import (
    COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG,
    COMMON_CHAR_FIELD_MAX_LENGTH,
    BaseModel,
    FileOnlyModel,
)
from apps.learning.models.linkages import (
    BaseLinkagesModel,
    Category,
    Proficiency,
    Skill,
    Tag,
)
from apps.learning.models.course import CourseLevel
from apps.learning.models.price import AbstractPriceModelFields
from apps.common.helpers import validate_rating

class LearningPathImage(FileOnlyModel):
    """Image data for a `LearningPath`."""

    file = model_fields.AppSingleFileField(
        upload_to="files/learning-path/image/",
    )


class LearningPathLevel(BaseModel):
    """Holds data for a `Learning Path Level`."""

    DYNAMIC_KEY = "learning-path-level"

    identity = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH)


class LearningPath(BaseLinkagesModel, AbstractPriceModelFields, BaseModel):
    """
    Holds `LearningPath` data which contain `Courses` under it.

    NOTE:
        1. The linkage fields are only defined here for performance enhancements.
        2. The actual linkages are mentioned in the underlying `Course` model.
    """

    class Meta(BaseModel.Meta):
        default_related_name = "related_learning_paths"

    DYNAMIC_KEY = "learning-path"

    identity = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH)
    
    code = models.CharField(
        max_length=COMMON_CHAR_FIELD_MAX_LENGTH,
        **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG
    )
    language = models.ForeignKey(
        to="learning.Language",
        on_delete=models.SET_NULL,
        **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG
    )
    description = models.TextField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)

    duration = models.PositiveIntegerField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)

    start_date = models.DateField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    end_date = models.DateField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)

    skills = models.ManyToManyField(to="learning.Skill", blank=True)

    categories = models.ManyToManyField(to="learning.Category", blank=True)

    # Feedbacks
    enable_ratings = models.BooleanField(default=False)
    enable_feedback_comments = models.BooleanField(default=False)

    sequential_course_flow = models.BooleanField(default=False)
    make_this_lp_popular = models.BooleanField(default=False)

    make_this_lp_best_selling = models.BooleanField(default=False)
    make_this_lp_trending = models.BooleanField(default=False)

    requirements = models.TextField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    highlights = models.TextField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)

    image = models.ForeignKey(
        to=LearningPathImage,
        on_delete=models.SET_NULL,
        **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG
    )

    number_of_seats = models.PositiveIntegerField(
        **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG
    )

    rating = models.FloatField(default=5, validators=[validate_rating])  # aggregated on runtime

    level = models.ForeignKey(
        to=CourseLevel,
        on_delete=models.SET_NULL,
        **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG
    )

    accreditation = models.ForeignKey(
        to="learning.Accreditation",
        on_delete=models.SET_NULL,
        **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG
    )

    is_certification_enabled = models.BooleanField(default=False)
    is_free = models.BooleanField(default=False)
    is_private_course = models.BooleanField(default=False)
    mml_sku_id = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH, **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    vm_name = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH, **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    virtual_lab = models.BooleanField(default=False)
    
    def handle_performance_chain(self):
        """Uses chain of responsibility to update performance related fields."""

        filter_config = {
            "related_courses__related_learning_path_courses__learning_path": self
        }

        self.proficiency = Proficiency.objects.filter(**filter_config).last()
        self.tags.set(Tag.objects.filter(**filter_config))
        self.skills.set(Skill.objects.filter(**filter_config))
        self.categories.set(Category.objects.filter(**filter_config))
        self.save()


class LearningPathCourse(BaseModel):
    """
    Holds the data for a single `Course` inside a `LearningPath`.

    Needed because, each course can hold different position's
    under different learning paths..
    """

    DYNAMIC_KEY = "learning-path-course"

    position = models.PositiveIntegerField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    course = models.ForeignKey(
        to="learning.Course",
        on_delete=models.CASCADE,
        related_name="related_learning_path_courses",
    )

    learning_path = models.ForeignKey(
        to=LearningPath,
        on_delete=models.CASCADE,
        related_name="related_learning_path_courses",
    )
