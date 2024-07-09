from apps.cms.serializers.learning_content import CertificationPathSerializer, CourseSerializer, LearningPathSerializer, UserSerializer
from apps.common.pagination import AppPagination
from apps.common.serializers import AppReadOnlyModelSerializer
from apps.common.views.api.base import AppAPIView, NonAuthenticatedAPIMixin
from apps.learning.models.blended_learning_path import BlendedLearningPath
from apps.learning.models.certification_path import CertificationPath
from apps.learning.models.course import Course, LearningContentFeedback
from apps.learning.models.learning_path import LearningPath
from apps.web_portal.serializers.explore import ExploreSerializer
from rest_framework.generics import ListAPIView
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter
from rest_framework import serializers


class LearningContentAPIView(NonAuthenticatedAPIMixin, ListAPIView, AppAPIView):

    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = "__all__"
    search_fields = ["identity"]

    def get_validated_serialized_data(self):
        serializer = ExploreSerializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        return data

    def get_model_for_serializer(self):
        data = self.get_validated_serialized_data()

        MODEL_CHOICES = {
            "courses": Course,
            "learning_paths": LearningPath,
            "certification_paths": CertificationPath,
            "blended_learning_paths": BlendedLearningPath,
        }

        model = MODEL_CHOICES[data["type"]]
        return model
    

    def get_queryset(self):
        model = self.get_model_for_serializer()
        qs = model.objects.all()
        return qs

    def get_serializer_class(self):
        class LearningContentSerializer(serializers.ModelSerializer):
            def to_representation(self, instance):
                data = super().to_representation(instance=instance)

                image_url = "https://b2cstagingv2.blob.core.windows.net/appuploads/media/"
                if instance.image:
                    image = str(instance.image.file)
                    data["image"] = image_url+image
                return data
            class Meta:
                model = self.get_model_for_serializer()
                fields = ["id", "uuid", "identity", "description", "image", "current_price_inr", "rating", "duration"]
        
        return LearningContentSerializer


    def post(self, request, *args, **kwargs):
        return self.get(request, *args, **kwargs)
    
class AllLearningContentAPIView(NonAuthenticatedAPIMixin, ListAPIView, AppAPIView):

    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = "__all__"
    search_fields = ["identity"]

    def get_validated_serialized_data(self):
        serializer = ExploreSerializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        return data

    def get_model_for_serializer(self):
        data = self.get_validated_serialized_data()

        MODEL_CHOICES = {
            "courses": Course,
            "learning_paths": LearningPath,
            "certification_paths": CertificationPath,
            "blended_learning_paths": BlendedLearningPath,
        }

        model = MODEL_CHOICES[data["type"]]
        return model
    

    def get_queryset(self):
        model = self.get_model_for_serializer()
        qs = model.objects.all()
        return qs

    def get_serializer_class(self):
        class LearningContentSerializer(serializers.ModelSerializer):
            def to_representation(self, instance):
                data = super().to_representation(instance=instance)

                image_url = "https://b2cstagingv2.blob.core.windows.net/appuploads/media/"
                if instance.image:
                    image = str(instance.image.file)
                    data["image"] = image_url+image
                return data
            class Meta:
                model = self.get_model_for_serializer()
                fields = ["id", "uuid", "identity", "description", "image", "current_price_inr", "rating", "duration", "code"]
        
        return LearningContentSerializer


    def post(self, request, *args, **kwargs):
        return self.get(request, *args, **kwargs)
    

class LearningContentFeedbackAPIView(ListAPIView, AppAPIView):
    class _Serializer(AppReadOnlyModelSerializer):
        course = CourseSerializer()
        learning_path = LearningPathSerializer()
        certification_path = CertificationPathSerializer()
        created_by = UserSerializer()
        type = serializers.SerializerMethodField()

        class Meta:
            model = LearningContentFeedback
            fields = ['id', 'uuid', 'identity', 'course', 'learning_path', 'certification_path', 'created_by', 'type']
        
        def get_type(self,obj):
            if obj.course:
                return 'course'
            elif obj.learning_path:
                return 'learning_path'
            elif obj.certification_path:
                return 'certification_path'
            else:
                return None

    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = "__all__"
    search_fields = ["course", "learning_path", "certification_path"]
    pagination_class = AppPagination
    serializer_class = _Serializer

    def get_queryset(self, *args, **kwargs):
        feedback_data = LearningContentFeedback.objects.all()
        return feedback_data
    
class LearningContentFeedbackMeta(AppAPIView):
    def get(self, request, *args, **kwargs):
        data={}
        data['columns']={
            "serial_number": "S.No",
            "full_name": "Learner Name",
            "idp_email": "Email",
            "course": "Recent Course",
            "course_type": "Course Type"
        }
        return self.send_response(data=data)