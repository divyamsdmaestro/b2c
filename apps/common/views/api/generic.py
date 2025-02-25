from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, parsers
from rest_framework.decorators import action
from rest_framework.mixins import (
    CreateModelMixin,
    DestroyModelMixin,
    ListModelMixin,
    UpdateModelMixin,
)
from rest_framework.viewsets import GenericViewSet
import bleach
from apps.common.pagination import AppPagination
from apps.common.serializers import AppModelSerializer, simple_serialize_queryset
from apps.common.views.api.base import AppCreateAPIView, AppViewMixin
from django.conf import settings
from apps.common.views.api.base import NonAuthenticatedAPIMixin

class AppGenericViewSet(GenericViewSet):
    """
    Applications version of the `GenericViewSet`. Overridden to implement
    app's necessary features. Also used in the CRUD viewsets.

    Note:
        1. An APIView is different from an APIViewSet.
        2. An APIView is registered using:
            path("url/endpoint/", APIView.as_view())
        3. An APIViewSet is registered using:
            router.register(
                "url/endpoint",
                APIViewSet,
                basename="base_name_if_needed",
            )

    Why is this implemented?
        > Consider an Update API that has to be implemented.
        > The API has to send the following:
            >> Initial data (ids).
            >> Metadata for select options.
            >> Handle the update operations.
        > If implemented using APIView, there has to be at least 2 view classes.
        > If implemented using APIViewSet, it is only one view.
        > Hence reduces the development time.
    """

    pass


class AppSingletonInstanceUpdateAPIViewSet(
    AppViewMixin, UpdateModelMixin, AppGenericViewSet
):
    """
    What is a singleton instance?
        Only one object is present in the table. Or multiple/dynamic
        objects from the user is not allowed(from url variables).

        Only one instance is present. Like organisation in
        terms of multi-tenant apps.

    This is used to update that instance. The get_object has to
    be overridden on the defined child class.

    Urls Allowed:
        > PUT: {endpoint}/
            >> Input data & update the object. The `get_object` has to be defined.
        > GET: {endpoint}/meta/
            >> Returns the meta details for an object update to the font-end.
    """

    def get_object(self):
        """Overridden on child classes."""

        raise NotImplementedError

    def put(self, request, *args, **kwargs):
        """Handle on PUT method."""

        return self.update(request, *args, **kwargs)

    @action(
        methods=["GET"],
        url_path="meta",
        detail=False,
    )
    def get_meta_for_singleton_update(self, *args, **kwargs):
        """Returns the meta details necessary for the front-end."""

        # no data from request, just the user and request details
        serializer = self.get_serializer(instance=self.get_object())

        # send the meta and initial from the serializer
        return self.send_response(data=serializer.get_meta_for_update())


