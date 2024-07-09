from apps.learning.models.blended_learning_path import BlendedLearningClassroomAndVirtualDetails
from rest_framework import serializers
from django.db import models

from apps.learning.models.mml_course import MMLCourse, MMLCourseImage
from apps.my_learnings.models.trackers import StudentEnrolledMMLCourseTracker, UserMMLCourseTracker, UserBlendedLearningPathTracker
from apps.purchase.models.cart import MMLCourseAddToCart
from apps.purchase.models.wishlist import MMLCourseWishlist
from ...payments.models import SaleDiscount
from apps.common.serializers import (
    AppReadOnlyModelSerializer,
    get_app_read_only_serializer,
    get_read_serializer,
    get_app_read_only_optimize_serializer,
    AppModelSerializer
)
from apps.learning.models import (
    Author,
    Category,
    CategoryImage,
    CertificationPath,
    CertificationPathImage,
    CertificationPathLearningPath,
    Course,
    CourseResource,
    CourseImage,
    CourseModule,
    CourseSubModule,
    LearningPath,
    LearningPathCourse,
    LearningPathImage,
    Proficiency,
    Skill,
    SkillImage,
    Tag,
    Vendor,
    BlendedLearningPathImage,
    BlendedLearningPath,
    BlendedLearningPathCourseModesAndFee,
    BlendedLearningPathPriceDetails,
    BlendedLearningPathCourseMode,
    BlendedLearningPathScheduleDetails
)
from ...purchase.models import (
    CourseWishlist,
    CourseAddToCart,
    CertificationPathAddToCart,
    CertificationPathWishlist,
    LearningPathAddToCart,
    LearningPathWishlist,
    SkillAddToCart,
    SkillWishlist,
    BlendedLearningPathWishlist,
    BlendedLearningPathAddToCart,
)
from apps.web_portal.models import Testimonial
from django.contrib.auth.models import AnonymousUser
from apps.my_learnings.models import UserCourseTracker, StudentEnrolledCourseTracker, UserSkillTracker, UserLearningPathTracker
from datetime import datetime
from apps.web_portal.serializers.webinar import WebinarJobDetailSerializer
from apps.webinars.models import Webinar
from apps.jobs.models.job import Job
from apps.jobs.serializers import JobSerializer
from apps.hackathons.models import hackathon as hackathon_models
from apps.cms.serializers import HackathonJobListSerializer, ZoneSkillSerializer
from apps.forums.models import Zone

class ExploreRecommendationSerializer(serializers.Serializer):
    """Explore Page serializer, provided courses or learning path based on the query."""

    TYPE_CHOICES = (
        ("courses", "courses"),
        ("learning_paths", "learning_paths"),
        ("certification_paths", "certification_paths"),
        ("blended_learning_paths", "blended_learning_paths"),
        ("hackathons", "hackathons"),
        ("webinars", "webinars"),
        ("zones", "zones")
    )

    type = serializers.ChoiceField(choices=TYPE_CHOICES, default="courses")

class ExploreSerializer(serializers.Serializer):
    """Explore Page serializer, provided courses or learning path based on the query."""

    TYPE_CHOICES = (
        ("courses", "courses"),
        ("learning_paths", "learning_paths"),
        ("certification_paths", "certification_paths"),
        ("blended_learning_paths", "blended_learning_paths"),
        ("mml_courses", "mml_courses")
    )

    FILTER_CHOICES = (
        ("trending_courses", "trending_courses"),
        ("recently_published", "recently_published"),
        ("highly_popular", "highly_popular"),
        ("best_selling", "best_selling"),
        ("free", "free"),
        ("virtual_labs", "virtual_labs"),
    )

    type = serializers.ChoiceField(choices=TYPE_CHOICES, default="courses")
    advance_filter = serializers.ChoiceField(choices=FILTER_CHOICES, default="none")

class ExploreSearchSerializer(serializers.Serializer):
    """Explore Page overall search for skill, learning path, courses"""

    search = serializers.CharField(max_length=100)

class LinkageFieldsSerializer(AppReadOnlyModelSerializer):
    """
    This class contains default serializers for common linkages fields like tags,
    skills, categories, proficiency.
    """

    tags = get_app_read_only_serializer(Tag, meta_fields=['id','uuid','file'])(many=True)
    skills = get_app_read_only_serializer(Skill, meta_fields=['id','uuid','identity','description','image','category'])(many=True)
    categories = get_app_read_only_serializer(Category, meta_fields=['id','uuid','identity','image','popularity'])(
        many=True
    )
    proficiency = get_app_read_only_serializer(Proficiency, meta_fields=['id','uuid','identity'])()


   
class CourseSubModuleSerializer(AppReadOnlyModelSerializer):

    video_url = serializers.SerializerMethodField()
    class Meta:
        fields = ['id','uuid','identity','description','video_url','duration','position','module','azure_streaming_config','azure_streaming_video_url','azure_streaming_thumbnail_url','streaming_generation_process_status','streaming_generation_process_error','module_type','assessmentID']
        model = CourseSubModule

    def get_video_url(self, obj):
        value = obj.video_url
        if value:
            if "https://irisstorageprod.blob.core.windows.net" in value:
                new_split = value.split("?")[0]
                return new_split + "?sv=2022-11-02&ss=b&srt=co&sp=rtx&se=2024-07-30T20:58:56Z&st=2024-02-08T12:58:56Z&spr=https&sig=zN%2FksYNf%2FGxKBisRteGaEVvLQMOrQ72oYzLbnvc8JcU%3D"
            elif "https://irisdatacontainer.blob.core.windows.net" in value:
                new_split = value.split("?")[0]
                return new_split + "?sv=2022-11-02&ss=b&srt=co&sp=rtfx&se=2024-07-30T20:49:21Z&st=2024-02-08T12:49:21Z&spr=https&sig=19at7fk6WpIKkK6Db6xtdL3w0xlfFVkpCKd58AWzT3Q%3D"
        return value


