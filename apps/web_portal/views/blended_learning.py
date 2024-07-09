from apps.access.models import GuestUser
from apps.common.views.api import AppAPIView, AppCreateAPIView
from rest_framework.generics import ListAPIView
from ...common.serializers import get_app_read_only_serializer, AppWriteOnlyModelSerializer, AppModelSerializer
from django.shortcuts import get_object_or_404
from ...learning.models import BlendedLearningClassroomAndVirtualDetails, BlendedLearningPath, Course, BlendedLearningPathCourseMode, BlendedLearningUserEnroll, BlendedLearningUserEnrollCourseDetails, BlendedLearningPathCustomerEnquiry
from django.db import transaction
from apps.common.views.api.base import NonAuthenticatedAPIMixin
from apps.common.helpers import capture_blp_enquiry_to_lsq, capture_opportunities_blp_enquiry_auto_pop_up_to_lsq

class GetBlendedLearningPathCoursesMeta(ListAPIView, AppAPIView):
    def get(self, request, *args, **kwargs):
        print("id", kwargs['id'])
        blended_learning = get_object_or_404(BlendedLearningPath, id=kwargs['id'])
        
        classroom_virtual_details = BlendedLearningClassroomAndVirtualDetails.objects.filter(blended_learning=blended_learning)
        data = {
            "blp_classroom_virtual_details": get_app_read_only_serializer(
                BlendedLearningClassroomAndVirtualDetails, 
                meta_fields=[
                            'blended_learning', 
                            'classroom_number_of_sessions',
                            'online_number_of_sessions',
                            'classroom_details',
                            'online_details',
                            'virtual_session_link'
                            ],
                init_fields_config = {
                    "course_name": get_app_read_only_serializer(
                        meta_model=Course, meta_fields=['id', 'identity']
                    )(source="course"),
                }
            )(classroom_virtual_details, many=True).data,
            "blp_course_modes_fee": get_app_read_only_serializer(
                BlendedLearningPath, 
                meta_fields=[
                    "id",
                    "identity",
                    "self_paced_actual_price",
                    "self_paced_current_price",
                    "online_actual_price",
                    "online_current_price",
                    "classroom_actual_price",
                    "classroom_current_price",
                    "mode_details"
                ]
            )(blended_learning).data,
        }
        return self.send_response(data=data)
    


class _CourseDetailsSerializer(AppWriteOnlyModelSerializer):
        class Meta(AppWriteOnlyModelSerializer.Meta):
            fields = [
                "course",
                "mode",
                # "city",
                "address_details"
            ]
            model = BlendedLearningUserEnrollCourseDetails



class PostBlendedLearningUserEnroll(AppAPIView):

    class _Serializer(AppWriteOnlyModelSerializer):
        # course_details = _CourseDetailsSerializer(many=True)
        
        class Meta(AppWriteOnlyModelSerializer.Meta):
            fields = [
                "blended_learning",
                # "course_details",
                "current_price_inr"
            ]
            model = BlendedLearningUserEnroll
    
    serializer_class = _Serializer
    
    def post(self, *args, **kwargs):
        with transaction.atomic():
            course_details = self.request.data.pop("course_details", [])
            serializer = self._Serializer(data=self.request.data, context={'request':self.request})
            serializer.is_valid(raise_exception=True)
            user_enroll=serializer.save()
            blp_identity=user_enroll.blended_learning_id
            if blp_identity is not None:
                get_identity = BlendedLearningPath.objects.get(id=blp_identity)
                user_enroll.identity = get_identity.identity
                user_enroll.code = get_identity.learning_path_code
                user_enroll.duration = get_identity.duration
                user_enroll.image_id = get_identity.image_id
                user_enroll.save()
            created_uuid = user_enroll.uuid

            for course_detail in course_details:
                course_details_serializer = _CourseDetailsSerializer(data=course_detail, context={'request':self.request})
                course_details_serializer.is_valid(raise_exception=True)
                course_detail = course_details_serializer.save()
                user_enroll.course_details.add(course_detail)

            response_data = {
                "created_data": {
                    **serializer.data,
                    "uuid": created_uuid
                }
            }
            return self.send_response(data=response_data)

class PostBlendedLearningUserEnquiry(NonAuthenticatedAPIMixin, AppAPIView):    
    def post(self, request, *args, **kwargs):
        blp_reg = BlendedLearningPathCustomerEnquiry.objects.get_or_none(email=self.request.data.get("email"),blp_name=self.request.data.get("blp_name"),phone_number=self.request.data.get("phone_number"),)
        if blp_reg:
            if blp_reg.created_by == self.request.user and (blp_reg.mode == "Online instructor led training" or blp_reg.mode == "Classroom training"):
                return self.send_response(data={"status": "Already Registered"})
            else:
                return self.send_error_response()
        else:
            registration = BlendedLearningPathCustomerEnquiry(
                blp_name=self.request.data.get("blp_name"),
                name=self.request.data.get("name"),
                email=self.request.data.get("email"),
                phone_number=self.request.data.get("phone_number"),
                mode_id=self.request.data.get("mode"),
                is_customer=self.request.data.get("is_customer"),
            )
            registration.save()
            capture_blp_enquiry_to_lsq(registration)
            return self.send_response()
        
class BlendedLearningPathAutoPopUpUserInformation(NonAuthenticatedAPIMixin, AppAPIView):  
    """API to get user information via auto pop up"""
    def post(self, request, *args, **kwargs):
        # Create a new BlendedLearningPathCustomerEnquiry instance with the extracted data
        registration = BlendedLearningPathCustomerEnquiry(
                form_from = self.request.data.get("form_from"), # Get the source of the form submission (listing/detail)
                blp_name=self.request.data.get("blp_name"),
                name=self.request.data.get("name"),
                email=self.request.data.get("email"),
                phone_number=self.request.data.get("phone_number"),
                is_customer=self.request.data.get("is_customer"), 
            )
        registration.save()
        # Capture the blended learning path user information to lsq
        capture_opportunities_blp_enquiry_auto_pop_up_to_lsq(registration)
        return self.send_response()