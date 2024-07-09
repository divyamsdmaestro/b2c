from apps.meta.models import EducationDetail
from apps.common.serializers import AppWriteOnlyModelSerializer, AppReadOnlyModelSerializer
from apps.access.models import User, UserRole
from rest_framework import serializers


class StudentSerializer(AppWriteOnlyModelSerializer):
    class _EducationDetailSerializer(AppWriteOnlyModelSerializer):

        class Meta(AppWriteOnlyModelSerializer.Meta):
            model = EducationDetail
            fields = ["qualification", "university_name", "degree", "college_name"]

    education_details = _EducationDetailSerializer(many=True)

    class Meta(AppWriteOnlyModelSerializer.Meta):
        model = User
        fields = [
            "first_name",
            "middle_name",
            "last_name",
            "gender",
            # "user_role",
            # "martial_status",
            "birth_date",
            "identification_type",
            "identification_number",
            "address",
            "country",
            "state",
            "city",
            "pincode",
            "admission_id",
            "alternative_email",
            "education_details",
        ]

    def update(self, instance, validated_data):
        education_details_data = validated_data.pop(
            "education_details", []
        )
        user = super().update(validated_data=validated_data, instance=instance)

        # M2M fields
        if education_details_data:
            user.education_details.clear()
            for data in education_details_data:
                education_details = EducationDetail.objects.filter(**data)
                if education_details.exists():
                    education_detail = education_details.first()
                else:
                    education_detail = EducationDetail.objects.create(**data)
                user.education_details.add(education_detail)
        return user


class StaffSerializer(AppWriteOnlyModelSerializer):

    class Meta(AppWriteOnlyModelSerializer.Meta):
        model = User
        fields = [
            "first_name",
            "middle_name",
            "last_name",
            # "user_role",
            "alternative_email",
        ]

class StudentDetailSerializer(AppReadOnlyModelSerializer):
    user_role = serializers.SerializerMethodField()

    class Meta(AppReadOnlyModelSerializer.Meta):
        model = User
        fields = [
            "first_name",
            "middle_name",
            "last_name",
            "user_role",
            "idp_email",
        ]
    def get_user_role(self,obj):
        if obj.user_role:
            user_role = UserRole.objects.get(id=obj.user_role.id)
            if user_role:
                return user_role.identity
            else:
                return None
        else:
            return None