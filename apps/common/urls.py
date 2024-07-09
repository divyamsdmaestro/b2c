from django.urls import path

from .views import api

app_name = "common"
API_URL_PREFIX = "api/"

urlpatterns = [
    path("server/status/", api.ServerStatusAPIView.as_view()),
]
