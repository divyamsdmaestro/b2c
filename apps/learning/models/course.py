from django.db import models

from apps.common import model_fields
from apps.common.helpers import pause_thread
from apps.common.models import (
    COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG,
    COMMON_CHAR_FIELD_MAX_LENGTH,
    BaseModel,
    FileOnlyModel,
)
from apps.learning.models.linkages import BaseLinkagesModel
from apps.learning.models.price import AbstractPriceModelFields
from django.contrib.auth.models import AnonymousUser
from apps.purchase.models import CourseModuleVideoBookMarklist
from apps.common.helpers import validate_rating
class CourseImage(FileOnlyModel):
    """Image data for a `Course`."""

    file = model_fields.AppSingleFileField(
        upload_to="files/course/image/",
    )

class CourseResource(FileOnlyModel):
    """Resourse data for a `Course`."""

    file = model_fields.AppSingleFileField(
        upload_to="files/course/resource/",
    )


class CourseLevel(BaseModel):
    DYNAMIC_KEY = "course-level"

    identity = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH, unique=True)
    position = models.PositiveIntegerField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)

RESOURCE_TYPE = (
    ("pdf", "pdf"),
    ("word", "word"),
    ("video", "video"),
    ("image", "image"),
    ("zip", "zip"),
)

class Course(BaseLinkagesModel, AbstractPriceModelFields, BaseModel):
    """Holds the course data."""

    class Meta(BaseModel.Meta):
        default_related_name = "related_courses"

    DYNAMIC_KEY = "course"

    cms_reference = models.CharField(
        max_length=COMMON_CHAR_FIELD_MAX_LENGTH,
        **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG,
    )

    identity = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH)
    code = models.CharField(
        max_length=COMMON_CHAR_FIELD_MAX_LENGTH,
        **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG,
    )
    description = models.TextField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)

    level = models.ForeignKey(
        to=CourseLevel,
        on_delete=models.SET_NULL,
        **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG,
    )

    language = models.ForeignKey(
        to="learning.Language",
        on_delete=models.SET_NULL,
        **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG,
    )

    image = models.ForeignKey(
        to=CourseImage,
        on_delete=models.SET_NULL,
        **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG,
    )

    duration = models.PositiveIntegerField(default=1)  # denoted in minutes

    start_date = models.DateField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    end_date = models.DateField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)

    # Feedbacks
    enable_ratings = models.BooleanField(default=False)
    enable_feedback_comments = models.BooleanField(default=False)

    sequential_course_flow = models.BooleanField(default=False)

    is_certification_enabled = models.BooleanField(default=False)

    is_private_course = models.BooleanField(default=False)

    make_this_course_popular = models.BooleanField(default=False)
    make_this_course_trending = models.BooleanField(default=False)
    make_this_course_best_selling = models.BooleanField(default=False)

    accreditation = models.ForeignKey(
        to="learning.Accreditation",
        on_delete=models.SET_NULL,
        **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG,
    )
    is_free = models.BooleanField(default=False)
    tutor = models.ForeignKey(
        to="learning.Tutor",
        related_name="related_courses_tutor",
        null=True,
        on_delete=models.SET_NULL,
    )
    author = models.ForeignKey(
        to="learning.Author",
        related_name="related_courses_author",
        null=True,
        on_delete=models.SET_NULL,
    )
    vendor = models.ForeignKey(
        to="learning.Vendor",
        related_name="related_courses_vendor",
        null=True,
        on_delete=models.SET_NULL,
    )

    requirements = models.TextField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    highlights = models.TextField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)

    rating = models.FloatField(default=5, validators=[validate_rating])  # aggregated on runtime
    validity = models.IntegerField(
        **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG
    )
    resource_title = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH, **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    resource_type = models.CharField(
        choices=RESOURCE_TYPE,
        max_length=COMMON_CHAR_FIELD_MAX_LENGTH,
        **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG
    )
    resource = models.ForeignKey(
        to=CourseResource,
        on_delete=models.SET_NULL,
        **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG,
    )
    complete_in_a_day = models.BooleanField(default=False)
    editors_pick = models.BooleanField(default=False)
    mml_sku_id = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH, **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    vm_name = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH, **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    virtual_lab = models.BooleanField(default=False)
    
    def handle_performance_chain(self):
        """Uses chain of responsibility to update performance related fields."""

        for _ in self.related_learning_path_courses.all():
            _.learning_path.handle_performance_chain()


class CourseModule(BaseModel):
    """Holds the `Section` data under a `Course`."""

    DYNAMIC_KEY = "course-module"

    identity = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH)
    description = models.TextField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)

    position = models.PositiveIntegerField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    course = models.ForeignKey(
        to=Course, related_name="related_courses", on_delete=models.CASCADE
    )

class ModuleType(BaseModel):

    DYNAMIC_KEY = "course-module-type"

    identity = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH, unique=True)

class ModuleTypeDocument(FileOnlyModel):
    """Document data for a `Module Type` document."""

    file = model_fields.AppSingleFileField(
        upload_to="files/course/moduletype_document/",
    )

