from django.db import models

from apps.common.models import BaseModel


class CourseBuylist(BaseModel):
    """
    Holds courses that are in the users already buy or not.
    The created_by holds the user data.
    """

    entity = models.ForeignKey(
        to="learning.Course",
        on_delete=models.CASCADE,
    )


class LearningPathBuylist(BaseModel):
    """
    Holds learning paths that are in the users already buy or not.
    The created_by holds the user data.
    """

    entity = models.ForeignKey(
        to="learning.LearningPath",
        on_delete=models.CASCADE,
    )


class CertificationPathBuylist(BaseModel):
    """
    Holds certification paths that are in the users already buy or not.
    The created_by holds the user data.
    """

    entity = models.ForeignKey(
        to="learning.CertificationPath",
        on_delete=models.CASCADE,
    )