class CourseModuleSerializer(AppReadOnlyModelSerializer):
    sub_modules = CourseSubModuleSerializer(source="related_modules", many=True)

    class Meta:
        fields = ['id','uuid','identity','description','position','course','sub_modules']
        model = CourseModule

class YouMayAlsoLikeMMLCourseSerializer(AppReadOnlyModelSerializer):

    class Meta:
        fields = "__all__"
        model = MMLCourse
class YouMayAlsoLikeCourseSerializer(AppReadOnlyModelSerializer):

    class Meta:
        fields = "__all__"
        model = Course

class YouMayAlsoLikeLearningPathSerializer(AppReadOnlyModelSerializer):
    image = get_app_read_only_serializer(LearningPathImage, meta_fields=['id','uuid','file'])()

    class Meta:
        fields =  ['id', 'uuid','image','actual_price_inr', 'current_price_inr',
    'identity', 'description', 'duration', 'rating', 'virtual_lab',
    'learning_role', 'language']
        model = LearningPath

class YouMayAlsoLikeCertificationPathSerializer(AppReadOnlyModelSerializer):

    class Meta:
        fields = "__all__"
        model = CertificationPath

class TestimonialSerializer(AppReadOnlyModelSerializer):
    """This serializer contains Testimonial list"""

    class Meta:
        fields = ['id','uuid','name','designation','image','video_url','message']
        model = Testimonial


class CourseSerializer(AppReadOnlyModelSerializer):
    """This serializer contains configuration for Course."""

    image = get_app_read_only_serializer(CourseImage, meta_fields=['id','uuid','file'])()
    author = get_app_read_only_serializer(Author, meta_fields=['id','uuid','identity','designation','image','rating','vendor'])()
    # vendor = get_app_read_only_serializer(Vendor, meta_fields=['id','uuid','identity','image'])()
    # resource = get_read_serializer(CourseResource, meta_fields=['id','uuid','file'])()
    skills = get_app_read_only_serializer(Skill, meta_fields=['id','uuid','identity'])(many=True)

    modules = CourseModuleSerializer(source="related_courses", many=True)
    is_in_wishlist = serializers.SerializerMethodField()
    is_in_cart = serializers.SerializerMethodField()
    is_in_buy = serializers.SerializerMethodField()
    sale_discount = serializers.SerializerMethodField()
    testimonial = serializers.SerializerMethodField()
    you_may_also_like = serializers.SerializerMethodField()
    enrolled_student = serializers.SerializerMethodField()
   
    class Meta:    
        fields = "__all__"
        model = Course

    def get_is_in_wishlist(self, obj):
        user = self.get_user()
        """This function used to get course is already in wishlist or not"""
        if isinstance(user, AnonymousUser) or user == None:
            return False
        else:
            is_in_wishlist = CourseWishlist.objects.filter(
                entity_id=obj.id, created_by=user
            ).exists()
            return is_in_wishlist

    def get_is_in_cart(self, obj):
        """This function used to get course is already in cart or not"""
        user = self.get_user()
        if isinstance(user, AnonymousUser) or user == None:
            return False
        else:
            is_in_cart = CourseAddToCart.objects.filter(
                entity_id=obj.id, created_by=user
            ).exists()
            return is_in_cart
   
    def get_is_in_buy(self,obj):
        """This function used to get course is already in buy or not"""
        auth_user = self.get_user()
        user = self.get_user()
        if isinstance(user, AnonymousUser) or user == None:
            return False
        elif auth_user.user_role:
            if auth_user.user_role.identity == "Student":
                is_in_buy = StudentEnrolledCourseTracker.objects.filter(entity_id=obj.id, created_by=user).exists()
                return is_in_buy
            else:
                is_buy = UserCourseTracker.objects.filter(entity_id=obj.id, created_by=user).exists()
                return is_buy
        else:
            is_buy = UserCourseTracker.objects.filter(entity_id=obj.id, created_by=user).exists()
            return is_buy

    def get_enrolled_student(self, obj):
        """This function used to get enrolled student count"""
        auth_user = self.get_user()
        student_count =  UserCourseTracker.objects.filter(entity_id=obj.id).count()
        if isinstance(auth_user, AnonymousUser) or auth_user == None:
            return student_count
        else:
            if auth_user:
                if auth_user.user_role:
                    if auth_user.user_role.identity == "Student":
                        student_count = StudentEnrolledCourseTracker.objects.filter(entity_id=obj.id).count()
            return student_count

    def get_sale_discount(self,obj):
        """This function used to get sale discount"""
        today = datetime.now().date()
        sale_discount_data = SaleDiscount.objects.filter(courses=obj.id, start_date__lte=today, end_date__gte=today).first()
        if sale_discount_data:
            sale_discount = True
            sale_discount_percentage = sale_discount_data.sale_discount_percentage
            discount_price = obj.current_price_inr - ((obj.current_price_inr*sale_discount_data.sale_discount_percentage)/100)
        else:
            sale_discount = False
            sale_discount_percentage = None
            discount_price = None

        return {"sale_discount":sale_discount, "sale_discount_percentage":sale_discount_percentage, "discount_price":discount_price}

    def get_testimonial(self, obj):
        testimonial_data = Testimonial.objects.all()[:18]
        testimonial_serializer = TestimonialSerializer(testimonial_data, many=True)
        return testimonial_serializer.data
   
    def get_you_may_also_like(self,obj):
        course_data = Course.objects.filter(skills__in=obj.skills.values_list("id", flat=True)).distinct()[:4]
        course_serializer = YouMayAlsoLikeCourseSerializer(course_data, many=True)
        return course_serializer.data
   