class CourseSubModule(BaseModel):
    """Holds the `Module` data under a `CourseSection`."""

    DYNAMIC_KEY = "course-sub-module"

    # TODO: Complete other fields after getting confirmation from @Vashanth

    identity = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH)
    description = models.TextField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)

    video_url = models.TextField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG, max_length=8000)

    duration = models.PositiveIntegerField(default=1)  # denoted in minutes
    position = models.PositiveIntegerField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)

    module = models.ForeignKey(
        to=CourseModule, on_delete=models.CASCADE, related_name="related_modules"
    )

    # azure - config from `get_azure_streaming_config_from_public_url`
    azure_streaming_config = models.JSONField(default=dict)
    # azure - streaming urls
    azure_streaming_video_url = models.URLField(
        **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG
    )
    # azure - thumbnail images
    azure_streaming_thumbnail_url = models.URLField(
        **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG
    )
    # async | TODO
    streaming_generation_process_status = models.CharField(
        max_length=COMMON_CHAR_FIELD_MAX_LENGTH,
        **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG,
    )
    streaming_generation_process_error = models.TextField(
        **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG,
    )
    module_type = models.ForeignKey(
        to=ModuleType, on_delete=models.CASCADE, related_name="related_modules_type", **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG
    )
    document = models.ForeignKey(
        to=ModuleTypeDocument,
        on_delete=models.SET_NULL,
        **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG,
    )
    assessmentID = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH, **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    # def save(self, *args, **kwargs):
    #         # Run your function here before saving the model
           
    #         self.create_azure_streaming_urls()

    #         super().save(*args, **kwargs)

    def create_azure_streaming_urls(self):
        """Used for creating streaming urls from azure."""

        video_public_url = self.video_url
       
        if video_public_url:
            from apps.azure_media_services.helpers.app_adapter import (
                get_azure_streaming_config_from_public_url,
            )

            streaming_config = get_azure_streaming_config_from_public_url(
                video_public_url=video_public_url
            )
            self.azure_streaming_config = streaming_config
            self.azure_streaming_video_url = streaming_config["azure_streaming_url"]
            self.azure_streaming_thumbnail_url = streaming_config["azure_thumbnail_url"]

        pause_thread(seconds=1)  # wait for some time

    def is_in_bookmark(self, user):
        """This function used to get course is already in wishlist or not"""
        if isinstance(user, AnonymousUser) or user == None:
            return False
        else:
            is_in_bookmark = CourseModuleVideoBookMarklist.objects.filter(
                entity_id=self.id, created_by=user
            ).exists()
            return is_in_bookmark
        
    def get_resources(self) -> list[dict]:
        """Returns the resources used in the `CourseSubModule`."""
        def get_url_type(_v: str):
            """Returns the type of url given."""

            if "youtube" in _v:
                return "youtube"

            if "azure" in _v:
                return "azure_streaming"

            if "mux" in _v:
                return "mux_streaming"

            return _v.split(".")[-1]
                    
        resources = []
        for k in ["video_url"]:
            value = getattr(self, k, None)

            # Handled for authentication error in video streaming
            if value is not None:
                if "https://irisstorageprod.blob.core.windows.net" in value:
                    new_split = value.split("?")[0]
                    value = new_split + "?sv=2022-11-02&ss=b&srt=co&sp=rtx&se=2024-07-30T20:58:56Z&st=2024-02-08T12:58:56Z&spr=https&sig=zN%2FksYNf%2FGxKBisRteGaEVvLQMOrQ72oYzLbnvc8JcU%3D"
                elif "https://irisdatacontainer.blob.core.windows.net" in value:
                    new_split = value.split("?")[0]
                    value = new_split + "?sv=2022-11-02&ss=b&srt=co&sp=rtfx&se=2024-07-30T20:49:21Z&st=2024-02-08T12:49:21Z&spr=https&sig=19at7fk6WpIKkK6Db6xtdL3w0xlfFVkpCKd58AWzT3Q%3D"
                
                if value:
                    resources.append(
                        {
                            "url": value,
                            "type": get_url_type(value),
                        }
                    )

        return resources


class MyLearningsNotes(BaseModel):
    DYNAMIC_KEY = "mylearning-notes"

    # TODO: Complete other fields after getting confirmation from @Vashanth

    course_sub_module = models.ForeignKey(
        to=CourseSubModule, on_delete=models.CASCADE, related_name="related_modules"
    )
    description = models.TextField()
    time_stamp = models.CharField(
        max_length=COMMON_CHAR_FIELD_MAX_LENGTH,
        **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG
    )

class LearningContentFeedback(BaseModel):

    DYNAMIC_KEY = "learning-content-feedback"

    identity = models.TextField()
    course = models.ForeignKey(
        'learning.Course', on_delete=models.CASCADE,
        related_name='course_feedbacks', null=True, blank=True
    )
    learning_path = models.ForeignKey(
        'learning.LearningPath', on_delete=models.CASCADE,
        related_name='learning_path_feedbacks', null=True, blank=True
    )
    certification_path = models.ForeignKey(
        'learning.CertificationPath', on_delete=models.CASCADE,
        related_name='certification_path_feedbacks', null=True, blank=True
    )

    def save(self, *args, **kwargs):
        if self.course:
            self.learning_path = None
            self.certification_path = None
        elif self.learning_path:
            self.course = None
            self.certification_path = None
        elif self.certification_path:
            self.course = None
            self.learning_path = None

        super().save(*args, **kwargs)

class CourseRating(BaseModel):

    DYNAMIC_KEY = "course-rating"

    rating = models.FloatField(default=5, validators=[validate_rating])
    course = models.ForeignKey(
        to=Course, on_delete=models.CASCADE
    )