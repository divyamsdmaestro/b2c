from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from apps.learning.models import BlendedLearningPath,BlendedLearningPathCourseModesAndFee,BlendedLearningClassroomAndVirtualDetails, Course, BlendedLearningPathPriceDetails,BlendedLearningPathScheduleDetails
from django.db import transaction
from apps.common.views.api import AppAPIView
from apps.common.serializers import AppWriteOnlyModelSerializer, AppModelSerializer, get_app_read_only_serializer, AppReadOnlyModelSerializer
from rest_framework.pagination import PageNumberPagination
from apps.cms.views import get_model_list_api_viewset
from rest_framework.generics import ListAPIView
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter
from rest_framework import serializers
from apps.common.pagination import AppPagination
from apps.my_learnings.models import UserBlendedLearningPathTracker
from apps.web_portal.serializers import BlendedLearningPathScheduleDetailsSerializer

class CreateBlendedLearningAPIView(AppAPIView):
    """
    API to Create Blended Learning from CMS.
    """

    class _Serializer(AppWriteOnlyModelSerializer):

        class Meta(AppWriteOnlyModelSerializer.Meta):
            fields = [
                "identity",
                "description",
                "image",
                "skills",
                "learning_path_category",
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
                "self_paced_current_price",
                "self_paced_actual_price",
                "online_actual_price",
                "online_current_price",
                "classroom_current_price",
                "classroom_actual_price",
                "mode_details",
                "learning_points",
                "is_this_paid_learning_path",
                "ratings",
                "feedback_comments",
                "make_course_in_learning_path_sequential",
                "accreditation",
                "requirements",
                "highlights",
                "mml_sku_id",
                "vm_name",
                "virtual_lab"
            ]
            model = BlendedLearningPath

    serializer_class = _Serializer    
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_valid_serializer()
        with transaction.atomic():
            instance = serializer.save()

            class _BlendedLearningClassroomAndVirtualDetailsSerializer(AppModelSerializer):
                class Meta(AppWriteOnlyModelSerializer.Meta):
                    model = BlendedLearningClassroomAndVirtualDetails
                    fields = [
                        # "blended_learning",
                        "course",
                        "classroom_number_of_sessions",
                        "online_number_of_sessions",
                        "classroom_details",
                        "online_details",
                        "virtual_session_link",
                    ]
            serializer_class = _BlendedLearningClassroomAndVirtualDetailsSerializer

            address_session_details = request.data.get("address_session_details", [])
            for address_detail in address_session_details:
                blended_course_classroom_virtual_serializer = _BlendedLearningClassroomAndVirtualDetailsSerializer(data=address_detail)
                blended_course_classroom_virtual_serializer.is_valid(raise_exception=True)
                blended_course_classroom_virtual_serializer.validated_data["blended_learning"] = instance
                blended_course_classroom_virtual_serializer.save()

            return self.send_response()



