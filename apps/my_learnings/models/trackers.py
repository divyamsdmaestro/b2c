from datetime import datetime

from django.db import models

from apps.common.models import COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG, BaseModel, COMMON_CHAR_FIELD_MAX_LENGTH
from apps.learning.models.certification_path import CertificationPath
from apps.learning.models.course import Course
from apps.learning.models.learning_path import LearningPath
from apps.web_portal.models.notification import Notification
from apps.ecash.reward_points import trigger_reward_points
from apps.cms.celery import shared_task
class UserMMLCourseTracker(BaseModel):
    """
    Model used to track the progress of user under a given mml course.
    The `created_by` column is used to hold the user.

    This is created when the user purchases the course.
    """

    entity = models.ForeignKey(to="learning.MMLCourse", on_delete=models.CASCADE)

    valid_till = models.DateField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)

    last_accessed_on = models.DateTimeField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)

    # saved in percentage | ranges 0 - 100
    progress = models.IntegerField(default=0)

    institute = models.ForeignKey(to="access.InstitutionDetail",
                                  on_delete=models.SET_NULL,
                                  **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    
    started_on = models.DateTimeField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    completed_on = models.DateTimeField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)

    def handle_started_learning(self):
        """Handles the fact that user has opened and started learning."""

        self.last_accessed_on = datetime.now()
        if self.started_on is None:
            self.started_on =  datetime.now()
        if self.progress is None:
            self.progress = 100
            notification = Notification(
                    user=self.created_by,
                    message="You have successfully completed the MML course: " + self.entity.identity,
                    course=self.entity,
                    purpose="completed"
                )
            notification.save()
        self.save()
        
class UserCourseTracker(BaseModel):
    """
    Model used to track the progress of user under a given course.
    The `created_by` column is used to hold the user.

    This is created when the user purchases the course.
    """

    entity = models.ForeignKey(to="learning.Course", on_delete=models.CASCADE)

    valid_till = models.DateField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)

    last_accessed_on = models.DateTimeField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)

    # saved in percentage | ranges 0 - 100
    progress = models.IntegerField(default=0)

    institute = models.ForeignKey(to="access.InstitutionDetail",
                                  on_delete=models.SET_NULL,
                                  **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    
    started_on = models.DateTimeField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    completed_on = models.DateTimeField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
     
    def handle_started_learning(self):
        """Handles the fact that user has opened and started learning."""

        self.last_accessed_on = datetime.now()
        if self.started_on is None:
            self.started_on =  datetime.now()
        self.save()

    def handle_user_enrolled(self):
        """Handles the chain reaction that user has enrolled to a course."""

        kwargs = {"parent_tracker": self, "created_by": self.created_by}

        from apps.learning.models import CourseModule
       
        for module in CourseModule.objects.filter(course=self.entity):
            UserCourseModuleTracker.objects.filter(entity=module, **kwargs).delete()

            tracker = UserCourseModuleTracker.objects.create(entity=module, **kwargs)

            # chain of responsibility
            tracker.handle_user_enrolled()

    def handle_child_modified(self):
        """Chain of responsibility from the bottom up."""

        self.progress = (
            UserCourseModuleTracker.objects.filter(
                parent_tracker=self, progress__gt=0
            ).count()
            / UserCourseModuleTracker.objects.filter(parent_tracker=self).count()
        ) * 100
        if self.completed_on is None and self.progress == 100:
            self.completed_on =  datetime.now()
            #trigger reward points on course completion
            trigger_reward_points(self.created_by,action="course completed")
            notification = Notification(
                    user=self.created_by,
                    message="You have successfully completed the course: " + self.entity.identity,
                    course=self.entity,
                    purpose="completed"
                )
            notification.save()
        # print(self.progress)
        # breakpoint() 
        self.save()
        

class UserCourseModuleTracker(BaseModel):
    """Tracker for a `CourseModule` under a `UserCourseTracker` and a `User`."""

    # module
    entity = models.ForeignKey(to="learning.CourseModule", on_delete=models.CASCADE)

    # parents
    parent_tracker = models.ForeignKey(to=UserCourseTracker, on_delete=models.CASCADE)

    # run time calculated
    progress = models.IntegerField(default=0)

    def handle_child_modified(self):
        """Chain of responsibility from the bottom up."""

        self.progress = (
            UserCourseSubModuleTracker.objects.filter(
                parent_tracker=self, progress=100
            ).count()
            / UserCourseSubModuleTracker.objects.filter(parent_tracker=self).count()
        ) * 100
        self.save()
        
        # chain of responsibility
        self.parent_tracker.handle_child_modified()

    def handle_user_enrolled(self):
        """Chain of responsibility."""

        kwargs = {"parent_tracker": self, "created_by": self.created_by}

        from apps.learning.models import CourseSubModule
        for sub_module in CourseSubModule.objects.filter(module=self.entity):
            UserCourseSubModuleTracker.objects.filter(
                entity=sub_module, **kwargs
            ).delete()

            tracker = UserCourseSubModuleTracker.objects.create(
                entity=sub_module, **kwargs
            )

            # chain of responsibility
            tracker.handle_user_enrolled()


class UserCourseSubModuleTracker(BaseModel):
    """Tracker for a `CourseSubModule` under a `UserCourseModuleTracker` and `User`."""

    # sub-module
    entity = models.ForeignKey(to="learning.CourseSubModule", on_delete=models.CASCADE)

    # parents
    parent_tracker = models.ForeignKey(
        to=UserCourseModuleTracker, on_delete=models.CASCADE
    )

    # run time calculated
    progress = models.IntegerField(default=0)

   

    def handle_user_enrolled(self):
        """Chain of responsibility."""

        pass

    def handle_viewed(self):
        """Handles the fact that the user has viewed the tracker."""

        self.progress = 100
        self.save()

        # chain of responsibility
        self.parent_tracker.handle_child_modified()


# Learning Path Course Trackers
class UserLearningPathTracker(BaseModel):
    """
    Model used to track the progress of user under a given learning path course.
    The `created_by` column is used to hold the user.

    This is created when the user purchases the lp course.
    """

    entity = models.ForeignKey(to="learning.learningpath", on_delete=models.CASCADE)

    valid_till = models.DateField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)

    last_accessed_on = models.DateTimeField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)

    # saved in percentage | ranges 0 - 100
    progress = models.IntegerField(default=0)

    institute = models.ForeignKey(to="access.InstitutionDetail",
                                  on_delete=models.SET_NULL,
                                  **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)

    def handle_started_learning(self):
        """Handles the fact that user has opened and started learning."""

        self.last_accessed_on = datetime.now()
        self.save()

    def handle_user_enrolled(self):
        """Handles the chain reaction that user has enrolled to a course."""
        
        kwargs = {"parent_tracker": self, "created_by": self.created_by}

        from apps.learning.models import LearningPathCourse
        for module in LearningPathCourse.objects.filter(learning_path=self.entity):
           
            UserLearningPathCourseTracker.objects.filter(entity=module.course, **kwargs).delete()
            
            tracker = UserLearningPathCourseTracker.objects.create(entity=module.course, **kwargs)
            # chain of responsibility
            tracker.handle_user_enrolled()


    def handle_child_modified(self):
        """Chain of responsibility from the bottom up."""

        self.progress = (
            UserLearningPathCourseTracker.objects.filter(
                parent_tracker=self, progress__gt=0
            ).count()
            / UserLearningPathCourseTracker.objects.filter(parent_tracker=self).count()
        ) * 100
        if self.progress == 100:
            notification = Notification(
                    user=self.created_by,
                    message="You have successfully completed the course: " + self.entity.identity,
                    learning_path=self.entity,
                    purpose="completed"
                )
            notification.save()
        self.save()


class UserLearningPathCourseTracker(BaseModel):
    """
    Model used to track the progress of user under a given learning path course.
    The `created_by` column is used to hold the user.

    This is created when the user purchases the lp course.
    """

    entity = models.ForeignKey(to="learning.Course", on_delete=models.CASCADE)

    valid_till = models.DateField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)

    last_accessed_on = models.DateTimeField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    
    # parents
    parent_tracker = models.ForeignKey(to=UserLearningPathTracker, on_delete=models.CASCADE, null=True)

    # saved in percentage | ranges 0 - 100
    progress = models.IntegerField(default=0)

    institute = models.ForeignKey(to="access.InstitutionDetail",
                                  on_delete=models.SET_NULL,
                                  **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)

    def handle_child_modified(self):
        """Chain of responsibility from the bottom up."""

        self.progress = (
            UserLearningPathCourseModuleTracker.objects.filter(
                parent_tracker=self, progress=100
            ).count()
            / UserLearningPathCourseModuleTracker.objects.filter(parent_tracker=self).count()
        ) * 100
        self.save()

        # chain of responsibility
        self.parent_tracker.handle_child_modified()

    def handle_user_enrolled(self):
        """Chain of responsibility."""

        kwargs = {"parent_tracker": self, "created_by": self.created_by}

        from apps.learning.models import CourseModule
        for module in CourseModule.objects.filter(course=self.entity):
            print(module)
            UserLearningPathCourseModuleTracker.objects.filter(entity=module, **kwargs).delete()

            tracker = UserLearningPathCourseModuleTracker.objects.create(entity=module, **kwargs)
            # chain of responsibility
            tracker.handle_user_enrolled()

   
class UserLearningPathCourseModuleTracker(BaseModel):
    """Tracker for a `CourseModule` under a `UserLearningPathCourseTracker` and a `User`."""

    # module
    entity = models.ForeignKey(to="learning.CourseModule", on_delete=models.CASCADE)

    # parents
    parent_tracker = models.ForeignKey(to=UserLearningPathCourseTracker, on_delete=models.CASCADE)

    # run time calculated
    progress = models.IntegerField(default=0)

    def handle_child_modified(self):
        """Chain of responsibility from the bottom up."""

        self.progress = (
            UserLearningPathCourseSubModuleTracker.objects.filter(
                parent_tracker=self, progress=100
            ).count()
            / UserLearningPathCourseSubModuleTracker.objects.filter(parent_tracker=self).count()
        ) * 100
        self.save()

        # chain of responsibility
        self.parent_tracker.handle_child_modified()

    def handle_user_enrolled(self):
        """Chain of responsibility."""

        kwargs = {"parent_tracker": self, "created_by": self.created_by}

        from apps.learning.models import CourseSubModule
        for sub_module in CourseSubModule.objects.filter(module=self.entity):
            print(sub_module)
            UserLearningPathCourseSubModuleTracker.objects.filter(
                entity=sub_module, **kwargs
            ).delete()

            tracker = UserLearningPathCourseSubModuleTracker.objects.create(
                entity=sub_module, **kwargs
            )
            # chain of responsibility
            tracker.handle_user_enrolled()

class UserLearningPathCourseSubModuleTracker(BaseModel):
    """Tracker for a `CourseSubModule` under a `UserLearningPathCourseModuleTracker` and `User`."""

    # sub-module
    entity = models.ForeignKey(to="learning.CourseSubModule", on_delete=models.CASCADE)

    # parents
    parent_tracker = models.ForeignKey(
        to=UserLearningPathCourseModuleTracker, on_delete=models.CASCADE
    )

    # run time calculated
    progress = models.IntegerField(default=0)

    def handle_user_enrolled(self):
        """Chain of responsibility."""

        pass

    def handle_viewed(self):
        """Handles the fact that the user has viewed the tracker."""

        self.progress = 100
        self.save()

        # chain of responsibility
        self.parent_tracker.handle_child_modified()

# Advanced Learning Path Course Trackers (certificate path Trackers)
class UserCertificatePathTracker(BaseModel):
    """
    Model used to track the progress of user under a given certificate path learning path course.
    The `created_by` column is used to hold the user.

    This is created when the user purchases the certificate path learning path course.
    """

    entity = models.ForeignKey(to="learning.CertificationPath", on_delete=models.CASCADE)

    valid_till = models.DateField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)

    last_accessed_on = models.DateTimeField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)

    # saved in percentage | ranges 0 - 100
    progress = models.IntegerField(default=0)

    institute = models.ForeignKey(to="access.InstitutionDetail",
                                  on_delete=models.SET_NULL,
                                  **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)

    def handle_started_learning(self):
        """Handles the fact that user has opened and started learning."""

        self.last_accessed_on = datetime.now()
        self.save()

    def handle_user_enrolled(self):
        """Handles the chain reaction that user has enrolled to a course."""

        kwargs = {"parent_tracker": self, "created_by": self.created_by}

        from apps.learning.models import CertificationPathLearningPath

        for module in CertificationPathLearningPath.objects.filter(certification_path=self.entity):
            UserCertificatePathLearningPathCourseTracker.objects.filter(entity=module.learning_path, **kwargs).delete()

            tracker = UserCertificatePathLearningPathCourseTracker.objects.create(entity=module.learning_path, **kwargs)

            # chain of responsibility
            tracker.handle_user_enrolled()

    def handle_child_modified(self):
        """Chain of responsibility from the bottom up."""

        self.progress = (
            UserCertificatePathLearningPathCourseTracker.objects.filter(
                parent_tracker=self, progress__gt=0
            ).count()
            / UserCertificatePathLearningPathCourseTracker.objects.filter(parent_tracker=self).count()
        ) * 100

        if self.progress == 100:
            notification = Notification(
                    user=self.created_by,
                    message="You have successfully completed the course: " + self.entity.identity,
                    certification_path=self.entity,
                    purpose="completed"
                )
            notification.save()
        self.save()


