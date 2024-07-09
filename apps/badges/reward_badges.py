# from apps.badges.models.badges import Badges
# from apps.access.models import User, UserBadges
# from django.core.exceptions import ObjectDoesNotExist, ValidationError

# def trigger_reward_badges(user, action):
#     """User performed an action. Add points accordingly."""
#     try:
#         action = Badges.objects.get_or_none(badgesmeta__identity=action)
#         if action:
#             user = User.objects.get_or_none(id=user.id)
#             if user:
#                 user_badge, created = UserBadges.objects.get_or_create(user=user, badges=action)
#                 if created:
#                     user_badge.badges = action
#                     user_badge.points += action.points
#                     user_badge.user = user
#                     user.total_badge_points += action.points
#                     user_badge.save()
#                     user.save()
#     except ObjectDoesNotExist as e:
#         print(f"Error: {e}")
#     except ValidationError as e:
#         print(f"Validation Error: {e}")
#     except Exception as e:
#         print(f"An unexpected error occurred: {e}")