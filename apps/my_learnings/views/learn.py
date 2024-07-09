from apps.common.serializers import simple_serialize_instance, simple_serialize_foreignkey_instance
from apps.common.views.api import AppAPIView
from apps.common.views.api.generic import AbstractLookUpFieldMixin
from apps.learning.models.course import CourseSubModule
from apps.web_portal.models.assessment import UserAssessmentResult
from ...common.helpers import get_file_field_url
from apps.my_learnings.models import UserCourseTracker, UserLearningPathTracker, UserCertificatePathTracker, UserSkillTracker
from apps.my_learnings.models.trackers import (
    UserCourseModuleTracker,
    UserCourseSubModuleTracker,
    UserJobEligibleSkillCertificatePathCourseModuleTracker,
    UserJobEligibleSkillCertificatePathCourseSubModuleTracker,
    UserJobEligibleSkillCertificatePathCourseTracker,
    UserJobEligibleSkillCertificatePathLearningPathCourseTracker,
    UserJobEligibleSkillCertificatePathTracker,
    UserJobEligibleSkillCourseModuleTracker,
    UserJobEligibleSkillCourseSubModuleTracker,
    UserJobEligibleSkillLearningPathCourseModuleTracker,
    UserJobEligibleSkillLearningPathCourseSubModuleTracker,
    UserJobEligibleSkillLearningPathCourseTracker,
    UserJobEligibleSkillLearningPathTracker,
    UserJobEligibleSkillTracker,
    UserJobEligibleSkillCourseTracker,
    UserLearningPathCourseTracker,
    UserLearningPathCourseModuleTracker,
    UserLearningPathCourseSubModuleTracker,
    UserCertificatePathLearningPathCourseTracker,
    UserCertificatePathCourseTracker,
    UserCertificatePathCourseModuleTracker,
    UserCertificatePathCourseSubModuleTracker,
    StudentEnrolledCourseModuleTracker,
    StudentEnrolledSubModuleTracker,
    StudentEnrolledCourseTracker,
    UserMMLCourseTracker,
    UserSkillCertificatePathCourseModuleTracker,
    UserSkillCertificatePathCourseSubModuleTracker,
    UserSkillCertificatePathCourseTracker,
    UserSkillCertificatePathLearningPathCourseTracker,
    UserSkillCertificatePathTracker,
    UserSkillCourseTracker,
    UserSkillCourseModuleTracker,
    UserSkillCourseSubModuleTracker,
    UserSkillLearningPathCourseModuleTracker,
    UserSkillLearningPathCourseSubModuleTracker,
    UserSkillLearningPathCourseTracker,
    UserSkillLearningPathTracker,
    UserSubscriptionPlanTracker,
    UserSubscriptionPlanCourseTracker,
    UserSubscriptionPlanCourseModuleTracker,
    UserSubscriptionPlanCourseSubModuleTracker,
    StudentEnrolledCertificatePathCourseModuleTracker,
    StudentEnrolledCertificatePathCourseSubModuleTracker,
    StudentEnrolledCertificatePathCourseTracker,
    StudentEnrolledCertificatePathLearningPathCourseTracker,
    StudentEnrolledCertificatePathTracker,
    StudentEnrolledCourseModuleTracker,
    StudentEnrolledLearningPathCourseModuleTracker,
    StudentEnrolledLearningPathCourseSubModuleTracker,
    StudentEnrolledLearningPathCourseTracker,
    StudentEnrolledLearningPathTracker,
    StudentEnrolledSubModuleTracker,
    UserSubscriptionPlanCertificatePathCourseModuleTracker,
    UserSubscriptionPlanCertificatePathCourseSubModuleTracker,
    UserSubscriptionPlanCertificatePathCourseTracker,
    UserSubscriptionPlanCertificatePathLearningPathCourseTracker,
    UserSubscriptionPlanCertificatePathTracker,
    UserSubscriptionPlanLearningPathCourseModuleTracker,
    UserSubscriptionPlanLearningPathCourseSubModuleTracker,
    UserSubscriptionPlanLearningPathCourseTracker,
    UserSubscriptionPlanLearningPathTracker,
    UserBlendedLearningPathTracker,
    UserBlendedLearningPathCourseTracker,
    UserBlendedLearningPathCourseModuleTracker,
    UserBlendedLearningPathCourseSubModuleTracker
)
from apps.learning.models import LearningRole, Skill
from apps.learning.models import BlendedLearningUserEnrollCourseDetails

def get_module_trackers_data(user, course_tracker: UserCourseTracker):
    """
    Returns the data for module trackers inside the course tracker.

    This is used in `UserLearningTrackerStartAPIView` and the
    detail page for the modules inside the page.
    """

    data = []
    for module_tracker in UserCourseModuleTracker.objects.filter(
        parent_tracker=course_tracker,
    ).order_by("entity__position"):
        module = module_tracker.entity
        module_tracker_data = simple_serialize_instance(
            instance=module_tracker,
            keys=[
                "uuid",
                "progress",
            ],
            parent_data={
                "sub_module_trackers": [],
                "entity": simple_serialize_instance(
                    instance=module,
                    keys=[
                        "uuid",
                        "identity",
                    ],
                ),
            },
        )

        for sub_module_tracker in UserCourseSubModuleTracker.objects.filter(
            parent_tracker=module_tracker
        ).order_by("entity__position"):
            sub_module = sub_module_tracker.entity
            module_tracker_data["sub_module_trackers"].append(
                simple_serialize_instance(
                    instance=sub_module_tracker,
                    keys=[
                        "uuid",
                        "progress",
                    ],
                    parent_data={
                        "entity": simple_serialize_instance(
                            instance=sub_module,
                            keys=[
                                "id",
                                "uuid",
                                "identity",
                                "description",
                                "duration",
                                "position",
                                "assessmentID",
                                
                            ],
                        ),
                        "resources": sub_module.get_resources(),
                        "is_in_bookmark": sub_module.is_in_bookmark(user),

                    },
                )
            )

        data.append(module_tracker_data)

    return data

def get_module_learning_path_trackers_data(user, lp_tracker: UserLearningPathTracker):
    """
    Returns the data for module trackers inside the course tracker.

    This is used in `UserLearningTrackerStartAPIView` and the
    detail page for the modules inside the page.
    """

    data = []
    for course_tracker in UserLearningPathCourseTracker.objects.filter(parent_tracker=lp_tracker):
        course = course_tracker.entity
        course_data = simple_serialize_instance(
            instance=course_tracker,
            keys=[
                "uuid",
                "progress",
            ],
            parent_data={
                "module_trackers": [],
                "entity": simple_serialize_instance(
                    instance=course,
                    keys=[
                        "uuid",
                        "identity",
                        "description",
                        "duration",
                    ],
                    parent_data={
                        "image": get_file_field_url(course, "image")
                    }
                ),
            },
        )

        for module_tracker in UserLearningPathCourseModuleTracker.objects.filter(parent_tracker=course_tracker).order_by(
                "entity__position"):
            module = module_tracker.entity
            module_data = simple_serialize_instance(
                instance=module_tracker,
                keys=[
                    "uuid",
                    "progress",
                ],
                parent_data={
                    "sub_module_trackers": [],
                    "entity": simple_serialize_instance(
                        instance=module,
                        keys=[
                            "uuid",
                            "identity",
                        ],
                    ),
                },
            )

            for sub_module_tracker in UserLearningPathCourseSubModuleTracker.objects.filter(
                    parent_tracker=module_tracker).order_by("entity__position"):
                sub_module = sub_module_tracker.entity
                sub_module_data = simple_serialize_instance(
                    instance=sub_module_tracker,
                    keys=[
                        "uuid",
                        "progress",
                    ],
                    parent_data={
                        "entity": simple_serialize_instance(
                            instance=sub_module,
                            keys=[
                                "id",
                                "uuid",
                                "identity",
                                "description",
                                "duration",
                                "position",
                            ],
                        ),
                        "resources": sub_module.get_resources(),
                        "is_in_bookmark": sub_module.is_in_bookmark(user),
                    },
                )
                module_data["sub_module_trackers"].append(sub_module_data)

            course_data["module_trackers"].append(module_data)

        data.append(course_data)

    return data



def get_module_certificate_path_trackers_data(user, cp_tracker: UserCertificatePathTracker):
    """
    Returns the data for module trackers inside the course tracker.

    This is used in `UserLearningTrackerStartAPIView` and the
    detail page for the modules inside the page.
    """

    data = []
    for cpath_tracker in UserCertificatePathLearningPathCourseTracker.objects.filter(parent_tracker=cp_tracker):
        lp = cpath_tracker.entity
        module_tracker_data = simple_serialize_instance(
            instance=cpath_tracker,
            keys=[
                "uuid",
                "progress",
            ],
            parent_data={
                "course_trackers": [],
                # "module_trackers": [],
                # "sub_module_trackers": [],
                "entity": simple_serialize_instance(
                    instance=lp,
                    keys=[
                        "uuid",
                        "identity",
                        "description",
                        "duration",
                    ],
                    parent_data={
                        "image": get_file_field_url(lp, "image")
                    }
                ),
            },
        )

        for cp_course_tracker in UserCertificatePathCourseTracker.objects.filter(parent_tracker=cpath_tracker):
            cp_course_module = cp_course_tracker.entity
            cp_module_data = simple_serialize_instance(
                instance=cp_course_tracker,
                keys=[
                    "uuid",
                    "progress",
                ],
                parent_data={
                    # "cp_course_trackers": [],
                    "module_trackers": [],
                    # "sub_module_trackers": [],
                    "entity": simple_serialize_instance(
                        instance=cp_course_module,
                        keys=[
                            "uuid",
                            "identity",
                            "description",
                            "duration",
                        ],
                        parent_data={
                            "image": get_file_field_url(cp_course_module, "image")
                        }
                    ),
                },
            )


            for module_tracker in UserCertificatePathCourseModuleTracker.objects.filter(parent_tracker=cp_course_tracker).order_by(
                    "entity__position"):
                module = module_tracker.entity
                module_data = simple_serialize_instance(
                    instance=module_tracker,
                    keys=[
                        "uuid",
                        "progress",
                    ],
                    parent_data={
                        # "cp_course_trackers": [],
                        # "module_tracker": [],
                        "sub_module_trackers": [],
                        "entity": simple_serialize_instance(
                            instance=module,
                            keys=[
                                "uuid",
                                "identity",
                            ],
                        ),
                    },
                )

                for sub_module_tracker in UserCertificatePathCourseSubModuleTracker.objects.filter(
                        parent_tracker=module_tracker).order_by("entity__position"):
                    sub_module = sub_module_tracker.entity
                    sub_module_data = simple_serialize_instance(
                        instance=sub_module_tracker,
                        keys=[
                            "uuid",
                            "progress",
                        ],
                        parent_data={
                            "entity": simple_serialize_instance(
                                instance=sub_module,
                                keys=[
                                    "uuid",
                                    "identity",
                                    "description",
                                    "duration",
                                    "position",
                                ],
                            ),
                            "resources": sub_module.get_resources(),
                            "is_in_bookmark": sub_module.is_in_bookmark(user),
                        },
                    )
                    module_data["sub_module_trackers"].append(sub_module_data)

                cp_module_data["module_trackers"].append(module_data)
            
            module_tracker_data["course_trackers"].append(cp_module_data)

        data.append(module_tracker_data)

    return data

