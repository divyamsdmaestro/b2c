from apps.common.views.api import AppAPIView
from apps.common.views.api.base import NonAuthenticatedAPIMixin
from rest_framework.generics import ListAPIView, RetrieveAPIView
from apps.web_portal.serializers import (
    JobEligibleSkillSerializer,
    JobEligibleSkillDetailSerializer,
    JobSkillCourseSerializer,
    JobSkillLearningPathSerializer,
    JobSkillCertificationPathSerializer,
    )
from apps.learning.models import JobEligibleSkill
from apps.common.pagination import HomePageAppPagination, AppPagination
from apps.common.views.api.generic import AbstractLookUpFieldMixin

class JobEligibleSkillListView(NonAuthenticatedAPIMixin, ListAPIView, AppAPIView):
    
    serializer_class = JobEligibleSkillSerializer
    queryset = JobEligibleSkill.objects.all()
    pagination_class = AppPagination

class JobEligibleSkillDetailView(NonAuthenticatedAPIMixin, AbstractLookUpFieldMixin, RetrieveAPIView, AppAPIView):

    queryset = JobEligibleSkill.objects.all()
    serializer_class = JobEligibleSkillDetailSerializer

class JobSkillCourseView(NonAuthenticatedAPIMixin, ListAPIView):
    serializer_class = JobSkillCourseSerializer
    pagination_class = HomePageAppPagination

    def get_queryset(self):
        job_skill = JobEligibleSkill.objects.get(uuid = self.kwargs['uuid'])
        return job_skill.courses.all()
    
class JobSkillLearningPathView(NonAuthenticatedAPIMixin, ListAPIView):
    serializer_class = JobSkillLearningPathSerializer
    pagination_class = HomePageAppPagination

    def get_queryset(self):
        job_skill = JobEligibleSkill.objects.get(uuid = self.kwargs['uuid'])
        return job_skill.learning_paths.all()
    
class JobSkillCertificationPathView(NonAuthenticatedAPIMixin, ListAPIView):
    serializer_class = JobSkillCertificationPathSerializer
    pagination_class = HomePageAppPagination

    def get_queryset(self):
        job_skill = JobEligibleSkill.objects.get(uuid = self.kwargs['uuid'])
        return job_skill.certification_paths.all()
    