class CourseSerializerWithExclusion(CourseSerializer):
    """Custom CourseSerializer to exclude specific fields."""

    def to_representation(self, instance):
        # Exclude the 'testimonial' and 'you_may_also_like' fields
        exclude_fields = ('testimonial', 'you_may_also_like')
        data = super().to_representation(instance)
        return {key: value for key, value in data.items() if key not in exclude_fields}
    
class LearningPathCourseSubModuleListSerializer(AppReadOnlyModelSerializer):
   
    class Meta:
        fields = ['identity','duration','video_url']
        model = CourseSubModule    


class LearningPathCourseModuleListSerializer(AppReadOnlyModelSerializer):
    # sub_modules = LearningPathCourseSubModuleListSerializer(source="related_modules", many=True)

    class Meta:
        fields = ['identity']
        model = CourseModule

# class LearningPathCourseModulePreviewListSerializer(AppReadOnlyModelSerializer):
#     sub_modules = LearningPathCourseSubModuleListSerializer(source="related_modules", many=True)

#     class Meta:
#         fields = ['identity', 'sub_modules']
#         model = CourseModule

class LearningPathCourseListSerializer(LinkageFieldsSerializer):
    """This serializer contains configuration for Course."""

    modules = LearningPathCourseModuleListSerializer(source="related_courses", many=True)
   
    class Meta:    
        fields = ['uuid','identity','modules','duration']
        model = Course

# class LearningPathCoursePreviewListSerializer(AppReadOnlyModelSerializer):
#     """This serializer contains configuration for Course."""

#     modules = LearningPathCourseModulePreviewListSerializer(source="related_courses", many=True)
   
#     class Meta:    
#         fields = ['uuid','identity','modules']
#         model = Course

class MMLCourseSerializer(LinkageFieldsSerializer):
    """This serializer contains configuration for MML Course."""

    image = get_app_read_only_serializer(MMLCourseImage, meta_fields="__all__")()
    author = get_app_read_only_serializer(Author, meta_fields="__all__")()
    vendor = get_app_read_only_serializer(Vendor, meta_fields="__all__")()
    resource = get_read_serializer(CourseResource, meta_fields="__all__")()

    is_in_wishlist = serializers.SerializerMethodField()
    is_in_cart = serializers.SerializerMethodField()
    is_in_buy = serializers.SerializerMethodField()
    sale_discount = serializers.SerializerMethodField()
    testimonial = serializers.SerializerMethodField()
    you_may_also_like = serializers.SerializerMethodField()
    enrolled_student = serializers.SerializerMethodField()
   
    class Meta:
        fields = "__all__"
        model = MMLCourse

    def get_is_in_wishlist(self, obj):
        user = self.get_user()
        """This function used to get course is already in wishlist or not"""
        if isinstance(user, AnonymousUser) or user == None:
            return False
        else:
            is_in_wishlist = MMLCourseWishlist.objects.filter(
                entity_id=obj.id, created_by=user
            ).exists()
            return is_in_wishlist

    def get_is_in_cart(self, obj):
        """This function used to get course is already in cart or not"""
        user = self.get_user()
        if isinstance(user, AnonymousUser) or user == None:
            return False
        else:
            is_in_cart = MMLCourseAddToCart.objects.filter(
                entity_id=obj.id, created_by=user
            ).exists()
            return is_in_cart
   
    def get_is_in_buy(self,obj):
        """This function used to get course is already in buy or not"""
        auth_user = self.get_user()
        user = self.get_user()
        if isinstance(user, AnonymousUser) or user == None:
            return False
        elif auth_user.user_role:
            if auth_user.user_role.identity == "Student":
                is_in_buy = StudentEnrolledMMLCourseTracker.objects.filter(entity_id=obj.id, created_by=user).exists()
                return is_in_buy
            else:
                is_buy = UserMMLCourseTracker.objects.filter(entity_id=obj.id, created_by=user).exists()
                return is_buy
        else:
            is_buy = UserMMLCourseTracker.objects.filter(entity_id=obj.id, created_by=user).exists()
            return is_buy

    def get_enrolled_student(self, obj):
        """This function used to get enrolled student count"""
        auth_user = self.get_user()
        student_count =  UserMMLCourseTracker.objects.filter(entity_id=obj.id).count()
        if isinstance(auth_user, AnonymousUser) or auth_user == None:
            return student_count
        else:
            if auth_user:
                if auth_user.user_role:
                    if auth_user.user_role.identity == "Student":
                        student_count = StudentEnrolledMMLCourseTracker.objects.filter(entity_id=obj.id).count()
            return student_count

    def get_sale_discount(self,obj):
        """This function used to get sale discount"""
        today = datetime.now().date()
        sale_discount_data = SaleDiscount.objects.filter(courses=obj.id, start_date__lte=today, end_date__gte=today).first()
        if sale_discount_data:
            sale_discount = True
            sale_discount_percentage = sale_discount_data.sale_discount_percentage
            discount_price = obj.current_price_inr - ((obj.current_price_inr*sale_discount_data.sale_discount_percentage)/100)
        else:
            sale_discount = False
            sale_discount_percentage = None
            discount_price = None

        return {"sale_discount":sale_discount, "sale_discount_percentage":sale_discount_percentage, "discount_price":discount_price}

    def get_testimonial(self, obj):
        testimonial_data = Testimonial.objects.all()[:18]
        testimonial_serializer = TestimonialSerializer(testimonial_data, many=True)
        return testimonial_serializer.data
   
    def get_you_may_also_like(self,obj):
        course_data = MMLCourse.objects.filter(skills__in=obj.skills.values_list("id", flat=True)).distinct()[:4]
        course_serializer = YouMayAlsoLikeMMLCourseSerializer(course_data, many=True)
        return course_serializer.data  
   
