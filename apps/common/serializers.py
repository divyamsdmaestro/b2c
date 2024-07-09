from rest_framework import serializers
from rest_framework.fields import SkipField
from rest_framework.serializers import ModelSerializer, Serializer

from apps.common import model_fields
from apps.common.config import CUSTOM_ERRORS_MESSAGES
from apps.common.helpers import get_display_name_for_slug, get_first_of
from django.db import models


class CustomErrorMessagesMixin:
    """
    Overrides the constructor of the serializer to add meaningful error
    messages to the serializer output. Also used to hide security
    related messages to the user.
    """

    def get_display(self, field_name):
        return field_name.replace("_", " ")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # adding custom error messages
        for field_name, field in getattr(self, "fields", {}).items():
            if field.__class__.__name__ == "ManyRelatedField":
                # many-to-many | uses foreign key field for children
                field.error_messages.update(CUSTOM_ERRORS_MESSAGES["ManyRelatedField"])
                field.child_relation.error_messages.update(
                    CUSTOM_ERRORS_MESSAGES["PrimaryKeyRelatedField"]
                )
            elif field.__class__.__name__ == "PrimaryKeyRelatedField":
                # foreign-key
                field.error_messages.update(
                    CUSTOM_ERRORS_MESSAGES["PrimaryKeyRelatedField"]
                )
            else:
                # other input-fields
                field.error_messages.update(
                    {
                        "blank": f"Please enter your {self.get_display(field_name)}",
                        "null": f"Please enter your {self.get_display(field_name)}",
                    }
                )


class AppSerializer(CustomErrorMessagesMixin, Serializer):
    """
    The app's version for the Serializer class. Just to implement common and
    other verifications and schema. Used only for light weight stuff.
    """

    def get_initial_data(self, key, expected_type):
        """
        Central function to get the initial data without breaking. We might
        expect a string, but user gave None. The given expected_type
        is what the type of data the caller is expecting.
        """

        _data = self.initial_data.get(key)

        if type(_data) != expected_type:
            raise SkipField()

        return _data

    def get_user(self):
        """Return the user from the request."""

        return self.get_request().user

    def get_request(self):
        """Returns the request."""

        return self.context["request"]


class AppModelSerializer(AppSerializer, ModelSerializer):
    """
    Applications version of the ModelSerializer. There are separate serializers
    defined for handling the read and write operations separately.

    Note:
        Never mix the `read` and `write` serializers, handle them separate.
    """

    class Meta:
        pass


