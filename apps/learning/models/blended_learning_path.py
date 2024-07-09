from django.db import models

from apps.common import model_fields
from django.db.models import JSONField
from apps.common.models import (
    COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG,
    COMMON_CHAR_FIELD_MAX_LENGTH,
    BaseModel,
    FileOnlyModel,
)
from apps.learning.models.certification_path import CertificationPath
from apps.learning.models.price import AbstractPriceModelFields

from apps.learning.models.course import CourseLevel
from apps.common.helpers import validate_rating
from django.core.validators import RegexValidator
from apps.meta.models.location import BLPAddress

class BlendedLearningPathImage(FileOnlyModel):
    """Image data for a `BlendedLearningPath`."""

    file = model_fields.AppSingleFileField(
        upload_to="files/blended-learning-path/image/",
    )


class BlendedLearningPathLevel(BaseModel):
    """Holds data for a `Blended Learning Path Level`."""

    DYNAMIC_KEY = "blended-learning-path-level"

    identity = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH)


class BlendedLearningPathLearningType(BaseModel):

    DYNAMIC_KEY = "blended-learning-path-learning-type"

    identity = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH)
    
class BlendedLearningPathCourseMode(BaseModel):

    DYNAMIC_KEY = "blended-learning-path-course-mode"

    identity = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH)


class BlendedLearningPath(AbstractPriceModelFields, BaseModel):
    """Holds the Blended Learning Path data. Just a collection of Blended Learning Paths."""

    DYNAMIC_KEY = "blended-learning-path"

    identity = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH)

    description = models.TextField()

    image = models.ForeignKey(
        to=BlendedLearningPathImage,
        on_delete=models.SET_NULL,
        **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG
    )
    learning_path_code = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH)

    learning_path_level = models.ForeignKey(
        to=CourseLevel,
        on_delete=models.SET_NULL,
        **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG
    )

    language = models.ForeignKey(
        to="learning.Language",
        on_delete=models.SET_NULL,
        **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG
    )

    duration = models.PositiveIntegerField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)

    start_date = models.DateField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    end_date = models.DateField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    cutoff_time_for_mode_changes = models.DateField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)

    #Learning path delivery modes
    self_paced = models.BooleanField(default=False)
    virtual = models.BooleanField(default=False)
    classroom = models.BooleanField(default=False)
    
    self_paced_actual_price = models.PositiveIntegerField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    self_paced_current_price = models.PositiveIntegerField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    online_actual_price = models.PositiveIntegerField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    online_current_price = models.PositiveIntegerField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    classroom_actual_price = models.PositiveIntegerField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    classroom_current_price = models.PositiveIntegerField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    mode_details = models.ManyToManyField(BlendedLearningPathCourseMode)


    learning_points = models.PositiveIntegerField(
        **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG
    )
    learning_type = models.ForeignKey(
        to=BlendedLearningPathLearningType,
        on_delete=models.SET_NULL,
        **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG
    )
    is_this_paid_learning_path = models.BooleanField(default=False)
    skills = models.ManyToManyField(to="learning.Skill", blank=True)

    learning_path_category = models.ManyToManyField(to="learning.Category", blank=True)

    ratings = models.BooleanField(default=False)
    feedback_comments = models.BooleanField(default=False)

    rating = models.FloatField(default=5, validators=[validate_rating])  # aggregated on runtime

    make_course_in_learning_path_sequential = models.BooleanField(default=False)

    requirements = models.TextField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    highlights = models.TextField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)

    accreditation = models.ForeignKey(
        to="learning.Accreditation",
        on_delete=models.SET_NULL,
        **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG
    )
    is_private_course = models.BooleanField(default=False)
    learning_role = models.ForeignKey(
        to='learning.LearningRole', 
        on_delete=models.SET_NULL, 
        **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG
    )
    mml_sku_id = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH, **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    vm_name = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH, **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    virtual_lab = models.BooleanField(default=False)


class BlendedLearningPathCourseModesAndFee(BaseModel):

    DYNAMIC_KEY = "blended-learning-path-modes-fee"

    blended_learning = models.ForeignKey(
        to="learning.BlendedLearningPath", 
        on_delete=models.CASCADE,
        related_name="related_blended_learning_path_courses"
    )
    course = models.ForeignKey(
        to="learning.Course", 
        on_delete=models.CASCADE,
        related_name="related_blended_learning_path_courses"
    )
    self_paced_actual_price = models.PositiveIntegerField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    self_paced_current_price = models.PositiveIntegerField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    online_actual_price = models.PositiveIntegerField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    online_current_price = models.PositiveIntegerField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    classroom_actual_price = models.PositiveIntegerField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    classroom_current_price = models.PositiveIntegerField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    mode_details = models.ManyToManyField(BlendedLearningPathCourseMode)


class BlendedLearningClassroomAndVirtualDetails(BaseModel):

    DYNAMIC_KEY = "blended-learning-course-classroom-virtual-details"

    blended_learning = models.ForeignKey(to="learning.BlendedLearningPath", on_delete=models.CASCADE)
    course = models.ForeignKey(to="learning.Course", on_delete=models.CASCADE)
    classroom_number_of_sessions = models.PositiveIntegerField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    online_number_of_sessions = models.PositiveIntegerField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    classroom_details = JSONField(default=dict)
    online_details = JSONField(default=dict)
    virtual_session_link = models.URLField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    