class LeaningPathCourseSerializer(AppReadOnlyModelSerializer):
    """This serializer contains configuration for LearningPathCourse."""

    course = LearningPathCourseListSerializer()
    # is_in_wishlist = serializers.SerializerMethodField()
    # is_in_cart = serializers.SerializerMethodField()
    # is_in_buy = serializers.SerializerMethodField()
    # sale_discount = serializers.SerializerMethodField()

    class Meta:
        model = LearningPathCourse
        fields = ['id','uuid','course']
        ordering = ["-position"]

    # def get_is_in_wishlist(self, obj):
    #     """This function used to get Learning Path is already in wishlist or not"""
    #     user = self.get_user()
    #     if isinstance(user, AnonymousUser) or user == None:
    #         return False
    #     else:
    #         is_in_wishlist = LearningPathWishlist.objects.filter(
    #             entity_id=obj.id, created_by=user
    #         ).exists()
    #         return is_in_wishlist

    # def get_is_in_cart(self, obj):
    #     """This function used to get Learning Path is already in cart or not"""
    #     user = self.get_user()
    #     if isinstance(user, AnonymousUser) or user == None:
    #         return False
    #     else:
    #         is_in_cart = LearningPathAddToCart.objects.filter(
    #             entity_id=obj.id, created_by=user
    #         ).exists()
    #         return is_in_cart
       
    # def get_is_in_buy(self,obj):
    #     """This function used to get course is already in buy or not"""
    #     user = self.get_user()
    #     if isinstance(user, AnonymousUser) or user == None:
    #         return False
    #     else:
    #         is_buy = UserCourseTracker.objects.filter(entity_id=obj.id, created_by=user).exists()
    #         return is_buy
       
    # def get_sale_discount(self,obj):
    #     """This function used to get sale discount"""
    #     today = datetime.now().date()
    #     sale_discount_data = SaleDiscount.objects.filter(learning_paths=obj.id, start_date__lte=today, end_date__gte=today).first()
    #     if sale_discount_data:
    #         sale_discount = True
    #         sale_discount_percentage = sale_discount_data.sale_discount_percentage
    #         discount_price = obj.current_price_inr - ((obj.current_price_inr*sale_discount_data.sale_discount_percentage)/100)
    #     else:
    #         sale_discount = False
    #         sale_discount_percentage = None
    #         discount_price = None

    #     return {"sale_discount":sale_discount, "sale_discount_percentage":sale_discount_percentage, "discount_price":discount_price}

class LeaningPathSerializer(AppReadOnlyModelSerializer):
    """This serializer contains configuration for LearningPath."""

    image = get_app_read_only_optimize_serializer(LearningPathImage, meta_fields=['id','uuid','file'])()
    # learning_path_courses = LeaningPathCourseSerializer(
    #     source="related_learning_path_courses", many=True
    # )
    # testimonial = serializers.SerializerMethodField()
    # you_may_also_like = serializers.SerializerMethodField()
    # tags = get_app_read_only_serializer(Tag, meta_fields=['id','uuid','file'])(many=True)
    skills = get_app_read_only_optimize_serializer(Skill, meta_fields=['id','uuid','identity'])(many=True)
    is_in_cart = serializers.SerializerMethodField()
    is_in_buy = serializers.SerializerMethodField()

    class Meta:
        model = LearningPath
        fields = ['id', 'uuid','image','actual_price_inr', 'current_price_inr','identity', 'description', 'duration', 'rating','skills', 'is_in_cart', 'is_in_buy']

    def get_is_in_cart(self, obj):
        """This function used to get Learning Path is already in cart or not"""
        user = self.get_user()
        if isinstance(user, AnonymousUser) or user == None:
            return False
        else:
            is_in_cart = LearningPathAddToCart.objects.filter(
                entity_id=obj.id, created_by=user
            ).exists()
            return is_in_cart
       
    def get_is_in_buy(self,obj):
        """This function used to get course is already in buy or not"""
        user = self.get_user()
        if isinstance(user, AnonymousUser) or user == None:
            return False
        else:
            is_buy = UserLearningPathTracker.objects.filter(entity_id=obj.id, created_by=user).exists()
            return is_buy
    # def get_testimonial(self, obj):
    #     testimonial_data = Testimonial.objects.all()[:18]
    #     testimonial_serializer = TestimonialSerializer(testimonial_data, many=True)
    #     return testimonial_serializer.data
   
    # def get_you_may_also_like(self, obj):
    #     lp_data = LearningPath.objects.filter(skills__in=obj.skills.values_list("id", flat=True)).distinct()[:4]
    #     lp_serializer = YouMayAlsoLikeLearningPathSerializer(lp_data, many=True)
    #     return lp_serializer.data
class LeaningPathCourseListSerializer(AppReadOnlyModelSerializer):
    course = LearningPathCourseListSerializer()

    class Meta:
        model = LearningPathCourse
        fields = ['uuid','course']
        ordering = ["-position"]

class LeaningPathCoursePreviewSerializer(AppReadOnlyModelSerializer):
    course = serializers.SerializerMethodField()

    class Meta:
        model = LearningPathCourse
        fields = ['uuid', 'course']

    def get_course(self, obj):
        courses_qs = CourseSubModule.objects.filter(module__course__id=obj.course.id)[:2]
        return LearningPathCourseSubModuleListSerializer(courses_qs, many=True).data
    
class LearningPathWithExclusion(LeaningPathSerializer):
    """Custom CourseSerializer to exclude specific fields."""

    def to_representation(self, instance):
        # Exclude the 'testimonial' and 'you_may_also_like' fields
        exclude_fields = ('testimonial', 'you_may_also_like')
        data = super().to_representation(instance)
        return {key: value for key, value in data.items() if key not in exclude_fields}

class CertificationPathLearningPathSerializer(AppReadOnlyModelSerializer):
    """This serializer contains configuration for CertificationPathLearningPath."""

    learning_path = LearningPathWithExclusion()

    class Meta:
        model = CertificationPathLearningPath
        fields = "__all__"
        ordering = ["-position"]


