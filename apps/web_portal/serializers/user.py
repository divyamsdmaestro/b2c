from apps.cms.serializers.hackathon import SkillSerializer
from apps.meta.models import EducationDetail, UserJobDetail, CareerHighlights, UserProject
from apps.common.serializers import AppWriteOnlyModelSerializer
from apps.access.models import User
from rest_framework import serializers



class JobDetailSerializer(AppWriteOnlyModelSerializer):
    class Meta(AppWriteOnlyModelSerializer.Meta):
        model = UserJobDetail
        fields = [
            "employment_type",
            "job_title",
            "location",
            "industry",
            "employer_name",
            "job_summary",
            "start_date",
            "end_date"
            ]

class CareerHighlightSerializer(AppWriteOnlyModelSerializer):
        class _ProjectSerializer(serializers.ModelSerializer):
            class Meta:
                model =  UserProject
                fields = ['identity', 'description']
        projects = _ProjectSerializer(many=True)

        class Meta(AppWriteOnlyModelSerializer.Meta):
            model = CareerHighlights
            fields = [
                "skills",
                "languages",
                "interests",
                "projects",
                "achievements",
                ]

class UserSerializer(AppWriteOnlyModelSerializer):
    
    class _EducationDetailSerializer(AppWriteOnlyModelSerializer):

        class Meta(AppWriteOnlyModelSerializer.Meta):
            model = EducationDetail
            fields = ["qualification", "university_name", "degree", "college_name", "class_name", "overall_percentage"]

    education_details = _EducationDetailSerializer(many=True)
    job_details = JobDetailSerializer(many=True)
    career_highlights = CareerHighlightSerializer()

    class Meta(AppWriteOnlyModelSerializer.Meta):
        model = User
        fields = [
            "first_name",
            "middle_name",
            "last_name",
            # "gender",
            # "birth_date",
            # "identification_type",
            # "identification_number",
            "address",
            "country",
            "state",
            "city",
            "pincode",
            "education_details",
            "resume",
            "job_details",
            "career_highlights",
        ]

    def update(self, instance, validated_data):
        
        # Retrieve and remove nested data from validated_data
        education_details_data = validated_data.pop("education_details", [])
        job_details_data = validated_data.pop("job_details", [])
        career_highlights_data = validated_data.pop("career_highlights", {})


        skills_data = career_highlights_data.pop("skills",[])
        languages_data = career_highlights_data.pop("languages",[])
        interests_data = career_highlights_data.pop("interests",[])
        projects_data = career_highlights_data.pop("projects",[])

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
        if job_details_data:
            user.job_details.clear()
            for data in job_details_data:
                job_details = UserJobDetail.objects.filter(**data)
                if job_details.exists():
                    job_detail = job_details.first()
                else:
                    job_detail = UserJobDetail.objects.create(**data)
                user.job_details.add(job_detail)

        if user.career_highlights:
            career_highlights = super().update(validated_data=career_highlights_data, instance=user.career_highlights)
        else:
            career_highlights = CareerHighlights.objects.create(**career_highlights_data)
            user.career_highlights = career_highlights
            user.save()

        if career_highlights.skills.exists():
            career_highlights.skills.clear()
        for data in skills_data:
            career_highlights.skills.add(data)
    
        if career_highlights.languages.exists():
            career_highlights.languages.clear()
        for data in languages_data:
            career_highlights.languages.add(data)

        if career_highlights.interests.exists():
            career_highlights.interests.clear()
        for data in interests_data:
            career_highlights.interests.add(data)
        
        if career_highlights.projects.exists():
            career_highlights.projects.clear()
        for data in projects_data:
            projects = UserProject.objects.filter(**data)
            if projects.exists():
                project = projects.first()
            else:
                project = UserProject.objects.create(**data)
            career_highlights.projects.add(project)

        return user