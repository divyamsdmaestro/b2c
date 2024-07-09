from django.db import models
from apps.access.models import InstitutionUserGroupDetail
from apps.common import model_fields
from apps.common.models import (
    COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG,
    COMMON_CHAR_FIELD_MAX_LENGTH,
    BaseModel,
    FileOnlyModel,
)
from apps.hackathons.models import prizes as prize_models
from apps.hackathons.models import round_details as round_models
from apps.hackathons.models import industry as industry_models

class HackathonImage(FileOnlyModel):
    """Image data for a `Hackathon`."""

    file = model_fields.AppSingleFileField(
        upload_to="files/hackathon/image/",
    )

class Hackathon(BaseModel):
    """
    This model holds information about the hackathon that will be provided.
    """

    DYNAMIC_KEY = "hackathon"

    #primary information
    identity = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH)
    language = models.ForeignKey(
        to="learning.Language",
        on_delete=models.SET_NULL,
        **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG,
    )
    image = models.ForeignKey(
        to=HackathonImage,
        on_delete=models.SET_NULL,
        **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG,
    )
    description = models.TextField()
    no_of_attempts_allowed = models.PositiveIntegerField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    no_of_participants_limit = models.PositiveIntegerField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    user_group = models.ManyToManyField(
        to=InstitutionUserGroupDetail,
        blank=True
    )
    skills = models.ManyToManyField(
        to="learning.Skill",
        blank=True,
    )
    hackathon_fees = models.FloatField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    #hackathon schedule
    start_date = models.DateField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    end_date = models.DateField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    #prizes details
    prizes_details = models.ManyToManyField(
        prize_models.HackathonPrizeDetails,
    )
    #hackathon details
    problem_statement = models.TextField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    expected_solution = models.TextField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    round_details = models.ManyToManyField(
        round_models.HackathonRoundDetails,
    )
    #rules
    general_rules = models.TextField()
    eligibility = models.TextField()
    how_to_enter = models.TextField()
    submission_required = models.TextField()
    terms_and_conditions = models.TextField()
    # Boolean field
    is_free = models.BooleanField(default=False)
    zone = models.ForeignKey(
        to="forums.Zone",
        on_delete=models.SET_NULL,
        **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG,
    )

# class HackathonParticipants(BaseModel):
#     """This model holds the fields of `Hackathon Participants`."""

#     DYNAMIC_KEY = "hackathon-participants"

#     JOIN_HACKATHON_CHOICES = (
#         ("individual", "individual"),
#         ("team", "team"),
#     )
#     user = models.ForeignKey(
#         to="access.user",
#         on_delete=models.SET_NULL,
#         **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG,
#     )
#     hackathon = models.ForeignKey(
#         to=Hackathon, on_delete=models.CASCADE,
#         null=True
#     )
#     join_hackathon_types = models.CharField(
#         max_length=COMMON_CHAR_FIELD_MAX_LENGTH,
#         choices=JOIN_HACKATHON_CHOICES,
#         default="individual",
#     )
#     industry = models.ForeignKey(
#         to=industry_models.IndustryType,
#         on_delete=models.SET_NULL,
#         null=True
#     )
#     skills = models.ManyToManyField(
#         to="learning.Skill",
#     )

class HackathonParticipant(BaseModel):

    entity = models.ForeignKey(to=Hackathon, on_delete=models.CASCADE)

class HackathonUpdates(BaseModel):
    """
    This model holds information about the hackathon update Details.
    """

    DYNAMIC_KEY = "hackathon-update"

    hackathon = models.ForeignKey(to=Hackathon, on_delete=models.CASCADE)
    desc = models.TextField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)

class HackathonSubmission(BaseModel):
    """
    This model holds information about the hackathon project submission Details by user.
    """

    DYNAMIC_KEY = "hackathon-submission"
    
    round = models.ForeignKey(to=round_models.HackathonRoundDetails, 
        on_delete=models.CASCADE, **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG,)
    hackathon = models.ForeignKey(Hackathon,
        on_delete=models.SET_NULL,
        **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG,)
    project_name = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH)
    elevator_pitch = models.TextField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    about_project = models.TextField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    built_with = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH)
    project_links = models.ManyToManyField(
        round_models.HackathonProjectLinks,
    )
    project_media = models.ForeignKey(to=round_models.HackathonSubmissionMediaFiles,
        on_delete=models.SET_NULL,
        **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG,)
    
class HackathonDiscussion(BaseModel):
    """
    This model holds information about the hackathon discussion details.
    """

    DYNAMIC_KEY = "hackathon-discussion"

    hackathon = models.ForeignKey(Hackathon,
        on_delete=models.SET_NULL,
        **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG,)
    title = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH)
    message = models.TextField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)

    def get_comments_count(self):
        comments = HackathonDiscussionComment.objects.filter(hackathon_discussion=self)
        return comments.count()

class HackathonDiscussionReply(BaseModel):
    """Holds the Hackathon Discussion comments replies data."""

    DYNAMIC_KEY = "hackathon-discussion-reply"

    comment = models.ForeignKey(
        to = "hackathons.HackathonDiscussionComment",
        on_delete=models.SET_NULL,
        **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG
    )
    identity = models.TextField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)


class HackathonDiscussionComment(BaseModel):
    """Holds the Hackathon Discussion comments data."""

    DYNAMIC_KEY = "hackathon-discussion-comment"
     
    hackathon_discussion = models.ForeignKey(
        to="hackathons.HackathonDiscussion",
        related_name="comments",
        on_delete=models.SET_NULL,
        **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG
    )
    identity = models.TextField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    replies = models.ManyToManyField(to="hackathons.HackathonDiscussionReply", blank=True)

    def replies_count(self):
        return self.replies.all().count()