class UserMMLCourseLearningTrackerStartAPIView(AbstractLookUpFieldMixin, AppAPIView):
    """View from where the user starts learning courses under his purchase."""

    get_object_model = UserMMLCourseTracker

    def get(self, *args, **kwargs):
        """Handle on get."""

        tracker = self.get_object(identifier=self.lookup_field)
        entity = tracker.entity

        data = simple_serialize_instance(
            instance=tracker,
            keys=[
                "uuid",
                "valid_till",
                "last_accessed_on",
                "progress",
                "created",
            ],
            parent_data={
                "entity": simple_serialize_instance(
                    instance=entity,
                    keys=[
                        "uuid",
                        "identity",
                        "code",
                        "duration",
                        "mml_sku_id",
                        "vm_name",
                    ],
                    parent_data={
                        "instructor": simple_serialize_instance(
                            instance=entity.author,
                            keys=["uuid", "identity", "designation"],
                        ),
                        "level": simple_serialize_instance(
                            instance=entity.level, keys=["uuid", "identity"]
                        ),
                    },
                )
            },
        )
        user = self.get_user()

        tracker.handle_started_learning()
        return self.send_response(data=data)

class UserLearningTrackerStartAPIView(AbstractLookUpFieldMixin, AppAPIView):
    """View from where the user starts learning courses under his purchase."""

    get_object_model = UserCourseTracker

    def get(self, *args, **kwargs):
        """Handle on get."""

        tracker = self.get_object(identifier=self.lookup_field)
        entity = tracker.entity

        course_submodules = CourseSubModule.objects.filter(module__course=tracker.entity)
        assessment_id = list(course_submodules.values_list('assessmentID', flat=True).distinct())
        if assessment_id:
            assessment_completed = UserAssessmentResult.objects.filter(
            assessment_id=assessment_id[0],
            user=self.get_user(),
            ).exists()
        else:
            assessment_completed = None

        data = simple_serialize_instance(
            instance=tracker,
            keys=[
                "uuid",
                "valid_till",
                "last_accessed_on",
                "progress",
                "created",
            ],
            parent_data={
                "entity": simple_serialize_instance(
                    instance=entity,
                    keys=[
                        "uuid",
                        "identity",
                        "code",
                        "duration",
                        "mml_sku_id",
                        "vm_name",
                    ],
                    parent_data={
                        "instructor": simple_serialize_instance(
                            instance=entity.author,
                            keys=["uuid", "identity", "designation"],
                        ),
                        "level": simple_serialize_instance(
                            instance=entity.level, keys=["uuid", "identity"]
                        ),
                    },
                )
            },
        )
        user = self.get_user()
        data["module_trackers"] = get_module_trackers_data(user,tracker)
        data["assessment_completed"] = assessment_completed

        tracker.handle_started_learning()
        return self.send_response(data=data)

class UserLearningPathTrackerStartAPIView(AbstractLookUpFieldMixin, AppAPIView):
    """View from where the user starts learning courses under his purchase."""

    get_object_model = UserLearningPathTracker

    def get(self, *args, **kwargs):
        """Handle on get."""

        tracker = self.get_object(identifier=self.lookup_field)
        entity = tracker.entity

        data = simple_serialize_instance(
            instance=tracker,
            keys=[
                "uuid",
                "valid_till",
                "last_accessed_on",
                "progress",
                "created",
            ],
            parent_data={
                "entity": simple_serialize_instance(
                    instance=entity,
                    keys=[
                        "uuid",
                        "identity",
                        "code",
                        "duration",
                        "mml_sku_id",
                        "vm_name",
                    ],
                    parent_data={
                        # "instructor": simple_serialize_instance(
                        #     instance=entity.author,
                        #     keys=["uuid", "identity", "designation"],
                        # ),
                        "level": simple_serialize_instance(
                            instance=entity.level, keys=["uuid", "identity"]
                        ),
                    },
                )
            },
        )
        user = self.get_user()
        data["lp_module_trackers"] = get_module_learning_path_trackers_data(user,tracker)

        tracker.handle_started_learning()
        return self.send_response(data=data)

class UserCertificatePathTrackerStartAPIView(AbstractLookUpFieldMixin, AppAPIView):
    """View from where the user starts learning courses under his purchase."""

    get_object_model = UserCertificatePathTracker

    def get(self, *args, **kwargs):
        """Handle on get."""

        tracker = self.get_object(identifier=self.lookup_field)
        entity = tracker.entity

        data = simple_serialize_instance(
            instance=tracker,
            keys=[
                "uuid",
                "valid_till",
                "last_accessed_on",
                "progress",
                "created",
            ],
            parent_data={
                "entity": simple_serialize_instance(
                    instance=entity,
                    keys=[
                        "uuid",
                        "identity",
                        "code",
                        "duration",
                        "mml_sku_id",
                        "vm_name",
                    ],
                    parent_data={
                        # "instructor": simple_serialize_instance(
                        #     instance=entity.author,
                        #     keys=["uuid", "identity", "designation"],
                        # ),
                        "level": simple_serialize_instance(
                            instance=entity.level, keys=["uuid", "identity"]
                        ),
                    },
                )
            },
        )
        user = self.get_user()
        data["cp_module_trackers"] = get_module_certificate_path_trackers_data(user,tracker)

        tracker.handle_started_learning()
        return self.send_response(data=data)


class UserVisitedMMLCourseTrackerAPIView(AbstractLookUpFieldMixin, AppAPIView):

    get_object_model = UserMMLCourseTracker

    def post(self, *args, **kwargs):
        """Handle on post."""

        tracker = self.get_object(identifier=self.lookup_field)
        tracker.handle_viewed()
        return self.send_response()

class UserVisitedCourseSubModuleTrackerAPIView(AbstractLookUpFieldMixin, AppAPIView):
    """Handles the fact that the user has visited a `UserCourseSubModuleTracker`."""

    get_object_model = UserCourseSubModuleTracker

    def post(self, *args, **kwargs):
        """Handle on post."""

        tracker = self.get_object(identifier=self.lookup_field)
        tracker.handle_viewed()
        return self.send_response()


# TODO: handle performance optimisations later
class UserVisitedCourseModuleTrackerAPIView(AbstractLookUpFieldMixin, AppAPIView):
    """Handles the fact that the user has visited a `UserCourseSubModuleTracker`."""

    get_object_model = UserCourseModuleTracker

    def post(self, *args, **kwargs):
        """Handle on post."""

        tracker = self.get_object(identifier=self.lookup_field)
        tracker.handle_viewed()
        return self.send_response()

#-------------------Learning Path Trackers---------------------#

class UserVisitedLearningPathCourseTrackerAPIView(AbstractLookUpFieldMixin, AppAPIView):
    """Handles the fact that the user has visited a `UserCourseSubModuleTracker`."""

    get_object_model = UserLearningPathCourseTracker

    def post(self, *args, **kwargs):
        """Handle on post."""

        tracker = self.get_object(identifier=self.lookup_field)
        tracker.handle_viewed()
        return self.send_response()


# TODO: handle performance optimisations later
class UserVisitedLearningPathCourseModuleTrackerAPIView(AbstractLookUpFieldMixin, AppAPIView):
    """Handles the fact that the user has visited a `UserCourseSubModuleTracker`."""

    get_object_model = UserLearningPathCourseModuleTracker

    def post(self, *args, **kwargs):
        """Handle on post."""

        tracker = self.get_object(identifier=self.lookup_field)
        tracker.handle_viewed()
        return self.send_response()
    
class UserVisitedLearningPathCourseSubModuleTrackerAPIView(AbstractLookUpFieldMixin, AppAPIView):
    """Handles the fact that the user has visited a `UserCourseSubModuleTracker`."""

    get_object_model = UserLearningPathCourseSubModuleTracker

    def post(self, *args, **kwargs):
        """Handle on post."""

        tracker = self.get_object(identifier=self.lookup_field)
        tracker.handle_viewed()
        return self.send_response()

#-------------------Certificate Learning Path Trackers---------------------#

class UserVisitedCertificatePathLearningPathTrackerAPIView(AbstractLookUpFieldMixin, AppAPIView):
    """Handles the fact that the user has visited a `UserCourseSubModuleTracker`."""

    get_object_model = UserCertificatePathLearningPathCourseTracker

    def post(self, *args, **kwargs):
        """Handle on post."""

        tracker = self.get_object(identifier=self.lookup_field)
        tracker.handle_viewed()
        return self.send_response()


# TODO: handle performance optimisations later
class UserVisitedCertificatePathLearningPathCourseTrackerAPIView(AbstractLookUpFieldMixin, AppAPIView):
    """Handles the fact that the user has visited a `UserCourseSubModuleTracker`."""

    get_object_model = UserCertificatePathCourseTracker

    def post(self, *args, **kwargs):
        """Handle on post."""

        tracker = self.get_object(identifier=self.lookup_field)
        tracker.handle_viewed()
        return self.send_response()
    
class UserVisitedCertificatePathLearningPathCourseModuleTrackerAPIView(AbstractLookUpFieldMixin, AppAPIView):
    """Handles the fact that the user has visited a `UserCourseSubModuleTracker`."""

    get_object_model = UserCertificatePathCourseModuleTracker

    def post(self, *args, **kwargs):
        """Handle on post."""

        tracker = self.get_object(identifier=self.lookup_field)
        tracker.handle_viewed()
        return self.send_response()
    
class UserVisitedCertificatePathLearningPathCourseSubModuleTrackerAPIView(AbstractLookUpFieldMixin, AppAPIView):
    """Handles the fact that the user has visited a `UserCourseSubModuleTracker`."""

    get_object_model = UserCertificatePathCourseSubModuleTracker

    def post(self, *args, **kwargs):
        """Handle on post."""

        tracker = self.get_object(identifier=self.lookup_field)
        tracker.handle_viewed()
        return self.send_response()
    
def get_module_student_trackers_data(user, course_tracker: StudentEnrolledCourseTracker):
    """
    Returns the data for module trackers inside the course tracker.

    This is used in `UserLearningTrackerStartAPIView` and the
    detail page for the modules inside the page.
    """

    data = []
    for module_tracker in StudentEnrolledCourseModuleTracker.objects.filter(
        parent_tracker=course_tracker,
    ).order_by("entity__position"):
        module = module_tracker.entity
        module_tracker_data = simple_serialize_instance(
            instance=module_tracker,
            keys=[
                "uuid",
                "progress",
            ],
            parent_data={
                "sub_module_trackers": [],
                "entity": simple_serialize_instance(
                    instance=module,
                    keys=[
                        "uuid",
                        "identity",
                    ],
                ),
            },
        )

        for sub_module_tracker in StudentEnrolledSubModuleTracker.objects.filter(
            parent_tracker=module_tracker
        ).order_by("entity__position"):
            sub_module = sub_module_tracker.entity
            module_tracker_data["sub_module_trackers"].append(
                simple_serialize_instance(
                    instance=sub_module_tracker,
                    keys=[
                        "uuid",
                        "progress",
                    ],
                    parent_data={
                        "entity": simple_serialize_instance(
                            instance=sub_module,
                            keys=[
                                "id",
                                "uuid",
                                "identity",
                                "description",
                                "duration",
                                "position",
                                "assessmentID",
                            ],
                        ),
                        "resources": sub_module.get_resources(),
                        "is_in_bookmark": sub_module.is_in_bookmark(user),

                    },
                )
            )

        data.append(module_tracker_data)

    return data