class CertificationPathSerializer(AppReadOnlyModelSerializer):
    """This serializer contains configuration for CertificationPath."""

    image = get_app_read_only_serializer(
        CertificationPathImage, meta_fields="__all__"
    )()
    tags = get_app_read_only_serializer(Tag, meta_fields="__all__")(many=True)
    skills = get_app_read_only_serializer(Skill, meta_fields="__all__")(many=True)
    categories = get_app_read_only_serializer(Category, meta_fields="__all__")(
        many=True
    )
    certification_learning_path = CertificationPathLearningPathSerializer(
        source="related_certification_path_learning_paths", many=True
    )
    is_in_wishlist = serializers.SerializerMethodField()
    is_in_cart = serializers.SerializerMethodField()
    is_in_buy = serializers.SerializerMethodField()
    sale_discount = serializers.SerializerMethodField()
    testimonial = serializers.SerializerMethodField()
    you_may_also_like = serializers.SerializerMethodField()

    class Meta:
        model = CertificationPath
        fields = "__all__"

    def get_is_in_wishlist(self, obj):
        """This function used to get Certificatepath is already in wishlist or not"""
        user = self.get_user()
        if isinstance(user, AnonymousUser) or user == None:
            return False
        else:
            is_in_wishlist = CertificationPathWishlist.objects.filter(
                entity_id=obj.id, created_by=user
            ).exists()
            return is_in_wishlist

    def get_is_in_cart(self, obj):
        """This function used to get Certificatepath is already in cart or not"""
        user = self.get_user()
        if isinstance(user, AnonymousUser) or user == None:
            return False
        else:
            is_in_cart = CertificationPathAddToCart.objects.filter(
                entity_id=obj.id, created_by=user
            ).exists()
            return is_in_cart
   
    def get_is_in_buy(self,obj):
        """This function used to get course is already in buy or not"""
        user = self.get_user()
        if isinstance(user, AnonymousUser) or user == None:
            return False
        else:
            is_buy = UserCourseTracker.objects.filter(entity_id=obj.id, created_by=user).exists()
            return is_buy
       
    def get_sale_discount(self,obj):
        """This function used to get sale discount"""
        today = datetime.now().date()
        sale_discount_data = SaleDiscount.objects.filter(certification_paths=obj.id, start_date__lte=today, end_date__gte=today).first()
        if sale_discount_data:
            sale_discount = True
            sale_discount_percentage = sale_discount_data.sale_discount_percentage
            discount_price = obj.current_price_inr - ((obj.current_price_inr*sale_discount_data.sale_discount_percentage)/100)
        else:
            sale_discount = False
            sale_discount_percentage = None
            discount_price = None

        return {"sale_discount":sale_discount, "sale_discount_percentage":sale_discount_percentage, "discount_price":discount_price}
       
    def get_testimonial(self, obj):
        testimonial_data = Testimonial.objects.all()[:18]
        testimonial_serializer = TestimonialSerializer(testimonial_data, many=True)
        return testimonial_serializer.data
   
    def get_you_may_also_like(self,obj):
        cp_data = CertificationPath.objects.filter(skills__in=obj.skills.values_list("id", flat=True)).distinct()[:4]
        cp_serializer = YouMayAlsoLikeCertificationPathSerializer(cp_data, many=True)
        return cp_serializer.data

class CategorySerializer(AppReadOnlyModelSerializer):
    """This serializer contains configuration for CertificationPathLearningPath."""

    image = get_app_read_only_serializer(
        CategoryImage, meta_fields=['id','uuid','file']
    )()
   
    class Meta:
        model = Category
        fields = ['id', 'uuid', 'identity', 'image', 'popularity']
        ordering = ["-position"]

class SkillListSerializer(AppReadOnlyModelSerializer):
    image = get_app_read_only_serializer(
        SkillImage, meta_fields=['id','uuid','file']
    )()
    category = CategorySerializer(many=True)
    is_in_wishlist = serializers.SerializerMethodField()
    is_in_cart = serializers.SerializerMethodField()
    is_in_buy = serializers.SerializerMethodField()

    class Meta:
        model = Skill
        fields = ['id', 'uuid', 'identity', 'image', 'description','category','make_this_skill_popular', 'actual_price_inr','current_price_inr', 
                  'is_archived','is_in_wishlist', 'is_in_cart', 'is_in_buy']

    def get_is_in_wishlist(self, obj):
        """This function used to get Certificatepath is already in wishlist or not"""
        user = self.get_user()
        if isinstance(user, AnonymousUser) or user == None:
            return False
        else:
            is_in_wishlist = SkillWishlist.objects.filter(
                entity_id=obj.id, created_by=user
            ).exists()
            return is_in_wishlist

    def get_is_in_cart(self, obj):
        """This function used to get Certificatepath is already in cart or not"""
        user = self.get_user()
        if isinstance(user, AnonymousUser) or user == None:
            return False
        else:
            is_in_cart = SkillAddToCart.objects.filter(
                entity_id=obj.id, created_by=user
            ).exists()
            return is_in_cart
   
    def get_is_in_buy(self,obj):
        """This function used to get course is already in buy or not"""
        user = self.get_user()
        if isinstance(user, AnonymousUser) or user == None:
            return False
        else:
            is_buy = UserSkillTracker.objects.filter(entity_id=obj.id, created_by=user).exists()
            return is_buy