class UserCertificatePathLearningPathCourseTracker(BaseModel):
    """
    Model used to track the progress of user under a given certificate path learning path course.
    The `created_by` column is used to hold the user.

    This is created when the user purchases the certificate path learning path course.
    """

    entity = models.ForeignKey(to="learning.learningpath", on_delete=models.CASCADE)

    valid_till = models.DateField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)

    last_accessed_on = models.DateTimeField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    
    # parents
    parent_tracker = models.ForeignKey(to=UserCertificatePathTracker, on_delete=models.CASCADE, null=True)

    # saved in percentage | ranges 0 - 100
    progress = models.IntegerField(default=0)

    institute = models.ForeignKey(to="access.InstitutionDetail",
                                  on_delete=models.SET_NULL,
                                  **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)

    def handle_started_learning(self):
        """Handles the fact that user has opened and started learning."""

        self.last_accessed_on = datetime.now()
        self.save()

    def handle_user_enrolled(self):
        """Handles the chain reaction that user has enrolled to a course."""

        kwargs = {"parent_tracker": self, "created_by": self.created_by}

        from apps.learning.models import LearningPathCourse

        for module in LearningPathCourse.objects.filter(learning_path=self.entity):

            UserCertificatePathCourseTracker.objects.filter(entity=module.course, **kwargs).delete()

            tracker = UserCertificatePathCourseTracker.objects.create(entity=module.course, **kwargs)
            
            # chain of responsibility
            tracker.handle_user_enrolled()

    def handle_child_modified(self):
        """Chain of responsibility from the bottom up."""

        self.progress = (
            UserCertificatePathCourseTracker.objects.filter(
                parent_tracker=self, progress=100
            ).count()
            / UserCertificatePathCourseTracker.objects.filter(parent_tracker=self).count()
        ) * 100
        self.save()

class UserCertificatePathCourseTracker(BaseModel):
    """
    Model used to track the progress of user under a given certificate path course.
    The `created_by` column is used to hold the user. 

    This is created when the user purchases the certificate path course.
    """

    entity = models.ForeignKey(to="learning.Course", on_delete=models.CASCADE)

    valid_till = models.DateField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)

    last_accessed_on = models.DateTimeField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)

    # parents
    parent_tracker = models.ForeignKey(to=UserCertificatePathLearningPathCourseTracker, on_delete=models.CASCADE, null=True)

    # saved in percentage | ranges 0 - 100
    progress = models.IntegerField(default=0)

    institute = models.ForeignKey(to="access.InstitutionDetail",
                                  on_delete=models.SET_NULL,
                                  **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)

    def handle_started_learning(self):
        """Handles the fact that user has opened and started learning."""

        self.last_accessed_on = datetime.now()
        self.save()

    def handle_user_enrolled(self):
        """Handles the chain reaction that user has enrolled to a course."""

        kwargs = {"parent_tracker": self, "created_by": self.created_by}

        from apps.learning.models import CourseModule

        for module in CourseModule.objects.filter(course=self.entity):
            UserCertificatePathCourseModuleTracker.objects.filter(entity=module, **kwargs).delete()

            tracker = UserCertificatePathCourseModuleTracker.objects.create(entity=module, **kwargs)

            # chain of responsibility
            tracker.handle_user_enrolled()

    def handle_child_modified(self):
        """Chain of responsibility from the bottom up."""

        self.progress = (
            UserCertificatePathCourseModuleTracker.objects.filter(
                parent_tracker=self, progress=100
            ).count()
            / UserCertificatePathCourseModuleTracker.objects.filter(parent_tracker=self).count()
        ) * 100
        self.save()
    
class UserCertificatePathCourseModuleTracker(BaseModel):
    """Tracker for a `CourseModule` under a `UserCertificatePathCourseTracker` and a `User`."""

    # module
    entity = models.ForeignKey(to="learning.CourseModule", on_delete=models.CASCADE)

    # parents
    parent_tracker = models.ForeignKey(to=UserCertificatePathCourseTracker, on_delete=models.CASCADE, null=True)

    # run time calculated
    progress = models.IntegerField(default=0)

    def handle_child_modified(self):
        """Chain of responsibility from the bottom up."""

        self.progress = (
            UserCertificatePathCourseSubModuleTracker.objects.filter(
                parent_tracker=self, progress=100
            ).count()
            / UserCertificatePathCourseSubModuleTracker.objects.filter(parent_tracker=self).count()
        ) * 100
        self.save()

        # chain of responsibility
        self.parent_tracker.handle_child_modified()

    def handle_user_enrolled(self):
        """Chain of responsibility."""

        kwargs = {"parent_tracker": self, "created_by": self.created_by}

        from apps.learning.models import CourseSubModule

        for sub_module in CourseSubModule.objects.filter(module=self.entity):
            UserCertificatePathCourseSubModuleTracker.objects.filter(
                entity=sub_module, **kwargs
            ).delete()

            tracker = UserCertificatePathCourseSubModuleTracker.objects.create(
                entity=sub_module, **kwargs
            )

            # chain of responsibility
            tracker.handle_user_enrolled()

class UserCertificatePathCourseSubModuleTracker(BaseModel):
    """Tracker for a `CourseSubModule` under a `UserCertificatePathCourseModuleTracker` and `User`."""

    # sub-module
    entity = models.ForeignKey(to="learning.CourseSubModule", on_delete=models.CASCADE)

    # parents
    parent_tracker = models.ForeignKey(
        to=UserCertificatePathCourseModuleTracker, on_delete=models.CASCADE, null=True
    )

    # run time calculated
    progress = models.IntegerField(default=0)

    def handle_user_enrolled(self):
        """Chain of responsibility."""

        pass

    def handle_viewed(self):
        """Handles the fact that the user has viewed the tracker."""

        self.progress = 100
        self.save()

        # chain of responsibility
        self.parent_tracker.handle_child_modified()

#Subscription Plan
class UserSubscriptionPlanTracker(BaseModel):
    """
    Model used to track the progress of user under a given learning path course.
    The `created_by` column is used to hold the user.

    This is created when the user purchases the lp course.
    """

    entity = models.ForeignKey(to="payments.SubscriptionPlan", on_delete=models.CASCADE)

    valid_till = models.DateField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)

    last_accessed_on = models.DateTimeField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)

    # saved in percentage | ranges 0 - 100
    progress = models.IntegerField(default=0)

    institute = models.ForeignKey(to="access.InstitutionDetail",
                                  on_delete=models.SET_NULL,
                                  **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)

    def handle_started_learning(self):
        """Handles the fact that user has opened and started learning."""

        self.last_accessed_on = datetime.now()
        self.save()

    def handle_user_enrolled(self):
        """Handles the chain reaction that user has enrolled to a course."""
        
        kwargs = {"parent_tracker": self, "created_by": self.created_by}

        from apps.payments.models import SubscriptionPlan
         # Get the IDs of existing trackers to delete
        courses = self.entity.courses.all()

        existing_tracker_ids = UserSubscriptionPlanCourseTracker.objects.filter(
            entity__in=courses, **kwargs
        ).values_list('id', flat=True)

        # Delete existing trackers
        UserSubscriptionPlanCourseTracker.objects.filter(id__in=existing_tracker_ids).delete()

        # Create a list of UserSubscriptionPlanCourseTracker instances to be created
        trackers_to_create = [
            UserSubscriptionPlanCourseTracker(entity=course, **kwargs)
            for course in courses
        ]
        # Use bulk_create to create the instances in a single query
        created_trackers = UserSubscriptionPlanCourseTracker.objects.bulk_create(trackers_to_create)

        # Call handle_user_enrolled method for each created tracker
        for tracker in created_trackers:
            tracker.handle_user_enrolled()

        lps = self.entity.learning_paths.all()
        existing_tracker_ids = UserSubscriptionPlanLearningPathTracker.objects.filter(
            entity__in=lps, **kwargs
        ).values_list('id', flat=True)

        # Delete existing trackers
        UserSubscriptionPlanLearningPathTracker.objects.filter(id__in=existing_tracker_ids).delete()

        # Create a list of UserSubscriptionPlanLearningPathTracker instances to be created
        trackers_to_create = [
            UserSubscriptionPlanLearningPathTracker(entity=lp, **kwargs)
            for lp in lps
        ]
        # Use bulk_create to create the instances in a single query
        created_trackers = UserSubscriptionPlanLearningPathTracker.objects.bulk_create(trackers_to_create)

        # Call handle_user_enrolled method for each created tracker
        for tracker in created_trackers:
            tracker.handle_user_enrolled()

        alps = self.entity.certification_paths.all()
        existing_tracker_ids = UserSubscriptionPlanCertificatePathTracker.objects.filter(
            entity__in=alps, **kwargs
        ).values_list('id', flat=True)

        # Delete existing trackers
        UserSubscriptionPlanCertificatePathTracker.objects.filter(id__in=existing_tracker_ids).delete()

        # Create a list of UserSubscriptionPlanCertificatePathTracker instances to be created
        trackers_to_create = [
            UserSubscriptionPlanCertificatePathTracker(entity=alp, **kwargs)
            for alp in alps
        ]
        # Use bulk_create to create the instances in a single query
        created_trackers = UserSubscriptionPlanCertificatePathTracker.objects.bulk_create(trackers_to_create)

        # Call handle_user_enrolled method for each created tracker
        for tracker in created_trackers:
            tracker.handle_user_enrolled()
       
    def handle_child_modified(self):
        """Chain of responsibility from the bottom up."""

        self.progress = (
            UserSubscriptionPlanCourseTracker.objects.filter(
                parent_tracker=self, progress__gt=0
            ).count()
            / UserSubscriptionPlanCourseTracker.objects.filter(parent_tracker=self).count()
        ) * 100
        self.save()


class UserSubscriptionPlanCourseTracker(BaseModel):
    """
    Model used to track the progress of user under a given learning path course.
    The `created_by` column is used to hold the user.

    This is created when the user purchases the lp course.
    """

    entity = models.ForeignKey(to="learning.Course", on_delete=models.CASCADE)

    valid_till = models.DateField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)

    last_accessed_on = models.DateTimeField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    
    # parents
    parent_tracker = models.ForeignKey(to=UserSubscriptionPlanTracker, on_delete=models.CASCADE, null=True)

    # saved in percentage | ranges 0 - 100
    progress = models.IntegerField(default=0)

    institute = models.ForeignKey(to="access.InstitutionDetail",
                                  on_delete=models.SET_NULL,
                                  **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)

    def handle_child_modified(self):
        """Chain of responsibility from the bottom up."""

        self.progress = (
            UserSubscriptionPlanCourseModuleTracker.objects.filter(
                parent_tracker=self, progress=100
            ).count()
            / UserSubscriptionPlanCourseModuleTracker.objects.filter(parent_tracker=self).count()
        ) * 100
        self.save()

        # chain of responsibility
        self.parent_tracker.handle_child_modified()

    def handle_user_enrolled(self):
        """Chain of responsibility."""
        kwargs = {"created_by": self.created_by}

        from apps.learning.models import CourseModule
        from django.db import transaction

        course_modules = CourseModule.objects.filter(course=self.entity)

        # Fetch existing trackers to delete
        existing_tracker_ids = UserSubscriptionPlanCourseModuleTracker.objects.filter(
            entity__in=course_modules, parent_tracker=self, **kwargs
        ).values_list('id', flat=True)

        # Delete existing trackers
        UserSubscriptionPlanCourseModuleTracker.objects.filter(id__in=existing_tracker_ids).delete()
         # Check if the parent tracker exists
        try:
            parent_tracker = UserSubscriptionPlanCourseTracker.objects.get(entity=self.entity,parent_tracker=self.parent_tracker,created_by=self.created_by)
        except UserSubscriptionPlanCourseTracker.DoesNotExist:
            parent_tracker = UserSubscriptionPlanCourseTracker.objects.create(entity=self.entity, created_by=self.created_by)
        # Check if the parent tracker exists
        course_modules_to_create = [
            UserSubscriptionPlanCourseModuleTracker(entity=module, parent_tracker=parent_tracker, **kwargs)
            for module in course_modules
        ]
        
        batch_size = 200  # Set an appropriate batch size
        num_modules = len(course_modules_to_create)
        with transaction.atomic():
            for i in range(0, num_modules, batch_size):
                # Calculate the end index of the current batch
                end_index = min(i + batch_size, num_modules)
                # Create instances for the current batch
                for tracker in course_modules_to_create[i:end_index]:
                    tracker.save()
                    tracker.handle_user_enrolled()
   
class UserSubscriptionPlanCourseModuleTracker(BaseModel):
    """Tracker for a `CourseModule` under a `UserSubscriptionPlanTracker` and a `User`."""

    # module
    entity = models.ForeignKey(to="learning.CourseModule", on_delete=models.CASCADE)

    # parents
    parent_tracker = models.ForeignKey(to=UserSubscriptionPlanCourseTracker, on_delete=models.CASCADE)

    # run time calculated
    progress = models.IntegerField(default=0)

    def handle_child_modified(self):
        """Chain of responsibility from the bottom up."""

        self.progress = (
            UserSubscriptionPlanCourseSubModuleTracker.objects.filter(
                parent_tracker=self, progress=100
            ).count()
            / UserSubscriptionPlanCourseSubModuleTracker.objects.filter(parent_tracker=self).count()
        ) * 100
        self.save()

        # chain of responsibility
        self.parent_tracker.handle_child_modified()

    def handle_user_enrolled(self):
        """Chain of responsibility."""

        kwargs = {"created_by": self.created_by}

        from apps.learning.models import CourseSubModule
        from django.db import transaction

        # Fetch all CourseSubModule objects related to the CourseModule
        sub_modules = CourseSubModule.objects.filter(module=self.entity)
        # Fetch existing trackers to delete
        existing_tracker_ids = UserSubscriptionPlanCourseSubModuleTracker.objects.filter(
            entity__in=sub_modules, parent_tracker=self, **kwargs
        ).values_list('id', flat=True)

        # Delete existing trackers
        UserSubscriptionPlanCourseSubModuleTracker.objects.filter(id__in=existing_tracker_ids).delete()
         # Check if the parent tracker exists
        try:
            parent_tracker = UserSubscriptionPlanCourseModuleTracker.objects.get(entity=self.entity,parent_tracker=self.parent_tracker,created_by=self.created_by)
        except UserSubscriptionPlanCourseModuleTracker.DoesNotExist:
            parent_tracker = UserSubscriptionPlanCourseModuleTracker.objects.create(entity=self.entity, created_by=self.created_by)
        # Check if the parent tracker exists
        course_sub_modules_to_create = [
            UserSubscriptionPlanCourseSubModuleTracker(entity=module, parent_tracker=parent_tracker, **kwargs)
            for module in sub_modules
        ]
        
        batch_size = 200  # Set an appropriate batch size
        num_modules = len(course_sub_modules_to_create)
        with transaction.atomic():
            for i in range(0, num_modules, batch_size):
                # Calculate the end index of the current batch
                end_index = min(i + batch_size, num_modules)
                # Create instances for the current batch
                for tracker in course_sub_modules_to_create[i:end_index]:
                    tracker.save()
                    tracker.handle_user_enrolled()


