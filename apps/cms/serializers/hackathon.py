from rest_framework import serializers
from apps.hackathons.models import prizes as prize_models
from apps.hackathons.models import hackathon as hackathon_models
from apps.hackathons.models import round_details as round_models
from apps.learning.models import Skill
from django.contrib.auth.models import AnonymousUser
from apps.common.serializers import (
    AppReadOnlyModelSerializer
)

class HackathonPrizeDetailsSerializer(AppReadOnlyModelSerializer):
    class Meta:
        model = prize_models.HackathonPrizeDetails
        fields = ['rank', 'prize_amount']

class JudgeImageSerializer(AppReadOnlyModelSerializer):
    class Meta:
        model = round_models.JudgeImage
        fields = ['id', 'uuid', 'file']

class JudgeDetailsSerializer(AppReadOnlyModelSerializer):
    image = JudgeImageSerializer()
    class Meta:
        model = round_models.HackathonJudge
        fields = ['id', 'uuid', 'identity', 'designation', 'image']

class HackathonRoundDetailsSerializer(AppReadOnlyModelSerializer):
    class Meta:
        model = round_models.HackathonRoundDetails
        fields = "__all__"

class SkillSerializer(AppReadOnlyModelSerializer):
    class Meta:
        model =  Skill
        fields = ['uuid', 'identity']

class HackathonImageSerializer(AppReadOnlyModelSerializer):
    class Meta:
        model = hackathon_models.HackathonImage
        fields = ['id', 'uuid', 'file']

class HackathonListSerializer(AppReadOnlyModelSerializer):
    prizes_details = HackathonPrizeDetailsSerializer(many=True)
    round_details = HackathonRoundDetailsSerializer(many=True)
    skills = SkillSerializer(many=True)
    image = HackathonImageSerializer()
    is_registered = serializers.SerializerMethodField()
    participant_count = serializers.SerializerMethodField()

    class Meta:
        model = hackathon_models.Hackathon
        fields = [
            'id',
            'uuid',
            'identity',
            'language',
            'image',
            'description',
            'no_of_attempts_allowed',
            'no_of_participants_limit',
            'user_group',
            'skills',
            'hackathon_fees',
            'start_date',
            'end_date',
            'prizes_details',
            'problem_statement',
            'expected_solution',
            'round_details',
            'general_rules',
            'eligibility',
            'how_to_enter',
            'submission_required',
            'terms_and_conditions',
            'is_registered',
            'is_free',
            'participant_count',
        ]
    
    def get_is_registered(self,obj):
        """This function used to get course is already in buy or not"""
        user = self.get_user()
        if isinstance(user, AnonymousUser) or user == None:
            return False
        else:
            is_buy = hackathon_models.HackathonParticipant.objects.filter(entity_id=obj.id, created_by=user).exists()
            return is_buy

    def get_participant_count(self, obj):
        return hackathon_models.HackathonParticipant.objects.filter(entity_id=obj.id).count()
        
class HackathonJobListSerializer(AppReadOnlyModelSerializer):
    image = HackathonImageSerializer()

    class Meta:
        model = hackathon_models.Hackathon
        fields = [
            'id',
            'uuid',
            'identity',
            'language',
            'image',
            'description',
            'skills',
            'hackathon_fees',
            'start_date',
            'end_date',
            'prizes_details',
            'eligibility',
        ]