def get_module_student_learning_path_trackers_data(user, lp_tracker: StudentEnrolledLearningPathTracker):
    """
    Returns the data for module trackers inside the course tracker.

    This is used in `UserLearningTrackerStartAPIView` and the
    detail page for the modules inside the page.
    """

    data = []
    for course_tracker in StudentEnrolledLearningPathCourseTracker.objects.filter(parent_tracker=lp_tracker):
        course = course_tracker.entity
        course_data = simple_serialize_instance(
            instance=course_tracker,
            keys=[
                "uuid",
                "progress",
            ],
            parent_data={
                "module_trackers": [],
                "entity": simple_serialize_instance(
                    instance=course,
                    keys=[
                        "uuid",
                        "identity",
                        "description",
                        "duration",
                    ],
                    parent_data={
                        "image": get_file_field_url(course, "image")
                    }
                ),
            },
        )

        for module_tracker in StudentEnrolledLearningPathCourseModuleTracker.objects.filter(parent_tracker=course_tracker).order_by(
                "entity__position"):
            module = module_tracker.entity
            module_data = simple_serialize_instance(
                instance=module_tracker,
                keys=[
                    "uuid",
                    "progress",
                ],
                parent_data={
                    "sub_module_trackers": [],
                    "entity": simple_serialize_instance(
                        instance=module,
                        keys=[
                            "uuid",
                            "identity",
                        ],
                    ),
                },
            )

            for sub_module_tracker in StudentEnrolledLearningPathCourseSubModuleTracker.objects.filter(
                    parent_tracker=module_tracker).order_by("entity__position"):
                sub_module = sub_module_tracker.entity
                sub_module_data = simple_serialize_instance(
                    instance=sub_module_tracker,
                    keys=[
                        "uuid",
                        "progress",
                    ],
                    parent_data={
                        "entity": simple_serialize_instance(
                            instance=sub_module,
                            keys=[
                                "id",
                                "uuid",
                                "identity",
                                "description",
                                "duration",
                                "position",
                            ],
                        ),
                        "resources": sub_module.get_resources(),
                        "is_in_bookmark": sub_module.is_in_bookmark(user),
                    },
                )
                module_data["sub_module_trackers"].append(sub_module_data)

            course_data["module_trackers"].append(module_data)

        data.append(course_data)

    return data



def get_module_student_certificate_path_trackers_data(user, cp_tracker: StudentEnrolledCertificatePathTracker):
    """
    Returns the data for module trackers inside the course tracker.

    This is used in `UserLearningTrackerStartAPIView` and the
    detail page for the modules inside the page.
    """

    data = []
    for cpath_tracker in StudentEnrolledCertificatePathLearningPathCourseTracker.objects.filter(parent_tracker=cp_tracker):
        lp = cpath_tracker.entity
        module_tracker_data = simple_serialize_instance(
            instance=cpath_tracker,
            keys=[
                "uuid",
                "progress",
            ],
            parent_data={
                "course_trackers": [],
                # "module_trackers": [],
                # "sub_module_trackers": [],
                "entity": simple_serialize_instance(
                    instance=lp,
                    keys=[
                        "uuid",
                        "identity",
                        "description",
                        "duration",
                    ],
                    parent_data={
                        "image": get_file_field_url(lp, "image")
                    }
                ),
            },
        )

        for cp_course_tracker in StudentEnrolledCertificatePathCourseTracker.objects.filter(parent_tracker=cpath_tracker):
            cp_course_module = cp_course_tracker.entity
            cp_module_data = simple_serialize_instance(
                instance=cp_course_tracker,
                keys=[
                    "uuid",
                    "progress",
                ],
                parent_data={
                    # "cp_course_trackers": [],
                    "module_trackers": [],
                    # "sub_module_trackers": [],
                    "entity": simple_serialize_instance(
                        instance=cp_course_module,
                        keys=[
                            "uuid",
                            "identity",
                            "description",
                            "duration",
                        ],
                        parent_data={
                            "image": get_file_field_url(cp_course_module, "image")
                        }
                    ),
                },
            )


            for module_tracker in StudentEnrolledCertificatePathCourseModuleTracker.objects.filter(parent_tracker=cp_course_tracker).order_by(
                    "entity__position"):
                module = module_tracker.entity
                module_data = simple_serialize_instance(
                    instance=module_tracker,
                    keys=[
                        "uuid",
                        "progress",
                    ],
                    parent_data={
                        "sub_module_trackers": [],
                        "entity": simple_serialize_instance(
                            instance=module,
                            keys=[
                                "uuid",
                                "identity",
                            ],
                        ),
                    },
                )

                for sub_module_tracker in StudentEnrolledCertificatePathCourseSubModuleTracker.objects.filter(
                        parent_tracker=module_tracker).order_by("entity__position"):
                    sub_module = sub_module_tracker.entity
                    sub_module_data = simple_serialize_instance(
                        instance=sub_module_tracker,
                        keys=[
                            "uuid",
                            "progress",
                        ],
                        parent_data={
                            "entity": simple_serialize_instance(
                                instance=sub_module,
                                keys=[
                                    "id",
                                    "uuid",
                                    "identity",
                                    "description",
                                    "duration",
                                    "position",
                                ],
                            ),
                            "resources": sub_module.get_resources(),
                            "is_in_bookmark": sub_module.is_in_bookmark(user),
                        },
                    )
                    module_data["sub_module_trackers"].append(sub_module_data)

                cp_module_data["module_trackers"].append(module_data)
            
            module_tracker_data["course_trackers"].append(cp_module_data)

        data.append(module_tracker_data)

    return data

def get_module_learning_role_trackers_data(user, course_tracker: LearningRole):
    """
    Returns the data for module trackers inside the course tracker.

    This is used in `SubscriptionLearningTrackerStartAPIView` and the
    detail page for the modules inside the page.
    """
    data=[]
    for course_tracker in UserCourseTracker.objects.filter(entity__learning_role_id=course_tracker, created_by=user):
        course = course_tracker.entity
        course_data = simple_serialize_instance(
            instance=course_tracker,
            keys=[
                "uuid",
                "progress",
            ],
            parent_data={
                "module_trackers": [],
                "entity": simple_serialize_instance(
                    instance=course,
                    keys=[
                        "id",
                        "uuid",
                        "identity",
                        "description",
                        "duration",
                    ],
                    parent_data={
                        "image": get_file_field_url(course, "image")
                    }
                ),
            },
        )

        for module_tracker in UserCourseModuleTracker.objects.filter(parent_tracker=course_tracker).order_by(
                "entity__position"):
            module = module_tracker.entity
            module_data = simple_serialize_instance(
                instance=module_tracker,
                keys=[
                    "uuid",
                    "progress",
                ],
                parent_data={
                    "sub_module_trackers": [],
                    "entity": simple_serialize_instance(
                        instance=module,
                        keys=[
                            "uuid",
                            "identity",
                        ],
                    ),
                },
            )

            for sub_module_tracker in UserCourseSubModuleTracker.objects.filter(
                    parent_tracker=module_tracker).order_by("entity__position"):
                sub_module = sub_module_tracker.entity
                sub_module_data = simple_serialize_instance(
                    instance=sub_module_tracker,
                    keys=[
                        "uuid",
                        "progress",
                    ],
                    parent_data={
                        "entity": simple_serialize_instance(
                            instance=sub_module,
                            keys=[
                                "id",
                                "uuid",
                                "identity",
                                "description",
                                "duration",
                                "position",
                            ],
                        ),
                        "resources": sub_module.get_resources(),
                        "is_in_bookmark": sub_module.is_in_bookmark(user),
                    },
                )
                module_data["sub_module_trackers"].append(sub_module_data)

            course_data["module_trackers"].append(module_data)

        data.append(course_data)

    return data

def get_module_learning_role_learning_path_trackers_data(user, course_tracker: LearningRole):
    data = []
    for learning_path_tracker in UserLearningPathTracker.objects.filter(entity__learning_role_id=course_tracker, created_by=user):
        learning_path = learning_path_tracker.entity
        learning_path_data = simple_serialize_instance(
            instance=learning_path_tracker,
            keys=[
                "uuid",
                "progress",
            ],
            parent_data={
                "course_trackers": [],
                "entity": simple_serialize_instance(
                    instance=learning_path,
                    keys=[
                        "id",
                        "uuid",
                        "identity",
                        "description",
                        "duration",
                    ],
                    parent_data={
                        "image": get_file_field_url(learning_path, "image")
                    }
                ),
            },
        )
        for course_tracker in UserLearningPathCourseTracker.objects.filter(parent_tracker=learning_path_tracker):
            course = course_tracker.entity
            course_data = simple_serialize_instance(
                instance=course_tracker,
                keys=[
                    "uuid",
                    "progress",
                ],
                parent_data={
                    "module_trackers": [],
                    "entity": simple_serialize_instance(
                        instance=course,
                        keys=[
                            "id",
                            "uuid",
                            "identity",
                            "description",
                            "duration",
                        ],
                        parent_data={
                            "image": get_file_field_url(course, "image")
                        }
                    ),
                },
            )
            for module_tracker in UserLearningPathCourseModuleTracker.objects.filter(parent_tracker=course_tracker).order_by(
                "entity__position"):
                module = module_tracker.entity
                module_data = simple_serialize_instance(
                    instance=module_tracker,
                    keys=[
                        "uuid",
                        "progress",
                    ],
                    parent_data={
                        "sub_module_trackers": [],
                        "entity": simple_serialize_instance(
                            instance=module,
                            keys=[
                                "uuid",
                                "identity",
                            ],
                        ),
                    },
                )
                for sub_module_tracker in UserLearningPathCourseSubModuleTracker.objects.filter(
                    parent_tracker=module_tracker).order_by("entity__position"):
                    sub_module = sub_module_tracker.entity
                    sub_module_data = simple_serialize_instance(
                        instance=sub_module_tracker,
                        keys=[
                            "uuid",
                            "progress",
                        ],
                        parent_data={
                            "entity": simple_serialize_instance(
                                instance=sub_module,
                                keys=[
                                    "id",
                                    "uuid",
                                    "identity",
                                    "description",
                                    "duration",
                                    "position",
                                ],
                            ),
                            "resources": sub_module.get_resources(),
                            "is_in_bookmark": sub_module.is_in_bookmark(user),
                        },
                    )
                    module_data["sub_module_trackers"].append(sub_module_data)

                course_data["module_trackers"].append(module_data)

            learning_path_data["course_trackers"].append(course_data)

        data.append(learning_path_data) 

    return data