class AppWriteOnlyModelSerializer(AppModelSerializer):
    """
    Write only version of the `AppModelSerializer`. Does not support read
    operations and to_representations. Validations are implemented here.

    Note:
        Never mix the `read` and `write` serializers, handle them separate.
    """

    def create(self, validated_data):
        """Overridden to set the `created_by` field."""

        instance = super().create(validated_data=validated_data)

        # setting the anonymous fields
        if hasattr(instance, "created_by") and not instance.created_by:
            user = self.get_user()

            instance.created_by = user if user and user.is_authenticated else None
            instance.save()

        return instance

    def get_validated_data(self, key=None):
        """Central function to return the validated data."""

        if not key:
            return self.validated_data
        return self.validated_data[key]

    def __init__(self, *args, **kwargs):
        # all fields are required
        for field in self.Meta.fields:
            self.Meta.extra_kwargs.setdefault(field, {})
            self.Meta.extra_kwargs[field]["required"] = True

        super().__init__(*args, **kwargs)

    class Meta(AppModelSerializer.Meta):
        model = None
        fields = []
        extra_kwargs = {}

    def to_internal_value(self, data):
        """Overridden to pre-process inbound data."""

        data = super().to_internal_value(data=data)

        # blank values are not allowed in our application | convert to null
        for k, v in data.items():
            if not v and v not in [False, 0, []]:
                data[k] = None

        return data

    def to_representation(self, instance):
        """Always show the updated data from instance back to the front-end."""

        return self.get_meta_initial()

    def serialize_choices(self, choices: list):
        """
        Given a list of choices like:
            ['active', ...]

        This will return the following:
            [{'id': 'active', 'identity': 'Active'}, ...]

        This will be convenient for the front end to integrate. Also
        this is considered as a standard.
        """

        from apps.common.helpers import get_display_name_for_slug

        return [{"id": _, "identity": get_display_name_for_slug(_)} for _ in choices]

    def serialize_for_meta(self, queryset, fields=None):
        """Central serializer for the `get_meta`. Just a dry function."""

        if not fields:
            fields = ["id", "identity"]

        return simple_serialize_queryset(fields=fields, queryset=queryset)

    def get_dynamic_render_config(self):
        """
        Returns a config that can be used by the front-end to dynamically
        render and handle the form fields. This improves delivery speed.
        """

        from django.db import models

        from apps.common.models import FileOnlyModel

        request = self.get_request()
        model = self.Meta.model
        render_config = []

        for _ in self.get_fields():
            model_field = model.get_model_field(_, fallback=None)

            field_type = "UNKNOWN_CONTACT_DEVELOPER"
            other_config = {}

            if model_field:
                # type
                try:
                    if (isinstance(model_field, models.ForeignKey) or isinstance(model_field, models.ManyToManyField)) and issubclass(
                        model_field.related_model, FileOnlyModel
                    ):
                        if "image" in _:
                            field_type = "ImageUpload"
                        else:
                            field_type = "FileUpload"

                        # TODO: REMEMBER: Hard Coded & Build Specifically for admin like panels
                        other_config[
                            "upload_path"
                        ] = f"{request.path.split('cud')[0]}{_}/upload/"
                    else:
                        field_type = model_field.__class__.__name__
                except Exception as e:
                    print(e)  # noqa

                # other render config
                try:
                    other_config["label"] = get_display_name_for_slug(
                        get_first_of(model_field.verbose_name, _)
                    )
                    other_config["help_text"] = get_first_of(model_field.help_text)
                    other_config["allow_null"] = model_field.null
                except Exception as e:
                    print(e)  # noqa

            render_config.append(
                {
                    "key": _,
                    "type": field_type,
                    "other_config": other_config,
                }
            )

        return render_config

    def get_meta(self) -> dict:
        """
        Returns the meta details for `get_meta_for_create` & `get_meta_for_update`.
        This is just a centralized function.
        """

        return {}

    def get_meta_for_create(self):
        """
        Returns the necessary meta details for front-end. Overridden
        on the child classes. Called from view.
        """

        return {
            "meta": self.get_meta(),
            "initial": {},
            "render_config": self.get_dynamic_render_config(),
        }

    def get_meta_for_update(self):
        """
        Returns the necessary meta details for front-end. Overridden
        on the child classes. Called from view.
        """

        return {
            "meta": self.get_meta(),
            "initial": self.get_meta_initial(),
            "urls": self.get_meta_urls(),  # file & images
            "render_config": self.get_dynamic_render_config(),
        }

    def get_meta_urls(self) -> dict:
        """
        Returns the file/image urls for the necessary fields for the FE.
        Just used for displaying for the front-end.
        """

        from apps.common.models import FileOnlyModel

        instance = self.instance
        urls = {}

        for field_name in self.fields.keys():
            field = self.Meta.model.get_model_field(field_name)
            related_model = field.related_model

            if (
                related_model
                and issubclass(related_model, FileOnlyModel)
                and getattr(instance, field_name)
            ):
                urls[field_name] = getattr(self.instance, field_name).file.url

        return urls


    def get_meta_initial(self):
        """
        Returns the `initial` data for `self.get_meta_for_update`. This is
        used by the front-end for setting initial values.
        """

        instance = self.instance
        initial = {
            field_name: getattr(instance, field_name, None)
            for field_name in ["id", *self.fields.keys()]
        }

        # simplify for FE
        for k, v in initial.items():
            # foreignkey
            if hasattr(initial[k], "pk"):
                if k == "representative":
                    # Get the foreign key object instead of calling `all()`
                    fk_instance = getattr(instance, k)
                    if fk_instance is not None:
                        initial[k] = {
                            "id": fk_instance.id,
                            "first_name": fk_instance.first_name,  # Replace with appropriate attribute
                            "middle_name": fk_instance.middle_name,
                            "last_name": fk_instance.last_name,
                            "alternative_email": fk_instance.alternative_email
                        }
                    else:
                        initial[k] = None
                else:
                    initial[k] = v.pk

            # not a model field
            if not instance.__class__.get_model_field(k, None):
                continue

            # many-to-many
            if instance.__class__.get_model_field(k).many_to_many:
                if k == "prizes_details" or k == "round_details" or k == "role_permissions" or k == "education_details" or k == "poll_options" or k == "eligibility_criteria" or k == "job_round_details" or k == "feedback_question" or k == "forums" or k=="schedule_details":
                    if k=="schedule_details":
                        """for getting address_id as address and mode_id as mode"""
                        
                        if k not in initial or not isinstance(initial[k], list):
                            initial[k] = []
                        m2m_values = getattr(instance, k).all().values()
                        for value in list(m2m_values):
                            data = {
                                "address": value.get('address_id', None),
                                "created": value.get('created'),
                                "created_by": value.get('created_by'),
                                "duration": value.get('duration'),
                                "end_date": value.get('end_date'),
                                "end_time": value.get('end_time'),
                                "id": value.get('id'),
                                "is_day_batch": value.get('is_day_batch'),
                                "is_weekend_batch": value.get('is_weekend_batch'),
                                "mentor": value.get('mentor'),
                                "mode": value.get('mode_id', None),
                                "modified": value.get('modified'),
                                "start_date": value.get('start_date'),
                                "start_time": value.get('start_time'),
                                "uuid": value.get('uuid'),
                                "virtual_url": value.get('virtual_url'),
                                "filling_fast": value.get('filling_fast') 
                            }
                            initial[k].append(data)
                    else:
                        m2m_values = getattr(instance, k).all().values()
                        initial[k] = list(m2m_values)
                else:
                    initial[k] = getattr(instance, k).values_list("pk", flat=True)


            if (
                instance.__class__.get_model_field(k).__class__
                == model_fields.AppPhoneNumberField
            ):
                initial[k] = (
                    getattr(instance, k).raw_input if getattr(instance, k) else None
                )

        return initial


