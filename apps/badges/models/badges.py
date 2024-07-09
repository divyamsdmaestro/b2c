# from django.db import models
# from apps.common import model_fields
# from apps.common.models import (
#     COMMON_CHAR_FIELD_MAX_LENGTH,
#     BaseModel,
# )
# from apps.common.models.base import COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG, FileOnlyModel

# # Create your models here.
# class BadgesMeta(BaseModel):
    
#     """
#     Holds the `Badge` details
#     """

#     DYNAMIC_KEY = "badgesmeta"

#     identity = models.CharField(unique=True,max_length=COMMON_CHAR_FIELD_MAX_LENGTH)
    
    
# class BadgeImage(FileOnlyModel):
#     """Holds Image data for a `Badge`."""

#     DYNAMIC_KEY = "badge-image"

#     file = model_fields.AppSingleFileField(
#         upload_to="files/badges/image/",
#     ) 

    
# class Badges(BaseModel):
    

#     """
#     Holds the `Badge and its points` details
#     """

#     DYNAMIC_KEY = "badges"
    
#     name = models.CharField(unique=True,**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG,max_length=COMMON_CHAR_FIELD_MAX_LENGTH)
#     badgesmeta = models.ForeignKey(
#         to="BadgesMeta",
#         related_name="related_badgeMeta",
#         null=True,
#         on_delete=models.SET_NULL,
#     )
#     image = models.ForeignKey(to="BadgeImage", on_delete=models.SET_NULL,**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG,)
#     description = models.TextField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
#     points = models.IntegerField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)    
    

    
    