def get_module_learning_role_advance_learning_path_trackers_data(user, course_tracker: LearningRole):
    data = []
    for certification_path_tracker in UserCertificatePathTracker.objects.filter(entity__learning_role_id=course_tracker, created_by=user):
        certification_path = certification_path_tracker.entity
        certification_path_data = simple_serialize_instance(
            instance=certification_path_tracker,
            keys=[
                "uuid",
                "progress",
            ],
            parent_data={
                "learning_path_trackers": [],
                "entity": simple_serialize_instance(
                    instance=certification_path,
                    keys=[
                        "id",
                        "uuid",
                        "identity",
                        "description",
                        "duration",
                    ],
                    parent_data={
                        "image": get_file_field_url(certification_path, "image")
                    }
                ),
            },
        )
        for learning_path_tracker in UserCertificatePathLearningPathCourseTracker.objects.filter(parent_tracker=certification_path_tracker):
            learning_path = learning_path_tracker.entity
            learning_path_data = simple_serialize_instance(
                instance=learning_path_tracker,
                keys=[
                    "uuid",
                    "progress",
                ],
                parent_data={
                    "course_trackers": [],
                    "entity": simple_serialize_instance(
                        instance=learning_path,
                        keys=[
                            "id",
                            "uuid",
                            "identity",
                            "description",
                            "duration",
                        ],
                        parent_data={
                            "image": get_file_field_url(learning_path, "image")
                        }
                    ),
                },
            )
            for course_tracker in UserCertificatePathCourseTracker.objects.filter(parent_tracker=learning_path_tracker):
                course = course_tracker.entity
                course_data = simple_serialize_instance(
                    instance=course_tracker,
                    keys=[
                        "uuid",
                        "progress",
                    ],
                    parent_data={
                        "module_trackers": [],
                        "entity": simple_serialize_instance(
                            instance=course,
                            keys=[
                                "id",
                                "uuid",
                                "identity",
                                "description",
                                "duration",
                            ],
                            parent_data={
                                "image": get_file_field_url(course, "image")
                            }
                        ),
                    },
                )
                for module_tracker in UserCertificatePathCourseModuleTracker.objects.filter(parent_tracker=course_tracker).order_by(
                    "entity__position"):
                    module = module_tracker.entity
                    module_data = simple_serialize_instance(
                        instance=module_tracker,
                        keys=[
                            "uuid",
                            "progress",
                        ],
                        parent_data={
                            "sub_module_trackers": [],
                            "entity": simple_serialize_instance(
                                instance=module,
                                keys=[
                                    "uuid",
                                    "identity",
                                ],
                            ),
                        },
                    )
                    for sub_module_tracker in UserCertificatePathCourseSubModuleTracker.objects.filter(
                        parent_tracker=module_tracker).order_by("entity__position"):
                        sub_module = sub_module_tracker.entity
                        sub_module_data = simple_serialize_instance(
                            instance=sub_module_tracker,
                            keys=[
                                "uuid",
                                "progress",
                            ],
                            parent_data={
                                "entity": simple_serialize_instance(
                                    instance=sub_module,
                                    keys=[
                                        "id",
                                        "uuid",
                                        "identity",
                                        "description",
                                        "duration",
                                        "position",
                                    ],
                                ),
                                "resources": sub_module.get_resources(),
                                "is_in_bookmark": sub_module.is_in_bookmark(user),
                            },
                        )
                        module_data["sub_module_trackers"].append(sub_module_data)

                    course_data["module_trackers"].append(module_data)

                learning_path_data["course_trackers"].append(course_data)

            certification_path_data["learning_path_trackers"].append(learning_path_data)
        
        data.append(certification_path_data)
    
    return data

def get_module_skill_trackers_data(user, course_tracker: UserSkillTracker):
    """
    Returns the data for module trackers inside the course tracker.

    This is used in `SubscriptionLearningTrackerStartAPIView` and the
    detail page for the modules inside the page.
    """
    data=[]
    for course_tracker in UserSkillCourseTracker.objects.filter(parent_tracker=course_tracker, created_by=user):
        course = course_tracker.entity
        course_data = simple_serialize_instance(
            instance=course_tracker,
            keys=[
                "uuid",
                "progress",
            ],
            parent_data={
                "module_trackers": [],
                "entity": simple_serialize_instance(
                    instance=course,
                    keys=[
                        "uuid",
                        "identity",
                        "description",
                        "duration",
                    ],
                    parent_data={
                        "image": get_file_field_url(course, "image")
                    }
                ),
            },
        )

        for module_tracker in UserSkillCourseModuleTracker.objects.filter(parent_tracker=course_tracker).order_by(
                "entity__position"):
            module = module_tracker.entity
            module_data = simple_serialize_instance(
                instance=module_tracker,
                keys=[
                    "uuid",
                    "progress",
                ],
                parent_data={
                    "sub_module_trackers": [],
                    "entity": simple_serialize_instance(
                        instance=module,
                        keys=[
                            "uuid",
                            "identity",
                        ],
                    ),
                },
            )

            for sub_module_tracker in UserSkillCourseSubModuleTracker.objects.filter(
                    parent_tracker=module_tracker).order_by("entity__position"):
                sub_module = sub_module_tracker.entity
                sub_module_data = simple_serialize_instance(
                    instance=sub_module_tracker,
                    keys=[
                        "uuid",
                        "progress",
                    ],
                    parent_data={
                        "entity": simple_serialize_instance(
                            instance=sub_module,
                            keys=[
                                "id",
                                "uuid",
                                "identity",
                                "description",
                                "duration",
                                "position",
                            ],
                        ),
                        "resources": sub_module.get_resources(),
                        "is_in_bookmark": sub_module.is_in_bookmark(user),
                    },
                )
                module_data["sub_module_trackers"].append(sub_module_data)

            course_data["module_trackers"].append(module_data)

        data.append(course_data)

    return data

def get_module_skill_learning_path_trackers_data(user, course_tracker: UserSkillTracker):
    data = []
    for learning_path_tracker in UserSkillLearningPathTracker.objects.filter(parent_tracker=course_tracker, created_by=user):
        learning_path = learning_path_tracker.entity
        learning_path_data = simple_serialize_instance(
            instance=learning_path_tracker,
            keys=[
                "uuid",
                "progress",
            ],
            parent_data={
                "course_trackers": [],
                "entity": simple_serialize_instance(
                    instance=learning_path,
                    keys=[
                        "uuid",
                        "identity",
                        "description",
                        "duration",
                    ],
                    parent_data={
                        "image": get_file_field_url(learning_path, "image")
                    }
                ),
            },
        )
        for course_tracker in UserSkillLearningPathCourseTracker.objects.filter(parent_tracker=learning_path_tracker):
            course = course_tracker.entity
            course_data = simple_serialize_instance(
                instance=course_tracker,
                keys=[
                    "uuid",
                    "progress",
                ],
                parent_data={
                    "module_trackers": [],
                    "entity": simple_serialize_instance(
                        instance=course,
                        keys=[
                            "uuid",
                            "identity",
                            "description",
                            "duration",
                        ],
                        parent_data={
                            "image": get_file_field_url(course, "image")
                        }
                    ),
                },
            )
            for module_tracker in UserSkillLearningPathCourseModuleTracker.objects.filter(parent_tracker=course_tracker).order_by(
                "entity__position"):
                module = module_tracker.entity
                module_data = simple_serialize_instance(
                    instance=module_tracker,
                    keys=[
                        "uuid",
                        "progress",
                    ],
                    parent_data={
                        "sub_module_trackers": [],
                        "entity": simple_serialize_instance(
                            instance=module,
                            keys=[
                                "uuid",
                                "identity",
                            ],
                        ),
                    },
                )
                for sub_module_tracker in UserSkillLearningPathCourseSubModuleTracker.objects.filter(
                    parent_tracker=module_tracker).order_by("entity__position"):
                    sub_module = sub_module_tracker.entity
                    sub_module_data = simple_serialize_instance(
                        instance=sub_module_tracker,
                        keys=[
                            "uuid",
                            "progress",
                        ],
                        parent_data={
                            "entity": simple_serialize_instance(
                                instance=sub_module,
                                keys=[
                                    "id",
                                    "uuid",
                                    "identity",
                                    "description",
                                    "duration",
                                    "position",
                                ],
                            ),
                            "resources": sub_module.get_resources(),
                            "is_in_bookmark": sub_module.is_in_bookmark(user),
                        },
                    )
                    module_data["sub_module_trackers"].append(sub_module_data)

                course_data["module_trackers"].append(module_data)

            learning_path_data["course_trackers"].append(course_data)

        data.append(learning_path_data) 

    return data

def get_module_skill_advance_learning_path_trackers_data(user, course_tracker: UserSkillTracker):
    data = []
    for certification_path_tracker in UserSkillCertificatePathTracker.objects.filter(parent_tracker=course_tracker, created_by=user):
        certification_path = certification_path_tracker.entity
        certification_path_data = simple_serialize_instance(
            instance=certification_path_tracker,
            keys=[
                "uuid",
                "progress",
            ],
            parent_data={
                "learning_path_trackers": [],
                "entity": simple_serialize_instance(
                    instance=certification_path,
                    keys=[
                        "uuid",
                        "identity",
                        "description",
                        "duration",
                    ],
                    parent_data={
                        "image": get_file_field_url(certification_path, "image")
                    }
                ),
            },
        )
        for learning_path_tracker in UserSkillCertificatePathLearningPathCourseTracker.objects.filter(parent_tracker=certification_path_tracker):
            learning_path = learning_path_tracker.entity
            learning_path_data = simple_serialize_instance(
                instance=learning_path_tracker,
                keys=[
                    "uuid",
                    "progress",
                ],
                parent_data={
                    "course_trackers": [],
                    "entity": simple_serialize_instance(
                        instance=learning_path,
                        keys=[
                            "uuid",
                            "identity",
                            "description",
                            "duration",
                        ],
                        parent_data={
                            "image": get_file_field_url(learning_path, "image")
                        }
                    ),
                },
            )
            for course_tracker in UserSkillCertificatePathCourseTracker.objects.filter(parent_tracker=learning_path_tracker):
                course = course_tracker.entity
                course_data = simple_serialize_instance(
                    instance=course_tracker,
                    keys=[
                        "uuid",
                        "progress",
                    ],
                    parent_data={
                        "module_trackers": [],
                        "entity": simple_serialize_instance(
                            instance=course,
                            keys=[
                                "uuid",
                                "identity",
                                "description",
                                "duration",
                            ],
                            parent_data={
                                "image": get_file_field_url(course, "image")
                            }
                        ),
                    },
                )
                for module_tracker in UserSkillCertificatePathCourseModuleTracker.objects.filter(parent_tracker=course_tracker).order_by(
                    "entity__position"):
                    module = module_tracker.entity
                    module_data = simple_serialize_instance(
                        instance=module_tracker,
                        keys=[
                            "uuid",
                            "progress",
                        ],
                        parent_data={
                            "sub_module_trackers": [],
                            "entity": simple_serialize_instance(
                                instance=module,
                                keys=[
                                    "uuid",
                                    "identity",
                                ],
                            ),
                        },
                    )
                    for sub_module_tracker in UserSkillCertificatePathCourseSubModuleTracker.objects.filter(
                        parent_tracker=module_tracker).order_by("entity__position"):
                        sub_module = sub_module_tracker.entity
                        sub_module_data = simple_serialize_instance(
                            instance=sub_module_tracker,
                            keys=[
                                "uuid",
                                "progress",
                            ],
                            parent_data={
                                "entity": simple_serialize_instance(
                                    instance=sub_module,
                                    keys=[
                                        "id",
                                        "uuid",
                                        "identity",
                                        "description",
                                        "duration",
                                        "position",
                                    ],
                                ),
                                "resources": sub_module.get_resources(),
                                "is_in_bookmark": sub_module.is_in_bookmark(user),
                            },
                        )
                        module_data["sub_module_trackers"].append(sub_module_data)

                    course_data["module_trackers"].append(module_data)

                learning_path_data["course_trackers"].append(course_data)

            certification_path_data["learning_path_trackers"].append(learning_path_data)
        
        data.append(certification_path_data)
    
    return data