class CourseSkillSerializer(LinkageFieldsSerializer):
    """This serializer contains configuration for Course."""


    image = get_app_read_only_serializer(CourseImage, meta_fields=['id','uuid','file'])()
    sale_discount = serializers.SerializerMethodField()
   
    class Meta:
        fields = ['id','uuid','identity','description','actual_price_inr','current_price_inr','image','duration','rating','validity',
                'make_this_course_popular','make_this_course_trending','make_this_course_best_selling','complete_in_a_day','is_private_course',
                'editors_pick','is_free','sale_discount']
        model = Course

    def get_sale_discount(self,obj):
        """This function used to get sale discount"""
        today = datetime.now().date()
        sale_discount_data = SaleDiscount.objects.filter(courses=obj.id, start_date__lte=today, end_date__gte=today).first()
        if sale_discount_data:
            sale_discount = True
            sale_discount_percentage = sale_discount_data.sale_discount_percentage
            discount_price = obj.current_price_inr - ((obj.current_price_inr*sale_discount_data.sale_discount_percentage)/100)
        else:
            sale_discount = False
            sale_discount_percentage = None
            discount_price = None

        return {"sale_discount":sale_discount, "sale_discount_percentage":sale_discount_percentage, "discount_price":discount_price}

class LeaningPathSkillSerializer(LinkageFieldsSerializer):
    """This serializer contains configuration for LearningPath."""


    image = get_app_read_only_serializer(LearningPathImage, meta_fields=['id','uuid','file'])()


    class Meta:
        model = LearningPath
        fields = ['id', 'uuid','image','actual_price_inr', 'current_price_inr','is_private_course',
    'identity', 'description', 'duration', 'rating','make_this_lp_popular','make_this_lp_trending',
    'make_this_lp_best_selling','learning_role','is_free']


class CertificationPathSkillSerializer(AppReadOnlyModelSerializer):
    """This serializer contains configuration for CertificationPath."""

    image = get_app_read_only_serializer(
        CertificationPathImage, meta_fields=['id','uuid','file']
    )()
    # tags = get_app_read_only_serializer(Tag, meta_fields=['id','uuid','file'])(many=True)
    # skills = get_app_read_only_serializer(Skill, meta_fields=['id','uuid','identity','description','image','category'])(many=True)
    # categories = get_app_read_only_serializer(Category, meta_fields=['id','uuid','identity','image','popularity'])(
    #     many=True
    # )
    sale_discount = serializers.SerializerMethodField()

    class Meta:
        model = CertificationPath
        fields = ['id','uuid','identity','description','image','level','language','duration','is_private_course',
                  'make_this_alp_popular','make_this_alp_trending','make_this_alp_best_selling','is_private_course',
                  'learning_role','requirements','highlights','number_of_seats',
                  'rating','is_free','sale_discount']


    def get_sale_discount(self,obj):
        """This function used to get sale discount"""
        today = datetime.now().date()
        sale_discount_data = SaleDiscount.objects.filter(certification_paths=obj.id, start_date__lte=today, end_date__gte=today).first()
        if sale_discount_data:
            sale_discount = True
            sale_discount_percentage = sale_discount_data.sale_discount_percentage
            discount_price = obj.current_price_inr - ((obj.current_price_inr*sale_discount_data.sale_discount_percentage)/100)
        else:
            sale_discount = False
            sale_discount_percentage = None
            discount_price = None

        return {"sale_discount":sale_discount, "sale_discount_percentage":sale_discount_percentage, "discount_price":discount_price}


class SkillDetailSerializer(AppReadOnlyModelSerializer):
    image = get_app_read_only_serializer(
        SkillImage, meta_fields=['id','uuid','file']
    )()
    # category = CategorySerializer(many=True)
    webinars = serializers.SerializerMethodField()
    forums = serializers.SerializerMethodField()
    hackathons = serializers.SerializerMethodField()
    # # job_interests = serializers.SerializerMethodField()
    # # news_and_blog = serializers.SerializerMethodField()
    courses = serializers.SerializerMethodField()
    learning_path = serializers.SerializerMethodField()
    advanced_learning_path = serializers.SerializerMethodField()  
    is_in_wishlist = serializers.SerializerMethodField()
    is_in_cart = serializers.SerializerMethodField()
    is_in_buy = serializers.SerializerMethodField()
   
    class Meta:
        model = Skill
        fields = ['id', 'uuid', 'identity', 'image', 'description','make_this_skill_popular', 'webinars', 'forums', 'hackathons', 'courses', 'learning_path', 'advanced_learning_path',
                  'actual_price_inr', 'current_price_inr', 'assessmentID', 'vm_name', 'mml_sku_id', 'is_in_wishlist', 
                  'is_in_cart', 'is_in_buy','is_archived']

    def get_webinars(self, obj):
        today = datetime.now().date()
        webinar_data = Webinar.objects.filter(skills__in=[obj.id], start_date__gte=today).distinct()[:6]
        webinar_serializer = WebinarJobDetailSerializer(webinar_data, many=True)
        return webinar_serializer.data
   
    def get_forums(self, obj):
        forums_data = Zone.objects.filter(skills__in=[obj.id], zone_type__identity__icontains="public").distinct()[:6]
        forums_serializer = ZoneSkillSerializer(forums_data, many=True)
        return forums_serializer.data
   
    def get_hackathons(self, obj):
        today = datetime.now().date()
        hackathon_data = hackathon_models.Hackathon.objects.filter(skills__in=[obj.id], start_date__gte=today).distinct()[:6]
        hackathon_serializer = HackathonJobListSerializer(hackathon_data, many=True)
        return hackathon_serializer.data
   
    # def get_job_interests(self, obj):
    #     job_data = Job.objects.filter(skills__in=[obj.id]).distinct()[:6]
    #     job_serializer = JobSerializer(job_data, many=True)
    #     return job_serializer.data
   
    # def get_news_and_blog(self, obj):
    #     pass

    def get_courses(self, obj):
        course_data = Course.objects.filter(skills__in=[obj.id], is_private_course=False).distinct()[:6]
        course_serializer = CourseSkillSerializer(course_data, many=True)
        return course_serializer.data  
     
    def get_learning_path(self, obj):
        learning_path_data = LearningPath.objects.filter(skills__in=[obj.id], is_private_course=False).distinct()[:6]
        learning_path_serializer = LeaningPathSkillSerializer(learning_path_data, many=True)
        return learning_path_serializer.data
   
    def get_advanced_learning_path(self, obj):
        certificate_path_data = CertificationPath.objects.filter(skills__in=[obj.id], is_private_course=False).distinct()[:6]
        certificate_path_serializer = CertificationPathSkillSerializer(certificate_path_data, many=True)
        return certificate_path_serializer.data
   
    def get_is_in_wishlist(self, obj):
        """This function used to get Certificatepath is already in wishlist or not"""
        user = self.get_user()
        if isinstance(user, AnonymousUser) or user == None:
            return False
        else:
            is_in_wishlist = SkillWishlist.objects.filter(
                entity_id=obj.id, created_by=user
            ).exists()
            return is_in_wishlist

    def get_is_in_cart(self, obj):
        """This function used to get Certificatepath is already in cart or not"""
        user = self.get_user()
        if isinstance(user, AnonymousUser) or user == None:
            return False
        else:
            is_in_cart = SkillAddToCart.objects.filter(
                entity_id=obj.id, created_by=user
            ).exists()
            return is_in_cart
   
    def get_is_in_buy(self,obj):
        """This function used to get course is already in buy or not"""
        user = self.get_user()
        if isinstance(user, AnonymousUser) or user == None:
            return False
        else:
            is_buy = UserSkillTracker.objects.filter(entity_id=obj.id, created_by=user).exists()
            return is_buy
        