class UserSubscriptionPlanCourseSubModuleTracker(BaseModel):
    """Tracker for a `CourseSubModule` under a `UserSubscriptionPlanCourseModuleTracker` and `User`."""

    # sub-module
    entity = models.ForeignKey(to="learning.CourseSubModule", on_delete=models.CASCADE)

    # parents
    parent_tracker = models.ForeignKey(
        to=UserSubscriptionPlanCourseModuleTracker, on_delete=models.CASCADE
    )

    # run time calculated
    progress = models.IntegerField(default=0)

    def handle_user_enrolled(self):
        """Chain of responsibility."""

        pass

    def handle_viewed(self):
        """Handles the fact that the user has viewed the tracker."""

        self.progress = 100
        self.save()

        # chain of responsibility
        self.parent_tracker.handle_child_modified()

# Learning Path Course Trackers
class UserSubscriptionPlanLearningPathTracker(BaseModel):
    """
    Model used to track the progress of user under a given learning path course.
    The `created_by` column is used to hold the user.

    This is created when the user purchases the lp course.
    """

    entity = models.ForeignKey(to="learning.learningpath", on_delete=models.CASCADE)

    valid_till = models.DateField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)

    last_accessed_on = models.DateTimeField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)

    # parents
    parent_tracker = models.ForeignKey(to=UserSubscriptionPlanTracker, on_delete=models.CASCADE, null=True)

    # saved in percentage | ranges 0 - 100
    progress = models.IntegerField(default=0)

    institute = models.ForeignKey(to="access.InstitutionDetail",
                                  on_delete=models.SET_NULL,
                                  **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)

    def handle_started_learning(self):
        """Handles the fact that user has opened and started learning."""

        self.last_accessed_on = datetime.now()
        self.save()

    def handle_user_enrolled(self):
        """Handles the chain reaction that user has enrolled to a course."""
        
        kwargs = {"created_by": self.created_by}

        from apps.learning.models import LearningPathCourse
        from django.db import transaction

        lp_courses = LearningPathCourse.objects.filter(learning_path=self.entity)

        # Fetch existing trackers to delete
        existing_tracker_ids = UserSubscriptionPlanLearningPathCourseTracker.objects.filter(
            entity__in=lp_courses, parent_tracker=self, **kwargs
        ).values_list('id', flat=True)

        # Delete existing trackers
        UserSubscriptionPlanLearningPathCourseTracker.objects.filter(id__in=existing_tracker_ids).delete()
         # Check if the parent tracker exists
        try:
            parent_tracker = UserSubscriptionPlanLearningPathTracker.objects.get(entity=self.entity,parent_tracker=self.parent_tracker,created_by=self.created_by)
        except UserSubscriptionPlanLearningPathTracker.DoesNotExist:
            parent_tracker = UserSubscriptionPlanLearningPathTracker.objects.create(entity=self.entity, created_by=self.created_by)
        # Check if the parent tracker exists
        course_modules_to_create = [
            UserSubscriptionPlanLearningPathCourseTracker(entity=module, parent_tracker=parent_tracker, **kwargs)
            for module in lp_courses
        ]
        
        batch_size = 200  # Set an appropriate batch size
        num_modules = len(course_modules_to_create)
        with transaction.atomic():
            for i in range(0, num_modules, batch_size):
                # Calculate the end index of the current batch
                end_index = min(i + batch_size, num_modules)
                # Create instances for the current batch
                for tracker in course_modules_to_create[i:end_index]:
                    tracker.save()
                    tracker.handle_user_enrolled()
        # for module in LearningPathCourse.objects.filter(learning_path=self.entity):
           
        #     UserSubscriptionPlanLearningPathCourseTracker.objects.filter(entity=module.course, **kwargs).delete()
            
        #     tracker = UserSubscriptionPlanLearningPathCourseTracker.objects.create(entity=module.course, **kwargs)
        #     # chain of responsibility
        #     tracker.handle_user_enrolled()


    def handle_child_modified(self):
        """Chain of responsibility from the bottom up."""

        self.progress = (
            UserSubscriptionPlanLearningPathCourseTracker.objects.filter(
                parent_tracker=self, progress__gt=0
            ).count()
            / UserSubscriptionPlanLearningPathCourseTracker.objects.filter(parent_tracker=self).count()
        ) * 100
        self.save()


class UserSubscriptionPlanLearningPathCourseTracker(BaseModel):
    """
    Model used to track the progress of user under a given learning path course.
    The `created_by` column is used to hold the user.

    This is created when the user purchases the lp course.
    """

    entity = models.ForeignKey(to="learning.Course", on_delete=models.CASCADE)

    valid_till = models.DateField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)

    last_accessed_on = models.DateTimeField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    
    # parents
    parent_tracker = models.ForeignKey(to=UserSubscriptionPlanLearningPathTracker, on_delete=models.CASCADE, null=True)

    # saved in percentage | ranges 0 - 100
    progress = models.IntegerField(default=0)

    institute = models.ForeignKey(to="access.InstitutionDetail",
                                  on_delete=models.SET_NULL,
                                  **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)

    def handle_child_modified(self):
        """Chain of responsibility from the bottom up."""

        self.progress = (
            UserSubscriptionPlanLearningPathCourseModuleTracker.objects.filter(
                parent_tracker=self, progress=100
            ).count()
            / UserSubscriptionPlanLearningPathCourseModuleTracker.objects.filter(parent_tracker=self).count()
        ) * 100
        self.save()

        # chain of responsibility
        self.parent_tracker.handle_child_modified()

    def handle_user_enrolled(self):
        """Chain of responsibility."""

        kwargs = {"created_by": self.created_by}

        from apps.learning.models import CourseModule
        from django.db import transaction

        lp_course_modules = CourseModule.objects.filter(course=self.entity)

        # Fetch existing trackers to delete
        existing_tracker_ids = UserSubscriptionPlanLearningPathCourseModuleTracker.objects.filter(
            entity__in=lp_course_modules, parent_tracker=self, **kwargs
        ).values_list('id', flat=True)

        # Delete existing trackers
        UserSubscriptionPlanLearningPathCourseModuleTracker.objects.filter(id__in=existing_tracker_ids).delete()
         # Check if the parent tracker exists
        try:
            parent_tracker = UserSubscriptionPlanLearningPathCourseTracker.objects.get(entity=self.entity,parent_tracker=self.parent_tracker,created_by=self.created_by)
        except UserSubscriptionPlanLearningPathCourseTracker.DoesNotExist:
            parent_tracker = UserSubscriptionPlanLearningPathCourseTracker.objects.create(entity=self.entity, created_by=self.created_by)
        # Check if the parent tracker exists
        course_modules_to_create = [
            UserSubscriptionPlanLearningPathCourseModuleTracker(entity=module, parent_tracker=parent_tracker, **kwargs)
            for module in lp_course_modules
        ]
        
        batch_size = 200  # Set an appropriate batch size
        num_modules = len(course_modules_to_create)
        with transaction.atomic():
            for i in range(0, num_modules, batch_size):
                # Calculate the end index of the current batch
                end_index = min(i + batch_size, num_modules)
                # Create instances for the current batch
                for tracker in course_modules_to_create[i:end_index]:
                    tracker.save()
                    tracker.handle_user_enrolled()
        # for module in CourseModule.objects.filter(course=self.entity):
        #     UserSubscriptionPlanLearningPathCourseModuleTracker.objects.filter(entity=module, **kwargs).delete()

        #     tracker = UserSubscriptionPlanLearningPathCourseModuleTracker.objects.create(entity=module, **kwargs)
        #     # chain of responsibility
        #     tracker.handle_user_enrolled()

   
class UserSubscriptionPlanLearningPathCourseModuleTracker(BaseModel):
    """Tracker for a `CourseModule` under a `UserSubscriptionPlanLearningPathCourseTracker` and a `User`."""

    # module
    entity = models.ForeignKey(to="learning.CourseModule", on_delete=models.CASCADE)

    # parents
    parent_tracker = models.ForeignKey(to=UserSubscriptionPlanLearningPathCourseTracker, on_delete=models.CASCADE)

    # run time calculated
    progress = models.IntegerField(default=0)

    def handle_child_modified(self):
        """Chain of responsibility from the bottom up."""

        self.progress = (
            UserSubscriptionPlanLearningPathCourseSubModuleTracker.objects.filter(
                parent_tracker=self, progress=100
            ).count()
            / UserSubscriptionPlanLearningPathCourseSubModuleTracker.objects.filter(parent_tracker=self).count()
        ) * 100
        self.save()

        # chain of responsibility
        self.parent_tracker.handle_child_modified()

    def handle_user_enrolled(self):
        """Chain of responsibility."""

        kwargs = { "created_by": self.created_by}

        from apps.learning.models import CourseSubModule
        from django.db import transaction

        lp_course_modules = CourseSubModule.objects.filter(course=self.entity)

        # Fetch existing trackers to delete
        existing_tracker_ids = UserSubscriptionPlanLearningPathCourseSubModuleTracker.objects.filter(
            entity__in=lp_course_modules, parent_tracker=self, **kwargs
        ).values_list('id', flat=True)

        # Delete existing trackers
        UserSubscriptionPlanLearningPathCourseSubModuleTracker.objects.filter(id__in=existing_tracker_ids).delete()
         # Check if the parent tracker exists
        try:
            parent_tracker = UserSubscriptionPlanLearningPathCourseModuleTracker.objects.get(entity=self.entity,parent_tracker=self.parent_tracker,created_by=self.created_by)
        except UserSubscriptionPlanLearningPathCourseModuleTracker.DoesNotExist:
            parent_tracker = UserSubscriptionPlanLearningPathCourseModuleTracker.objects.create(entity=self.entity, created_by=self.created_by)
        # Check if the parent tracker exists
        course_modules_to_create = [
            UserSubscriptionPlanLearningPathCourseSubModuleTracker(entity=module, parent_tracker=parent_tracker, **kwargs)
            for module in lp_course_modules
        ]
        
        batch_size = 200  # Set an appropriate batch size
        num_modules = len(course_modules_to_create)
        with transaction.atomic():
            for i in range(0, num_modules, batch_size):
                # Calculate the end index of the current batch
                end_index = min(i + batch_size, num_modules)
                # Create instances for the current batch
                for tracker in course_modules_to_create[i:end_index]:
                    tracker.save()
                    tracker.handle_user_enrolled()

        # for sub_module in CourseSubModule.objects.filter(module=self.entity):
        #     UserSubscriptionPlanLearningPathCourseSubModuleTracker.objects.filter(
        #         entity=sub_module, **kwargs
        #     ).delete()

        #     tracker = UserSubscriptionPlanLearningPathCourseSubModuleTracker.objects.create(
        #         entity=sub_module, **kwargs
        #     )
        #     # chain of responsibility
        #     tracker.handle_user_enrolled()

class UserSubscriptionPlanLearningPathCourseSubModuleTracker(BaseModel):
    """Tracker for a `CourseSubModule` under a `UserSubscriptionPlanLearningPathCourseModuleTracker` and `User`."""

    # sub-module
    entity = models.ForeignKey(to="learning.CourseSubModule", on_delete=models.CASCADE)

    # parents
    parent_tracker = models.ForeignKey(
        to=UserSubscriptionPlanLearningPathCourseModuleTracker, on_delete=models.CASCADE
    )

    # run time calculated
    progress = models.IntegerField(default=0)

    def handle_user_enrolled(self):
        """Chain of responsibility."""

        pass

    def handle_viewed(self):
        """Handles the fact that the user has viewed the tracker."""

        self.progress = 100
        self.save()

        # chain of responsibility
        self.parent_tracker.handle_child_modified()


# Advanced Learning Path Course Trackers (certificate path Trackers)
class UserSubscriptionPlanCertificatePathTracker(BaseModel):
    """
    Model used to track the progress of user under a given certificate path learning path course.
    The `created_by` column is used to hold the user.

    This is created when the user purchases the certificate path learning path course.
    """

    entity = models.ForeignKey(to="learning.CertificationPath", on_delete=models.CASCADE)

    valid_till = models.DateField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)

    last_accessed_on = models.DateTimeField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)

    # parents
    parent_tracker = models.ForeignKey(to=UserSubscriptionPlanTracker, on_delete=models.CASCADE, null=True)

    # saved in percentage | ranges 0 - 100
    progress = models.IntegerField(default=0)

    institute = models.ForeignKey(to="access.InstitutionDetail",
                                  on_delete=models.SET_NULL,
                                  **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)

    def handle_started_learning(self):
        """Handles the fact that user has opened and started learning."""

        self.last_accessed_on = datetime.now()
        self.save()

    def handle_user_enrolled(self):
        """Handles the chain reaction that user has enrolled to a course."""

        kwargs = {"parent_tracker": self, "created_by": self.created_by}

        from apps.learning.models import CertificationPathLearningPath

        for module in CertificationPathLearningPath.objects.filter(certification_path=self.entity):
            UserSubscriptionPlanCertificatePathLearningPathCourseTracker.objects.filter(entity=module.learning_path, **kwargs).delete()

            tracker = UserSubscriptionPlanCertificatePathLearningPathCourseTracker.objects.create(entity=module.learning_path, **kwargs)

            # chain of responsibility
            tracker.handle_user_enrolled()

    def handle_child_modified(self):
        """Chain of responsibility from the bottom up."""

        self.progress = (
            UserSubscriptionPlanCertificatePathLearningPathCourseTracker.objects.filter(
                parent_tracker=self, progress__gt=0
            ).count()
            / UserSubscriptionPlanCertificatePathLearningPathCourseTracker.objects.filter(parent_tracker=self).count()
        ) * 100
        self.save()