def get_module_subscription_trackers_data(user, course_tracker: UserSubscriptionPlanTracker):
    """
    Returns the data for module trackers inside the course tracker.

    This is used in `SubscriptionLearningTrackerStartAPIView` and the
    detail page for the modules inside the page.
    """
    data=[]
    for course_tracker in UserSubscriptionPlanCourseTracker.objects.filter(parent_tracker=course_tracker):
        course = course_tracker.entity
        course_data = simple_serialize_instance(
            instance=course_tracker,
            keys=[
                "uuid",
                "progress",
            ],
            parent_data={
                "module_trackers": [],
                "entity": simple_serialize_instance(
                    instance=course,
                    keys=[
                        "id",
                        "uuid",
                        "identity",
                        "description",
                        "duration",
                    ],
                    parent_data={
                        "image": get_file_field_url(course, "image")
                    }
                ),
            },
        )

        for module_tracker in UserSubscriptionPlanCourseModuleTracker.objects.filter(parent_tracker=course_tracker).order_by(
                "entity__position"):
            module = module_tracker.entity
            module_data = simple_serialize_instance(
                instance=module_tracker,
                keys=[
                    "uuid",
                    "progress",
                ],
                parent_data={
                    "sub_module_trackers": [],
                    "entity": simple_serialize_instance(
                        instance=module,
                        keys=[
                            "uuid",
                            "identity",
                        ],
                    ),
                },
            )

            for sub_module_tracker in UserSubscriptionPlanCourseSubModuleTracker.objects.filter(
                    parent_tracker=module_tracker).order_by("entity__position"):
                sub_module = sub_module_tracker.entity
                sub_module_data = simple_serialize_instance(
                    instance=sub_module_tracker,
                    keys=[
                        "uuid",
                        "progress",
                    ],
                    parent_data={
                        "entity": simple_serialize_instance(
                            instance=sub_module,
                            keys=[
                                "id",
                                "uuid",
                                "identity",
                                "description",
                                "duration",
                                "position",
                                "assessmentID",
                            ],
                        ),
                        "resources": sub_module.get_resources(),
                        "is_in_bookmark": sub_module.is_in_bookmark(user),
                    },
                )
                module_data["sub_module_trackers"].append(sub_module_data)

            course_data["module_trackers"].append(module_data)

        data.append(course_data)

    return data

def get_module_subscription_learning_path_trackers_data(user, course_tracker: UserSubscriptionPlanTracker):
    data = []
    for learning_path_tracker in UserSubscriptionPlanLearningPathTracker.objects.filter(parent_tracker=course_tracker):
        learning_path = learning_path_tracker.entity
        learning_path_data = simple_serialize_instance(
            instance=learning_path_tracker,
            keys=[
                "uuid",
                "progress",
            ],
            parent_data={
                "course_trackers": [],
                "entity": simple_serialize_instance(
                    instance=learning_path,
                    keys=[
                        "id",
                        "uuid",
                        "identity",
                        "description",
                        "duration",
                    ],
                    parent_data={
                        "image": get_file_field_url(learning_path, "image")
                    }
                ),
            },
        )
        for course_tracker in UserSubscriptionPlanLearningPathCourseTracker.objects.filter(parent_tracker=learning_path_tracker):
            course = course_tracker.entity
            course_data = simple_serialize_instance(
                instance=course_tracker,
                keys=[
                    "uuid",
                    "progress",
                ],
                parent_data={
                    "module_trackers": [],
                    "entity": simple_serialize_instance(
                        instance=course,
                        keys=[
                            "id",
                            "uuid",
                            "identity",
                            "description",
                            "duration",
                        ],
                        parent_data={
                            "image": get_file_field_url(course, "image")
                        }
                    ),
                },
            )
            for module_tracker in UserSubscriptionPlanLearningPathCourseModuleTracker.objects.filter(parent_tracker=course_tracker).order_by(
                "entity__position"):
                module = module_tracker.entity
                module_data = simple_serialize_instance(
                    instance=module_tracker,
                    keys=[
                        "uuid",
                        "progress",
                    ],
                    parent_data={
                        "sub_module_trackers": [],
                        "entity": simple_serialize_instance(
                            instance=module,
                            keys=[
                                "uuid",
                                "identity",
                            ],
                        ),
                    },
                )
                for sub_module_tracker in UserSubscriptionPlanLearningPathCourseSubModuleTracker.objects.filter(
                    parent_tracker=module_tracker).order_by("entity__position"):
                    sub_module = sub_module_tracker.entity
                    sub_module_data = simple_serialize_instance(
                        instance=sub_module_tracker,
                        keys=[
                            "uuid",
                            "progress",
                        ],
                        parent_data={
                            "entity": simple_serialize_instance(
                                instance=sub_module,
                                keys=[
                                    "id",
                                    "uuid",
                                    "identity",
                                    "description",
                                    "duration",
                                    "position",
                                    "assessmentID",
                                ],
                            ),
                            "resources": sub_module.get_resources(),
                            "is_in_bookmark": sub_module.is_in_bookmark(user),
                        },
                    )
                    module_data["sub_module_trackers"].append(sub_module_data)

                course_data["module_trackers"].append(module_data)

            learning_path_data["course_trackers"].append(course_data)

        data.append(learning_path_data) 

    return data

def get_module_subscription_advance_learning_path_trackers_data(user, course_tracker: UserSubscriptionPlanTracker):
    data = []
    for certification_path_tracker in UserSubscriptionPlanCertificatePathTracker.objects.filter(parent_tracker=course_tracker):
        certification_path = certification_path_tracker.entity
        certification_path_data = simple_serialize_instance(
            instance=certification_path_tracker,
            keys=[
                "uuid",
                "progress",
            ],
            parent_data={
                "learning_path_trackers": [],
                "entity": simple_serialize_instance(
                    instance=certification_path,
                    keys=[
                        "id",
                        "uuid",
                        "identity",
                        "description",
                        "duration",
                    ],
                    parent_data={
                        "image": get_file_field_url(certification_path, "image")
                    }
                ),
            },
        )
        for learning_path_tracker in UserSubscriptionPlanCertificatePathLearningPathCourseTracker.objects.filter(parent_tracker=certification_path_tracker):
            learning_path = learning_path_tracker.entity
            learning_path_data = simple_serialize_instance(
                instance=learning_path_tracker,
                keys=[
                    "uuid",
                    "progress",
                ],
                parent_data={
                    "course_trackers": [],
                    "entity": simple_serialize_instance(
                        instance=learning_path,
                        keys=[
                            "id",
                            "uuid",
                            "identity",
                            "description",
                            "duration",
                        ],
                        parent_data={
                            "image": get_file_field_url(learning_path, "image")
                        }
                    ),
                },
            )
            for course_tracker in UserSubscriptionPlanCertificatePathCourseTracker.objects.filter(parent_tracker=learning_path_tracker):
                course = course_tracker.entity
                course_data = simple_serialize_instance(
                    instance=course_tracker,
                    keys=[
                        "uuid",
                        "progress",
                    ],
                    parent_data={
                        "module_trackers": [],
                        "entity": simple_serialize_instance(
                            instance=course,
                            keys=[
                                "id",
                                "uuid",
                                "identity",
                                "description",
                                "duration",
                            ],
                            parent_data={
                                "image": get_file_field_url(course, "image")
                            }
                        ),
                    },
                )
                for module_tracker in UserSubscriptionPlanCertificatePathCourseModuleTracker.objects.filter(parent_tracker=course_tracker).order_by(
                    "entity__position"):
                    module = module_tracker.entity
                    module_data = simple_serialize_instance(
                        instance=module_tracker,
                        keys=[
                            "uuid",
                            "progress",
                        ],
                        parent_data={
                            "sub_module_trackers": [],
                            "entity": simple_serialize_instance(
                                instance=module,
                                keys=[
                                    "uuid",
                                    "identity",
                                ],
                            ),
                        },
                    )
                    for sub_module_tracker in UserSubscriptionPlanCertificatePathCourseSubModuleTracker.objects.filter(
                        parent_tracker=module_tracker).order_by("entity__position"):
                        sub_module = sub_module_tracker.entity
                        sub_module_data = simple_serialize_instance(
                            instance=sub_module_tracker,
                            keys=[
                                "uuid",
                                "progress",
                            ],
                            parent_data={
                                "entity": simple_serialize_instance(
                                    instance=sub_module,
                                    keys=[
                                        "id",
                                        "uuid",
                                        "identity",
                                        "description",
                                        "duration",
                                        "position",
                                        "assessmentID",
                                    ],
                                ),
                                "resources": sub_module.get_resources(),
                                "is_in_bookmark": sub_module.is_in_bookmark(user),
                            },
                        )
                        module_data["sub_module_trackers"].append(sub_module_data)

                    course_data["module_trackers"].append(module_data)

                learning_path_data["course_trackers"].append(course_data)

            certification_path_data["learning_path_trackers"].append(learning_path_data)
        
        data.append(certification_path_data)
    
    return data

class SubscriptionLearningTrackerStartAPIView(AbstractLookUpFieldMixin, AppAPIView):
    """View from where the user starts learning courses under his purchase."""

    get_object_model = UserSubscriptionPlanTracker

    def get(self, *args, **kwargs):
        """Handle on get."""

        tracker = self.get_object(identifier=self.lookup_field)
        entity = tracker.entity

        data = simple_serialize_instance(
            instance=tracker,
            keys=[
                "uuid",
                "valid_till",
                "last_accessed_on",
                "progress",
                "created",
            ],
            parent_data={
                "entity": simple_serialize_instance(
                    instance=entity,
                    keys=[
                        "id",
                        "uuid",
                        "identity",
                        "code",
                        "duration",
                    ],
                    parent_data={
                        # "instructor": simple_serialize_instance(
                        #     instance=entity.author,
                        #     keys=["uuid", "identity", "designation"],
                        # ),
                        # "level": simple_serialize_instance(
                        #     instance=entity.level, keys=["uuid", "identity"]
                        # ),
                    },
                )
            },
        )
        user=self.get_user()
        data["course_trackers"] = get_module_subscription_trackers_data(user, tracker)
        data["learning_path_trackers"] = get_module_subscription_learning_path_trackers_data(user,tracker)
        data["advance_learning_path_trackers"] = get_module_subscription_advance_learning_path_trackers_data(user,tracker)

        tracker.handle_started_learning()
        return self.send_response(data=data)



# TODO: handle performance optimisations later
class SubscriptionVisitedCourseModuleTrackerAPIView(AbstractLookUpFieldMixin, AppAPIView):
    """Handles the fact that the user has visited a `UserCourseSubModuleTracker`."""

    get_object_model = UserSubscriptionPlanCourseModuleTracker

    def post(self, *args, **kwargs):
        """Handle on post."""

        tracker = self.get_object(identifier=self.lookup_field)
        tracker.handle_viewed()
        return self.send_response()
    
# TODO: handle performance optimisations later
class SubscriptionVisitedCourseSubModuleTrackerAPIView(AbstractLookUpFieldMixin, AppAPIView):
    """Handles the fact that the user has visited a `UserCourseSubModuleTracker`."""

    get_object_model = UserSubscriptionPlanCourseSubModuleTracker

    def post(self, *args, **kwargs):
        """Handle on post."""

        tracker = self.get_object(identifier=self.lookup_field)
        tracker.handle_viewed()
        return self.send_response()
    
class SubscriptionVisitedLearningPathCourseTrackerAPIView(AbstractLookUpFieldMixin, AppAPIView):
    """Handles the fact that the Subscription has visited a `SubscriptionCourseSubModuleTracker`."""

    get_object_model = UserSubscriptionPlanLearningPathCourseTracker

    def post(self, *args, **kwargs):
        """Handle on post."""

        tracker = self.get_object(identifier=self.lookup_field)
        tracker.handle_viewed()
        return self.send_response()


# TODO: handle performance optimisations later
class SubscriptionVisitedLearningPathCourseModuleTrackerAPIView(AbstractLookUpFieldMixin, AppAPIView):
    """Handles the fact that the Subscription has visited a `SubscriptionCourseSubModuleTracker`."""

    get_object_model = UserSubscriptionPlanLearningPathCourseModuleTracker

    def post(self, *args, **kwargs):
        """Handle on post."""

        tracker = self.get_object(identifier=self.lookup_field)
        tracker.handle_viewed()
        return self.send_response()
    
