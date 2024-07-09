from apps.web_portal.models.assessment import UserAssessmentResult
from rest_framework import serializers

class UserAssessmentResultSerializer(serializers.ModelSerializer):
        class Meta:
            model = UserAssessmentResult
            fields = ['assessment_name', 'assessment_date', 'score_percentage', 'result_status']