class SkillWebinarDetailSerializer(AppReadOnlyModelSerializer):
    webinars = serializers.SerializerMethodField()
    class Meta:
        model = Skill
        fields = ['webinars']
    
    def get_webinars(self, obj):
        today = datetime.now().date()
        webinar_data = Webinar.objects.filter(skills__in=[obj.id], start_date__gte=today).distinct()[:6]
        webinar_serializer = WebinarJobDetailSerializer(webinar_data, many=True)
        return webinar_serializer.data
    
class SkillZoneDetailsSerializer(AppReadOnlyModelSerializer):
    forums = serializers.SerializerMethodField()
    class Meta:
        model = Skill
        fields = ['forums']
   
    def get_forums(self, obj):
        forums_data = Zone.objects.filter(skills__in=[obj.id], zone_type__identity__icontains="public").distinct()[:6]
        forums_serializer = ZoneSkillSerializer(forums_data, many=True)
        return forums_serializer.data

class SkillHackathonDetailsSerializer(AppReadOnlyModelSerializer):
    hackathons = serializers.SerializerMethodField()
    class Meta:
        model = Skill
        fields = ['hackathons']
   
    def get_hackathons(self, obj):
        today = datetime.now().date()
        hackathon_data = hackathon_models.Hackathon.objects.filter(skills__in=[obj.id], start_date__gte=today).distinct()[:6]
        hackathon_serializer = HackathonJobListSerializer(hackathon_data, many=True)
        return hackathon_serializer.data
    
class SkillCourseDetailsSerializer(AppReadOnlyModelSerializer):
    courses = serializers.SerializerMethodField()

    class Meta:
        model = Skill
        fields = ['courses']
      
    def get_courses(self, obj):
        course_data = Course.objects.filter(skills__in=[obj.id], is_private_course=False).distinct()[:6]
        course_serializer = CourseSkillSerializer(course_data, many=True)
        return course_serializer.data  

class SkillLeaningPathDetailsSerializer(AppReadOnlyModelSerializer):
    learning_path = serializers.SerializerMethodField()
    class Meta:
        model = Skill
        fields = ['learning_path']

    def get_learning_path(self, obj):
        learning_path_data = LearningPath.objects.filter(skills__in=[obj.id], is_private_course=False).distinct()[:6]
        learning_path_serializer = LeaningPathSkillSerializer(learning_path_data, many=True)
        return learning_path_serializer.data
    
class SkillCertificationPathDetailsSerializer(AppReadOnlyModelSerializer):
    advanced_learning_path = serializers.SerializerMethodField() 

    class Meta:
        model = Skill
        fields = ['advanced_learning_path']
   
    def get_advanced_learning_path(self, obj):
        certificate_path_data = CertificationPath.objects.filter(skills__in=[obj.id], is_private_course=False).distinct()[:6]
        certificate_path_serializer = CertificationPathSkillSerializer(certificate_path_data, many=True)
        return certificate_path_serializer.data
# Course Bulk Details List
class CourseUUIDListSerializer(serializers.Serializer):
    # To get the uuids list from payload
    course_uuids = serializers.ListField(child=serializers.UUIDField())

class CourseBulkDetailSerializer(AppReadOnlyModelSerializer):
    tags = get_app_read_only_serializer(Tag, meta_fields="__all__")(many=True)
    skills = get_app_read_only_serializer(Skill, meta_fields="__all__")(many=True)
    categories = get_app_read_only_serializer(Category, meta_fields="__all__")(many=True)
    image = get_app_read_only_serializer(CourseImage, meta_fields="__all__")()

    class Meta(AppReadOnlyModelSerializer.Meta):
            fields = '__all__'
            model = Course
