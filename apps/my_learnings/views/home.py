from apps.common.serializers import simple_serialize_instance, simple_serialize_queryset
from apps.common.views.api import AppAPIView
from apps.my_learnings.models import (
    UserCourseTracker, 
    UserLearningPathTracker, 
    UserCertificatePathTracker, 
    UserSubscriptionPlanTracker, 
    StudentEnrolledCourseTracker, 
    UserSkillTracker, 
    StudentEnrolledLearningPathTracker, 
    StudentEnrolledCertificatePathTracker,
    UserBlendedLearningPathTracker,
    UserJobEligibleSkillTracker,
)
from apps.common.views.api.generic import AbstractLookUpFieldMixin
from rest_framework.generics import ListAPIView

from apps.my_learnings.models.trackers import UserMMLCourseTracker
from ...common.serializers import get_app_read_only_serializer, get_read_serializer
from rest_framework.permissions import IsAuthenticated
from apps.learning.models import Course, MyLearningsNotes, CourseModule, CourseSubModule, LearningPath, CertificationPath, Skill, CourseLevel
from apps.learning.models import Certificate
from django.db.models import Q
from ...common.serializers import (
    AppWriteOnlyModelSerializer,
    AppReadOnlyModelSerializer,
    get_app_read_only_serializer as read_serializer
)
from apps.purchase.models import CourseModuleVideoBookMarklist, LearningPathModuleVideoBookMarklist, CertificationPathModuleVideoBookMarklist
from django.db import models
from apps.web_portal.serializers import serialize_for_bookmark_list, LearningRoleListSerializer, SkillListSerializer
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import serializers
from apps.common.pagination import AppPagination
from apps.learning.models import LearningRole, LearningContentFeedback, CourseRating
from rest_framework.filters import SearchFilter
from django.utils.datetime_safe import datetime
from rest_framework.response import Response
from rest_framework import serializers
import base64,requests
from apps.common.helpers import get_file_field_url
from apps.learning.models import Author
from apps.web_portal.serializers.explore import LinkageFieldsSerializer
from rest_framework.generics import RetrieveAPIView

class MyCourseLearningsHomeAPIView(AppAPIView):
    """Returns the data for my learnings home/list page."""

    def get(self, request, *args, **kwargs):
        """Handle on get."""

        user = self.get_user()
        trackers = [
            *UserCourseTracker.objects.filter(created_by=user)
            .select_related("entity", "entity__author")
            .prefetch_related("entity__skills")
        ]

        return self.send_response(data=[self.serialize_trackers(_) for _ in trackers])

    @staticmethod
    def serialize_trackers(tracker):
        """Serialize data for the front-end."""

        entity = tracker.entity

        data = simple_serialize_instance(
            instance=tracker,
            keys=[
                "uuid",
                "created",
                "valid_till",
                "progress",
                "last_accessed_on",
            ],
            parent_data={
                "entity": simple_serialize_instance(
                    instance=entity,
                    keys=[
                        "identity",
                        "image.file.url",
                        "uuid",
                        "__class__.__name__",
                    ],
                    parent_data={
                        "skills": simple_serialize_queryset(
                            queryset=entity.skills.all(), fields=["identity", "uuid"]
                        ),
                        "tutor": simple_serialize_instance(
                            instance=entity.author,
                            keys=["id", "identity", "designation"],
                        ),
                    },
                    display={
                        "image.file.url": "image",
                        "__class__.__name__": "type",
                    },
                ),
            },
        )

        return data
    
