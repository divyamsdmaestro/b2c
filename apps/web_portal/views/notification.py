from apps.common.views.api import AppAPIView
from apps.learning.models.course import Course
from apps.web_portal.models.notification import Notification
from apps.web_portal.serializers.notification import NotificationSerializer
from rest_framework.generics import ListAPIView

class UserNotificationListAPIView(ListAPIView, AppAPIView):
    serializer_class = NotificationSerializer

    def get_queryset(self):
        user = self.get_user()
        return Notification.objects.filter(user=user, is_delete=False)


class UserNotificationUpdateAPIView(AppAPIView):
    def put(self, request, *args, **kwargs):
        try:
            notification = Notification.objects.get(uuid=kwargs["uuid"])
        except Notification.DoesNotExist:
            return self.send_error_response()

        notification.is_read = True
        notification.save()

        return self.send_response()
    
class UserNotificationClearAPIView(AppAPIView):
    def post(self, request, *args, **kwargs):
        Notification.objects.filter(user=self.get_user()).update(is_delete=True, is_read=True)
        return self.send_response()