class UserSubscriptionPlanCertificatePathLearningPathCourseTracker(BaseModel):
    """
    Model used to track the progress of user under a given certificate path learning path course.
    The `created_by` column is used to hold the user.

    This is created when the user purchases the certificate path learning path course.
    """

    entity = models.ForeignKey(to="learning.learningpath", on_delete=models.CASCADE)

    valid_till = models.DateField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)

    last_accessed_on = models.DateTimeField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    
    # parents
    parent_tracker = models.ForeignKey(to=UserSubscriptionPlanCertificatePathTracker, on_delete=models.CASCADE, null=True)

    # saved in percentage | ranges 0 - 100
    progress = models.IntegerField(default=0)

    institute = models.ForeignKey(to="access.InstitutionDetail",
                                  on_delete=models.SET_NULL,
                                  **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)

    def handle_started_learning(self):
        """Handles the fact that user has opened and started learning."""

        self.last_accessed_on = datetime.now()
        self.save()

    def handle_user_enrolled(self):
        """Handles the chain reaction that user has enrolled to a course."""

        kwargs = {"parent_tracker": self, "created_by": self.created_by}

        from apps.learning.models import LearningPathCourse

        for module in LearningPathCourse.objects.filter(learning_path=self.entity):

            UserSubscriptionPlanCertificatePathCourseTracker.objects.filter(entity=module.course, **kwargs).delete()

            tracker = UserSubscriptionPlanCertificatePathCourseTracker.objects.create(entity=module.course, **kwargs)
            
            # chain of responsibility
            tracker.handle_user_enrolled()

    def handle_child_modified(self):
        """Chain of responsibility from the bottom up."""

        self.progress = (
            UserSubscriptionPlanCertificatePathCourseTracker.objects.filter(
                parent_tracker=self, progress=100
            ).count()
            / UserSubscriptionPlanCertificatePathCourseTracker.objects.filter(parent_tracker=self).count()
        ) * 100
        self.save()

class UserSubscriptionPlanCertificatePathCourseTracker(BaseModel):
    """
    Model used to track the progress of user under a given certificate path course.
    The `created_by` column is used to hold the user. 

    This is created when the user purchases the certificate path course.
    """

    entity = models.ForeignKey(to="learning.Course", on_delete=models.CASCADE)

    valid_till = models.DateField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)

    last_accessed_on = models.DateTimeField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)

    # parents
    parent_tracker = models.ForeignKey(to=UserSubscriptionPlanCertificatePathLearningPathCourseTracker, on_delete=models.CASCADE, null=True)

    # saved in percentage | ranges 0 - 100
    progress = models.IntegerField(default=0)

    institute = models.ForeignKey(to="access.InstitutionDetail",
                                  on_delete=models.SET_NULL,
                                  **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)

    def handle_started_learning(self):
        """Handles the fact that user has opened and started learning."""

        self.last_accessed_on = datetime.now()
        self.save()

    def handle_user_enrolled(self):
        """Handles the chain reaction that user has enrolled to a course."""

        kwargs = {"parent_tracker": self, "created_by": self.created_by}

        from apps.learning.models import CourseModule

        for module in CourseModule.objects.filter(course=self.entity):
            UserSubscriptionPlanCertificatePathCourseModuleTracker.objects.filter(entity=module, **kwargs).delete()

            tracker = UserSubscriptionPlanCertificatePathCourseModuleTracker.objects.create(entity=module, **kwargs)

            # chain of responsibility
            tracker.handle_user_enrolled()

    def handle_child_modified(self):
        """Chain of responsibility from the bottom up."""

        self.progress = (
            UserSubscriptionPlanCertificatePathCourseModuleTracker.objects.filter(
                parent_tracker=self, progress=100
            ).count()
            / UserSubscriptionPlanCertificatePathCourseModuleTracker.objects.filter(parent_tracker=self).count()
        ) * 100
        self.save()
    
class UserSubscriptionPlanCertificatePathCourseModuleTracker(BaseModel):
    """Tracker for a `CourseModule` under a `UserSubscriptionPlanCertificatePathCourseTracker` and a `User`."""

    # module
    entity = models.ForeignKey(to="learning.CourseModule", on_delete=models.CASCADE)

    # parents
    parent_tracker = models.ForeignKey(to=UserSubscriptionPlanCertificatePathCourseTracker, on_delete=models.CASCADE, null=True)

    # run time calculated
    progress = models.IntegerField(default=0)

    def handle_child_modified(self):
        """Chain of responsibility from the bottom up."""

        self.progress = (
            UserSubscriptionPlanCertificatePathCourseSubModuleTracker.objects.filter(
                parent_tracker=self, progress=100
            ).count()
            / UserSubscriptionPlanCertificatePathCourseSubModuleTracker.objects.filter(parent_tracker=self).count()
        ) * 100
        self.save()

        # chain of responsibility
        self.parent_tracker.handle_child_modified()

    def handle_user_enrolled(self):
        """Chain of responsibility."""

        kwargs = {"parent_tracker": self, "created_by": self.created_by}

        from apps.learning.models import CourseSubModule

        for sub_module in CourseSubModule.objects.filter(module=self.entity):
            UserSubscriptionPlanCertificatePathCourseSubModuleTracker.objects.filter(
                entity=sub_module, **kwargs
            ).delete()

            tracker = UserSubscriptionPlanCertificatePathCourseSubModuleTracker.objects.create(
                entity=sub_module, **kwargs
            )

            # chain of responsibility
            tracker.handle_user_enrolled()

class UserSubscriptionPlanCertificatePathCourseSubModuleTracker(BaseModel):
    """Tracker for a `CourseSubModule` under a `UserSubscriptionPlanCertificatePathCourseModuleTracker` and `User`."""

    # sub-module
    entity = models.ForeignKey(to="learning.CourseSubModule", on_delete=models.CASCADE)

    # parents
    parent_tracker = models.ForeignKey(
        to=UserSubscriptionPlanCertificatePathCourseModuleTracker, on_delete=models.CASCADE, null=True
    )

    # run time calculated
    progress = models.IntegerField(default=0)

    def handle_user_enrolled(self):
        """Chain of responsibility."""

        pass

    def handle_viewed(self):
        """Handles the fact that the user has viewed the tracker."""

        self.progress = 100
        self.save()

        # chain of responsibility
        self.parent_tracker.handle_child_modified()

# Student Enroll MML Course Tracker
class StudentEnrolledMMLCourseTracker(BaseModel):
    """
    Model used to track the progress of user under a given mml course.
    The `created_by` column is used to hold the user.

    This is created when the user purchases the course.
    """

    entity = models.ForeignKey(to="learning.MMLCourse", on_delete=models.CASCADE)

    valid_till = models.DateField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)

    last_accessed_on = models.DateTimeField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)

    started_on = models.DateTimeField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    completed_on = models.DateTimeField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    # saved in percentage | ranges 0 - 100
    progress = models.IntegerField(default=0)

    def handle_started_learning(self):
        """Handles the fact that user has opened and started learning."""

        self.last_accessed_on = datetime.now()
        if self.started_on is None:
            self.started_on =  datetime.now()
        if self.progress is None:
            self.progress = 100
            notification = Notification(
                user=self.created_by,
                message="You have successfully completed the MML course: " + self.entity.identity,
                course=self.entity,
                purpose="completed"
            )
            notification.save()
        self.save()


# student Entroll Course Tracker
class StudentEnrolledCourseTracker(BaseModel):
    """
    Model used to track the progress of user under a given course.
    The `created_by` column is used to hold the user.

    This is created when the user purchases the course.
    """

    entity = models.ForeignKey(to="learning.Course", on_delete=models.CASCADE)

    valid_till = models.DateField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)

    last_accessed_on = models.DateTimeField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)

    started_on = models.DateTimeField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    completed_on = models.DateTimeField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    # saved in percentage | ranges 0 - 100
    progress = models.IntegerField(default=0)

    def handle_started_learning(self):
        """Handles the fact that user has opened and started learning."""

        self.last_accessed_on = datetime.now()
        if self.started_on is None:
            self.started_on =  datetime.now()
        self.save()

    def handle_user_enrolled(self):
        """Handles the chain reaction that user has enrolled to a course."""

        kwargs = {"parent_tracker": self, "created_by": self.created_by}

        from apps.learning.models import CourseModule

        for module in CourseModule.objects.filter(course=self.entity):
            StudentEnrolledCourseModuleTracker.objects.filter(entity=module, **kwargs).delete()

            tracker = StudentEnrolledCourseModuleTracker.objects.create(entity=module, **kwargs)

            # chain of responsibility
            tracker.handle_user_enrolled()

    def handle_child_modified(self):
        """Chain of responsibility from the bottom up."""

        self.progress = (
            StudentEnrolledCourseModuleTracker.objects.filter(
                parent_tracker=self, progress=100
            ).count()
            / StudentEnrolledCourseModuleTracker.objects.filter(parent_tracker=self).count()
        ) * 100

        if self.completed_on is None and self.progress == 100:
            self.completed_on =  datetime.now()
            notification = Notification(
                user=self.created_by,
                message="You have successfully completed the course: " + self.entity.identity,
                course=self.entity,
                purpose="completed"
            )
            notification.save()
        self.save()

class StudentEnrolledCourseModuleTracker(BaseModel):
    """Tracker for a `CourseModule` under a `StudentEnrolledTracker` and a `User`."""

    # module
    entity = models.ForeignKey(to="learning.CourseModule", on_delete=models.CASCADE)

    # parents
    parent_tracker = models.ForeignKey(to=StudentEnrolledCourseTracker, on_delete=models.CASCADE)

    # run time calculated
    progress = models.IntegerField(default=0)

    def handle_child_modified(self):
        """Chain of responsibility from the bottom up."""

        self.progress = (
            StudentEnrolledSubModuleTracker.objects.filter(
                parent_tracker=self, progress=100
            ).count()
            / StudentEnrolledSubModuleTracker.objects.filter(parent_tracker=self).count()
        ) * 100
        self.save()

        # chain of responsibility
        self.parent_tracker.handle_child_modified()

    def handle_user_enrolled(self):
        """Chain of responsibility."""

        kwargs = {"parent_tracker": self, "created_by": self.created_by}

        from apps.learning.models import CourseSubModule

        for sub_module in CourseSubModule.objects.filter(module=self.entity):
            StudentEnrolledSubModuleTracker.objects.filter(
                entity=sub_module, **kwargs
            ).delete()

            tracker = StudentEnrolledSubModuleTracker.objects.create(
                entity=sub_module, **kwargs
            )

            # chain of responsibility
            tracker.handle_user_enrolled()


class StudentEnrolledSubModuleTracker(BaseModel):
    """Tracker for a `CourseSubModule` under a `StudentEnrolledCourseModuleTracker` and `User`."""

    # sub-module
    entity = models.ForeignKey(to="learning.CourseSubModule", on_delete=models.CASCADE)

    # parents
    parent_tracker = models.ForeignKey(
        to=StudentEnrolledCourseModuleTracker, on_delete=models.CASCADE
    )

    # run time calculated
    progress = models.IntegerField(default=0)

    def handle_user_enrolled(self):
        """Chain of responsibility."""

        pass

    def handle_viewed(self):
        """Handles the fact that the user has viewed the tracker."""

        self.progress = 100
        self.save()

        # chain of responsibility
        self.parent_tracker.handle_child_modified()

# Learning Path Course Trackers
class StudentEnrolledLearningPathTracker(BaseModel):
    """
    Model used to track the progress of student under a given learning path course.
    The `created_by` column is used to hold the student.
    This is created when the student enroll the lp course.
    """

    entity = models.ForeignKey(to="learning.learningpath", on_delete=models.CASCADE)

    valid_till = models.DateField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)

    last_accessed_on = models.DateTimeField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)

    # saved in percentage | ranges 0 - 100
    progress = models.IntegerField(default=0)\

    def handle_started_learning(self):
        """Handles the fact that user has opened and started learning."""

        self.last_accessed_on = datetime.now()
        self.save()

    def handle_user_enrolled(self):
        """Handles the chain reaction that user has enrolled to a course."""
        
        kwargs = {"parent_tracker": self, "created_by": self.created_by}

        from apps.learning.models import LearningPathCourse
        for module in LearningPathCourse.objects.filter(learning_path=self.entity):
           
            StudentEnrolledLearningPathCourseTracker.objects.filter(entity=module.course, **kwargs).delete()
            
            tracker = StudentEnrolledLearningPathCourseTracker.objects.create(entity=module.course, **kwargs)
            # chain of responsibility
            tracker.handle_user_enrolled()


    def handle_child_modified(self):
        """Chain of responsibility from the bottom up."""

        self.progress = (
            StudentEnrolledLearningPathCourseTracker.objects.filter(
                parent_tracker=self, progress__gt=0
            ).count()
            / StudentEnrolledLearningPathCourseTracker.objects.filter(parent_tracker=self).count()
        ) * 100
        if self.progress == 100:
            notification = Notification(
                    user=self.created_by,
                    message="You have successfully completed the course: " + self.entity.identity,
                    learning_path=self.entity,
                    purpose="completed"
                )
            notification.save()
        self.save()


class StudentEnrolledLearningPathCourseTracker(BaseModel):
    """
    Model used to track the progress of user under a given learning path course.
    The `created_by` column is used to hold the user.

    This is created when the user purchases the lp course.
    """

    entity = models.ForeignKey(to="learning.Course", on_delete=models.CASCADE)
    # parents
    parent_tracker = models.ForeignKey(to=StudentEnrolledLearningPathTracker, on_delete=models.CASCADE, null=True)

    # saved in percentage | ranges 0 - 100
    progress = models.IntegerField(default=0)

    def handle_child_modified(self):
        """Chain of responsibility from the bottom up."""

        self.progress = (
            StudentEnrolledLearningPathCourseModuleTracker.objects.filter(
                parent_tracker=self, progress=100
            ).count()
            / StudentEnrolledLearningPathCourseModuleTracker.objects.filter(parent_tracker=self).count()
        ) * 100
        self.save()

        # chain of responsibility
        self.parent_tracker.handle_child_modified()

    def handle_user_enrolled(self):
        """Chain of responsibility."""

        kwargs = {"parent_tracker": self, "created_by": self.created_by}

        from apps.learning.models import CourseModule

        for module in CourseModule.objects.filter(course=self.entity):
            StudentEnrolledLearningPathCourseModuleTracker.objects.filter(entity=module, **kwargs).delete()

            tracker = StudentEnrolledLearningPathCourseModuleTracker.objects.create(entity=module, **kwargs)
            # chain of responsibility
            tracker.handle_user_enrolled()

   