class MyMMLCourseLearningsHomeAPIView(AppAPIView):
    """Returns the data for my learnings home/list page."""

    def get(self, request, *args, **kwargs):
        """Handle on get."""

        user = self.get_user()
        trackers = [
            *UserMMLCourseTracker.objects.filter(created_by=user)
            .select_related("entity", "entity__author")
            .prefetch_related("entity__skills")
        ]

        return self.send_response(data=[self.serialize_trackers(_) for _ in trackers])

    @staticmethod
    def serialize_trackers(tracker):
        """Serialize data for the front-end."""

        entity = tracker.entity

        data = simple_serialize_instance(
            instance=tracker,
            keys=[
                "uuid",
                "created",
                "valid_till",
                "progress",
                "last_accessed_on",
            ],
            parent_data={
                "entity": simple_serialize_instance(
                    instance=entity,
                    keys=[
                        "identity",
                        "image.file.url",
                        "uuid",
                        "__class__.__name__",
                    ],
                    parent_data={
                        "skills": simple_serialize_queryset(
                            queryset=entity.skills.all(), fields=["identity", "uuid"]
                        ),
                        "tutor": simple_serialize_instance(
                            instance=entity.author,
                            keys=["id", "identity", "designation"],
                        ),
                    },
                    display={
                        "image.file.url": "image",
                        "__class__.__name__": "type",
                    },
                ),
            },
        )

        return data

class MyLearningsCertificateDownloadAPIView(AbstractLookUpFieldMixin, AppAPIView):
    """This view used to download the profile details of a user"""
    def get(self, request, *args, **kwargs):
        if self.kwargs['uuid']:
            course = Course.objects.filter(uuid=self.kwargs['uuid']).exists()
            if course:
                course_details = Course.objects.filter(uuid=self.kwargs['uuid']).get()
                certificate_details = Certificate.objects.get_or_none(learning_type__identity="Course")

            learning_path = LearningPath.objects.filter(uuid=self.kwargs['uuid']).exists()
            if learning_path:
                course_details = LearningPath.objects.filter(uuid=self.kwargs['uuid']).get()
                certificate_details = Certificate.objects.get_or_none(learning_type__identity="Learning Path")

            certification_path = CertificationPath.objects.filter(uuid=self.kwargs['uuid']).exists()
            if certification_path:
                course_details = CertificationPath.objects.filter(uuid=self.kwargs['uuid']).get()
                certificate_details = Certificate.objects.get_or_none(learning_type__identity="Certification Path")
        if certificate_details:
            if certificate_details.sponsor_logo:
                sponsor_logo =  get_file_field_url(certificate_details, "sponsor_logo")
                try:
                    response = requests.get(sponsor_logo)
                    response.raise_for_status()
                except requests.RequestException as e:
                    return e
                image_data = response.content
                sponsor_logo_base64 = base64.b64encode(image_data).decode('utf-8')
            else:
                sponsor_logo_base64 = None
            # for company image
            if certificate_details.image:
                company_image =  get_file_field_url(certificate_details, "image")
                try:
                    response = requests.get(company_image)
                    response.raise_for_status()
                except requests.RequestException as e:
                    return e
                image_data = response.content
                company_image_base64 = base64.b64encode(image_data).decode('utf-8')
            else:
                company_image_base64 = None
            context = {
                'identity': course_details.identity,
                'sponsor_logo': sponsor_logo_base64,
                'keep_techademy_logo': certificate_details.keep_techademy_logo,
                'orientation': certificate_details.orientation,
                'headline_text' : certificate_details.headline_text,
                'body_text': certificate_details.body_text,
                'image': company_image_base64,
                'username' : self.get_user().full_name,
                'created_date': datetime.now()
                }
            return self.send_response(context)
        else:
            return self.send_error_response({'message': 'Certificate Not Provided'})
        
class CertificateIdentitySerializer(serializers.Serializer):
    uuid = serializers.CharField()
    identity = serializers.CharField()
    level =  serializers.SerializerMethodField()

    def get_level(self, obj):
        level_identity = CourseLevel.objects.get(id=obj.level_id)
        return level_identity.identity

class CertificateSerializer(serializers.Serializer):
    entity = CertificateIdentitySerializer()