class SubscriptionVisitedLearningPathCourseSubModuleTrackerAPIView(AbstractLookUpFieldMixin, AppAPIView):
    """Handles the fact that the Subscription has visited a `SubscriptionCourseSubModuleTracker`."""

    get_object_model = UserSubscriptionPlanLearningPathCourseSubModuleTracker

    def post(self, *args, **kwargs):
        """Handle on post."""

        tracker = self.get_object(identifier=self.lookup_field)
        tracker.handle_viewed()
        return self.send_response()
    

class SubscriptionVisitedCertificatePathLearningPathTrackerAPIView(AbstractLookUpFieldMixin, AppAPIView):
    """Handles the fact that the user has visited a `UserCourseSubModuleTracker`."""

    get_object_model = UserSubscriptionPlanCertificatePathLearningPathCourseTracker

    def post(self, *args, **kwargs):
        """Handle on post."""

        tracker = self.get_object(identifier=self.lookup_field)
        tracker.handle_viewed()
        return self.send_response()


# TODO: handle performance optimisations later
class SubscriptionVisitedCertificatePathLearningPathCourseTrackerAPIView(AbstractLookUpFieldMixin, AppAPIView):
    """Handles the fact that the user has visited a `UserCourseSubModuleTracker`."""

    get_object_model = UserSubscriptionPlanCertificatePathCourseTracker

    def post(self, *args, **kwargs):
        """Handle on post."""

        tracker = self.get_object(identifier=self.lookup_field)
        tracker.handle_viewed()
        return self.send_response()
    
class SubscriptionVisitedCertificatePathLearningPathCourseModuleTrackerAPIView(AbstractLookUpFieldMixin, AppAPIView):
    """Handles the fact that the user has visited a `UserCourseSubModuleTracker`."""

    get_object_model = UserSubscriptionPlanCertificatePathCourseModuleTracker

    def post(self, *args, **kwargs):
        """Handle on post."""

        tracker = self.get_object(identifier=self.lookup_field)
        tracker.handle_viewed()
        return self.send_response()
    
class SubscriptionVisitedCertificatePathLearningPathCourseSubModuleTrackerAPIView(AbstractLookUpFieldMixin, AppAPIView):
    """Handles the fact that the user has visited a `UserCourseSubModuleTracker`."""

    get_object_model = UserSubscriptionPlanCertificatePathCourseSubModuleTracker

    def post(self, *args, **kwargs):
        """Handle on post."""

        tracker = self.get_object(identifier=self.lookup_field)
        tracker.handle_viewed()
        return self.send_response()
    
# Student Learning tracker
class StudentLearningTrackerStartAPIView(AbstractLookUpFieldMixin, AppAPIView):
    """View from where the user starts learning courses under his purchase."""

    get_object_model = StudentEnrolledCourseTracker

    def get(self, *args, **kwargs):
        """Handle on get."""

        tracker = self.get_object(identifier=self.lookup_field)
        entity = tracker.entity
        course_submodules = CourseSubModule.objects.filter(module__course=tracker.entity)
        assessment_id = list(course_submodules.values_list('assessmentID', flat=True).distinct())
        assessment_completed = UserAssessmentResult.objects.filter(
            assessment_id=assessment_id[0],
            user=self.get_user(),
        ).exists()

        data = simple_serialize_instance(
            instance=tracker,
            keys=[
                "uuid",
                "valid_till",
                "last_accessed_on",
                "progress",
                "created",
            ],
            parent_data={
                "entity": simple_serialize_instance(
                    instance=entity,
                    keys=[
                        "uuid",
                        "identity",
                        "code",
                        "duration",
                        "mml_sku_id",
                        "vm_name",
                    ],
                    parent_data={
                        "instructor": simple_serialize_instance(
                            instance=entity.author,
                            keys=["uuid", "identity", "designation"],
                        ),
                        "level": simple_serialize_instance(
                            instance=entity.level, keys=["uuid", "identity"]
                        ),
                    },
                )
            },
        )
        user=self.get_user()
        data["module_trackers"] = get_module_student_trackers_data(user, tracker)
        data["assessment_completed"] = assessment_completed

        tracker.handle_started_learning()
        return self.send_response(data=data)
    
class LearningRoleStartAPIView(AbstractLookUpFieldMixin, AppAPIView):
    """View from where the user starts learning courses under his purchase."""

    get_object_model = LearningRole

    def get(self, *args, **kwargs):
        """Handle on get."""

        tracker = self.get_object(identifier=self.lookup_field)

        data = simple_serialize_instance(instance=tracker, keys=['id'])
        user=self.get_user()
        data["course_trackers"] = get_module_learning_role_trackers_data(user, tracker)
        data["learning_path_trackers"] = get_module_learning_role_learning_path_trackers_data(user,tracker)
        data["advance_learning_path_trackers"] = get_module_learning_role_advance_learning_path_trackers_data(user,tracker)

        return self.send_response(data=data)
    
class SkillStartAPIView(AbstractLookUpFieldMixin, AppAPIView):
    """View from where the user starts learning courses under his purchase."""

    get_object_model = UserSkillTracker

    def get(self, *args, **kwargs):
        """Handle on get."""

        tracker = self.get_object(identifier=self.lookup_field)

        data = simple_serialize_instance(instance=tracker, keys=['id'])
        user=self.get_user()
        data["course_trackers"] = get_module_skill_trackers_data(user, tracker)
        data["learning_path_trackers"] = get_module_skill_learning_path_trackers_data(user,tracker)
        data["advance_learning_path_trackers"] = get_module_skill_advance_learning_path_trackers_data(user,tracker)

        return self.send_response(data=data)
    
class SkillVisitedCourseModuleTrackerAPIView(AbstractLookUpFieldMixin, AppAPIView):
    """Handles the fact that the user has visited a `UserCourseSubModuleTracker`."""

    get_object_model = UserSkillCourseModuleTracker

    def post(self, *args, **kwargs):
        """Handle on post."""

        tracker = self.get_object(identifier=self.lookup_field)
        tracker.handle_viewed()
        return self.send_response()
    
# TODO: handle performance optimisations later
class SkillVisitedCourseSubModuleTrackerAPIView(AbstractLookUpFieldMixin, AppAPIView):
    """Handles the fact that the user has visited a `UserCourseSubModuleTracker`."""

    get_object_model = UserSkillCourseSubModuleTracker

    def post(self, *args, **kwargs):
        """Handle on post."""

        tracker = self.get_object(identifier=self.lookup_field)
        tracker.handle_viewed()
        return self.send_response()
    
class SkillVisitedLearningPathCourseTrackerAPIView(AbstractLookUpFieldMixin, AppAPIView):
    """Handles the fact that the Subscription has visited a `SkillCourseSubModuleTracker`."""

    get_object_model = UserSkillLearningPathCourseTracker

    def post(self, *args, **kwargs):
        """Handle on post."""

        tracker = self.get_object(identifier=self.lookup_field)
        tracker.handle_viewed()
        return self.send_response()


# TODO: handle performance optimisations later
class SkillVisitedLearningPathCourseModuleTrackerAPIView(AbstractLookUpFieldMixin, AppAPIView):
    """Handles the fact that the Subscription has visited a `SkillCourseSubModuleTracker`."""

    get_object_model = UserSkillLearningPathCourseModuleTracker

    def post(self, *args, **kwargs):
        """Handle on post."""

        tracker = self.get_object(identifier=self.lookup_field)
        tracker.handle_viewed()
        return self.send_response()
    
class SkillVisitedLearningPathCourseSubModuleTrackerAPIView(AbstractLookUpFieldMixin, AppAPIView):
    """Handles the fact that the Subscription has visited a `SkillCourseSubModuleTracker`."""

    get_object_model = UserSkillLearningPathCourseSubModuleTracker

    def post(self, *args, **kwargs):
        """Handle on post."""

        tracker = self.get_object(identifier=self.lookup_field)
        tracker.handle_viewed()
        return self.send_response()
    

class SkillVisitedCertificatePathLearningPathTrackerAPIView(AbstractLookUpFieldMixin, AppAPIView):
    """Handles the fact that the user has visited a `UserCourseSubModuleTracker`."""

    get_object_model = UserSkillCertificatePathLearningPathCourseTracker

    def post(self, *args, **kwargs):
        """Handle on post."""

        tracker = self.get_object(identifier=self.lookup_field)
        tracker.handle_viewed()
        return self.send_response()


# TODO: handle performance optimisations later
class SkillVisitedCertificatePathLearningPathCourseTrackerAPIView(AbstractLookUpFieldMixin, AppAPIView):
    """Handles the fact that the user has visited a `UserCourseSubModuleTracker`."""

    get_object_model = UserSkillCertificatePathCourseTracker

    def post(self, *args, **kwargs):
        """Handle on post."""

        tracker = self.get_object(identifier=self.lookup_field)
        tracker.handle_viewed()
        return self.send_response()
    
class SkillVisitedCertificatePathLearningPathCourseModuleTrackerAPIView(AbstractLookUpFieldMixin, AppAPIView):
    """Handles the fact that the user has visited a `UserCourseSubModuleTracker`."""

    get_object_model = UserSkillCertificatePathCourseModuleTracker

    def post(self, *args, **kwargs):
        """Handle on post."""

        tracker = self.get_object(identifier=self.lookup_field)
        tracker.handle_viewed()
        return self.send_response()
    
class SkillVisitedCertificatePathLearningPathCourseSubModuleTrackerAPIView(AbstractLookUpFieldMixin, AppAPIView):
    """Handles the fact that the user has visited a `UserCourseSubModuleTracker`."""

    get_object_model = UserSkillCertificatePathCourseSubModuleTracker

    def post(self, *args, **kwargs):
        """Handle on post."""

        tracker = self.get_object(identifier=self.lookup_field)
        tracker.handle_viewed()
        return self.send_response()
# TODO: handle performance optimisations later
class StudentVisitedCourseModuleTrackerAPIView(AbstractLookUpFieldMixin, AppAPIView):
    """Handles the fact that the user has visited a `UserCourseSubModuleTracker`."""

    get_object_model = StudentEnrolledCourseModuleTracker

    def post(self, *args, **kwargs):
        """Handle on post."""

        tracker = self.get_object(identifier=self.lookup_field)
        tracker.handle_viewed()
        return self.send_response()
    
# TODO: handle performance optimisations later
class StudentVisitedCourseSubModuleTrackerAPIView(AbstractLookUpFieldMixin, AppAPIView):
    """Handles the fact that the user has visited a `UserCourseSubModuleTracker`."""

    get_object_model = StudentEnrolledSubModuleTracker

    def post(self, *args, **kwargs):
        """Handle on post."""

        tracker = self.get_object(identifier=self.lookup_field)
        tracker.handle_viewed()
        return self.send_response()

class StudentVisitedLearningPathCourseTrackerAPIView(AbstractLookUpFieldMixin, AppAPIView):
    """Handles the fact that the user has visited a `UserCourseSubModuleTracker`."""

    get_object_model = StudentEnrolledLearningPathCourseTracker

    def post(self, *args, **kwargs):
        """Handle on post."""

        tracker = self.get_object(identifier=self.lookup_field)
        tracker.handle_viewed()
        return self.send_response()


# TODO: handle performance optimisations later
class StudentVisitedLearningPathCourseModuleTrackerAPIView(AbstractLookUpFieldMixin, AppAPIView):
    """Handles the fact that the user has visited a `UserCourseSubModuleTracker`."""

    get_object_model = StudentEnrolledLearningPathCourseModuleTracker

    def post(self, *args, **kwargs):
        """Handle on post."""

        tracker = self.get_object(identifier=self.lookup_field)
        tracker.handle_viewed()
        return self.send_response()
    