class StudentEnrolledLearningPathCourseModuleTracker(BaseModel):
    """Tracker for a `CourseModule` under a `StudentEnrolledLearningPathCourseTracker` and a `User`."""

    # module
    entity = models.ForeignKey(to="learning.CourseModule", on_delete=models.CASCADE)

    # parents
    parent_tracker = models.ForeignKey(to=StudentEnrolledLearningPathCourseTracker, on_delete=models.CASCADE)

    # run time calculated
    progress = models.IntegerField(default=0)

    def handle_child_modified(self):
        """Chain of responsibility from the bottom up."""

        self.progress = (
            StudentEnrolledLearningPathCourseSubModuleTracker.objects.filter(
                parent_tracker=self, progress=100
            ).count()
            / StudentEnrolledLearningPathCourseSubModuleTracker.objects.filter(parent_tracker=self).count()
        ) * 100
        self.save()

        # chain of responsibility
        self.parent_tracker.handle_child_modified()

    def handle_user_enrolled(self):
        """Chain of responsibility."""

        kwargs = {"parent_tracker": self, "created_by": self.created_by}

        from apps.learning.models import CourseSubModule

        for sub_module in CourseSubModule.objects.filter(module=self.entity):
            StudentEnrolledLearningPathCourseSubModuleTracker.objects.filter(
                entity=sub_module, **kwargs
            ).delete()

            tracker = StudentEnrolledLearningPathCourseSubModuleTracker.objects.create(
                entity=sub_module, **kwargs
            )
            # chain of responsibility
            tracker.handle_user_enrolled()

class StudentEnrolledLearningPathCourseSubModuleTracker(BaseModel):
    """Tracker for a `CourseSubModule` under a `StudentEnrolledLearningPathCourseModuleTracker` and `User`."""

    # sub-module
    entity = models.ForeignKey(to="learning.CourseSubModule", on_delete=models.CASCADE)

    # parents
    parent_tracker = models.ForeignKey(
        to=StudentEnrolledLearningPathCourseModuleTracker, on_delete=models.CASCADE
    )

    # run time calculated
    progress = models.IntegerField(default=0)

    def handle_user_enrolled(self):
        """Chain of responsibility."""

        pass

    def handle_viewed(self):
        """Handles the fact that the user has viewed the tracker."""

        self.progress = 100
        self.save()

        # chain of responsibility
        self.parent_tracker.handle_child_modified()

# Advanced Learning Path Course Trackers (certificate path Trackers)
class StudentEnrolledCertificatePathTracker(BaseModel):
    """
    Model used to track the progress of user under a given certificate path learning path course.
    The `created_by` column is used to hold the user.

    This is created when the user purchases the certificate path learning path course.
    """

    entity = models.ForeignKey(to="learning.CertificationPath", on_delete=models.CASCADE)

    valid_till = models.DateField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)

    last_accessed_on = models.DateTimeField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)

    # saved in percentage | ranges 0 - 100
    progress = models.IntegerField(default=0)

    def handle_started_learning(self):
        """Handles the fact that user has opened and started learning."""

        self.last_accessed_on = datetime.now()
        self.save()

    def handle_user_enrolled(self):
        """Handles the chain reaction that user has enrolled to a course."""

        kwargs = {"parent_tracker": self, "created_by": self.created_by}

        from apps.learning.models import CertificationPathLearningPath

        for module in CertificationPathLearningPath.objects.filter(certification_path=self.entity):
            StudentEnrolledCertificatePathLearningPathCourseTracker.objects.filter(entity=module.learning_path, **kwargs).delete()

            tracker = StudentEnrolledCertificatePathLearningPathCourseTracker.objects.create(entity=module.learning_path, **kwargs)

            # chain of responsibility
            tracker.handle_user_enrolled()

    def handle_child_modified(self):
        """Chain of responsibility from the bottom up."""

        self.progress = (
            StudentEnrolledCertificatePathLearningPathCourseTracker.objects.filter(
                parent_tracker=self, progress__gt=0
            ).count()
            / StudentEnrolledCertificatePathLearningPathCourseTracker.objects.filter(parent_tracker=self).count()
        ) * 100

        if self.progress == 100:
            notification = Notification(
                    user=self.created_by,
                    message="You have successfully completed the course: " + self.entity.identity,
                    certification_path=self.entity,
                    purpose="completed"
                )
            notification.save()
        self.save()


class StudentEnrolledCertificatePathLearningPathCourseTracker(BaseModel):
    """
    Model used to track the progress of user under a given certificate path learning path course.
    The `created_by` column is used to hold the user.

    This is created when the user purchases the certificate path learning path course.
    """

    entity = models.ForeignKey(to="learning.learningpath", on_delete=models.CASCADE)
    # parents
    parent_tracker = models.ForeignKey(to=StudentEnrolledCertificatePathTracker, on_delete=models.CASCADE, null=True)

    # saved in percentage | ranges 0 - 100
    progress = models.IntegerField(default=0)

    def handle_started_learning(self):
        """Handles the fact that user has opened and started learning."""

        self.last_accessed_on = datetime.now()
        self.save()

    def handle_user_enrolled(self):
        """Handles the chain reaction that user has enrolled to a course."""

        kwargs = {"parent_tracker": self, "created_by": self.created_by}

        from apps.learning.models import LearningPathCourse

        for module in LearningPathCourse.objects.filter(learning_path=self.entity):

            StudentEnrolledCertificatePathCourseTracker.objects.filter(entity=module.course, **kwargs).delete()

            tracker = StudentEnrolledCertificatePathCourseTracker.objects.create(entity=module.course, **kwargs)
            
            # chain of responsibility
            tracker.handle_user_enrolled()

    def handle_child_modified(self):
        """Chain of responsibility from the bottom up."""

        self.progress = (
            StudentEnrolledCertificatePathCourseTracker.objects.filter(
                parent_tracker=self, progress=100
            ).count()
            / StudentEnrolledCertificatePathCourseTracker.objects.filter(parent_tracker=self).count()
        ) * 100
        self.save()

class StudentEnrolledCertificatePathCourseTracker(BaseModel):
    """
    Model used to track the progress of user under a given certificate path course.
    The `created_by` column is used to hold the user. 

    This is created when the user purchases the certificate path course.
    """

    entity = models.ForeignKey(to="learning.Course", on_delete=models.CASCADE)
    # parents
    parent_tracker = models.ForeignKey(to=StudentEnrolledCertificatePathLearningPathCourseTracker, on_delete=models.CASCADE, null=True)

    # saved in percentage | ranges 0 - 100
    progress = models.IntegerField(default=0)

    def handle_started_learning(self):
        """Handles the fact that user has opened and started learning."""

        self.last_accessed_on = datetime.now()
        self.save()

    def handle_user_enrolled(self):
        """Handles the chain reaction that user has enrolled to a course."""

        kwargs = {"parent_tracker": self, "created_by": self.created_by}

        from apps.learning.models import CourseModule

        for module in CourseModule.objects.filter(course=self.entity):
            StudentEnrolledCertificatePathCourseModuleTracker.objects.filter(entity=module, **kwargs).delete()

            tracker = StudentEnrolledCertificatePathCourseModuleTracker.objects.create(entity=module, **kwargs)

            # chain of responsibility
            tracker.handle_user_enrolled()

    def handle_child_modified(self):
        """Chain of responsibility from the bottom up."""

        self.progress = (
            StudentEnrolledCertificatePathCourseModuleTracker.objects.filter(
                parent_tracker=self, progress=100
            ).count()
            / StudentEnrolledCertificatePathCourseModuleTracker.objects.filter(parent_tracker=self).count()
        ) * 100
        self.save()
    
class StudentEnrolledCertificatePathCourseModuleTracker(BaseModel):
    """Tracker for a `CourseModule` under a `StudentEnrolledCertificatePathCourseTracker` and a `User`."""

    # module
    entity = models.ForeignKey(to="learning.CourseModule", on_delete=models.CASCADE)

    # parents
    parent_tracker = models.ForeignKey(to=StudentEnrolledCertificatePathCourseTracker, on_delete=models.CASCADE, null=True)

    # run time calculated
    progress = models.IntegerField(default=0)

    def handle_child_modified(self):
        """Chain of responsibility from the bottom up."""

        self.progress = (
            StudentEnrolledCertificatePathCourseSubModuleTracker.objects.filter(
                parent_tracker=self, progress=100
            ).count()
            / StudentEnrolledCertificatePathCourseSubModuleTracker.objects.filter(parent_tracker=self).count()
        ) * 100
        self.save()

        # chain of responsibility
        self.parent_tracker.handle_child_modified()

    def handle_user_enrolled(self):
        """Chain of responsibility."""

        kwargs = {"parent_tracker": self, "created_by": self.created_by}

        from apps.learning.models import CourseSubModule

        for sub_module in CourseSubModule.objects.filter(module=self.entity):
            StudentEnrolledCertificatePathCourseSubModuleTracker.objects.filter(
                entity=sub_module, **kwargs
            ).delete()

            tracker = StudentEnrolledCertificatePathCourseSubModuleTracker.objects.create(
                entity=sub_module, **kwargs
            )

            # chain of responsibility
            tracker.handle_user_enrolled()

class StudentEnrolledCertificatePathCourseSubModuleTracker(BaseModel):
    """Tracker for a `CourseSubModule` under a `StudentEnrolledCertificatePathCourseModuleTracker` and `User`."""

    # sub-module
    entity = models.ForeignKey(to="learning.CourseSubModule", on_delete=models.CASCADE)

    # parents
    parent_tracker = models.ForeignKey(
        to=StudentEnrolledCertificatePathCourseModuleTracker, on_delete=models.CASCADE, null=True
    )

    # run time calculated
    progress = models.IntegerField(default=0)

    def handle_user_enrolled(self):
        """Chain of responsibility."""

        pass

    def handle_viewed(self):
        """Handles the fact that the user has viewed the tracker."""

        self.progress = 100
        self.save()

        # chain of responsibility
        self.parent_tracker.handle_child_modified()

#Blended Learning Path
class UserBlendedLearningPathTracker(BaseModel):
    
    DYNAMIC_KEY = "user-blended-learning-path-tracker"
    """
    Model used to track the progress of user under a given blended learning path course.
    The `created_by` column is used to hold the user.

    This is created when the user purchases the blp course.
    """

    entity = models.ForeignKey(to="learning.BlendedLearningPath", on_delete=models.CASCADE)

    valid_till = models.DateField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)

    last_accessed_on = models.DateTimeField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)

    # saved in percentage | ranges 0 - 100
    progress = models.IntegerField(default=0)

    blp_learning_mode = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH,**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    blp_schedule = models.ForeignKey(to="learning.BlendedLearningPathScheduleDetails", on_delete=models.CASCADE, **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)

    def handle_started_learning(self):
        """Handles the fact that user has opened and started learning."""

        self.last_accessed_on = datetime.now()
        self.save()

    def handle_user_enrolled(self):
        """Handles the chain reaction that user has enrolled to a course."""
        
        kwargs = {"parent_tracker": self, "created_by": self.created_by}

        # from apps.learning.models import BlendedLearningUserEnrollCourseDetails
        # course_detail = self.entity.course_details.all()
        # course=[]
        # for courses in course_detail:
        #     course.append(courses.course)
        # for module in BlendedLearningUserEnrollCourseDetails.objects.filter(course__in=course):
           
        #     UserBlendedLearningPathCourseTracker.objects.filter(entity=module.course, **kwargs).delete()
            
        #     tracker = UserBlendedLearningPathCourseTracker.objects.create(entity=module.course, **kwargs)
        #     # chain of responsibility
        #     tracker.handle_user_enrolled()
        from apps.learning.models import BlendedLearningPathCourseModesAndFee
        for module in BlendedLearningPathCourseModesAndFee.objects.filter(blended_learning_id=self.entity.id):
           
            UserBlendedLearningPathCourseTracker.objects.filter(entity=module.course, **kwargs).delete()
            
            tracker = UserBlendedLearningPathCourseTracker.objects.create(entity=module.course, **kwargs)
            # chain of responsibility
            tracker.handle_user_enrolled()

    def handle_child_modified(self):
        """Chain of responsibility from the bottom up."""

        self.progress = (
            UserBlendedLearningPathCourseTracker.objects.filter(
                parent_tracker=self, progress__gt=0
            ).count()
            / UserBlendedLearningPathCourseTracker.objects.filter(parent_tracker=self).count()
        ) * 100
        self.save()


class UserBlendedLearningPathCourseTracker(BaseModel):
    """
    Model used to track the progress of user under a given blended learning path course.
    The `created_by` column is used to hold the user.

    This is created when the user purchases the blp course.
    """

    entity = models.ForeignKey(to="learning.Course", on_delete=models.CASCADE)

    valid_till = models.DateField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)

    last_accessed_on = models.DateTimeField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    
    # parents
    parent_tracker = models.ForeignKey(to=UserBlendedLearningPathTracker, on_delete=models.CASCADE, null=True)

    # saved in percentage | ranges 0 - 100
    progress = models.IntegerField(default=0)

    def handle_child_modified(self):
        """Chain of responsibility from the bottom up."""

        self.progress = (
            UserBlendedLearningPathCourseModuleTracker.objects.filter(
                parent_tracker=self, progress=100
            ).count()
            / UserBlendedLearningPathCourseModuleTracker.objects.filter(parent_tracker=self).count()
        ) * 100
        self.save()

        # chain of responsibility
        self.parent_tracker.handle_child_modified()

    def handle_user_enrolled(self):
        """Chain of responsibility."""

        kwargs = {"parent_tracker": self, "created_by": self.created_by}

        from apps.learning.models import CourseModule

        for module in CourseModule.objects.filter(course=self.entity):
            UserBlendedLearningPathCourseModuleTracker.objects.filter(entity=module, **kwargs).delete()

            tracker = UserBlendedLearningPathCourseModuleTracker.objects.create(entity=module, **kwargs)
            # chain of responsibility
            tracker.handle_user_enrolled()


