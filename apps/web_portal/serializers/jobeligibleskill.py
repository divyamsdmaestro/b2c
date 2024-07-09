from rest_framework import serializers
from apps.learning.models import (
    JobEligibleSkill,
    JobEligibleSkillImage,
    Category,
    CourseImage,
    Course,
    LearningPathImage,
    LearningPath,
    CertificationPath,
    CertificationPathImage
    )
from apps.common.serializers import AppReadOnlyModelSerializer, get_app_read_only_serializer, get_read_serializer
from django.contrib.auth.models import AnonymousUser
from apps.purchase.models import JobEligibilitySkillAddToCart
from apps.purchase.models import JobEligibilitySkillWishlist
from apps.my_learnings.models import UserJobEligibleSkillTracker


class JobEligibleSkillSerializer(AppReadOnlyModelSerializer):
    image = get_app_read_only_serializer(JobEligibleSkillImage, meta_fields="__all__")
    is_in_cart = serializers.SerializerMethodField()
    is_in_wishlist = serializers.SerializerMethodField()
    is_in_buy = serializers.SerializerMethodField()
    
    class Meta(AppReadOnlyModelSerializer.Meta):
        model = JobEligibleSkill
        fields = [
            "id",
            "uuid",
            "identity",
            "description",
            "image",
            "category","make_this_skill_popular",
            "assessment_id",
            "is_in_cart",
            "is_in_wishlist",
            "is_in_buy",
            "current_price_inr",
        ]
    
    def get_is_in_cart(self, obj):
        """This is a function to get Job_Eligible_Skill is already in cart or not"""
        user = self.get_user()
        if isinstance(user, AnonymousUser) or user == None:
            return False
        else:
            is_in_cart = JobEligibilitySkillAddToCart.objects.filter(
                entity_id = obj.id, created_by = user
            ).exists()
            return is_in_cart
        
    def get_is_in_wishlist(self, obj):
        """This is a function to get Job_Eligible_Skill is already in wishlist or not"""
        user = self.get_user()
        if isinstance(user, AnonymousUser) or user == None:
            return False
        else:
            is_in_cart = JobEligibilitySkillWishlist.objects.filter(
                entity_id = obj.id, created_by = user
            ).exists()
            return is_in_cart
        
    def get_is_in_buy(self, obj):
        """This is a function to get Job_Eligible_Skill is already bought or not"""
        user = self.get_user()
        if isinstance(user, AnonymousUser) or user == None:
            return False
        else:
            is_in_buy =  UserJobEligibleSkillTracker.objects.filter(
                entity_id = obj.id, created_by = user
            ).exists()
            return is_in_buy
        
class JobEligibleSkillDetailSerializer(AppReadOnlyModelSerializer):
    image = get_read_serializer(JobEligibleSkillImage, meta_fields="__all__")
    category = get_read_serializer(Category, meta_fields= ["id", "uuid", "identity"])
    is_in_cart = serializers.SerializerMethodField()
    is_in_wishlist = serializers.SerializerMethodField()
    is_in_buy = serializers.SerializerMethodField()
    learning_content_count = serializers.SerializerMethodField()
    
    class Meta(AppReadOnlyModelSerializer.Meta):
        model = JobEligibleSkill
        fields = [
            "id",
            "uuid",
            "identity",
            "description",
            "image",
            "category",
            "make_this_skill_popular",
            "assessment_id",
            "is_in_cart",
            "is_in_wishlist",
            "is_in_buy",
            "current_price_inr",
            "learning_content_count",
        ]
    
    def get_is_in_cart(self, obj):
        """This is a function to get Job_Eligible_Skill is already in cart or not"""
        user = self.get_user()
        if isinstance(user, AnonymousUser) or user == None:
            return False
        else:
            is_in_cart = JobEligibilitySkillAddToCart.objects.filter(
                entity_id = obj.id, created_by = user
            ).exists()
            return is_in_cart
        
    def get_is_in_wishlist(self, obj):
        """This is a function to get Job_Eligible_Skill is already in wishlist or not"""
        user = self.get_user()
        if isinstance(user, AnonymousUser) or user == None:
            return False
        else:
            is_in_cart = JobEligibilitySkillWishlist.objects.filter(
                entity_id = obj.id, created_by = user
            ).exists()
            return is_in_cart
        
    def get_is_in_buy(self, obj):
        """This is a function to get Job_Eligible_Skill is already bought or not"""
        user = self.get_user()
        if isinstance(user, AnonymousUser) or user == None:
            return False
        else:
            is_in_buy =  UserJobEligibleSkillTracker.objects.filter(
                entity_id = obj.id, created_by = user
            ).exists()
            return is_in_buy
        
    def get_learning_content_count(self, obj):
        return{
            "courses_count": obj.courses.count(),
            "learning_paths_count": obj.learning_paths.count(),
            "certification_paths_count": obj.certification_paths.count()
        }
        
class JobSkillCourseSerializer(serializers.ModelSerializer):
    image = get_read_serializer(CourseImage, meta_fields="__all__")()

    class Meta:
        model = Course
        fields = ['id', 'uuid', 'identity', 'description', 'rating', 'duration', 'make_this_course_popular', 'make_this_course_trending', 'make_this_course_best_selling', 'image']

class JobSkillLearningPathSerializer(serializers.ModelSerializer):
    image = get_read_serializer(LearningPathImage, meta_fields="__all__")()

    class Meta:
        model = LearningPath
        fields = ['id', 'uuid', 'identity', 'description', 'rating', 'duration', 'make_this_lp_popular', 'make_this_lp_best_selling', 'make_this_lp_trending', 'image']
    
class JobSkillCertificationPathSerializer(serializers.ModelSerializer):
    image = get_read_serializer(CertificationPathImage, meta_fields="__all__")

    class Meta:
        model = CertificationPath
        fields = ['id', 'uuid', 'identity', 'description', 'rating', 'duration', 'make_this_alp_popular', 'make_this_alp_trending', 'make_this_alp_best_selling', 'image']