class AppModelListAPIViewSet(
    AppViewMixin,
    ListModelMixin,
    AppGenericViewSet,
):
    """
    Applications base list APIViewSet. Handles all the listing views.
    This also sends the necessary filter meta and table config data.

    Also handles listing operations like sort, search, filter and
    table preferences of the user.

    References:
        1. https://github.com/miki725/django-url-filter
        2. https://www.django-rest-framework.org/api-guide/filtering/
    """

    pagination_class = AppPagination  # page-size: 25
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]

    filterset_fields = []  # override
    search_fields = []  # override
    ordering_fields = "__all__"

    all_table_columns = {}  # defined in the child class
    # table_preference_identifier = None  # key to query the model

    @action(
        methods=["GET"],
        url_path="table-meta",
        detail=False,
    )
    def get_meta_for_table_handler(self, *args, **kwargs):
        """
        Sends out all the necessary config for the front-end table. The
        config can vary based on user permission and preference.
        """

        return self.send_response(data=self.get_meta_for_table())

    def get_meta_for_table(self) -> dict:
        """
        Just an adaptor class for the `get_meta_for_table_handler`.
        Overridden on the child classes to send data.
        """

        return {
            "columns": self.get_table_columns(),
            # "all_columns": self.all_table_columns,  # used in the FE
        }

    def get_table_columns(self) -> dict:
        """
        Returns all the columns for the table in order. Got from the
        preference of the user. Overridden in child.
        """

        # if self.table_preference_identifier:
        #     preference_object = TableColumnsPreferenceTracker.objects.get_or_none(
        #         created_by=self.get_organisation_user(),
        #         table_identifier=self.table_preference_identifier,
        #     )
        #     if preference_object:
        #         return {
        #             k: self.all_table_columns.get(k, get_display_name_for_slug(k))
        #             for k in preference_object.columns
        #         }

        return self.all_table_columns

    # @action(
    #     methods=["POST"],
    #     url_path="sync-export",
    #     detail=False,
    # )
    # def export_list_handler(self, *args, **kwargs):
    #     qs = self.filter_queryset(self.get_queryset())
    #
    #     class _Serializer(AppSerializer):
    #         ids = serializers.PrimaryKeyRelatedField(
    #             queryset=qs, allow_empty=True, many=True
    #         )
    #
    #     validation_serializer = _Serializer(data=self.get_request().data)
    #     if not validation_serializer.is_valid():
    #         return self.send_error_response(data=validation_serializer.errors)
    #
    #     ids = validation_serializer.validated_data["ids"]
    #     if ids:
    #         qs = qs.filter(id__in=[_.id for _ in ids])
    #
    #     columns_config = self.get_table_columns()
    #     return sync_export_csv_response(
    #         columns=columns_config.values(),
    #         queryset_values_list=qs.values_list(*columns_config.keys()),
    #     )

    # @action(
    #     methods=["POST"],
    #     url_path="table-columns-preference",
    #     detail=False,
    # )
    # def set_preference_for_table_columns_handler(self, *args, **kwargs):
    #     """
    #     Saves the `TableColumnsPreferenceTracker` for the given `user` and
    #     the given `self.table_preference_identifier`.
    #     """
    #
    #     if self.table_preference_identifier:
    #
    #         class _Serializer(AppSerializer):
    #             columns = serializers.MultipleChoiceField(
    #                 choices=[*self.all_table_columns.keys()], allow_empty=False
    #             )
    #
    #         serializer = _Serializer(data=self.get_request().data)
    #         serializer.is_valid(raise_exception=True)
    #
    #         TableColumnsPreferenceTracker.objects.filter(
    #             created_by=self.get_organisation_user(),
    #             table_identifier=self.table_preference_identifier,
    #         ).delete()
    #         TableColumnsPreferenceTracker.objects.create(
    #             columns=[
    #                 _
    #                 for _ in self.request.data["columns"]
    #                 if _ in serializer.validated_data["columns"]
    #             ],
    #             created_by=self.get_organisation_user(),
    #             table_identifier=self.table_preference_identifier,
    #         )
    #
    #     return self.send_response()

    # @action(
    #     methods=["GET"],
    #     url_path="filter-meta",
    #     detail=False,
    # )
    # def get_meta_for_filter_handler(self, *args, **kwargs):
    #     """
    #     Sends out all the necessary data of the filter component for the
    #     front-end. This is from where the user selects the options.
    #     """
    #
    #     return self.send_response(data=self.get_meta_for_filter())

    # def get_meta_for_filter(self) -> dict:
    #     """
    #     Just an adaptor class for the `get_meta_for_filter_handler`.
    #     Overridden on the child classes to send data.
    #     """
    #
    #     return {}

    def serialize_for_filter(self, queryset, fields=None):
        """Simple central function to serialize data for the filter component."""

        if not fields:
            fields = ["id", "identity"]

        return simple_serialize_queryset(queryset=queryset, fields=fields)


