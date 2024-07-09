from django.urls import path

from . import views

app_name = "service_idp"
API_URL_PREFIX = "api/service/idp/"

urlpatterns = [
    path(
        f"{API_URL_PREFIX}user-created/oauth/webhook/",
        views.UserCreatedByOauthWebhookAPIView.as_view(),
    ),
]
