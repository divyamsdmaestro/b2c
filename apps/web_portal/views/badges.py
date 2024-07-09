from rest_framework import serializers
# from apps.badges.models.badges import BadgeImage, Badges
from apps.common.views.api import AppAPIView
from apps.access.models import User

from ...common.serializers import  AppReadOnlyModelSerializer

# class BadgeImageSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = BadgeImage
#         fields = ('id','file')
        
# class BadgesSerializer(serializers.ModelSerializer):
#     image = BadgeImageSerializer()
#     class Meta:
#         model = Badges
#         fields = ('id','name','image')
        
# class UserBadgesSerializer(serializers.ModelSerializer):
#     badges = BadgesSerializer()
#     class Meta:
#         model = UserBadges
#         fields = ('badges', 'points')

# class UserSerializer(serializers.ModelSerializer):
#     # userbadges_set = UserBadgesSerializer(many=True, read_only=True)

#     class Meta:
#         model = User
#         fields = ('id', 'full_name', 'total_badge_points')

# class LeaderBoardListAPIView(AppAPIView):
#     def get(self, request):
#         users = User.objects.all().order_by('-total_badge_points')  # Retrieve users ordered by total badge points
#         serializer = UserSerializer(users, many=True)

#         data = {
#             'leaderboard': serializer.data,
#             'achievers': serializer.data[:3]
#         }
#         return self.send_response(data=data)