class BlendedLearningUserEnrollCourseDetails(BaseModel):

    course = models.ForeignKey(
        to="learning.Course", 
        on_delete=models.CASCADE,
    )
    mode = models.ForeignKey(to="learning.BlendedLearningPathCourseMode", on_delete=models.CASCADE)
    # city = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH, null=True, blank=True)
    address_details = models.JSONField()


class BlendedLearningUserEnroll(BaseModel):

    DYNAMIC_KEY = "blended-learning-user-enroll"

    identity = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH, **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    code = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH, **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    duration = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH, **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    image = models.ForeignKey(
        to=BlendedLearningPathImage,
        on_delete=models.SET_NULL,
        **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG
    )
    blended_learning = models.ForeignKey(to="learning.BlendedLearningPath", on_delete=models.CASCADE)
    course_details =  models.ManyToManyField(BlendedLearningUserEnrollCourseDetails, blank=True)
    current_price_inr = models.PositiveIntegerField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)

# class BlendedLearningClassroomDetails(BaseModel):

#     DYNAMIC_KEY = "blended-learning-course-classroom-details"

#     city = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH)
#     address = models.TextField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
#     date = models.DateField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
#     classroom_session_start_time = models.TimeField()
#     classroom_session_end_time = models.TimeField()


# class VirtualDetails(BaseModel):

#     DYNAMIC_KEY = "blended-learning-course-virtual-details"

#     # course = models.ForeignKey(BlendedLearningCourses, on_delete=models.CASCADE)
#     course = models.ForeignKey(to="learning.Course", on_delete=models.CASCADE)
#     session_link = models.URLField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
#     start_time = models.TimeField()
#     end_time = models.TimeField()

class BlendedLearningPathCustomerEnquiry(BaseModel):
    DYNAMIC_KEY = "campaign-leads"

    mode = models.ForeignKey(to="learning.BlendedLearningPathCourseMode", on_delete=models.CASCADE, **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    blp_name = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH)
    name = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH)
    email = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH)
    phone_number = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH)
    is_customer = models.BooleanField(default=False)
    lead_squared_id = models.CharField(
        max_length=COMMON_CHAR_FIELD_MAX_LENGTH,
        **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG
    )
    form_from = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH,**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)

class BlendedLearningPathScheduleDetails(BaseModel):
    """Holds the Blended Learning Path data. Just a collection of Blended Learning Paths schedule Details."""
    
    
    DYNAMIC_KEY = "blended-learning-path-schedule-details"
    
    mentor = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH)
    start_date = models.DateField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    end_date = models.DateField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    start_time = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH, **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    end_time = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH, **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    virtual_url = models.URLField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    address = models.ForeignKey(to=BLPAddress, on_delete=models.SET_NULL,
        **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG,)
    mode = models.ForeignKey(
        to="learning.BlendedLearningPathCourseMode",
        on_delete=models.SET_NULL,
        **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG,
    )
    duration = models.PositiveIntegerField(default=1) 
    is_weekend_batch = models.BooleanField(default=False)
    is_day_batch = models.BooleanField(default=False)
    filling_fast = models.BooleanField(default=False)
    
class BlendedLearningPathPriceDetails(BaseModel):
    """Holds the Blended Learning Path data. Just a collection of Blended Learning Paths Price Details."""

    DYNAMIC_KEY = "blended-learning-path-price-details"

    blended_learning = models.ForeignKey(to="learning.BlendedLearningPath", on_delete=models.CASCADE)
    mode = models.ManyToManyField(
        to="learning.BlendedLearningPathCourseMode",
        blank=True
    )
    # self_paced_fee = models.PositiveIntegerField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    online_actual_fee = models.PositiveIntegerField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    online_discounted_fee = models.IntegerField(default=0)
    online_discount_rate = models.IntegerField(default=0)
    
    classroom_actual_fee = models.PositiveIntegerField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    classroom_discounted_fee = models.IntegerField(default=0)
    classroom_discount_rate = models.IntegerField(default=0)
    schedule_details = models.ManyToManyField(to = BlendedLearningPathScheduleDetails, blank=True)
    
    def save(self, *args, **kwargs):
        """Do the calculation for discounted_fee for classroom and online mode"""
        if self.online_discount_rate and self.online_actual_fee:
            self.online_discounted_fee = self.online_actual_fee-(self.online_actual_fee*(self.online_discount_rate/100))
        elif self.online_discount_rate == 0:
            self.online_discounted_fee=0
            
        if self.classroom_discount_rate and self.classroom_actual_fee:
            self.classroom_discounted_fee = self.classroom_actual_fee-(self.classroom_actual_fee*(self.classroom_discount_rate/100))
        elif self.classroom_discount_rate == 0:
            self.classroom_discounted_fee=0

        super().save(*args, **kwargs)