class AppReadOnlyModelSerializer(AppModelSerializer):
    """
    Read only version of the `AppModelSerializer`. Does not
    support write operations.

    Note:
        Never mix the `read` and `write` serializers, handle them separate.
    """

    class Meta(AppModelSerializer.Meta):
        pass

    def create(self, validated_data):
        raise NotImplementedError

    def update(self, instance, validated_data):
        raise NotImplementedError


def get_app_read_only_serializer(
    meta_model,
    meta_fields=None,
    init_fields_config=None,
    queryset=None
):
    """
    Generates a `AppReadOnlyModelSerializer` on the runtime and returns the same.
    Just used for creating a light weigth stuff.
    """

    if meta_fields is None:
        meta_fields = ["id", "identity"]

    if meta_fields != "__all__":
        meta_fields = [*meta_fields] if type(meta_fields) == list else meta_fields

    class _Serializer(AppReadOnlyModelSerializer):
        serial_number = serializers.SerializerMethodField()
        
        class Meta(AppReadOnlyModelSerializer.Meta):
            model = meta_model
            fields = (
                meta_fields
                if meta_fields == "__all__"
                else [_ for _ in meta_fields if meta_model.get_model_field(_, None)]
                + ['serial_number']
            )

        def __init__(self, *args, **kwargs):
            """
            Overridden to set the custom fields passed on init_fields_config on init.
            Ex: { "logo": ImageDataSerializer() }
            """

            super().__init__(*args, **kwargs)
            if init_fields_config:
                for field, value in init_fields_config.items():
                    self.fields[field] = value

        def get_serial_number(self, instance):
            """Method to get the serial number for each item."""
            if queryset:
                return list(queryset).index(instance) + 1
            default_queryset = meta_model.objects.all()  # Replace this with the appropriate queryset
            return list(default_queryset).index(instance) + 1



    return _Serializer


def simple_serialize_queryset(fields, queryset):
    """Lightweight queryset serializer. Also implements performance booster."""

    if "id" in fields:
        # performance booster
        return [
            {**_, "id": str(_["id"])} for _ in queryset.only(*fields).values(*fields)
        ]

    return queryset.only(*fields).values(*fields)