class StudentVisitedLearningPathCourseSubModuleTrackerAPIView(AbstractLookUpFieldMixin, AppAPIView):
    """Handles the fact that the user has visited a `UserCourseSubModuleTracker`."""

    get_object_model = StudentEnrolledLearningPathCourseSubModuleTracker

    def post(self, *args, **kwargs):
        """Handle on post."""

        tracker = self.get_object(identifier=self.lookup_field)
        tracker.handle_viewed()
        return self.send_response()


class StudentLearningPathTrackerStartAPIView(AbstractLookUpFieldMixin, AppAPIView):
    """View from where the user starts learning courses under his purchase."""

    get_object_model = StudentEnrolledLearningPathTracker

    def get(self, *args, **kwargs):
        """Handle on get."""

        tracker = self.get_object(identifier=self.lookup_field)
        entity = tracker.entity

        data = simple_serialize_instance(
            instance=tracker,
            keys=[
                "uuid",
                "valid_till",
                "last_accessed_on",
                "progress",
                "created",
            ],
            parent_data={
                "entity": simple_serialize_instance(
                    instance=entity,
                    keys=[
                        "uuid",
                        "identity",
                        "code",
                        "duration",
                        "mml_sku_id",
                        "vm_name",
                    ],
                    parent_data={
                        "level": simple_serialize_instance(
                            instance=entity.level, keys=["uuid", "identity"]
                        ),
                    },
                )
            },
        )
        user = self.get_user()
        data["learning_path_module_trackers"] = get_module_student_learning_path_trackers_data(user,tracker)

        tracker.handle_started_learning()
        return self.send_response(data=data)

class StudentCertificatePathTrackerStartAPIView(AbstractLookUpFieldMixin, AppAPIView):
    """View from where the user starts learning courses under his purchase."""

    get_object_model = StudentEnrolledCertificatePathTracker

    def get(self, *args, **kwargs):
        """Handle on get."""

        tracker = self.get_object(identifier=self.lookup_field)
        entity = tracker.entity

        data = simple_serialize_instance(
            instance=tracker,
            keys=[
                "uuid",
                "valid_till",
                "last_accessed_on",
                "progress",
                "created",
            ],
            parent_data={
                "entity": simple_serialize_instance(
                    instance=entity,
                    keys=[
                        "uuid",
                        "identity",
                        "code",
                        "duration",
                        "mml_sku_id",
                        "vm_name",
                    ],
                    parent_data={
                        "level": simple_serialize_instance(
                            instance=entity.level, keys=["uuid", "identity"]
                        ),
                    },
                )
            },
        )
        user = self.get_user()
        data["certificate_path_module_trackers"] = get_module_student_certificate_path_trackers_data(user,tracker)
        tracker.handle_started_learning()
        return self.send_response(data=data)

def get_module_blended_learning_path_trackers_data(user, blp_tracker: UserBlendedLearningPathTracker):
    """
    Returns the data for module trackers inside the course tracker.

    This is used in `UserBlendedLearningTrackerStartAPIView` and the
    detail page for the modules inside the page.
    """

    data = []
    for course_tracker in UserBlendedLearningPathCourseTracker.objects.filter(parent_tracker=blp_tracker):
        course = course_tracker.entity
        course_data = simple_serialize_instance(
            instance=course_tracker,
            keys=[
                "uuid",
                "progress",
            ],
            parent_data={
                "module_trackers": [],
                "entity": simple_serialize_foreignkey_instance(
                    instance=course,
                    keys=[
                        "uuid",
                        "course__id",
                        "course__identity",
                        "course__description",
                        "course__duration",
                        "course__code",
                        "mode__id",
                        "mode__identity",
                    ],
                    parent_data={
                        "course__image": get_file_field_url(course, "course__image")
                    }
                ),
            },
        )

        for module_tracker in UserBlendedLearningPathCourseModuleTracker.objects.filter(parent_tracker=course_tracker).order_by(
                "entity__position"):
            module = module_tracker.entity
            module_data = simple_serialize_instance(
                instance=module_tracker,
                keys=[
                    "uuid",
                    "progress",
                ],
                parent_data={
                    "sub_module_trackers": [],
                    "entity": simple_serialize_instance(
                        instance=module,
                        keys=[
                            "uuid",
                            "identity",
                        ],
                    ),
                },
            )

            for sub_module_tracker in UserBlendedLearningPathCourseSubModuleTracker.objects.filter(
                    parent_tracker=module_tracker).order_by("entity__position"):
                sub_module = sub_module_tracker.entity
                sub_module_data = simple_serialize_instance(
                    instance=sub_module_tracker,
                    keys=[
                        "uuid",
                        "progress",
                    ],
                    parent_data={
                        "entity": simple_serialize_instance(
                            instance=sub_module,
                            keys=[
                                "id",
                                "uuid",
                                "identity",
                                "description",
                                "duration",
                                "position",
                            ],
                        ),
                        "resources": sub_module.get_resources(),
                        "is_in_bookmark": sub_module.is_in_bookmark(user),
                    },
                )
                module_data["sub_module_trackers"].append(sub_module_data)

            course_data["module_trackers"].append(module_data)

        data.append(course_data)

    return data

class UserBlendedLearningPathTrackerDetailsAPIView(AppAPIView):
    def post(self, request, *args, **kwargs):
        course_id = self.request.data["course_id"]
        mode = self.request.data["mode"]
        user = self.get_authenticated_user()
        if course_id and mode:
            get_course_address_data = BlendedLearningUserEnrollCourseDetails.objects.get_or_none(course_id=course_id, mode_id=mode, created_by_id=user.id)
            if get_course_address_data is not None:
                return self.send_response({'data': get_course_address_data.address_details})
            else:
                return self.send_error_response({'data': "data not found"})
        else:
            return self.send_error_response({'data': "data not found"})

class UserBlendedLearningPathTrackerStartAPIView(AbstractLookUpFieldMixin, AppAPIView):
    """View from where the user starts learning courses under his purchase."""

    get_object_model  = UserBlendedLearningPathTracker

    def get(self, *args, **kwargs):
        """Handle on get."""

        tracker = self.get_object(identifier=self.lookup_field)
        entity = tracker.entity

        data = simple_serialize_instance(
            instance=tracker,
            keys=[
                "uuid",
                "valid_till",
                "last_accessed_on",
                "progress",
                "created",
            ],
            parent_data={
                "entity": simple_serialize_instance(
                    instance=entity,
                    keys=[
                        "identity",
                        "code",
                        "duration",
                        "mml_sku_id",
                        "vm_name",
                    ],
                    parent_data={
                        # "instructor": simple_serialize_instance(
                        #     instance=entity.author,
                        #     keys=["uuid", "identity", "designation"],
                        # ),
                        # "level": simple_serialize_instance(
                        #     instance=entity.level, keys=["uuid", "identity"]
                        # ),
                    },
                )
            },
        )
        user = self.get_user()
        data["blp_module_trackers"] = get_module_blended_learning_path_trackers_data(user,tracker)

        tracker.handle_started_learning()
        return self.send_response(data=data)

#-------------------Blended Learning Path Trackers---------------------#

class UserVisitedBlendedLearningPathCourseTrackerAPIView(AbstractLookUpFieldMixin, AppAPIView):
    """Handles the fact that the user has visited a `UserCourseSubModuleTracker`."""

    get_object_model = UserBlendedLearningPathCourseTracker

    def post(self, *args, **kwargs):
        """Handle on post."""

        tracker = self.get_object(identifier=self.lookup_field)
        tracker.handle_viewed()
        return self.send_response()


# TODO: handle performance optimisations later
class UserVisitedBlendedLearningPathCourseModuleTrackerAPIView(AbstractLookUpFieldMixin, AppAPIView):
    """Handles the fact that the user has visited a `UserCourseSubModuleTracker`."""

    get_object_model = UserBlendedLearningPathCourseModuleTracker

    def post(self, *args, **kwargs):
        """Handle on post."""

        tracker = self.get_object(identifier=self.lookup_field)
        tracker.handle_viewed()
        return self.send_response()
    
class UserVisitedBlendedLearningPathCourseSubModuleTrackerAPIView(AbstractLookUpFieldMixin, AppAPIView):
    """Handles the fact that the user has visited a `UserCourseSubModuleTracker`."""

    get_object_model = UserBlendedLearningPathCourseSubModuleTracker

    def post(self, *args, **kwargs):
        """Handle on post."""

        tracker = self.get_object(identifier=self.lookup_field)
        tracker.handle_viewed()
        return self.send_response()


def get_module_skill_job_trackers_data(user, course_tracker: UserJobEligibleSkillTracker):
    """
    Returns the data for module trackers inside the course tracker.

    This is used in `SubscriptionLearningTrackerStartAPIView` and the
    detail page for the modules inside the page.
    """
    data=[]
    for course_tracker in UserJobEligibleSkillCourseTracker.objects.filter(parent_tracker=course_tracker):
        course = course_tracker.entity
        course_data = simple_serialize_instance(
            instance=course_tracker,
            keys=[
                "uuid",
                "progress",
            ],
            parent_data={
                "module_trackers": [],
                "entity": simple_serialize_instance(
                    instance=course,
                    keys=[
                        "uuid",
                        "identity",
                        "description",
                        "duration",
                    ],
                    parent_data={
                        "image": get_file_field_url(course, "image")
                    }
                ),
            },
        )

        for module_tracker in UserJobEligibleSkillCourseModuleTracker.objects.filter(parent_tracker=course_tracker).order_by(
                "entity__position"):
            module = module_tracker.entity
            module_data = simple_serialize_instance(
                instance=module_tracker,
                keys=[
                    "uuid",
                    "progress",
                ],
                parent_data={
                    "sub_module_trackers": [],
                    "entity": simple_serialize_instance(
                        instance=module,
                        keys=[
                            "uuid",
                            "identity",
                        ],
                    ),
                },
            )

            for sub_module_tracker in UserJobEligibleSkillCourseSubModuleTracker.objects.filter(
                    parent_tracker=module_tracker).order_by("entity__position"):
                sub_module = sub_module_tracker.entity
                sub_module_data = simple_serialize_instance(
                    instance=sub_module_tracker,
                    keys=[
                        "uuid",
                        "progress",
                    ],
                    parent_data={
                        "entity": simple_serialize_instance(
                            instance=sub_module,
                            keys=[
                                "id",
                                "uuid",
                                "identity",
                                "description",
                                "duration",
                                "position",
                            ],
                        ),
                        "resources": sub_module.get_resources(),
                        "is_in_bookmark": sub_module.is_in_bookmark(user),
                    },
                )
                module_data["sub_module_trackers"].append(sub_module_data)

            course_data["module_trackers"].append(module_data)

        data.append(course_data)

    return data

