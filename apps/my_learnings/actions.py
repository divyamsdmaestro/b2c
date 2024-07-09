from apps.my_learnings.helpers import get_one_year_datetime_from_now
from apps.hackathons.models.hackathon import HackathonParticipant
from apps.my_learnings.models.trackers import (
    UserCourseTracker, 
    UserLearningPathTracker, 
    UserCertificatePathTracker,
    UserMMLCourseTracker, 
    UserSubscriptionPlanTracker, 
    UserSkillTracker, 
    UserBlendedLearningPathTracker, 
    UserJobEligibleSkillTracker,
)
from apps.web_portal.models.notification import Notification


def handle_user_enrolled_to_course(user, course):
    """Handle the fact that user has enrolled to course. Creates trackers."""

    UserCourseTracker.objects.filter(created_by=user, entity=course).delete()

    tracker = UserCourseTracker.objects.create(
        created_by=user, entity=course, valid_till=get_one_year_datetime_from_now()
    )

    # chain of responsibility
    tracker.handle_user_enrolled()

    notification = Notification(user=user, course=course, purpose="completed", message=f'Successfully enrolled in the course {course.identity}')
    notification.save()


def handle_user_enrolled_to_learning_path(user, learning_path):
    """Handle the fact that user has enrolled to learning path. Creates trackers."""

    UserLearningPathTracker.objects.filter(created_by=user, entity=learning_path).delete()

    tracker = UserLearningPathTracker.objects.create(
        created_by=user, entity=learning_path, valid_till=get_one_year_datetime_from_now()
    )
    # chain of responsibility
    tracker.handle_user_enrolled()

    notification = Notification(user=user, learning_path=learning_path, purpose="completed", message=f'Successfully enrolled in the course {learning_path.identity}')
    notification.save()

def handle_user_enrolled_to_certification_path(user, certification_path):
    """Handle the fact that user has enrolled to certification path. Creates trackers."""

    UserCertificatePathTracker.objects.filter(created_by=user, entity=certification_path).delete()

    tracker = UserCertificatePathTracker.objects.create(
        created_by=user, entity=certification_path, valid_till=get_one_year_datetime_from_now()
    )

    # chain of responsibility
    tracker.handle_user_enrolled()

    notification = Notification(user=user, certification_path=certification_path, purpose="completed", message=f'Successfully enrolled in the course {certification_path.identity}')
    notification.save()

def handle_user_enrolled_to_mml_course(user, mml_course):
    """Handle the fact that user has enrolled to course. Creates trackers."""

    UserMMLCourseTracker.objects.filter(created_by=user, entity=mml_course).delete()

    tracker = UserMMLCourseTracker.objects.create(
        created_by=user, entity=mml_course, valid_till=get_one_year_datetime_from_now()
    )

    # chain of responsibility
    tracker.handle_started_learning()

def handle_user_enrolled_to_subscription_plan(user, subscription_plan_courses):
    """Handle the fact that user has enrolled to certification path. Creates trackers."""

    UserSubscriptionPlanTracker.objects.filter(created_by=user, entity=subscription_plan_courses).delete()

    tracker = UserSubscriptionPlanTracker.objects.create(
        created_by=user, entity=subscription_plan_courses, valid_till=get_one_year_datetime_from_now()
    )
    # chain of responsibility
    tracker.handle_user_enrolled()

    notification = Notification(user=user, learning_path=subscription_plan_courses, purpose="completed", message=f'Successfully enrolled in the course {subscription_plan_courses.identity}')
    notification.save()

def handle_user_enrolled_to_hackathon(user, hackathon):
    """Handle the fact that user has enrolled to course. Creates trackers."""

    HackathonParticipant.objects.filter(created_by=user, entity=hackathon).delete()

    tracker = HackathonParticipant.objects.create(
        created_by=user, entity=hackathon
    )

    # chain of responsibility
    tracker.handle_user_enrolled()

def handle_user_enrolled_to_skill_learning_path(user, skill):
    """Handle the fact that user has enrolled to certification path. Creates trackers."""

    UserSkillTracker.objects.filter(created_by=user, entity=skill).delete()

    tracker = UserSkillTracker.objects.create(
        created_by=user, entity=skill, valid_till=get_one_year_datetime_from_now()
    )

    # chain of responsibility
    tracker.handle_user_enrolled()

def handle_user_enrolled_to_blended_learning_path(user, blended_learning_path, blp_learning_mode, blp_schedule):
    """Handle the fact that user has enrolled to blended learning path. Creates trackers."""

    UserBlendedLearningPathTracker.objects.filter(created_by=user, entity=blended_learning_path, blp_learning_mode=blp_learning_mode, blp_schedule=blp_schedule).delete()

    tracker = UserBlendedLearningPathTracker.objects.create(
        created_by=user, entity=blended_learning_path, valid_till=get_one_year_datetime_from_now(), blp_learning_mode=blp_learning_mode, blp_schedule_id=blp_schedule
    )

    # chain of responsibility
    tracker.handle_user_enrolled()

def handle_user_enrolled_to_job_eligible_Skill(user, blended_learning_path):
    """Handle the fact that user has enrolled to blended learning path. Creates trackers."""

    UserJobEligibleSkillTracker.objects.filter(created_by=user, entity=blended_learning_path).delete()

    tracker = UserJobEligibleSkillTracker.objects.create(
        created_by=user, entity=blended_learning_path, valid_till=get_one_year_datetime_from_now()
    )

    # chain of responsibility
    tracker.handle_user_enrolled()