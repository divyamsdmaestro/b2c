from rest_framework import serializers
from apps.learning.models import  LearningRole
from apps.learning.models import Skill, LearningRoleImage, SkillImage
from apps.common.serializers import (
    AppReadOnlyModelSerializer,
)
from apps.purchase.models import (
    SkillWishlist,
    SkillAddToCart
)
from apps.my_learnings.models import (
    UserSkillTracker
)

class LearningRoleImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = LearningRoleImage
        fields = [
            'id',
            'uuid',
            'file'
        ]

class SkillImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = SkillImage
        fields = [
            'id',
            'uuid',
            'file'
        ]

class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model =  Skill
        fields = ['uuid', 'identity']

class LearningRoleListSerializer(AppReadOnlyModelSerializer):
    image = LearningRoleImageSerializer()
    skills = SkillSerializer(many=True)

    class Meta:
        model = LearningRole
        fields = [
            'id',
            'uuid',
            'identity',
            'image',
            'description',
            'skills',
            'duration',
            'rating',
        ]

class ExploreRoleSerializer(serializers.Serializer):
    """Explore Page serializer, provided courses or learning path based on the query."""

    TYPE_CHOICES = (
        ("courses", "courses"),
        ("learning_paths", "learning_paths"),
        ("certification_paths", "certification_paths"),
        ("blended_learning_paths", "blended_learning_paths"),
    )

    type = serializers.ChoiceField(choices=TYPE_CHOICES, default="courses")