class MyLearningsCertificateListAPIView(AppAPIView):

    """List down my certificate to the user. This is a read-only view."""
    def get(self, request, *args, **kwargs):
        user = self.get_user()  # Assuming this method works fine

        if user.user_role.identity == "Student":
            course_tracker = StudentEnrolledCourseTracker
            learning_path_tracker = StudentEnrolledLearningPathTracker
            certificate_path_tracker = StudentEnrolledCertificatePathTracker

        if user.user_role.identity == "Learner":
            course_tracker = StudentEnrolledCourseTracker
            learning_path_tracker = StudentEnrolledLearningPathTracker
            certificate_path_tracker = StudentEnrolledCertificatePathTracker

        course_trackers = course_tracker.objects.filter(created_by=user, progress=100)
        learning_path_trackers = learning_path_tracker.objects.filter(created_by=user, progress=100)
        certificate_path_trackers = certificate_path_tracker.objects.filter(created_by=user, progress=100)

        # Combine querysets
        qs = list(course_trackers) + list(learning_path_trackers) + list(certificate_path_trackers)

        serializer = CertificateSerializer(qs, many=True)  # Use your serializer class
        return Response(serializer.data)

class MyLearningsNotesAPIView(AppAPIView):
    class _Serializer(AppWriteOnlyModelSerializer):
        """Handle input data."""
        time_stamp = serializers.CharField(required=False) #time_stamp is not required for updating the notes
        class Meta(AppWriteOnlyModelSerializer.Meta):
            fields = ["course_sub_module","description","time_stamp"]
            model = MyLearningsNotes
    serializer_class = _Serializer

    def get_serializer(self, *args, **kwargs):
        kwargs['context'] = self.get_serializer_context()
        return self.serializer_class(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return self.send_response(serializer.data)
        return self.send_error_response(serializer.errors)
    
    def put(self, request, pk):
        # Update operation
        try:
            instance = MyLearningsNotes.objects.get(pk=pk)
        except MyLearningsNotes.DoesNotExist:
            return self.send_response()

        serializer = self.get_serializer(instance, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return self.send_response(serializer.data)
        return self.send_error_response(serializer.errors)

    def delete(self, request, pk):
        # Delete operation
        try:
            instance = MyLearningsNotes.objects.get(pk=pk)
        except MyLearningsNotes.DoesNotExist:
            return self.send_error_response()

        instance.delete()
        return self.send_response()

class MyLearningsNotesListAPIView(AbstractLookUpFieldMixin, ListAPIView, AppAPIView):

    def get(self, request, *args, **kwargs):
        # learing_course = UserCourseTracker.objects.filter(uuid=self.kwargs['uuid']).get()
        notes_list = []
        notes_details = MyLearningsNotes.objects.filter(course_sub_module__uuid=self.kwargs['uuid'], created_by=self.get_user())
        if notes_details:
            for notes_details in notes_details:
                notes_list.append({
                    'id': notes_details.id,
                    'uuid': notes_details.uuid,
                    'identity': notes_details.description,
                    'time_stamp': notes_details.time_stamp,
                })
        return self.send_response(notes_list)
        
class MyLearningsOverallNotesListAPIView(ListAPIView, AppAPIView):
    """Sends out data for the notes Listing Page."""

    class _Serializer(AppReadOnlyModelSerializer):
        """Handle input data."""

        class CourseSubModuleSerializer(AppReadOnlyModelSerializer):
            """Handle input data."""
            my_learnings_notes = serializers.SerializerMethodField()
            class Meta(AppReadOnlyModelSerializer.Meta):
                fields = ["id","uuid","identity","video_url","my_learnings_notes"]
                model = CourseSubModule

            def get_my_learnings_notes(self, obj):
                notes = MyLearningsNotes.objects.filter(course_sub_module=obj)
                serializer = read_serializer(MyLearningsNotes, meta_fields="__all__")(notes, many=True)
                return serializer.data


        course_sub_module = serializers.SerializerMethodField() 
        class Meta(AppReadOnlyModelSerializer.Meta):
            fields = ["id","uuid","identity","course_sub_module"]
            model = CourseModule

        def get_course_sub_module(self, obj):
            sub_modules = CourseSubModule.objects.filter(module=obj)
            data = self.get_request().data
            sub_module_id = data.get('sub_module_id')
            if sub_module_id:
                sub_modules = sub_modules.filter(id=sub_module_id)
            serializer = self.CourseSubModuleSerializer(
                sub_modules, many=True
            )
            return serializer.data

    filter_backends = [DjangoFilterBackend]
    filterset_fields = "__all__"
    pagination_class = AppPagination
    serializer_class = _Serializer

    def get_queryset(self):
        course = Course.objects.get(uuid=self.kwargs["uuid"])
        data = self.get_request().data
        module_id = data.get("module_id")
        sub_module_id = data.get("sub_module_id")
        queryset = CourseModule.objects.filter(course=course)

        if module_id:
            queryset = queryset.filter(id=module_id)
        elif sub_module_id:
            sub_module = CourseSubModule.objects.get(id=sub_module_id)
            queryset = queryset.filter(id=sub_module.module.id)

        return queryset

    def post(self, request, *args, **kwargs):
        return self.get(request, *args, **kwargs)

class MyLearningsNotesFilterMetaAPIView(AppAPIView):
    """Provides Meta Data for filtering"""
    class CourseModuleSerializer(AppReadOnlyModelSerializer):
        """Handle input data."""
    def get(self, request, *args, **kwargs):
        course = Course.objects.get(uuid=self.kwargs["uuid"])
        course_sub_modules = CourseSubModule.objects.filter(module__course=course)
        data = {
            "course_modules": get_read_serializer(
                CourseModule, meta_fields=["id","uuid","identity"]
            )(CourseModule.objects.filter(course=course), many=True).data,
            "course_sub_modules": get_read_serializer(
                CourseSubModule, meta_fields=["id","uuid","identity","module"]
            )(course_sub_modules, many=True).data,
        }
        return self.send_response(data=data)

class MyLearningPathHomeAPIView(AppAPIView):
    """Returns the data for my learnings path home/list page."""

    def get(self, request, *args, **kwargs):
        """Handle on get."""

        user = self.get_user()
        trackers = [
            *UserLearningPathTracker.objects.filter(created_by=user)
            # .select_related("entity", "entity__author")
            # .prefetch_related("entity__skills")
        ]

        return self.send_response(data=[self.serialize_trackers(_) for _ in trackers])

    @staticmethod
    def serialize_trackers(tracker):
        """Serialize data for the front-end."""

        entity = tracker.entity

        data = simple_serialize_instance(
            instance=tracker,
            keys=[
                "uuid",
                "created",
                "valid_till",
                "progress",
                "last_accessed_on",
            ],
            parent_data={
                "entity": simple_serialize_instance(
                    instance=entity,
                    keys=[
                        "identity",
                        "image.file.url",
                        "uuid",
                        "__class__.__name__",
                    ],
                    parent_data={
                        # "skills": simple_serialize_queryset(
                        #     queryset=entity.skills.all(), fields=["identity", "uuid"]
                        # ),
                        # "tutor": simple_serialize_instance(
                        #     instance=entity.author,
                        #     keys=["id", "identity", "designation"],
                        # ),
                    },
                    display={
                        "image.file.url": "image",
                        "__class__.__name__": "type",
                    },
                ),
            },
        )

        return data
    
class MyCertificatePathHomeAPIView(AppAPIView):
    """Returns the data for my certificate path home/list page."""

    def get(self, request, *args, **kwargs):
        """Handle on get."""

        user = self.get_user()
        trackers = [
            *UserCertificatePathTracker.objects.filter(created_by=user)
            # .select_related("entity", "entity__author")
            # .prefetch_related("entity__skills")
        ]

        return self.send_response(data=[self.serialize_trackers(_) for _ in trackers])

    @staticmethod
    def serialize_trackers(tracker):
        """Serialize data for the front-end."""

        entity = tracker.entity

        data = simple_serialize_instance(
            instance=tracker,
            keys=[
                "uuid",
                "created",
                "valid_till",
                "progress",
                "last_accessed_on",
            ],
            parent_data={
                "entity": simple_serialize_instance(
                    instance=entity,
                    keys=[
                        "identity",
                        "image.file.url",
                        "uuid",
                        "__class__.__name__",
                    ],
                    parent_data={
                        # "skills": simple_serialize_queryset(
                        #     queryset=entity.skills.all(), fields=["identity", "uuid"]
                        # ),
                        # "tutor": simple_serialize_instance(
                        #     instance=entity.author,
                        #     keys=["id", "identity", "designation"],
                        # ),
                    },
                    display={
                        "image.file.url": "image",
                        "__class__.__name__": "type",
                    },
                ),
            },
        )

        return data
    
class MySubscriptionPlanHomeAPIView(AppAPIView):
    """Returns the data for my role based learning path home/list page."""

    def get(self, request, *args, **kwargs):
        """Handle on get."""

        user = self.get_user()
        trackers = [
            *UserSubscriptionPlanTracker.objects.filter(created_by=user)
            # .select_related("entity", "entity__author")
            # .prefetch_related("entity__skills") 
        ]

        return self.send_response(data=[self.serialize_trackers(_) for _ in trackers])

    @staticmethod
    def serialize_trackers(tracker):
        """Serialize data for the front-end."""

        entity = tracker.entity

        data = simple_serialize_instance(
            instance=tracker,
            keys=[
                "uuid",
                "created",
                "valid_till",
                "progress",
                "last_accessed_on",
            ],
            parent_data={
                "entity": simple_serialize_instance(
                    instance=entity,
                    keys=[
                        "identity",
                        "image.file.url",
                        "uuid",
                        "__class__.__name__",
                    ],
                    parent_data={
                        # "skills": simple_serialize_queryset(
                        #     queryset=entity.skills.all(), fields=["identity", "uuid"]
                        # ),
                        # "tutor": simple_serialize_instance(
                        #     instance=entity.author,
                        #     keys=["id", "identity", "designation"],
                        # ),
                    },
                    display={
                        "image.file.url": "image",
                        "__class__.__name__": "type",
                    },
                ),
            },
        )

        return data
    
class MyJobEligibleSkillHomeAPIView(AppAPIView):
    """Returns the data for my Job Eligible Skill home/list page."""

    def get(self, request, *args, **kwargs):
        """Handle on get."""

        user = self.get_user()
        trackers = [
            *UserJobEligibleSkillTracker.objects.filter(created_by=user)
            # .select_related("entity", "entity__author")
            # .prefetch_related("entity__skills") 
        ]

        return self.send_response(data=[self.serialize_trackers(_) for _ in trackers])

    @staticmethod
    def serialize_trackers(tracker):
        """Serialize data for the front-end."""

        entity = tracker.entity

        data = simple_serialize_instance(
            instance=tracker,
            keys=[
                "uuid",
                "created",
                "valid_till",
                "progress",
                "last_accessed_on",
            ],
            parent_data={
                "entity": simple_serialize_instance(
                    instance=entity,
                    keys=[
                        "identity",
                        "image.file.url",
                        "uuid",
                        "__class__.__name__",
                    ],
                    parent_data={
                        # "skills": simple_serialize_queryset(
                        #     queryset=entity.skills.all(), fields=["identity", "uuid"]
                        # ),
                        # "tutor": simple_serialize_instance(
                        #     instance=entity.author,
                        #     keys=["id", "identity", "designation"],
                        # ),
                    },
                    display={
                        "image.file.url": "image",
                        "__class__.__name__": "type",
                    },
                ),
            },
        )

        return data

class MyLearningRoleHomeAPIView(ListAPIView, AppAPIView):
    serializer_class = LearningRoleListSerializer
    filter_backends = [SearchFilter]
    search_fields = ['identity']
    pagination_class = AppPagination

    def get_queryset(self):
        user = self.get_user()
        list =[]

        data = [
            *UserCourseTracker.objects.filter(created_by=user),
            *UserLearningPathTracker.objects.filter(created_by=user),
            *UserCertificatePathTracker.objects.filter(created_by=user)
        ]
        for data in data:
            if data.entity.learning_role:
                list.append(data.entity.learning_role.id)
        return LearningRole.objects.filter(id__in=list).distinct()

class StudentMyCourseLearningsHomeAPIView(AppAPIView):
    """Returns the data for my learnings home/list page."""

    def get(self, request, *args, **kwargs):
        """Handle on get."""

        user = self.get_user()
        trackers = [
            *StudentEnrolledCourseTracker.objects.filter(created_by=user)
            .select_related("entity", "entity__author")
            .prefetch_related("entity__skills")
        ]

        return self.send_response(data=[self.serialize_trackers(_) for _ in trackers])

    @staticmethod
    def serialize_trackers(tracker):
        """Serialize data for the front-end."""

        entity = tracker.entity

        data = simple_serialize_instance(
            instance=tracker,
            keys=[
                "uuid",
                "created",
                "valid_till",
                "progress",
                "last_accessed_on",
            ],
            parent_data={
                "entity": simple_serialize_instance(
                    instance=entity,
                    keys=[
                        "identity",
                        "image.file.url",
                        "uuid",
                        "__class__.__name__",
                    ],
                    parent_data={
                        "skills": simple_serialize_queryset(
                            queryset=entity.skills.all(), fields=["identity", "uuid"]
                        ),
                        "tutor": simple_serialize_instance(
                            instance=entity.author,
                            keys=["id", "identity", "designation"],
                        ),
                    },
                    display={
                        "image.file.url": "image",
                        "__class__.__name__": "type",
                    },
                ),
            },
        )

        return data
    
class StudentMyLearningPathHomeAPIView(AppAPIView):
    """Returns the data for my learnings path home/list page."""

    def get(self, request, *args, **kwargs):
        """Handle on get."""

        user = self.get_user()
        trackers = [
            *StudentEnrolledLearningPathTracker.objects.filter(created_by=user)
        ]

        return self.send_response(data=[self.serialize_trackers(_) for _ in trackers])

    @staticmethod
    def serialize_trackers(tracker):
        """Serialize data for the front-end."""

        entity = tracker.entity

        data = simple_serialize_instance(
            instance=tracker,
            keys=[
                "uuid",
                "created",
                "valid_till",
                "progress",
                "last_accessed_on",
            ],
            parent_data={
                "entity": simple_serialize_instance(
                    instance=entity,
                    keys=[
                        "identity",
                        "image.file.url",
                        "uuid",
                        "__class__.__name__",
                    ],
                    parent_data={},
                    display={
                        "image.file.url": "image",
                        "__class__.__name__": "type",
                    },
                ),
            },
        )

        return data

class StudentMyCertificatePathHomeAPIView(AppAPIView):
    """Returns the data for my certificate path home/list page."""

    def get(self, request, *args, **kwargs):
        """Handle on get."""

        user = self.get_user()
        trackers = [
            *StudentEnrolledCertificatePathTracker.objects.filter(created_by=user)
        ]

        return self.send_response(data=[self.serialize_trackers(_) for _ in trackers])

    @staticmethod
    def serialize_trackers(tracker):
        """Serialize data for the front-end."""

        entity = tracker.entity

        data = simple_serialize_instance(
            instance=tracker,
            keys=[
                "uuid",
                "created",
                "valid_till",
                "progress",
                "last_accessed_on",
            ],
            parent_data={
                "entity": simple_serialize_instance(
                    instance=entity,
                    keys=[
                        "identity",
                        "image.file.url",
                        "uuid",
                        "__class__.__name__",
                    ],
                    parent_data={},
                    display={
                        "image.file.url": "image",
                        "__class__.__name__": "type",
                    },
                ),
            },
        )

        return data

class MySubModulesVideoBookMarkAPIView(AppAPIView):
    """View to list out entities in the user's bookmarklist trackers."""

    def get(self, request, *args, **kwargs):
        """Handle on get."""

        user = self.get_user()
        identity = request.GET.get('search')
      
        qs = [
            *CourseModuleVideoBookMarklist.objects.filter(created_by=user).annotate(
                is_in_bookmark=models.Exists(
                    CourseModuleVideoBookMarklist.objects.filter(
                        id=models.OuterRef("id"), created_by=user
                    )
                )
            )
            # *LearningPathModuleVideoBookMarklist.objects.filter(created_by=user).annotate(
            #     is_in_bookmark=models.Exists(
            #         LearningPathModuleVideoBookMarklist.objects.filter(
            #             id=models.OuterRef("id"), created_by=user
            #         )
            #     )
            # ),
            # *CertificationPathModuleVideoBookMarklist.objects.filter(created_by=user).annotate(
            #     is_in_bookmark=models.Exists(
            #         CertificationPathModuleVideoBookMarklist.objects.filter(
            #             id=models.OuterRef("id"), created_by=user
            #         )
            #     )
            # ),
        ]
        if identity:
            qs = [
                tracker
                for tracker in qs
                if tracker.entity.identity == identity
            ]
            
        return self.send_response([serialize_for_bookmark_list(_) for _ in qs])
    
class EntityAddToBookMarkAPIView(AppAPIView):
    """
    View used to bookmark the submodules of entities like Course, Learning Path, Certification Path
    into the users bookmarklist. This works in a toggle way(add & then delete).
    """

    def post(self, *args, **kwargs):
        """Handle on post."""

        uuid = kwargs["uuid"]
        user = self.get_user()
        # config = [
        #     [Course, CourseModuleVideoBookMarklist],
        #     [LearningPath, LearningPathModuleVideoBookMarklist],
        #     [CertificationPath, CertificationPathModuleVideoBookMarklist],
        # ]

        # for _ in config:
        #     model = _[0]
        #     bookmark_model = _[1]

        entity = CourseSubModule.objects.get_or_none(uuid=uuid)
        if entity:
            bookmark_instance = CourseModuleVideoBookMarklist.objects.get_or_none(
                entity=entity, created_by=user
            )

            if bookmark_instance:
                bookmark_instance.delete()
            else:
                CourseModuleVideoBookMarklist.objects.create(entity=entity, created_by=user)
            return self.send_response()
        return self.send_error_response()
    
class MySkillHomeAPIView(ListAPIView, AppAPIView):
    def get(self, request, *args, **kwargs):
        """Handle on get."""

        user = self.get_user()
        trackers = [
            *UserSkillTracker.objects.filter(created_by=user)
        ]

        return self.send_response(data=[self.serialize_trackers(_) for _ in trackers])

    @staticmethod
    def serialize_trackers(tracker):
        """Serialize data for the front-end."""

        entity = tracker.entity

        data = simple_serialize_instance(
            instance=tracker,
            keys=[
                "uuid",
                "created",
                "valid_till",
                "progress",
                "last_accessed_on",
            ],
            parent_data={
                "entity": simple_serialize_instance(
                    instance=entity,
                    keys=[
                        "identity",
                        "image.file.url",
                        "uuid",
                        "__class__.__name__",
                    ],
                    display={
                        "image.file.url": "image",
                        "__class__.__name__": "type",
                    },
                ),
            },
        )

        return data

class CourseRatingAPIView(AppAPIView):

    class _Serializer(AppWriteOnlyModelSerializer):
        class Meta(AppWriteOnlyModelSerializer.Meta):
            fields = ["rating"]
            model = CourseRating
    serializer_class = _Serializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_valid_serializer()
        serializer.is_valid()
        user = self.get_user()
        course = Course.objects.get(uuid=kwargs["uuid"])
        rating = CourseRating.objects.get_or_none(created_by=user,course=course)
        if user and rating is None:
            serializer.save(created_by=user,course=course)
            return self.send_response(serializer.data)
        return self.send_error_response(serializer.errors)
    
class LearningContentFeedbackAPIView(AppAPIView):

    class _Serializer(AppWriteOnlyModelSerializer):
        class Meta(AppWriteOnlyModelSerializer.Meta):
            fields = ["identity"]
            model = LearningContentFeedback
    serializer_class = _Serializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_valid_serializer()
        serializer.is_valid()
        user = self.get_user()
        course = Course.objects.get_or_none(uuid=kwargs["uuid"])
        learning_path = LearningPath.objects.get_or_none(uuid=kwargs["uuid"])
        certification_path = CertificationPath.objects.get_or_none(uuid=kwargs["uuid"])
        if user:
            if course:
                serializer.save(created_by=user, course=course)
            elif learning_path:
                serializer.save(created_by=user, learning_path=learning_path)
            elif certification_path:
                serializer.save(created_by=user, certification_path=certification_path)
            return self.send_response(serializer.data)
        return self.send_error_response(serializer.errors)

class CourseCompletedPageAPIView(AbstractLookUpFieldMixin, RetrieveAPIView, AppAPIView):
    """
    This view provides endpoint to access Course in detail along with
    expanded related views.
    """
    class CourseSerializer(LinkageFieldsSerializer):
        """This serializer contains configuration for Course."""
        class CourseModuleSerializer(AppReadOnlyModelSerializer):
            class CourseSubModuleSerializer(AppReadOnlyModelSerializer):
                class Meta:
                    fields = ["id","uuid","identity"]
                    model = CourseSubModule
            sub_modules = CourseSubModuleSerializer(source="related_modules", many=True)
            class Meta:
                fields = ["id","uuid","identity","sub_modules"]
                model = CourseModule
        author = get_app_read_only_serializer(Author, meta_fields=["id","uuid","identity"])()
        level = get_app_read_only_serializer(CourseLevel, meta_fields=["id","uuid","identity"])()
        skills = get_app_read_only_serializer(Skill, meta_fields=["id","uuid","identity"])(many=True)

        modules = CourseModuleSerializer(source="related_courses", many=True)
        is_already_rated = serializers.SerializerMethodField()
        is_feedback = serializers.SerializerMethodField()
        course_status = serializers.SerializerMethodField()
        
        class Meta(AppReadOnlyModelSerializer.Meta):
            fields = ["id","uuid","identity","level","duration","start_date","end_date","author","skills","is_already_rated","is_feedback","modules","course_status"]
            model = Course

        def get_is_already_rated(self, obj):
            user = self.get_user()
            rating = CourseRating.objects.get_or_none(course=obj,created_by=user)
            if rating:
                return True
            return False

        def get_is_feedback(self, obj):
            user = self.get_user()
            feedback = LearningContentFeedback.objects.get_or_none(course=obj,created_by=user)
            if feedback:
                return True 
            return False
        
        def get_course_status(self, obj):
            return "Completed"
    serializer_class = CourseSerializer
    queryset = Course.objects.all()


class MyBlendedLearningPathHomeAPIView(AppAPIView):
    """Returns the data for my blended learning path home/list page."""

    def get(self, request, *args, **kwargs):
        """Handle on get."""

        user = self.get_user()
        trackers = [
            *UserBlendedLearningPathTracker.objects.filter(created_by=user,blp_learning_mode="self-paced")
            # .select_related("entity", "entity__author")
            # .prefetch_related("entity__skills")
        ]

        return self.send_response(data=[self.serialize_trackers(_) for _ in trackers])

    @staticmethod
    def serialize_trackers(tracker):
        """Serialize data for the front-end."""

        entity = tracker.entity

        data = simple_serialize_instance(
            instance=tracker,
            keys=[
                "uuid",
                "created",
                "valid_till",
                "progress",
                "last_accessed_on",
            ],
            parent_data={
                "entity": simple_serialize_instance(
                    instance=entity,
                    keys=[
                        "identity",
                        "image.file.url",
                        "uuid",
                        "__class__.__name__",
                    ],
                    parent_data={
                        # "skills": simple_serialize_queryset(
                        #     queryset=entity.skills.all(), fields=["identity", "uuid"]
                        # ),
                        # "tutor": simple_serialize_instance(
                        #     instance=entity.author,
                        #     keys=["id", "identity", "designation"],
                        # ),
                    },
                    display={
                        "image.file.url": "image",
                        "__class__.__name__": "type",
                    },
                ),
            },
        )

        return data