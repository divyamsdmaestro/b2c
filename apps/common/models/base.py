import uuid
from contextlib import suppress

from django.conf import settings
from django.core.exceptions import FieldDoesNotExist
from django.db import DEFAULT_DB_ALIAS, IntegrityError, models

from apps.common.managers import BaseObjectManagerQuerySet

# top level config
COMMON_CHAR_FIELD_MAX_LENGTH = 512
COMMON_NULLABLE_FIELD_CONFIG = {  # user for API based stuff
    "default": None,
    "null": True,
}
COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG = {  # user for Form/app based stuff
    **COMMON_NULLABLE_FIELD_CONFIG,
    "blank": True,
}


class FixturesLoadingMixin:
    """Central class to load fixtures data in the database."""

    FIXTURES_DATA: list[dict] = []

    @classmethod
    def load_fixtures_data(cls, use_db=DEFAULT_DB_ALIAS):
        """Function that loads the fixtures' data when called."""

        for data in cls.get_fixtures_data(use_db=use_db):
            # M2M data
            m2m_data = {}

            # pre-process the single data dict
            for key, value in data.items():
                field = cls.get_model_field(key)
                related_model = field.related_model

                # All data | M2M field
                if value == "__all__":
                    assert related_model

                    m2m_data[key] = [*related_model.objects.using(use_db).all()]

                # Specific data | M2M field
                elif field.many_to_many:
                    assert type(value) is list

                    m2m_data[key] = []
                    for _ in value:
                        instance = related_model.objects.using(use_db).get_or_none(**_)
                        assert instance
                        m2m_data[key].append(instance)

                else:
                    pass

            with suppress(IntegrityError):  # ignore constrains | skip if already exists
                # save the instance | ignore the M2M data
                instance = cls(**{k: v for k, v in data.items() if k not in m2m_data})
                instance.save(using=use_db)

                # set the M2M data
                for k, v in m2m_data.items():
                    getattr(instance, k).set(v)

    @classmethod
    def get_fixtures_data(cls, use_db):
        """
        Returns the fixtures' data. Override in child when pre-processing
        of data is required, Like DB querying and replacing with FK.
        """

        return cls.FIXTURES_DATA


class BaseModel(models.Model):
    """
    Contains the last modified and the created fields, basically
    the base model for the entire app.
    """

    # unique id field
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)

    # time tracking
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    # by whom
    created_by = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        related_name="created_%(class)s",
        on_delete=models.SET_DEFAULT,
        **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG,
    )

    # custom manager
    objects = BaseObjectManagerQuerySet.as_manager()

    class Meta:
        abstract = True

    @classmethod
    def get_model_fields(cls):
        """
        Returns all the model fields. This does not
        include the defined M2M & related fields.
        """

        return cls._meta.fields

    @classmethod
    def get_all_model_fields(cls):
        """
        Returns all model fields, this includes M2M and related fields.
        Note: The field classes will be different & additional here.
        """

        return cls._meta.get_fields()

    @classmethod
    def get_model_field_names(cls, exclude=[]):  # noqa
        """Returns only the flat field names of the model."""

        exclude = ["id", "created_by", "created", "modified", *exclude]
        return [_.name for _ in cls.get_model_fields() if _.name not in exclude]

    @classmethod
    def get_model_field(cls, field_name, fallback=None):
        """Returns a single model field given by `field_name`."""

        with suppress(FieldDoesNotExist):
            return cls._meta.get_field(field_name)

        return fallback


class FileOnlyModel(BaseModel):
    """
    Parent class for all the file only models. This is used as a common class
    and for differentiating field on the run time.

    This will contain only:
        file = model_fields.AppSingleFileField(...)

    This model is then linked as a foreign key where ever necessary.
    """

    class Meta(BaseModel.Meta):
        abstract = True
