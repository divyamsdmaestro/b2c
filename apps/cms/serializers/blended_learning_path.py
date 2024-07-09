
from apps.common.serializers import AppWriteOnlyModelSerializer
from apps.learning.models import BlendedLearningPathScheduleDetails
from rest_framework import serializers


class ScheduleDetailsCreateSerializer(AppWriteOnlyModelSerializer):
    """This serializer contains configuration for BLP schedule details."""
    
    is_weekend_batch = serializers.BooleanField(required=False)
    class Meta(AppWriteOnlyModelSerializer.Meta):
        fields = ['mentor','start_date','end_date','start_time','end_time','virtual_url','address','duration','is_day_batch','mode','is_weekend_batch','filling_fast']
        model = BlendedLearningPathScheduleDetails