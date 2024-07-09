from apps.common.serializers import AppReadOnlyModelSerializer
from apps.meta.models.location import City, BLPAddress
from rest_framework import serializers


class CityListModelSerializer(AppReadOnlyModelSerializer):
    """List serializer for city"""
    
    class Meta:
        model = City
        fields = [
            "id",
            "identity",
            "state"
        ]
        
class BLPAddressListModelSerializer(AppReadOnlyModelSerializer):
    """List serializer for BLPAddress"""
    
    display_name = serializers.SerializerMethodField()
    
    class Meta:
        model = BLPAddress
        fields = [
            "id",
            "identity",
            "city",
            "display_name",
        ]
        
    def get_display_name(self, obj):
        """Returns the Address-City"""
        
        return f"{str(obj.identity).capitalize()}-{str(obj.city.identity).capitalize()}"
    