class UserBlendedLearningPathCourseModuleTracker(BaseModel):
    """Tracker for a `CourseModule` under a `UserBlendedLearningPathCourseTracker` and a `User`."""

    # module
    entity = models.ForeignKey(to="learning.CourseModule", on_delete=models.CASCADE)

    # parents
    parent_tracker = models.ForeignKey(to=UserBlendedLearningPathCourseTracker, on_delete=models.CASCADE)

    # run time calculated
    progress = models.IntegerField(default=0)

    def handle_child_modified(self):
        """Chain of responsibility from the bottom up."""

        self.progress = (
            UserBlendedLearningPathCourseSubModuleTracker.objects.filter(
                parent_tracker=self, progress=100
            ).count()
            / UserBlendedLearningPathCourseSubModuleTracker.objects.filter(parent_tracker=self).count()
        ) * 100
        self.save()

        # chain of responsibility
        self.parent_tracker.handle_child_modified()

    def handle_user_enrolled(self):
        """Chain of responsibility."""

        kwargs = {"parent_tracker": self, "created_by": self.created_by}

        from apps.learning.models import CourseSubModule

        for sub_module in CourseSubModule.objects.filter(module=self.entity):
            UserBlendedLearningPathCourseSubModuleTracker.objects.filter(
                entity=sub_module, **kwargs
            ).delete()

            tracker = UserBlendedLearningPathCourseSubModuleTracker.objects.create(
                entity=sub_module, **kwargs
            )
            # print('Course Sub Module')
            # print(tracker)
            # breakpoint()
            # chain of responsibility
            tracker.handle_user_enrolled()

class UserBlendedLearningPathCourseSubModuleTracker(BaseModel):
    """Tracker for a `CourseSubModule` under a `UserLearningPathCourseModuleTracker` and `User`."""

    # sub-module
    entity = models.ForeignKey(to="learning.CourseSubModule", on_delete=models.CASCADE)

    # parents
    parent_tracker = models.ForeignKey(
        to=UserBlendedLearningPathCourseModuleTracker, on_delete=models.CASCADE
    )

    # run time calculated
    progress = models.IntegerField(default=0)

    def handle_user_enrolled(self):
        """Chain of responsibility."""

        pass

    def handle_viewed(self):
        """Handles the fact that the user has viewed the tracker."""

        self.progress = 100
        self.save()

        # chain of responsibility
        self.parent_tracker.handle_child_modified()


#Skill
class UserSkillTracker(BaseModel):
    """
    Model used to track the progress of user under a given learning path course.
    The `created_by` column is used to hold the user.

    This is created when the user purchases the lp course.
    """

    entity = models.ForeignKey(to="learning.Skill", on_delete=models.CASCADE)

    valid_till = models.DateField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)

    last_accessed_on = models.DateTimeField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)

    # saved in percentage | ranges 0 - 100
    progress = models.IntegerField(default=0)

    institute = models.ForeignKey(to="access.InstitutionDetail",
                                  on_delete=models.SET_NULL,
                                  **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)

    def handle_started_learning(self):
        """Handles the fact that user has opened and started learning."""

        self.last_accessed_on = datetime.now()
        self.save()

    def handle_user_enrolled(self):
        """Handles the chain reaction that user has enrolled to a course."""
        
        kwargs = {"parent_tracker": self, "created_by": self.created_by}

        for module in Course.objects.filter(skills__in=[self.entity.id]):
           
            UserSkillCourseTracker.objects.filter(entity=module, **kwargs).delete()
            
            tracker = UserSkillCourseTracker.objects.create(entity=module, **kwargs)
            # chain of responsibility
            tracker.handle_user_enrolled()

        for module in LearningPath.objects.filter(skills__in=[self.entity.id]):
           
            UserSkillLearningPathTracker.objects.filter(entity=module, **kwargs).delete()
            
            tracker = UserSkillLearningPathTracker.objects.create(entity=module, **kwargs)
            # chain of responsibility
            tracker.handle_user_enrolled()
        
        for module in CertificationPath.objects.filter(skills__in=[self.entity.id]):
           
            UserSkillCertificatePathTracker.objects.filter(entity=module, **kwargs).delete()
            
            tracker = UserSkillCertificatePathTracker.objects.create(entity=module, **kwargs)
            # chain of responsibility
            tracker.handle_user_enrolled()

    def handle_child_modified(self):
        """Chain of responsibility from the bottom up."""

        self.progress = (
            UserSkillCourseTracker.objects.filter(
                parent_tracker=self, progress__gt=0
            ).count()
            / UserSkillCourseTracker.objects.filter(parent_tracker=self).count()
        ) * 100
        self.save()


class UserSkillCourseTracker(BaseModel):
    """
    Model used to track the progress of user under a given learning path course.
    The `created_by` column is used to hold the user.

    This is created when the user purchases the lp course.
    """

    entity = models.ForeignKey(to="learning.Course", on_delete=models.CASCADE)

    valid_till = models.DateField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)

    last_accessed_on = models.DateTimeField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    
    # parents
    parent_tracker = models.ForeignKey(to=UserSkillTracker, on_delete=models.CASCADE, null=True)

    # saved in percentage | ranges 0 - 100
    progress = models.IntegerField(default=0)

    institute = models.ForeignKey(to="access.InstitutionDetail",
                                  on_delete=models.SET_NULL,
                                  **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)

    def handle_child_modified(self):
        """Chain of responsibility from the bottom up."""

        self.progress = (
            UserSkillCourseModuleTracker.objects.filter(
                parent_tracker=self, progress=100
            ).count()
            / UserSkillCourseModuleTracker.objects.filter(parent_tracker=self).count()
        ) * 100
        self.save()

        # chain of responsibility
        self.parent_tracker.handle_child_modified()

    def handle_user_enrolled(self):
        """Chain of responsibility."""

        kwargs = {"parent_tracker": self, "created_by": self.created_by}

        from apps.learning.models import CourseModule

        for module in CourseModule.objects.filter(course=self.entity):
            UserSkillCourseModuleTracker.objects.filter(entity=module, **kwargs).delete()

            tracker = UserSkillCourseModuleTracker.objects.create(entity=module, **kwargs)
            # chain of responsibility
            tracker.handle_user_enrolled()

   
class UserSkillCourseModuleTracker(BaseModel):
    """Tracker for a `CourseModule` under a `UserSkillTracker` and a `User`."""

    # module
    entity = models.ForeignKey(to="learning.CourseModule", on_delete=models.CASCADE)

    # parents
    parent_tracker = models.ForeignKey(to=UserSkillCourseTracker, on_delete=models.CASCADE)

    # run time calculated
    progress = models.IntegerField(default=0)

    def handle_child_modified(self):
        """Chain of responsibility from the bottom up."""

        self.progress = (
            UserSkillCourseSubModuleTracker.objects.filter(
                parent_tracker=self, progress=100
            ).count()
            / UserSkillCourseSubModuleTracker.objects.filter(parent_tracker=self).count()
        ) * 100
        self.save()

        # chain of responsibility
        self.parent_tracker.handle_child_modified()

    def handle_user_enrolled(self):
        """Chain of responsibility."""

        kwargs = {"parent_tracker": self, "created_by": self.created_by}

        from apps.learning.models import CourseSubModule

        for sub_module in CourseSubModule.objects.filter(module=self.entity):
            UserSkillCourseSubModuleTracker.objects.filter(
                entity=sub_module, **kwargs
            ).delete()

            tracker = UserSkillCourseSubModuleTracker.objects.create(
                entity=sub_module, **kwargs
            )

            # chain of responsibility
            tracker.handle_user_enrolled()


class UserSkillCourseSubModuleTracker(BaseModel):
    """Tracker for a `CourseSubModule` under a `UserSkillCourseModuleTracker` and `User`."""

    # sub-module
    entity = models.ForeignKey(to="learning.CourseSubModule", on_delete=models.CASCADE)

    # parents
    parent_tracker = models.ForeignKey(
        to=UserSkillCourseModuleTracker, on_delete=models.CASCADE
    )

    # run time calculated
    progress = models.IntegerField(default=0)

    def handle_user_enrolled(self):
        """Chain of responsibility."""

        pass

    def handle_viewed(self):
        """Handles the fact that the user has viewed the tracker."""

        self.progress = 100
        self.save()

        # chain of responsibility
        self.parent_tracker.handle_child_modified()

# Learning Path Course Trackers
class UserSkillLearningPathTracker(BaseModel):
    """
    Model used to track the progress of user under a given learning path course.
    The `created_by` column is used to hold the user.

    This is created when the user purchases the lp course.
    """

    entity = models.ForeignKey(to="learning.learningpath", on_delete=models.CASCADE)

    valid_till = models.DateField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)

    last_accessed_on = models.DateTimeField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)

    # parents
    parent_tracker = models.ForeignKey(to=UserSkillTracker, on_delete=models.CASCADE, null=True)

    # saved in percentage | ranges 0 - 100
    progress = models.IntegerField(default=0)

    institute = models.ForeignKey(to="access.InstitutionDetail",
                                  on_delete=models.SET_NULL,
                                  **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)

    def handle_started_learning(self):
        """Handles the fact that user has opened and started learning."""

        self.last_accessed_on = datetime.now()
        self.save()

    def handle_user_enrolled(self):
        """Handles the chain reaction that user has enrolled to a course."""
        
        kwargs = {"parent_tracker": self, "created_by": self.created_by}

        from apps.learning.models import LearningPathCourse
        for module in LearningPathCourse.objects.filter(learning_path=self.entity):
           
            UserSkillLearningPathCourseTracker.objects.filter(entity=module.course, **kwargs).delete()
            
            tracker = UserSkillLearningPathCourseTracker.objects.create(entity=module.course, **kwargs)
            # chain of responsibility
            tracker.handle_user_enrolled()


    def handle_child_modified(self):
        """Chain of responsibility from the bottom up."""

        self.progress = (
            UserSkillLearningPathCourseTracker.objects.filter(
                parent_tracker=self, progress__gt=0
            ).count()
            / UserSkillLearningPathCourseTracker.objects.filter(parent_tracker=self).count()
        ) * 100
        self.save()


class UserSkillLearningPathCourseTracker(BaseModel):
    """
    Model used to track the progress of user under a given learning path course.
    The `created_by` column is used to hold the user.

    This is created when the user purchases the lp course.
    """

    entity = models.ForeignKey(to="learning.Course", on_delete=models.CASCADE)

    valid_till = models.DateField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)

    last_accessed_on = models.DateTimeField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    
    # parents
    parent_tracker = models.ForeignKey(to=UserSkillLearningPathTracker, on_delete=models.CASCADE, null=True)

    # saved in percentage | ranges 0 - 100
    progress = models.IntegerField(default=0)

    institute = models.ForeignKey(to="access.InstitutionDetail",
                                  on_delete=models.SET_NULL,
                                  **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)

    def handle_child_modified(self):
        """Chain of responsibility from the bottom up."""

        self.progress = (
            UserSkillLearningPathCourseModuleTracker.objects.filter(
                parent_tracker=self, progress=100
            ).count()
            / UserSkillLearningPathCourseModuleTracker.objects.filter(parent_tracker=self).count()
        ) * 100
        self.save()

        # chain of responsibility
        self.parent_tracker.handle_child_modified()

    def handle_user_enrolled(self):
        """Chain of responsibility."""

        kwargs = {"parent_tracker": self, "created_by": self.created_by}

        from apps.learning.models import CourseModule

        for module in CourseModule.objects.filter(course=self.entity):
            UserSkillLearningPathCourseModuleTracker.objects.filter(entity=module, **kwargs).delete()

            tracker = UserSkillLearningPathCourseModuleTracker.objects.create(entity=module, **kwargs)
            # chain of responsibility
            tracker.handle_user_enrolled()

   
class UserSkillLearningPathCourseModuleTracker(BaseModel):
    """Tracker for a `CourseModule` under a `UserSubscriptionPlanLearningPathCourseTracker` and a `User`."""

    # module
    entity = models.ForeignKey(to="learning.CourseModule", on_delete=models.CASCADE)

    # parents
    parent_tracker = models.ForeignKey(to=UserSkillLearningPathCourseTracker, on_delete=models.CASCADE)

    # run time calculated
    progress = models.IntegerField(default=0)

    def handle_child_modified(self):
        """Chain of responsibility from the bottom up."""

        self.progress = (
            UserSkillLearningPathCourseSubModuleTracker.objects.filter(
                parent_tracker=self, progress=100
            ).count()
            / UserSkillLearningPathCourseSubModuleTracker.objects.filter(parent_tracker=self).count()
        ) * 100
        self.save()

        # chain of responsibility
        self.parent_tracker.handle_child_modified()

    def handle_user_enrolled(self):
        """Chain of responsibility."""

        kwargs = {"parent_tracker": self, "created_by": self.created_by}

        from apps.learning.models import CourseSubModule

        for sub_module in CourseSubModule.objects.filter(module=self.entity):
            UserSkillLearningPathCourseSubModuleTracker.objects.filter(
                entity=sub_module, **kwargs
            ).delete()

            tracker = UserSkillLearningPathCourseSubModuleTracker.objects.create(
                entity=sub_module, **kwargs
            )
            # chain of responsibility
            tracker.handle_user_enrolled()

class UserSkillLearningPathCourseSubModuleTracker(BaseModel):
    """Tracker for a `CourseSubModule` under a `UserSkillLearningPathCourseModuleTracker` and `User`."""

    # sub-module
    entity = models.ForeignKey(to="learning.CourseSubModule", on_delete=models.CASCADE)

    # parents
    parent_tracker = models.ForeignKey(
        to=UserSkillLearningPathCourseModuleTracker, on_delete=models.CASCADE
    )

    # run time calculated
    progress = models.IntegerField(default=0)

    def handle_user_enrolled(self):
        """Chain of responsibility."""

        pass

    def handle_viewed(self):
        """Handles the fact that the user has viewed the tracker."""

        self.progress = 100
        self.save()

        # chain of responsibility
        self.parent_tracker.handle_child_modified()


