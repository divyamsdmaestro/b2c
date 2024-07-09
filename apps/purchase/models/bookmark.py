from django.db import models
from apps.common.models import BaseModel


class CourseModuleVideoBookMarklist(BaseModel):
    """
    Holds courses that are in the users wishlist.
    The created_by holds the user data.
    """

    entity = models.ForeignKey(
        to="learning.CourseSubModule",
        on_delete=models.CASCADE,
    )


class LearningPathModuleVideoBookMarklist(BaseModel):
    """
    Holds learning paths that are in the users wishlist.
    The created_by holds the user data.
    """

    entity = models.ForeignKey(
        to="learning.CourseSubModule",
        on_delete=models.CASCADE,
    )


class CertificationPathModuleVideoBookMarklist(BaseModel):
    """
    Holds certification paths that are in the users wishlist.
    The created_by holds the user data.
    """

    entity = models.ForeignKey(
        to="learning.CourseSubModule",
        on_delete=models.CASCADE,
    )