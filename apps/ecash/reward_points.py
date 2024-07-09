from apps.ecash.models import Ecash
from apps.access.models import User
from django.core.exceptions import ObjectDoesNotExist, ValidationError

def trigger_reward_points(user, action):
    """User performed an action. Add points accordingly."""
    try:
        action = Ecash.objects.get_or_none(ecashmeta__identity=action)
        if action:
            user = User.objects.get_or_none(id=user.id)
            if user:
                user.current_reward_points += action.points
                user.total_reward_points += action.points
                user.save()
    except ObjectDoesNotExist as e:
        print(f"Error: {e}")
    except ValidationError as e:
        print(f"Validation Error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")