# Advanced Learning Path Course Trackers (certificate path Trackers)
class UserSkillCertificatePathTracker(BaseModel):
    """
    Model used to track the progress of user under a given certificate path learning path course.
    The `created_by` column is used to hold the user.

    This is created when the user purchases the certificate path learning path course.
    """

    entity = models.ForeignKey(to="learning.CertificationPath", on_delete=models.CASCADE)

    valid_till = models.DateField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)

    last_accessed_on = models.DateTimeField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)

    # parents
    parent_tracker = models.ForeignKey(to=UserSkillTracker, on_delete=models.CASCADE, null=True)

    # saved in percentage | ranges 0 - 100
    progress = models.IntegerField(default=0)

    institute = models.ForeignKey(to="access.InstitutionDetail",
                                  on_delete=models.SET_NULL,
                                  **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)

    def handle_started_learning(self):
        """Handles the fact that user has opened and started learning."""

        self.last_accessed_on = datetime.now()
        self.save()

    def handle_user_enrolled(self):
        """Handles the chain reaction that user has enrolled to a course."""

        kwargs = {"parent_tracker": self, "created_by": self.created_by}

        from apps.learning.models import CertificationPathLearningPath

        for module in CertificationPathLearningPath.objects.filter(certification_path=self.entity):
            UserSkillCertificatePathLearningPathCourseTracker.objects.filter(entity=module.learning_path, **kwargs).delete()

            tracker = UserSkillCertificatePathLearningPathCourseTracker.objects.create(entity=module.learning_path, **kwargs)

            # chain of responsibility
            tracker.handle_user_enrolled()

    def handle_child_modified(self):
        """Chain of responsibility from the bottom up."""

        self.progress = (
            UserSkillCertificatePathLearningPathCourseTracker.objects.filter(
                parent_tracker=self, progress__gt=0
            ).count()
            / UserSkillCertificatePathLearningPathCourseTracker.objects.filter(parent_tracker=self).count()
        ) * 100
        self.save()


class UserSkillCertificatePathLearningPathCourseTracker(BaseModel):
    """
    Model used to track the progress of user under a given certificate path learning path course.
    The `created_by` column is used to hold the user.

    This is created when the user purchases the certificate path learning path course.
    """

    entity = models.ForeignKey(to="learning.learningpath", on_delete=models.CASCADE)

    valid_till = models.DateField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)

    last_accessed_on = models.DateTimeField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    
    # parents
    parent_tracker = models.ForeignKey(to=UserSkillCertificatePathTracker, on_delete=models.CASCADE, null=True)

    # saved in percentage | ranges 0 - 100
    progress = models.IntegerField(default=0)

    institute = models.ForeignKey(to="access.InstitutionDetail",
                                  on_delete=models.SET_NULL,
                                  **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)

    def handle_started_learning(self):
        """Handles the fact that user has opened and started learning."""

        self.last_accessed_on = datetime.now()
        self.save()

    def handle_user_enrolled(self):
        """Handles the chain reaction that user has enrolled to a course."""

        kwargs = {"parent_tracker": self, "created_by": self.created_by}

        from apps.learning.models import LearningPathCourse

        for module in LearningPathCourse.objects.filter(learning_path=self.entity):

            UserSkillCertificatePathCourseTracker.objects.filter(entity=module.course, **kwargs).delete()

            tracker = UserSkillCertificatePathCourseTracker.objects.create(entity=module.course, **kwargs)
            
            # chain of responsibility
            tracker.handle_user_enrolled()

    def handle_child_modified(self):
        """Chain of responsibility from the bottom up."""

        self.progress = (
            UserSkillCertificatePathCourseTracker.objects.filter(
                parent_tracker=self, progress=100
            ).count()
            / UserSkillCertificatePathCourseTracker.objects.filter(parent_tracker=self).count()
        ) * 100
        self.save()

class UserSkillCertificatePathCourseTracker(BaseModel):
    """
    Model used to track the progress of user under a given certificate path course.
    The `created_by` column is used to hold the user. 

    This is created when the user purchases the certificate path course.
    """

    entity = models.ForeignKey(to="learning.Course", on_delete=models.CASCADE)

    valid_till = models.DateField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)

    last_accessed_on = models.DateTimeField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)

    # parents
    parent_tracker = models.ForeignKey(to=UserSkillCertificatePathLearningPathCourseTracker, on_delete=models.CASCADE, null=True)

    # saved in percentage | ranges 0 - 100
    progress = models.IntegerField(default=0)

    institute = models.ForeignKey(to="access.InstitutionDetail",
                                  on_delete=models.SET_NULL,
                                  **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)

    def handle_started_learning(self):
        """Handles the fact that user has opened and started learning."""

        self.last_accessed_on = datetime.now()
        self.save()

    def handle_user_enrolled(self):
        """Handles the chain reaction that user has enrolled to a course."""

        kwargs = {"parent_tracker": self, "created_by": self.created_by}

        from apps.learning.models import CourseModule

        for module in CourseModule.objects.filter(course=self.entity):
            UserSkillCertificatePathCourseModuleTracker.objects.filter(entity=module, **kwargs).delete()

            tracker = UserSkillCertificatePathCourseModuleTracker.objects.create(entity=module, **kwargs)

            # chain of responsibility
            tracker.handle_user_enrolled()

    def handle_child_modified(self):
        """Chain of responsibility from the bottom up."""

        self.progress = (
            UserSkillCertificatePathCourseModuleTracker.objects.filter(
                parent_tracker=self, progress=100
            ).count()
            / UserSkillCertificatePathCourseModuleTracker.objects.filter(parent_tracker=self).count()
        ) * 100
        self.save()
    
class UserSkillCertificatePathCourseModuleTracker(BaseModel):
    """Tracker for a `CourseModule` under a `UserSubscriptionPlanCertificatePathCourseTracker` and a `User`."""

    # module
    entity = models.ForeignKey(to="learning.CourseModule", on_delete=models.CASCADE)

    # parents
    parent_tracker = models.ForeignKey(to=UserSkillCertificatePathCourseTracker, on_delete=models.CASCADE, null=True)

    # run time calculated
    progress = models.IntegerField(default=0)

    def handle_child_modified(self):
        """Chain of responsibility from the bottom up."""

        self.progress = (
            UserSkillCertificatePathCourseSubModuleTracker.objects.filter(
                parent_tracker=self, progress=100
            ).count()
            / UserSkillCertificatePathCourseSubModuleTracker.objects.filter(parent_tracker=self).count()
        ) * 100
        self.save()

        # chain of responsibility
        self.parent_tracker.handle_child_modified()

    def handle_user_enrolled(self):
        """Chain of responsibility."""

        kwargs = {"parent_tracker": self, "created_by": self.created_by}

        from apps.learning.models import CourseSubModule

        for sub_module in CourseSubModule.objects.filter(module=self.entity):
            UserSkillCertificatePathCourseSubModuleTracker.objects.filter(
                entity=sub_module, **kwargs
            ).delete()

            tracker = UserSkillCertificatePathCourseSubModuleTracker.objects.create(
                entity=sub_module, **kwargs
            )

            # chain of responsibility
            tracker.handle_user_enrolled()

class UserSkillCertificatePathCourseSubModuleTracker(BaseModel):
    """Tracker for a `CourseSubModule` under a `UserSubscriptionPlanCertificatePathCourseModuleTracker` and `User`."""

    # sub-module
    entity = models.ForeignKey(to="learning.CourseSubModule", on_delete=models.CASCADE)

    # parents
    parent_tracker = models.ForeignKey(
        to=UserSkillCertificatePathCourseModuleTracker, on_delete=models.CASCADE, null=True
    )

    # run time calculated
    progress = models.IntegerField(default=0)

    def handle_user_enrolled(self):
        """Chain of responsibility."""

        pass

    def handle_viewed(self):
        """Handles the fact that the user has viewed the tracker."""

        self.progress = 100
        self.save()

        # chain of responsibility
        self.parent_tracker.handle_child_modified()


#Job Eligibility Skill
class UserJobEligibleSkillTracker(BaseModel):
    """
    Model used to track the progress of user under a given learning path course.
    The `created_by` column is used to hold the user.

    This is created when the user purchases the lp course.
    """

    entity = models.ForeignKey(to="learning.JobEligibleSkill", on_delete=models.CASCADE)

    valid_till = models.DateField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)

    last_accessed_on = models.DateTimeField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)

    # saved in percentage | ranges 0 - 100
    progress = models.IntegerField(default=0)

    institute = models.ForeignKey(to="access.InstitutionDetail",
                                  on_delete=models.SET_NULL,
                                  **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)

    def handle_started_learning(self):
        """Handles the fact that user has opened and started learning."""

        self.last_accessed_on = datetime.now()
        self.save()

    def handle_user_enrolled(self):
        """Handles the chain reaction that user has enrolled to a course."""
        
        kwargs = {"parent_tracker": self, "created_by": self.created_by}

        from apps.learning.models import JobEligibleSkill
        for module in JobEligibleSkill.objects.get(id=self.entity.id).courses.all():
           
            UserJobEligibleSkillCourseTracker.objects.filter(entity=module, **kwargs).delete()
            
            tracker = UserJobEligibleSkillCourseTracker.objects.create(entity=module, **kwargs)
            # chain of responsibility
            tracker.handle_user_enrolled()

        for module in JobEligibleSkill.objects.get(id=self.entity.id).learning_paths.all():
           
            UserJobEligibleSkillLearningPathTracker.objects.filter(entity=module, **kwargs).delete()
            
            tracker = UserJobEligibleSkillLearningPathTracker.objects.create(entity=module, **kwargs)
            # chain of responsibility
            tracker.handle_user_enrolled()
        
        for module in JobEligibleSkill.objects.get(id=self.entity.id).certification_paths.all():
           
            UserJobEligibleSkillCertificatePathTracker.objects.filter(entity=module, **kwargs).delete()
            
            tracker = UserJobEligibleSkillCertificatePathTracker.objects.create(entity=module, **kwargs)
            # chain of responsibility
            tracker.handle_user_enrolled()

    def handle_child_modified(self):
        """Chain of responsibility from the bottom up."""

        self.progress = (
            UserJobEligibleSkillCourseTracker.objects.filter(
                parent_tracker=self, progress__gt=0
            ).count()
            / UserJobEligibleSkillCourseTracker.objects.filter(parent_tracker=self).count()
        ) * 100
        self.save()


class UserJobEligibleSkillCourseTracker(BaseModel):
    """
    Model used to track the progress of user under a given learning path course.
    The `created_by` column is used to hold the user.

    This is created when the user purchases the lp course.
    """

    entity = models.ForeignKey(to="learning.Course", on_delete=models.CASCADE)

    valid_till = models.DateField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)

    last_accessed_on = models.DateTimeField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    
    # parents
    parent_tracker = models.ForeignKey(to=UserJobEligibleSkillTracker, on_delete=models.CASCADE, null=True)

    # saved in percentage | ranges 0 - 100
    progress = models.IntegerField(default=0)

    institute = models.ForeignKey(to="access.InstitutionDetail",
                                  on_delete=models.SET_NULL,
                                  **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)

    def handle_child_modified(self):
        """Chain of responsibility from the bottom up."""

        self.progress = (
            UserJobEligibleSkillCourseModuleTracker.objects.filter(
                parent_tracker=self, progress=100
            ).count()
            / UserJobEligibleSkillCourseModuleTracker.objects.filter(parent_tracker=self).count()
        ) * 100
        self.save()

        # chain of responsibility
        self.parent_tracker.handle_child_modified()

    def handle_user_enrolled(self):
        """Chain of responsibility."""

        kwargs = {"parent_tracker": self, "created_by": self.created_by}

        from apps.learning.models import CourseModule

        for module in CourseModule.objects.filter(course=self.entity):
            UserJobEligibleSkillCourseModuleTracker.objects.filter(entity=module, **kwargs).delete()

            tracker = UserJobEligibleSkillCourseModuleTracker.objects.create(entity=module, **kwargs)
            # chain of responsibility
            tracker.handle_user_enrolled()

   
class UserJobEligibleSkillCourseModuleTracker(BaseModel):
    """Tracker for a `CourseModule` under a `UserSubscriptionPlanTracker` and a `User`."""

    # module
    entity = models.ForeignKey(to="learning.CourseModule", on_delete=models.CASCADE)

    # parents
    parent_tracker = models.ForeignKey(to=UserJobEligibleSkillCourseTracker, on_delete=models.CASCADE)

    # run time calculated
    progress = models.IntegerField(default=0)

    def handle_child_modified(self):
        """Chain of responsibility from the bottom up."""

        self.progress = (
            UserJobEligibleSkillCourseSubModuleTracker.objects.filter(
                parent_tracker=self, progress=100
            ).count()
            / UserJobEligibleSkillCourseSubModuleTracker.objects.filter(parent_tracker=self).count()
        ) * 100
        self.save()

        # chain of responsibility
        self.parent_tracker.handle_child_modified()

    def handle_user_enrolled(self):
        """Chain of responsibility."""

        kwargs = {"parent_tracker": self, "created_by": self.created_by}

        from apps.learning.models import CourseSubModule

        for sub_module in CourseSubModule.objects.filter(module=self.entity):
            UserJobEligibleSkillCourseSubModuleTracker.objects.filter(
                entity=sub_module, **kwargs
            ).delete()

            tracker = UserJobEligibleSkillCourseSubModuleTracker.objects.create(
                entity=sub_module, **kwargs
            )

            # chain of responsibility
            tracker.handle_user_enrolled()


class UserJobEligibleSkillCourseSubModuleTracker(BaseModel):
    """Tracker for a `CourseSubModule` under a `UserSubscriptionPlanCourseModuleTracker` and `User`."""

    # sub-module
    entity = models.ForeignKey(to="learning.CourseSubModule", on_delete=models.CASCADE)

    # parents
    parent_tracker = models.ForeignKey(
        to=UserJobEligibleSkillCourseModuleTracker, on_delete=models.CASCADE
    )

    # run time calculated
    progress = models.IntegerField(default=0)

    def handle_user_enrolled(self):
        """Chain of responsibility."""

        pass

    def handle_viewed(self):
        """Handles the fact that the user has viewed the tracker."""

        self.progress = 100
        self.save()

        # chain of responsibility
        self.parent_tracker.handle_child_modified()