def simple_serialize_instance(
    instance, keys: list, parent_data: dict = None, display=None
) -> dict:
    """
    Given a single object/instance, this will serialize the same.

    Params:
        -> instance         : Instance for serialization
        -> keys             : Serializable fields
        -> parent_data      : Inherited and returned
        -> display          : Display fields for the passed keys
    """

    def _serialize_value(_v):
        """Serialize objects for the front-end."""

        if type(_v) in [int, float]:
            return _v

        return str(_v) if _v else _v

    if not parent_data:
        parent_data = {}

    if not display:
        display = {}

    for key in keys:
        if "." in key:
            # eg: '__class__.__name__'
            _keys, _inter_value = key.split("."), None
            for _k in _keys:
                if not _inter_value:
                    _inter_value = getattr(instance, _k, None)
                else:
                    _inter_value = getattr(_inter_value, _k, None)
            parent_data[key] = _serialize_value(_inter_value)
        else:
            # eg: 'identity'
            parent_data[key] = _serialize_value(getattr(instance, key, None))

    # custom display for fields
    for k, d in display.items():
        parent_data[d] = parent_data.pop(k)

    return parent_data

def simple_serialize_foreignkey_instance(
    instance, keys: list, parent_data: dict = None, display=None
) -> dict:
    """
    Given a single object/instance, this will serialize the same.

    Params:
        -> instance         : Instance for serialization
        -> keys             : Serializable fields
        -> parent_data      : Inherited and returned
        -> display          : Display fields for the passed keys
    """

    def _serialize_value(_v):
        """Serialize objects for the front-end."""

        if type(_v) in [int, float]:
            return _v

        return str(_v) if _v else _v

    if not parent_data:
        parent_data = {}

    if not display:
        display = {}

    for key in keys:
        if "__" in key:
            # Handle related fields (foreign keys)
            related_fields = key.split("__")
            related_instance = instance
            for field in related_fields:
                if hasattr(related_instance, field):
                    related_instance = getattr(related_instance, field)
                else:
                    related_instance = None
                    break
            parent_data[key] = _serialize_value(related_instance)
        else:
            # Regular field serialization
            parent_data[key] = _serialize_value(getattr(instance, key, None))

    # Custom display for fields
    for k, d in display.items():
        parent_data[d] = parent_data.pop(k)

    return parent_data


class FileModelToURLField(serializers.Field):
    """
    Converts a given `FileUpload` instance to url directly.
    Used only as a read only serializer.
    """

    def to_internal_value(self, data):
        """Writeable method, not applicable."""

        raise NotImplementedError

    def to_representation(self, value):
        """Return the url."""

        return value.file.url
    
# For optimize performance
def get_read_serializer(meta_model, meta_fields=None, init_fields_config=None):

    if meta_fields is None:
        meta_fields = ['id', 'uuid', 'identity']
        
    class _Serializer(serializers.ModelSerializer):
        class Meta:
            model = meta_model
            fields = meta_fields

        def __init__(self, *args, **kwargs):
            """
            Overridden to set the custom fields passed on init_fields_config on init.
            Ex: { "logo": ImageDataSerializer() }
            """
            super().__init__(*args, **kwargs)
            if init_fields_config:
                for field, value in init_fields_config.items():
                    self.fields[field] = value

    return _Serializer

def get_app_read_only_optimize_serializer(
    meta_model,
    meta_fields=None,
    init_fields_config=None,
):
    """
    Generates a `AppReadOnlyModelSerializer` at runtime and returns the same.
    Used for creating lightweight serializers.
    """

    if meta_fields is None:
        meta_fields = ["id", "identity"]

    class _Serializer(AppReadOnlyModelSerializer):
        class Meta(AppReadOnlyModelSerializer.Meta):
            model = meta_model
            fields = [
                field for field in meta_fields if meta_model.get_model_field(field, None)
            ]

        def __init__(self, *args, **kwargs):
            """
            Overridden to set the custom fields passed in init_fields_config on init.
            Example: { "logo": ImageDataSerializer() }
            """
            super().__init__(*args, **kwargs)
            if init_fields_config:
                self.fields.update(init_fields_config)

    return _Serializer