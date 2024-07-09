import datetime
import random

from django.apps import apps
from django.core.management.base import BaseCommand
from django.db import models as django_models
from faker import Faker

from apps.common.models import FileOnlyModel
from apps.jobs import models as job_models
from apps.learning import models as learning_models
from apps.meta import models as meta_models
from apps.web_portal import fakers
from apps.web_portal.models import Testimonial
from apps.forums import models as forum_models
from apps.learning import models as certificate_models
class Command(BaseCommand):
    help = "Initializes the app by running the necessary initial commands."

    # number of fake instances
    FAKE_INSTANCES_COUNT = 30

    # fake image paths
    FAKE_IMAGE_PATHS = [
        "files/vendor/image/wallpaper5.JPG",
        "files/vendor/image/download.png",
    ]

    # holds images
    IMAGE_MODELS_TO_FAKE = [
        _ for _ in apps.get_models() if issubclass(_, FileOnlyModel)
    ]

    # other / regular
    OTHER_MODELS_TO_FAKE = [
        learning_models.Author,
        learning_models.Vendor,
        learning_models.Tutor,
        learning_models.Proficiency,
        learning_models.CategoryPopularity,
        learning_models.CategoryImage,
        # learning_models.Category,
        learning_models.SkillImage,
        learning_models.SkillPopularity,
        learning_models.Skill,
        learning_models.CourseLevel,
        learning_models.Language,
        learning_models.Accreditation,
        learning_models.Tag,
        learning_models.Course,
        learning_models.CourseModule,
        learning_models.CourseSubModule,
        learning_models.LearningPathLevel,
        learning_models.LearningPath,
        learning_models.LearningPathCourse,
        learning_models.CertificationPathImage,
        learning_models.CertificationPathLevel,
        learning_models.CertificationPath,
        learning_models.CertificationPathLearningPath,
        Testimonial,
        meta_models.OnboardingLevel,
        meta_models.OnboardingHighestEducation,
        meta_models.OnboardingAreaOfInterest,
        meta_models.FrequentlyAskedQuestion,
        meta_models.Country,
        meta_models.State,
        meta_models.City,
        meta_models.FontStyle,
        meta_models.SocialPlatform,
        meta_models.UserMartialStatus,
        meta_models.UserIdentificationType,
        job_models.Role,
        job_models.HiringCompanyImage,
        job_models.HiringCompany,
        job_models.FunctionalArea,
        job_models.Industry,
        job_models.Location,
        job_models.EducationQualification,
        job_models.Job,
        job_models.JobPerk,
    ]

    def handle(self, *args, **kwargs):  # noqa
        """Used to load fake data into our application for testing and development."""

        faker = Faker()

        genders = ["Male", "Female", "Others"]

        for _ in genders:
            gender = meta_models.UserGender(identity=_)
            gender.save()
        
        # Forum type (eg: Public, Private, Moderate)
        zone_types = ["Public", "Private", "Moderate"]

        for _ in zone_types:
            zone_type = forum_models.ZoneType(identity=_)
            zone_type.save()

        # Create forum post type (eg: Question/poll based post type)
        post_types = ["Question Based Post", "Poll Based Post"]

        for _ in post_types:
            post_type = forum_models.PostType(identity=_)
            post_type.save()
        
        # Certificate Learning type (eg: Course, Learning Path, Advanced Learning Path)
        certificate_learning_types = ["Course", "Learning Path", "Advanced Learning Path"]

        for _ in certificate_learning_types:
            certificate_learning_types = certificate_models.CertificateLearningType(identity=_)
            certificate_learning_types.save()

        for model in self.IMAGE_MODELS_TO_FAKE:
            print(f"Faking: {model}")  # noqa

            for _ in range(self.FAKE_INSTANCES_COUNT):
                path = random.choice(self.FAKE_IMAGE_PATHS)
                instance = model()
                instance.file.name = path
                instance.save()

        for model in self.OTHER_MODELS_TO_FAKE:
            print(f"Faking: {model}")  # noqa

            for _ in range(self.FAKE_INSTANCES_COUNT):
                instance_regular_data = {}
                instance_m2m_data = {}

                for field in model.get_all_model_fields():
                    field_class = field.__class__
                    field_name = field.name

                    if field_name in [
                        "id",
                        "uuid",
                        "created",
                        "modified",
                        "created_by",
                    ] or field_class in [
                        django_models.fields.reverse_related.ManyToOneRel,
                        django_models.fields.reverse_related.ManyToManyRel,
                    ]:
                        pass

                    elif field_class in [
                        django_models.CharField,
                        django_models.TextField,
                    ]:
                        instance_regular_data[field_name] = faker.name()

                    elif field_class == django_models.ForeignKey:
                        instance_regular_data[field_name] = random.choice(
                            field.related_model.objects.all()
                        )

                    elif field_class == django_models.BooleanField:
                        instance_regular_data[field_name] = random.choice([True, False])

                    elif field_class in [
                        django_models.IntegerField,
                        django_models.PositiveIntegerField,
                        django_models.PositiveBigIntegerField,
                        django_models.PositiveSmallIntegerField,
                        django_models.FloatField,
                        django_models.DecimalField,
                    ]:
                        instance_regular_data[field_name] = random.randint(5, 2000)

                    elif field_class == django_models.fields.related.ManyToManyField:
                        instance_m2m_data[field_name] = random.choices(
                            field.related_model.objects.all(), k=random.randint(2, 4)
                        )

                    elif field_class == django_models.URLField:
                        instance_regular_data[field_name] = random.choice(
                            [fakers.VIDEO_URL, None]
                        )

                    elif field_class == django_models.DateField:
                        instance_regular_data[field_name] = datetime.datetime.now()

                    else:
                        # Something is not handled
                        print(  # noqa
                            f"Field Class {field_class} For {field_name} Not Handled!"
                        )

                # regular data
                instance = model(**instance_regular_data)
                instance.save()

                # m2m data
                for m2m_key, m2m_data in instance_m2m_data.items():
                    getattr(instance, m2m_key).set(m2m_data)

        # performance related stuff
        for _ in learning_models.Course.objects.all():
            _.handle_performance_chain()