class AppModelCUDAPIViewSet(
    AppViewMixin,
    CreateModelMixin,
    UpdateModelMixin,
    DestroyModelMixin,
    AppGenericViewSet,
):
    """
    What is CUD?
        Create, Update & Delete

    What is a CUD ViewSet?
        A ViewSet that handles the necessary CUD operations.

    Why is this separated from the ModelViewSet?
        User Permissions can be two types:
            > View
            > Modify
        An user can have anyone or both for a particular entity like `ProjectType`.
        These conditions can be handled easily, when the CUD is separated.

    Urls Allowed:
        > POST: {endpoint}/
            >> Get data from front-end and creates an object.
        > GET: {endpoint}/meta/
            >> Returns metadata for the front-end for object creation.

        > PUT: {endpoint}/<pk>/
            >> Get data from font-end to update an object.
        > GET: {endpoint}/<pk>/meta/
            >> Returns metadata for the front-end for object update.

        > DELETE: {endpoint}/<pk>/
            >> Deletes the object identified by the passed `pk`.
    """

    @action(
        methods=["GET"],
        url_path="meta",
        detail=False,
    )
    def get_meta_for_create(self, *args, **kwargs):
        """Returns the meta details for create from serializer."""

        return self.send_response(data=self.get_serializer().get_meta_for_create())

    @action(
        methods=["GET"],
        url_path="meta",
        detail=True,
    )
    def get_meta_for_update(self, *args, **kwargs):
        """Returns the meta details for update from serializer."""
        return self.send_response(
                data=self.get_serializer(instance=self.get_object()).get_meta_for_update()
            )
    
    # Override the create method to sanitize content
    def create(self, request, *args, **kwargs):
        # For CKEditor
        description = request.data.get('description')
        if description is not None:
            sanitized_content = bleach.clean(description, tags=settings.BLEACH_ALLOWED_TAGS, attributes=settings.BLEACH_ALLOWED_ATTRIBUTES)
            request.data['description'] = sanitized_content
        return super().create(request, *args, **kwargs)

    # Override the update method to sanitize content
    def update(self, request, *args, **kwargs):
        # For CKEditor
        description = request.data.get('description')
        if description is not None:
            sanitized_content = bleach.clean(description, tags=settings.BLEACH_ALLOWED_TAGS, attributes=settings.BLEACH_ALLOWED_ATTRIBUTES)
            request.data['description'] = sanitized_content
        return super().update(request, *args, **kwargs)


# Config for Meta fields to send for filters and other place where identity only used.
DEFAULT_IDENTITY_DISPLAY_FIELDS = (
    "id",
    "identity",
    "uuid",
)


class AbstractLookUpFieldMixin:
    """
    This class provides config for which field to look in the model as well as
    in url.
    """

    lookup_url_kwarg = "uuid"
    lookup_field = "uuid"


def get_upload_api_view(meta_model, meta_fields=None):
    """Central function to return the UploadAPIView. Used to handle uploads."""

    if not meta_fields:
        meta_fields = ["file", "id"]

    class _View(AppCreateAPIView):
        """View to handle the upload."""

        class _Serializer(AppModelSerializer):
            """Serializer for write."""

            class Meta(AppModelSerializer.Meta):
                model = meta_model
                fields = meta_fields

        parser_classes = [parsers.MultiPartParser]
        serializer_class = _Serializer

    return _View

def get_upload_non_auth_api_view(meta_model, meta_fields=None):
    """Central function to return the UploadAPIView. Used to handle uploads. For Non Authenticte User."""

    if not meta_fields:
        meta_fields = ["file", "id"]

    class _View(NonAuthenticatedAPIMixin, AppCreateAPIView):
        """View to handle the upload."""

        class _Serializer(AppModelSerializer):
            """Serializer for write."""

            class Meta(AppModelSerializer.Meta):
                model = meta_model
                fields = meta_fields

        parser_classes = [parsers.MultiPartParser]
        serializer_class = _Serializer

    return _View
