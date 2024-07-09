from django.db import models

from apps.common.models import COMMON_CHAR_FIELD_MAX_LENGTH, BaseModel


class Country(BaseModel):
    """Holds country data."""
    DYNAMIC_KEY = "country"

    identity = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH, unique=True)


class State(BaseModel):
    """Holds state data under a country."""
    DYNAMIC_KEY = "state"

    identity = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH, unique=True)
    country = models.ForeignKey(to=Country, on_delete=models.CASCADE)


class City(BaseModel):
    """City information under a state."""
    DYNAMIC_KEY = "city"

    identity = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH, unique=True)
    state = models.ForeignKey(to=State, on_delete=models.CASCADE)

class BLPAddress(BaseModel):
    """Addres information under a City"""
    
    DYNAMIC_KEY = "blp-address"
    identity = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH, unique=True)
    city = models.ForeignKey(to=City, on_delete=models.CASCADE)