# Learning Path Course Trackers
class UserJobEligibleSkillLearningPathTracker(BaseModel):
    """
    Model used to track the progress of user under a given learning path course.
    The `created_by` column is used to hold the user.

    This is created when the user purchases the lp course.
    """

    entity = models.ForeignKey(to="learning.learningpath", on_delete=models.CASCADE)

    valid_till = models.DateField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)

    last_accessed_on = models.DateTimeField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)

    # parents
    parent_tracker = models.ForeignKey(to=UserJobEligibleSkillTracker, on_delete=models.CASCADE, null=True)

    # saved in percentage | ranges 0 - 100
    progress = models.IntegerField(default=0)

    institute = models.ForeignKey(to="access.InstitutionDetail",
                                  on_delete=models.SET_NULL,
                                  **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)

    def handle_started_learning(self):
        """Handles the fact that user has opened and started learning."""

        self.last_accessed_on = datetime.now()
        self.save()

    def handle_user_enrolled(self):
        """Handles the chain reaction that user has enrolled to a course."""
        
        kwargs = {"parent_tracker": self, "created_by": self.created_by}

        from apps.learning.models import LearningPathCourse
        for module in LearningPathCourse.objects.filter(learning_path=self.entity):
           
            UserJobEligibleSkillLearningPathCourseTracker.objects.filter(entity=module.course, **kwargs).delete()
            
            tracker = UserJobEligibleSkillLearningPathCourseTracker.objects.create(entity=module.course, **kwargs)
            # chain of responsibility
            tracker.handle_user_enrolled()


    def handle_child_modified(self):
        """Chain of responsibility from the bottom up."""

        self.progress = (
            UserJobEligibleSkillLearningPathCourseTracker.objects.filter(
                parent_tracker=self, progress__gt=0
            ).count()
            / UserJobEligibleSkillLearningPathCourseTracker.objects.filter(parent_tracker=self).count()
        ) * 100
        self.save()


class UserJobEligibleSkillLearningPathCourseTracker(BaseModel):
    """
    Model used to track the progress of user under a given learning path course.
    The `created_by` column is used to hold the user.

    This is created when the user purchases the lp course.
    """

    entity = models.ForeignKey(to="learning.Course", on_delete=models.CASCADE)

    valid_till = models.DateField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)

    last_accessed_on = models.DateTimeField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    
    # parents
    parent_tracker = models.ForeignKey(to=UserJobEligibleSkillLearningPathTracker, on_delete=models.CASCADE, null=True)

    # saved in percentage | ranges 0 - 100
    progress = models.IntegerField(default=0)

    institute = models.ForeignKey(to="access.InstitutionDetail",
                                  on_delete=models.SET_NULL,
                                  **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)

    def handle_child_modified(self):
        """Chain of responsibility from the bottom up."""

        self.progress = (
            UserJobEligibleSkillLearningPathCourseModuleTracker.objects.filter(
                parent_tracker=self, progress=100
            ).count()
            / UserJobEligibleSkillLearningPathCourseModuleTracker.objects.filter(parent_tracker=self).count()
        ) * 100
        self.save()

        # chain of responsibility
        self.parent_tracker.handle_child_modified()

    def handle_user_enrolled(self):
        """Chain of responsibility."""

        kwargs = {"parent_tracker": self, "created_by": self.created_by}

        from apps.learning.models import CourseModule

        for module in CourseModule.objects.filter(course=self.entity):
            UserJobEligibleSkillLearningPathCourseModuleTracker.objects.filter(entity=module, **kwargs).delete()

            tracker = UserJobEligibleSkillLearningPathCourseModuleTracker.objects.create(entity=module, **kwargs)
            # chain of responsibility
            tracker.handle_user_enrolled()

   
class UserJobEligibleSkillLearningPathCourseModuleTracker(BaseModel):
    """Tracker for a `CourseModule` under a `UserSubscriptionPlanLearningPathCourseTracker` and a `User`."""

    # module
    entity = models.ForeignKey(to="learning.CourseModule", on_delete=models.CASCADE)

    # parents
    parent_tracker = models.ForeignKey(to=UserJobEligibleSkillLearningPathCourseTracker, on_delete=models.CASCADE)

    # run time calculated
    progress = models.IntegerField(default=0)

    def handle_child_modified(self):
        """Chain of responsibility from the bottom up."""

        self.progress = (
            UserJobEligibleSkillLearningPathCourseSubModuleTracker.objects.filter(
                parent_tracker=self, progress=100
            ).count()
            / UserJobEligibleSkillLearningPathCourseSubModuleTracker.objects.filter(parent_tracker=self).count()
        ) * 100
        self.save()

        # chain of responsibility
        self.parent_tracker.handle_child_modified()

    def handle_user_enrolled(self):
        """Chain of responsibility."""

        kwargs = {"parent_tracker": self, "created_by": self.created_by}

        from apps.learning.models import CourseSubModule

        for sub_module in CourseSubModule.objects.filter(module=self.entity):
            UserJobEligibleSkillLearningPathCourseSubModuleTracker.objects.filter(
                entity=sub_module, **kwargs
            ).delete()

            tracker = UserJobEligibleSkillLearningPathCourseSubModuleTracker.objects.create(
                entity=sub_module, **kwargs
            )
            # chain of responsibility
            tracker.handle_user_enrolled()

class UserJobEligibleSkillLearningPathCourseSubModuleTracker(BaseModel):
    """Tracker for a `CourseSubModule` under a `UserSubscriptionPlanLearningPathCourseModuleTracker` and `User`."""

    # sub-module
    entity = models.ForeignKey(to="learning.CourseSubModule", on_delete=models.CASCADE)

    # parents
    parent_tracker = models.ForeignKey(
        to=UserJobEligibleSkillLearningPathCourseModuleTracker, on_delete=models.CASCADE
    )

    # run time calculated
    progress = models.IntegerField(default=0)

    def handle_user_enrolled(self):
        """Chain of responsibility."""

        pass

    def handle_viewed(self):
        """Handles the fact that the user has viewed the tracker."""

        self.progress = 100
        self.save()

        # chain of responsibility
        self.parent_tracker.handle_child_modified()


# Advanced Learning Path Course Trackers (certificate path Trackers)
class UserJobEligibleSkillCertificatePathTracker(BaseModel):
    """
    Model used to track the progress of user under a given certificate path learning path course.
    The `created_by` column is used to hold the user.

    This is created when the user purchases the certificate path learning path course.
    """

    entity = models.ForeignKey(to="learning.CertificationPath", on_delete=models.CASCADE)

    valid_till = models.DateField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)

    last_accessed_on = models.DateTimeField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)

    # parents
    parent_tracker = models.ForeignKey(to=UserJobEligibleSkillTracker, on_delete=models.CASCADE, null=True)

    # saved in percentage | ranges 0 - 100
    progress = models.IntegerField(default=0)

    institute = models.ForeignKey(to="access.InstitutionDetail",
                                  on_delete=models.SET_NULL,
                                  **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)

    def handle_started_learning(self):
        """Handles the fact that user has opened and started learning."""

        self.last_accessed_on = datetime.now()
        self.save()

    def handle_user_enrolled(self):
        """Handles the chain reaction that user has enrolled to a course."""

        kwargs = {"parent_tracker": self, "created_by": self.created_by}

        from apps.learning.models import CertificationPathLearningPath

        for module in CertificationPathLearningPath.objects.filter(certification_path=self.entity):
            UserJobEligibleSkillCertificatePathLearningPathCourseTracker.objects.filter(entity=module.learning_path, **kwargs).delete()

            tracker = UserJobEligibleSkillCertificatePathLearningPathCourseTracker.objects.create(entity=module.learning_path, **kwargs)

            # chain of responsibility
            tracker.handle_user_enrolled()

    def handle_child_modified(self):
        """Chain of responsibility from the bottom up."""

        self.progress = (
            UserJobEligibleSkillCertificatePathLearningPathCourseTracker.objects.filter(
                parent_tracker=self, progress__gt=0
            ).count()
            / UserJobEligibleSkillCertificatePathLearningPathCourseTracker.objects.filter(parent_tracker=self).count()
        ) * 100
        self.save()


class UserJobEligibleSkillCertificatePathLearningPathCourseTracker(BaseModel):
    """
    Model used to track the progress of user under a given certificate path learning path course.
    The `created_by` column is used to hold the user.

    This is created when the user purchases the certificate path learning path course.
    """

    entity = models.ForeignKey(to="learning.learningpath", on_delete=models.CASCADE)

    valid_till = models.DateField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)

    last_accessed_on = models.DateTimeField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    
    # parents
    parent_tracker = models.ForeignKey(to=UserJobEligibleSkillCertificatePathTracker, on_delete=models.CASCADE, null=True)

    # saved in percentage | ranges 0 - 100
    progress = models.IntegerField(default=0)

    institute = models.ForeignKey(to="access.InstitutionDetail",
                                  on_delete=models.SET_NULL,
                                  **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)

    def handle_started_learning(self):
        """Handles the fact that user has opened and started learning."""

        self.last_accessed_on = datetime.now()
        self.save()

    def handle_user_enrolled(self):
        """Handles the chain reaction that user has enrolled to a course."""

        kwargs = {"parent_tracker": self, "created_by": self.created_by}

        from apps.learning.models import LearningPathCourse

        for module in LearningPathCourse.objects.filter(learning_path=self.entity):

            UserJobEligibleSkillCertificatePathCourseTracker.objects.filter(entity=module.course, **kwargs).delete()

            tracker = UserJobEligibleSkillCertificatePathCourseTracker.objects.create(entity=module.course, **kwargs)
            
            # chain of responsibility
            tracker.handle_user_enrolled()

    def handle_child_modified(self):
        """Chain of responsibility from the bottom up."""

        self.progress = (
            UserJobEligibleSkillCertificatePathCourseTracker.objects.filter(
                parent_tracker=self, progress=100
            ).count()
            / UserJobEligibleSkillCertificatePathCourseTracker.objects.filter(parent_tracker=self).count()
        ) * 100
        self.save()

class UserJobEligibleSkillCertificatePathCourseTracker(BaseModel):
    """
    Model used to track the progress of user under a given certificate path course.
    The `created_by` column is used to hold the user. 

    This is created when the user purchases the certificate path course.
    """

    entity = models.ForeignKey(to="learning.Course", on_delete=models.CASCADE)

    valid_till = models.DateField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)

    last_accessed_on = models.DateTimeField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)

    # parents
    parent_tracker = models.ForeignKey(to=UserJobEligibleSkillCertificatePathLearningPathCourseTracker, on_delete=models.CASCADE, null=True)

    # saved in percentage | ranges 0 - 100
    progress = models.IntegerField(default=0)

    institute = models.ForeignKey(to="access.InstitutionDetail",
                                  on_delete=models.SET_NULL,
                                  **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)

    def handle_started_learning(self):
        """Handles the fact that user has opened and started learning."""

        self.last_accessed_on = datetime.now()
        self.save()

    def handle_user_enrolled(self):
        """Handles the chain reaction that user has enrolled to a course."""

        kwargs = {"parent_tracker": self, "created_by": self.created_by}

        from apps.learning.models import CourseModule

        for module in CourseModule.objects.filter(course=self.entity):
            UserJobEligibleSkillCertificatePathCourseModuleTracker.objects.filter(entity=module, **kwargs).delete()

            tracker = UserJobEligibleSkillCertificatePathCourseModuleTracker.objects.create(entity=module, **kwargs)

            # chain of responsibility
            tracker.handle_user_enrolled()

    def handle_child_modified(self):
        """Chain of responsibility from the bottom up."""

        self.progress = (
            UserJobEligibleSkillCertificatePathCourseModuleTracker.objects.filter(
                parent_tracker=self, progress=100
            ).count()
            / UserJobEligibleSkillCertificatePathCourseModuleTracker.objects.filter(parent_tracker=self).count()
        ) * 100
        self.save()
    
class UserJobEligibleSkillCertificatePathCourseModuleTracker(BaseModel):
    """Tracker for a `CourseModule` under a `UserSubscriptionPlanCertificatePathCourseTracker` and a `User`."""

    # module
    entity = models.ForeignKey(to="learning.CourseModule", on_delete=models.CASCADE)

    # parents
    parent_tracker = models.ForeignKey(to=UserJobEligibleSkillCertificatePathCourseTracker, on_delete=models.CASCADE, null=True)

    # run time calculated
    progress = models.IntegerField(default=0)

    def handle_child_modified(self):
        """Chain of responsibility from the bottom up."""

        self.progress = (
            UserJobEligibleSkillCertificatePathCourseSubModuleTracker.objects.filter(
                parent_tracker=self, progress=100
            ).count()
            / UserJobEligibleSkillCertificatePathCourseSubModuleTracker.objects.filter(parent_tracker=self).count()
        ) * 100
        self.save()

        # chain of responsibility
        self.parent_tracker.handle_child_modified()

    def handle_user_enrolled(self):
        """Chain of responsibility."""

        kwargs = {"parent_tracker": self, "created_by": self.created_by}

        from apps.learning.models import CourseSubModule

        for sub_module in CourseSubModule.objects.filter(module=self.entity):
            UserJobEligibleSkillCertificatePathCourseSubModuleTracker.objects.filter(
                entity=sub_module, **kwargs
            ).delete()

            tracker = UserJobEligibleSkillCertificatePathCourseSubModuleTracker.objects.create(
                entity=sub_module, **kwargs
            )

            # chain of responsibility
            tracker.handle_user_enrolled()

class UserJobEligibleSkillCertificatePathCourseSubModuleTracker(BaseModel):
    """Tracker for a `CourseSubModule` under a `UserSubscriptionPlanCertificatePathCourseModuleTracker` and `User`."""

    # sub-module
    entity = models.ForeignKey(to="learning.CourseSubModule", on_delete=models.CASCADE)

    # parents
    parent_tracker = models.ForeignKey(
        to=UserJobEligibleSkillCertificatePathCourseModuleTracker, on_delete=models.CASCADE, null=True
    )

    # run time calculated
    progress = models.IntegerField(default=0)

    def handle_user_enrolled(self):
        """Chain of responsibility."""

        pass

    def handle_viewed(self):
        """Handles the fact that the user has viewed the tracker."""

        self.progress = 100
        self.save()

        # chain of responsibility
        self.parent_tracker.handle_child_modified()