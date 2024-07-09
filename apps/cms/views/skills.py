from apps.common.views.api import AppAPIView
from apps.learning.models import Skill


class BulkSkillArchiveAPIView(AppAPIView):
    def post(self, request, *args, **kwargs):
        skill_ids = request.data.get('id', [])  # Assuming skill_ids are sent in the request body
        if not skill_ids:
            return self.send_response(data={"error": "No skill IDs provided"})

        try:
            skills = Skill.objects.filter(id__in=skill_ids)
            skills.update(is_archived=True)
            return self.send_response(data={"message": "Skills archived successfully"})
        except Skill.DoesNotExist:
            return self.send_response(data={"error": "One or more skill IDs are invalid"})
        except Exception as e:
            return self.send_response(data={"error": str(e)})