from rest_framework import serializers
from apps.access.models import User
from apps.learning.models.certification_path import CertificationPath
from apps.learning.models.course import Course, LearningContentFeedback
from apps.learning.models.learning_path import LearningPath

class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ['id', 'uuid', 'identity']

class LearningPathSerializer(serializers.ModelSerializer):
    class Meta:
        model = LearningPath
        fields = ['id', 'uuid', 'identity']

class CertificationPathSerializer(serializers.ModelSerializer):
    class Meta:
        model = CertificationPath
        fields = ['id', 'uuid', 'identity']

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'uuid', 'full_name', 'idp_email']