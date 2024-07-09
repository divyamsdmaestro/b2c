from apps.learning.models import Skill
from django_filters.rest_framework import DjangoFilterBackend
from apps.common.pagination import AppPagination
from rest_framework.filters import SearchFilter
from rest_framework import serializers
from rest_framework.generics import ListAPIView
from apps.common.views.api import AppAPIView
from apps.jobs.models import NewsDetail, NewsThumbnailImage
from django.contrib.auth.models import AnonymousUser
from ...common.serializers import get_app_read_only_serializer as read_serializer
from ...common.serializers import AppReadOnlyModelSerializer
from apps.cms.serializers import UserProfileSerializer

class NewsListAPIView(ListAPIView, AppAPIView):
    """Sends out data for the news Listing Page."""
    class _Serializer(AppReadOnlyModelSerializer):
        """This serializer contains configuration for news."""

        skills = read_serializer(Skill, meta_fields=["id","uuid","identity"])(many=True)
        image = read_serializer(NewsThumbnailImage, meta_fields="__all__")(NewsThumbnailImage.objects.all())
        created_by = UserProfileSerializer()

        class Meta(AppReadOnlyModelSerializer.Meta):
            model = NewsDetail
            fields = [
                "id",
                "uuid",
                "title",
                "image",
                "news_link",
                "tags",
                "published_by",
                "published_on",
                "skills",
                "created_by",
                "created",
            ]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = "__all__"
    search_fields = ["title"]
    pagination_class = AppPagination
    serializer_class = _Serializer
    queryset = NewsDetail.objects.all()