# Blended Learning Path
class BlendedLearningPathCourseSerializer(AppReadOnlyModelSerializer):
    """This serializer contains configuration for BlendedLearningPath."""

    course = CourseSerializerWithExclusion()
    # is_in_wishlist = serializers.SerializerMethodField()
    # is_in_cart = serializers.SerializerMethodField()

    class Meta:
        model = BlendedLearningClassroomAndVirtualDetails
        fields = "__all__"
        ordering = ["-position"]

    # def get_is_in_wishlist(self, obj):
    #     """This function used to get Blended Learning Path is already in wishlist or not"""
    #     user = self.get_user()
    #     if isinstance(user, AnonymousUser):
    #         return False
    #     else:
    #         is_in_wishlist = BlendedLearningPathWishlist.objects.filter(
    #             entity_id=obj.id, created_by=user
    #         ).exists()
    #         return is_in_wishlist

    # def get_is_in_cart(self, obj):
    #     """This function used to get Blended Learning Path is already in cart or not"""
    #     user = self.get_user()
    #     if isinstance(user, AnonymousUser):
    #         return False
    #     else:
    #         is_in_cart = BlendedLearningPathAddToCart.objects.filter(
    #             entity_id=obj.id, created_by=user
    #         ).exists()
    #         return is_in_cart

class YouMayAlsoLikeBlendedLearningPathSerializer(AppReadOnlyModelSerializer):

    class Meta:
        fields = "__all__"
        model = BlendedLearningPath


class BlendedLearningPathSerializer(AppReadOnlyModelSerializer):
    """This serializer contains configuration for Blended Learning Path."""

    image = get_app_read_only_serializer(
        BlendedLearningPathImage, meta_fields="__all__"
    )()
    skills = get_app_read_only_serializer(Skill, meta_fields="__all__")(many=True)
    learning_path_category = get_app_read_only_serializer(Category, meta_fields="__all__")(
        many=True
    )
    blended_learning_path_courses = BlendedLearningPathCourseSerializer(
        source="related_blended_learning_path_courses", many=True
    )
    is_in_wishlist = serializers.SerializerMethodField()
    is_in_cart = serializers.SerializerMethodField()
    is_in_buy = serializers.SerializerMethodField()
    you_may_also_like = serializers.SerializerMethodField()

    class Meta:
        model = BlendedLearningPath
        fields = "__all__"

    def get_you_may_also_like(self, obj):
        blp_data = BlendedLearningPath.objects.filter(skills__in=obj.skills.values_list("id", flat=True)).distinct()[:4]
        blp_serializer = YouMayAlsoLikeBlendedLearningPathSerializer(blp_data, many=True)
        return blp_serializer.data

    def get_is_in_wishlist(self, obj):
        """This function used to get Blended Learning Path is already in wishlist or not"""
        user = self.get_user()
        if isinstance(user, AnonymousUser) or user == None:
            return False
        else:
            is_in_wishlist = BlendedLearningPathWishlist.objects.filter(
                entity_id=obj.id, created_by=user
            ).exists()
            return is_in_wishlist

    def get_is_in_cart(self, obj):
        """This function used to get Blended Learning Path is already in cart or not"""
        user = self.get_user()
        if isinstance(user, AnonymousUser) or user == None:
            return False
        else:
            is_in_cart = BlendedLearningPathAddToCart.objects.filter(
                entity_id=obj.id, created_by=user
            ).exists()
            return is_in_cart
        
    def get_is_in_buy(self, obj):
        """This function used to get course is already in buy or not"""
        # auth_user = self.get_user()
        user = self.get_user()
        if isinstance(user, AnonymousUser) or user == None:
            return False
        # elif auth_user.user_role:
        #     if auth_user.user_role.identity == "Student":
        #         is_in_buy = StudentEnrolledCourseTracker.objects.filter(entity_id=obj.id, created_by=user).exists()
        #         return is_in_buy
        #     else:
        #         is_buy = UserBlendedLearningPathTracker.objects.filter(entity_id=obj.id, created_by=user).exists()
        #         return is_buy
        else:
            is_buy = UserBlendedLearningPathTracker.objects.filter(entity__blended_learning_id=obj.id, created_by=user).exists()
            return is_buy
        
class BlendedLearningPathPriceDetailsSerializer(AppReadOnlyModelSerializer):
    """This serializer contains configuration for Blended Learning Path Price Details."""

    blending_learning = get_app_read_only_serializer(
        BlendedLearningPath, meta_fields=["id", "uuid", "identity"]
    )()
    mode = get_app_read_only_serializer(BlendedLearningPathCourseMode, meta_fields=["id", "uuid", "identity"])(
        many=True
    )
    class Meta:
        model = BlendedLearningPathPriceDetails
        fields = ["id", "uuid", "blending_learning", "mode", "self_paced_fee", "online_fee", "classroom_fee"]
        
class BlendedLearningPathScheduleDetailsSerializer(AppModelSerializer):
    """serialzer for BLP schedule details"""
    price_details = serializers.SerializerMethodField()
    address = serializers.SerializerMethodField()
    class Meta:
        model = BlendedLearningPathScheduleDetails
        fields = ['id','mentor','start_date','end_date','start_time','end_time','virtual_url','address','price_details','duration','is_day_batch','mode','is_weekend_batch','filling_fast']
        
    def get_price_details(self, obj):
        if obj.mode and obj.mode.identity == "Online instructor led training":
            price_detail = BlendedLearningPathPriceDetails.objects.filter(schedule_details__in=[obj], mode__identity="Online instructor led training").first()
            return {
                "actual_fee":price_detail.online_actual_fee,
                "discount_rate":price_detail.online_discount_rate,
                "discounted_fee":price_detail.online_discounted_fee,
                "blended_learning":price_detail.blended_learning.identity,
            }
        elif obj.mode and obj.mode.identity == "Classroom training":
            price_detail = BlendedLearningPathPriceDetails.objects.filter(schedule_details__in=[obj], mode__identity="Classroom training").first()
            return {
                "actual_fee":price_detail.classroom_actual_fee,
                "discount_rate":price_detail.classroom_discount_rate,
                "discounted_fee":price_detail.classroom_discounted_fee,
                "blended_learning":price_detail.blended_learning.identity,
            }
        else:
            return None
        
    def get_address(self, obj):
        if obj.address:
            return f"{str(obj.address.identity).capitalize()}-{str(obj.address.city.identity).capitalize()}"
        return None