class UpdateBlendedLearningAPIView(AppAPIView):
    """This class updates the Blended Learning Details from CMS"""

    class _Serializer(AppWriteOnlyModelSerializer):

        class Meta(AppWriteOnlyModelSerializer.Meta):
            fields = [
                "identity",
                "description",
                "image",
                "skills",
                "learning_path_category",
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
                "self_paced_current_price",
                "self_paced_actual_price",
                "online_actual_price",
                "online_current_price",
                "classroom_current_price",
                "classroom_actual_price",
                "mode_details",
                "learning_points",
                "is_this_paid_learning_path",
                "ratings",
                "feedback_comments",
                "make_course_in_learning_path_sequential",
                "accreditation",
                "requirements",
                "highlights",
                "mml_sku_id",
                "vm_name",
                "virtual_lab"
            ]
            model = BlendedLearningPath
        def update(self, instance, validated_data):
            instance = super().update(validated_data=validated_data, instance=instance)
            return instance

    serializer_class = _Serializer    
    def post(self, request, *args, **kwargs):
        blended_learning = BlendedLearningPath.objects.get(id=kwargs['id'])
        serializer = self.get_valid_serializer(instance=blended_learning)
        serializer.save()

        class _BlendedLearningClassroomAndVirtualDetailsSerializer(AppModelSerializer):
            class Meta(AppWriteOnlyModelSerializer.Meta):
                model = BlendedLearningClassroomAndVirtualDetails
                fields = [
                        "course",
                        "classroom_number_of_sessions",
                        "online_number_of_sessions",
                        "classroom_details",
                        "online_details",
                        "virtual_session_link",
                    ]
        address_session_details = request.data.get("address_session_details", [])
        BlendedLearningClassroomAndVirtualDetails.objects.filter(blended_learning=blended_learning).delete()
        for address_session_detail in address_session_details:
            course = Course.objects.get(id=address_session_detail['course'])
            instance, create = BlendedLearningClassroomAndVirtualDetails.objects.update_or_create(blended_learning=blended_learning, course=course)
            serializer = _BlendedLearningClassroomAndVirtualDetailsSerializer(instance=instance, data=address_session_detail, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()

        return self.send_response()


# Create a custom pagination class to remove pagination
class NoPagination(PageNumberPagination):
    page_size = None

# Get the base _ListAPIViewSet using your function
BlendedLearningModesListAPIViewSet = get_model_list_api_viewset(
    meta_queryset=BlendedLearningPath.objects.all(),
    meta_all_table_columns={
        "identity": "Blended Learning",
        "self_paced_actual_price": "Self Paced Actual Price",
        "self_paced_current_price": "Self Paced Current Price",
        "online_actual_price": "Online Actual Price",
        "online_current_price": "Online Current Price",
        "classroom_actual_price": "Classroom Actual Price",
        "classroom_current_price": "Classroom Current Price",
        "mode_details": "Mode Details",
    },
    fields_to_filter=["blended_learning"],
)

# Create a custom view set based on the base view set
class BlendedLearningModeAndFeeListAPIViewSet(BlendedLearningModesListAPIViewSet):
    # Disable pagination for this specific API endpoint
    pagination_class = NoPagination

BlendedLearningClassroomListAPIViewSet = get_model_list_api_viewset(
        meta_queryset=BlendedLearningClassroomAndVirtualDetails.objects.all(),
        meta_all_table_columns={
            "blended_learning": "Blended Learning",
            "course": "Course",
            "classroom_number_of_sessions" : "Classroom Training - No.of.Sessions",
            "online_number_of_sessions" : "Online Training - No.of.Sessions",
            "classroom_details" : "Classroom Details",
            "online_details": "Online Details",
            "virtual_session_link": "Virtual Session Link",
        },
        fields_to_filter=["blended_learning"],
)

class BlendedLearningClassroomAndVirtualListAPIViewSet(BlendedLearningClassroomListAPIViewSet):
    # Disable pagination for this specific API endpoint
    pagination_class = NoPagination

class BlendedLearningPathCustomerOnlineListAPIViewset(ListAPIView, AppAPIView):
    class _Serializer(AppReadOnlyModelSerializer):
        entity = serializers.SerializerMethodField()
        created_by = serializers.SerializerMethodField()
        class Meta:
            model = UserBlendedLearningPathTracker
            fields = ['id', 'uuid', 'entity', 'blp_learning_mode','created_by', 'created']
        
        def get_entity(self, obj):
            return obj.entity.identity
        
        def get_created_by(self, obj):
            if obj.created_by is not None:
                data = {
                    "full_name": obj.created_by.full_name,
                    "email": obj.created_by.idp_email,
                    "phone_number": obj.created_by.phone_number
                }
                return data

    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = "__all__"
    search_fields = ["entity__identity", "blp_learning_mode"]
    pagination_class = AppPagination
    serializer_class = _Serializer

    def get_queryset(self, *args, **kwargs):
        data = UserBlendedLearningPathTracker.objects.filter(blp_learning_mode="Online instructor led training").order_by('-created')
        return data
    
class BlendedLearningPathCustomerClassroomListAPIViewset(ListAPIView, AppAPIView):
    class _Serializer(AppReadOnlyModelSerializer):
        entity = serializers.SerializerMethodField()
        created_by = serializers.SerializerMethodField()
        class Meta:
            model = UserBlendedLearningPathTracker
            fields = ['id', 'uuid', 'entity', 'blp_learning_mode','created_by','created']
        
        def get_entity(self, obj):
            return obj.entity.identity
        
        def get_created_by(self, obj):
            if obj.created_by is not None:
                data = {
                    "full_name": obj.created_by.full_name,
                    "email": obj.created_by.idp_email,
                    "phone_number": obj.created_by.phone_number
                }
                return data

    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = "__all__"
    search_fields = ["entity__identity", "blp_learning_mode"]
    pagination_class = AppPagination
    serializer_class = _Serializer

    def get_queryset(self, *args, **kwargs):
        data = UserBlendedLearningPathTracker.objects.filter(blp_learning_mode="Classroom training").order_by('-created')
        return data
    
class BlendedLearningPathCustomerOnlineListTableMetaAPIViewset(AppAPIView):
    def get(self, request, *args, **kwargs):
        data={}
        data['columns']={
            "created_by__full_name": "First Name",
            "created_by__email": "Email",
            "created_by__phone_number": "Phone Number",
            "entity": "BLP Name",
            "blp_learning_mode": "Learning Mode",
            "created": "Created At",
        }
        return self.send_response(data=data)

class BlendedLearningPathCustomerClassroomListTableMetaAPIViewset(AppAPIView):
    def get(self, request, *args, **kwargs):
        data={}
        data['columns']={
            "created_by__full_name": "First Name",
            "created_by__email": "Email",
            "created_by__phone_number": "Phone Number",
            "entity": "BLP Name",
            "blp_learning_mode": "Learning Mode",
            "created": "Created At",
        }
        return self.send_response(data=data)
    