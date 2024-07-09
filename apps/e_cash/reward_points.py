# from apps.e_cash.models import Ecash
# from apps.access.models import User
# from django.core.exceptions import ObjectDoesNotExist

# def trigger_reward_points(user,action):
#     """User performed an action.Add points accordingly"""
#     try:
#         #points added when an action is triggered
#         action = Ecash.objects.get_or_none(ecashmeta__identity=action)
#         if action:
#             user = User.objects.get_or_none(id=user.id)
#             if user:
#                 user.reward_points += action.points
#                 user.save() 
#     except ObjectDoesNotExist:
#         print(f"Action with identity '{action}' does not exist.")
#         return