def get_module_skill_job_learning_path_trackers_data(user, course_tracker: UserJobEligibleSkillTracker):
    data = []
    for learning_path_tracker in UserJobEligibleSkillLearningPathTracker.objects.filter(parent_tracker=course_tracker):
        learning_path = learning_path_tracker.entity
        learning_path_data = simple_serialize_instance(
            instance=learning_path_tracker,
            keys=[
                "uuid",
                "progress",
            ],
            parent_data={
                "course_trackers": [],
                "entity": simple_serialize_instance(
                    instance=learning_path,
                    keys=[
                        "uuid",
                        "identity",
                        "description",
                        "duration",
                    ],
                    parent_data={
                        "image": get_file_field_url(learning_path, "image")
                    }
                ),
            },
        )
        for course_tracker in UserJobEligibleSkillLearningPathCourseTracker.objects.filter(parent_tracker=learning_path_tracker):
            course = course_tracker.entity
            course_data = simple_serialize_instance(
                instance=course_tracker,
                keys=[
                    "uuid",
                    "progress",
                ],
                parent_data={
                    "module_trackers": [],
                    "entity": simple_serialize_instance(
                        instance=course,
                        keys=[
                            "uuid",
                            "identity",
                            "description",
                            "duration",
                        ],
                        parent_data={
                            "image": get_file_field_url(course, "image")
                        }
                    ),
                },
            )
            for module_tracker in UserJobEligibleSkillLearningPathCourseModuleTracker.objects.filter(parent_tracker=course_tracker).order_by(
                "entity__position"):
                module = module_tracker.entity
                module_data = simple_serialize_instance(
                    instance=module_tracker,
                    keys=[
                        "uuid",
                        "progress",
                    ],
                    parent_data={
                        "sub_module_trackers": [],
                        "entity": simple_serialize_instance(
                            instance=module,
                            keys=[
                                "uuid",
                                "identity",
                            ],
                        ),
                    },
                )
                for sub_module_tracker in UserJobEligibleSkillLearningPathCourseSubModuleTracker.objects.filter(
                    parent_tracker=module_tracker).order_by("entity__position"):
                    sub_module = sub_module_tracker.entity
                    sub_module_data = simple_serialize_instance(
                        instance=sub_module_tracker,
                        keys=[
                            "uuid",
                            "progress",
                        ],
                        parent_data={
                            "entity": simple_serialize_instance(
                                instance=sub_module,
                                keys=[
                                    "id",
                                    "uuid",
                                    "identity",
                                    "description",
                                    "duration",
                                    "position",
                                ],
                            ),
                            "resources": sub_module.get_resources(),
                            "is_in_bookmark": sub_module.is_in_bookmark(user),
                        },
                    )
                    module_data["sub_module_trackers"].append(sub_module_data)

                course_data["module_trackers"].append(module_data)

            learning_path_data["course_trackers"].append(course_data)

        data.append(learning_path_data) 

    return data

def get_module_skill_job_advance_learning_path_trackers_data(user, course_tracker: UserJobEligibleSkillTracker):
    data = []
    for certification_path_tracker in UserJobEligibleSkillCertificatePathTracker.objects.filter(parent_tracker=course_tracker):
        certification_path = certification_path_tracker.entity
        certification_path_data = simple_serialize_instance(
            instance=certification_path_tracker,
            keys=[
                "uuid",
                "progress",
            ],
            parent_data={
                "learning_path_trackers": [],
                "entity": simple_serialize_instance(
                    instance=certification_path,
                    keys=[
                        "uuid",
                        "identity",
                        "description",
                        "duration",
                    ],
                    parent_data={
                        "image": get_file_field_url(certification_path, "image")
                    }
                ),
            },
        )
        for learning_path_tracker in UserJobEligibleSkillCertificatePathLearningPathCourseTracker.objects.filter(parent_tracker=certification_path_tracker):
            learning_path = learning_path_tracker.entity
            learning_path_data = simple_serialize_instance(
                instance=learning_path_tracker,
                keys=[
                    "uuid",
                    "progress",
                ],
                parent_data={
                    "course_trackers": [],
                    "entity": simple_serialize_instance(
                        instance=learning_path,
                        keys=[
                            "uuid",
                            "identity",
                            "description",
                            "duration",
                        ],
                        parent_data={
                            "image": get_file_field_url(learning_path, "image")
                        }
                    ),
                },
            )
            for course_tracker in UserJobEligibleSkillCertificatePathCourseTracker.objects.filter(parent_tracker=learning_path_tracker):
                course = course_tracker.entity
                course_data = simple_serialize_instance(
                    instance=course_tracker,
                    keys=[
                        "uuid",
                        "progress",
                    ],
                    parent_data={
                        "module_trackers": [],
                        "entity": simple_serialize_instance(
                            instance=course,
                            keys=[
                                "uuid",
                                "identity",
                                "description",
                                "duration",
                            ],
                            parent_data={
                                "image": get_file_field_url(course, "image")
                            }
                        ),
                    },
                )
                for module_tracker in UserJobEligibleSkillCertificatePathCourseModuleTracker.objects.filter(parent_tracker=course_tracker).order_by(
                    "entity__position"):
                    module = module_tracker.entity
                    module_data = simple_serialize_instance(
                        instance=module_tracker,
                        keys=[
                            "uuid",
                            "progress",
                        ],
                        parent_data={
                            "sub_module_trackers": [],
                            "entity": simple_serialize_instance(
                                instance=module,
                                keys=[
                                    "uuid",
                                    "identity",
                                ],
                            ),
                        },
                    )
                    for sub_module_tracker in UserJobEligibleSkillCertificatePathCourseSubModuleTracker.objects.filter(
                        parent_tracker=module_tracker).order_by("entity__position"):
                        sub_module = sub_module_tracker.entity
                        sub_module_data = simple_serialize_instance(
                            instance=sub_module_tracker,
                            keys=[
                                "uuid",
                                "progress",
                            ],
                            parent_data={
                                "entity": simple_serialize_instance(
                                    instance=sub_module,
                                    keys=[
                                        "id",
                                        "uuid",
                                        "identity",
                                        "description",
                                        "duration",
                                        "position",
                                    ],
                                ),
                                "resources": sub_module.get_resources(),
                                "is_in_bookmark": sub_module.is_in_bookmark(user),
                            },
                        )
                        module_data["sub_module_trackers"].append(sub_module_data)

                    course_data["module_trackers"].append(module_data)

                learning_path_data["course_trackers"].append(course_data)

            certification_path_data["learning_path_trackers"].append(learning_path_data)
        
        data.append(certification_path_data)
    
    return data

# Job Eligible Skill
class JobEligibleSkillLearningTrackerStartAPIView(AbstractLookUpFieldMixin, AppAPIView):
    """View from where the user starts learning courses under his purchase."""

    get_object_model = UserJobEligibleSkillTracker

    def get(self, *args, **kwargs):
        """Handle on get."""

        tracker = self.get_object(identifier=self.lookup_field)
        entity = tracker.entity

        data = simple_serialize_instance(
            instance=tracker,
            keys=[
                "uuid",
                "valid_till",
                "last_accessed_on",
                "progress",
                "created",
            ],
            parent_data={
                "entity": simple_serialize_instance(
                    instance=entity,
                    keys=[
                        "uuid",
                        "identity",
                        "code",
                        "duration",
                    ],
                    parent_data={
                        # "instructor": simple_serialize_instance(
                        #     instance=entity.author,
                        #     keys=["uuid", "identity", "designation"],
                        # ),
                        # "level": simple_serialize_instance(
                        #     instance=entity.level, keys=["uuid", "identity"]
                        # ),
                    },
                )
            },
        )
        user=self.get_user()
        data["course_trackers"] = get_module_skill_job_trackers_data(user, tracker)
        data["learning_path_trackers"] = get_module_skill_job_learning_path_trackers_data(user,tracker)
        data["advance_learning_path_trackers"] = get_module_skill_job_advance_learning_path_trackers_data(user,tracker)

        tracker.handle_started_learning()
        return self.send_response(data=data)



# TODO: handle performance optimisations later
class JobEligibleSkillVisitedCourseModuleTrackerAPIView(AbstractLookUpFieldMixin, AppAPIView):
    """Handles the fact that the user has visited a `UserCourseSubModuleTracker`."""

    get_object_model = UserJobEligibleSkillCourseModuleTracker

    def post(self, *args, **kwargs):
        """Handle on post."""

        tracker = self.get_object(identifier=self.lookup_field)
        tracker.handle_viewed()
        return self.send_response()
    
# TODO: handle performance optimisations later
class JobEligibleSkillVisitedCourseSubModuleTrackerAPIView(AbstractLookUpFieldMixin, AppAPIView):
    """Handles the fact that the user has visited a `UserCourseSubModuleTracker`."""

    get_object_model = UserJobEligibleSkillCourseSubModuleTracker

    def post(self, *args, **kwargs):
        """Handle on post."""

        tracker = self.get_object(identifier=self.lookup_field)
        tracker.handle_viewed()
        return self.send_response()
    
class JobEligibleSkillVisitedLearningPathCourseTrackerAPIView(AbstractLookUpFieldMixin, AppAPIView):
    """Handles the fact that the Subscription has visited a `JobEligibleSkillCourseSubModuleTracker`."""

    get_object_model = UserJobEligibleSkillLearningPathCourseTracker

    def post(self, *args, **kwargs):
        """Handle on post."""

        tracker = self.get_object(identifier=self.lookup_field)
        tracker.handle_viewed()
        return self.send_response()


# TODO: handle performance optimisations later
class JobEligibleSkillVisitedLearningPathCourseModuleTrackerAPIView(AbstractLookUpFieldMixin, AppAPIView):
    """Handles the fact that the Subscription has visited a `JobEligibleSkillCourseSubModuleTracker`."""

    get_object_model = UserJobEligibleSkillLearningPathCourseModuleTracker

    def post(self, *args, **kwargs):
        """Handle on post."""

        tracker = self.get_object(identifier=self.lookup_field)
        tracker.handle_viewed()
        return self.send_response()
    
class JobEligibleSkillVisitedLearningPathCourseSubModuleTrackerAPIView(AbstractLookUpFieldMixin, AppAPIView):
    """Handles the fact that the Subscription has visited a `JobEligibleSkillCourseSubModuleTracker`."""

    get_object_model = UserJobEligibleSkillLearningPathCourseSubModuleTracker

    def post(self, *args, **kwargs):
        """Handle on post."""

        tracker = self.get_object(identifier=self.lookup_field)
        tracker.handle_viewed()
        return self.send_response()
    

class JobEligibleSkillVisitedCertificatePathLearningPathTrackerAPIView(AbstractLookUpFieldMixin, AppAPIView):
    """Handles the fact that the user has visited a `UserCourseSubModuleTracker`."""

    get_object_model = UserJobEligibleSkillCertificatePathLearningPathCourseTracker

    def post(self, *args, **kwargs):
        """Handle on post."""

        tracker = self.get_object(identifier=self.lookup_field)
        tracker.handle_viewed()
        return self.send_response()


# TODO: handle performance optimisations later
class JobEligibleSkillVisitedCertificatePathLearningPathCourseTrackerAPIView(AbstractLookUpFieldMixin, AppAPIView):
    """Handles the fact that the user has visited a `UserCourseSubModuleTracker`."""

    get_object_model = UserJobEligibleSkillCertificatePathCourseTracker

    def post(self, *args, **kwargs):
        """Handle on post."""

        tracker = self.get_object(identifier=self.lookup_field)
        tracker.handle_viewed()
        return self.send_response()
    
class JobEligibleSkillVisitedCertificatePathLearningPathCourseModuleTrackerAPIView(AbstractLookUpFieldMixin, AppAPIView):
    """Handles the fact that the user has visited a `UserCourseSubModuleTracker`."""

    get_object_model = UserJobEligibleSkillCertificatePathCourseModuleTracker

    def post(self, *args, **kwargs):
        """Handle on post."""

        tracker = self.get_object(identifier=self.lookup_field)
        tracker.handle_viewed()
        return self.send_response()
    
class JobEligibleSkillVisitedCertificatePathLearningPathCourseSubModuleTrackerAPIView(AbstractLookUpFieldMixin, AppAPIView):
    """Handles the fact that the user has visited a `UserCourseSubModuleTracker`."""

    get_object_model = UserJobEligibleSkillCertificatePathCourseSubModuleTracker

    def post(self, *args, **kwargs):
        """Handle on post."""

        tracker = self.get_object(identifier=self.lookup_field)
        tracker.handle_viewed()
        return self.send_response()