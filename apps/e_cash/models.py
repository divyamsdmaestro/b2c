# from django.db import models
# from apps.common.models import (
#     COMMON_CHAR_FIELD_MAX_LENGTH,
#     BaseModel,
# )
# from apps.common.models.base import COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG

# # Create your models here.
# class EcashMeta(BaseModel):
    
#     """
#     Holds the `Ecash actions` details
#     """

#     DYNAMIC_KEY = "ecashmeta"

#     identity = models.CharField(unique=True,max_length=COMMON_CHAR_FIELD_MAX_LENGTH)
    
# class Ecash(BaseModel):
    
    
#     """
#     Holds the `Ecash actions and its points` details
#     """

#     DYNAMIC_KEY = "ecash"
    
#     ecashmeta = models.ForeignKey(
#         to="e_cash.EcashMeta",
#         related_name="related_ecashMeta",
#         null=True,
#         on_delete=models.SET_NULL,
#     )
#     points = models.FloatField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
