from rest_framework import serializers
from apps.access.models import RolePermission

class RolePermissionDetailSerializer(serializers.ModelSerializer):

    class Meta:
        model = RolePermission
        fields = ['permission', 'to_create', 'to_view', 'to_edit', 'to_delete']