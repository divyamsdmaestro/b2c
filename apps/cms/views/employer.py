from apps.common.helpers import send_welcome_email
from apps.common.views.api import AppAPIView
from apps.common.serializers import AppWriteOnlyModelSerializer, AppModelSerializer, AppReadOnlyModelSerializer, get_app_read_only_serializer
from ...access.models import User, EmployerDetail, UserRole
from apps.service_idp.views import valid_idp_response
from apps.jobs.models import Job, JobAppliedList, JobRoundDetails, JobFeedbackTemplate, JobInterviewSchedule
from apps.common.serializers import get_app_read_only_serializer as read_serializer
from django.db.models import Count
from apps.cms.serializers.hackathon import HackathonImageSerializer
from apps.webinars.models import Webinar, WebinarImage
from apps.hackathons.models import hackathon as hackathon_models
from datetime import date
import requests
from django.conf import settings

def get_admin_headers():

    data_token = get_admin_token()
    header = {
        'Content-Type' : 'application/json',
        'Authorization': f'Bearer {data_token}'
    }
    return header

def get_admin_token():

    try:
        payload = {
            "userNameOrEmailAddress": settings.APP_SUPER_ADMIN['email'],
            "password": settings.APP_SUPER_ADMIN['password'],
            "rememberClient": True,
            "tenancyName": settings.IDP_TENANT_NAME
        }
        response = requests.post(settings.IDP_CONFIG['host'] + settings.IDP_CONFIG['authenticate_url'], json=payload)
        data = response.json()
        return data.get('accessToken')
    except Exception as e:
        raise e   
    
class CreateEmployerAPIView(AppAPIView):
    """
    API to Create Employer from CMS.
    """

    class _Serializer(AppWriteOnlyModelSerializer):

        class Meta(AppWriteOnlyModelSerializer.Meta):
            fields = ["first_name", "middle_name", "last_name", "alternative_email"]
            model = User

    serializer_class = _Serializer

    def post(self, request, *args, **kwargs):
        """Use IDP to handle the same."""

        serializer = self.get_valid_serializer()
        
        # idp_response = valid_idp_response(
        #     url_path="/api/access/v1/simple-signup/",
        #     request=self.get_request(),
        #     method="POST",
        # )
        # role = UserRole.objects.get(identity__icontains="Employer")
        # serializer.save(idp_user_id=idp_response["user"]["uuid"],user_role=role)
        # idp_response["user"] = {**idp_response["user"], **serializer.data}

        # print(idp_response["user"]["id"])

        class _EmployerSerializer(AppModelSerializer):
            class Meta(AppWriteOnlyModelSerializer.Meta):
                model = EmployerDetail
                fields = [
                    "identity", 
                    "description",
                    "logo_image", 
                    "contact_email_id", 
                    "alternative_conatct_email_id", 
                    "contact_number",
                    "locality_street_address",
                    "city",
                    "state",
                    "country",
                    "pincode",
                    "representative"
                ]

        serializer_class = _EmployerSerializer  # Assign the serializer class

        employer_serializer = serializer_class(data=self.request.data)
        employer_serializer.is_valid(raise_exception=True)
        headers = get_admin_headers()
        email = self.request.data["email"]
        password = self.request.data["password"]
        name = self.request.data["first_name"]
        payload = {
            "userId": 0,
            "tenantId": settings.IDP_TENANT_ID,
            "tenantDisplayName": name,
            "tenantName": settings.IDP_TENANT_NAME,
            "role": "TenantUser",
            "email": email,
            "name": name,
            "surname": name,
            "configJson": "string",
            "password": password,
            "businessUnitName": "test",
            "userIdNumber": "string",
            "userGrade": "string",
            "isOnsiteUser": "yes",
            "managerName": "test",
            "managerEmail": "test@gmail.com",
            "managerId": 0,
            "organizationUnitId": 0
        }

        idp_response = requests.post(settings.IDP_CONFIG['host'] + settings.IDP_CONFIG['user_create_url'], json=payload, headers=headers)
        data = idp_response.json()
        user_id = User.objects.filter(idp_user_id=data.get('userId')).first()
        # full_name = data.get('name') + data.get('surname')
        if user_id is None:
        # full_name = data.get('name') + data.get('surname')
            role = UserRole.objects.get(identity__icontains="Employer")

            serializer.save(idp_user_id=data.get('userId'), password=data.get('password'), idp_email=data.get('email'), user_name=data.get('email'), first_name=data.get('name'), last_name=data.get('surname'), full_name=name, user_role=role)
            user = User.objects.get(idp_user_id=data.get('userId'))
            employer_serializer.save(representative=user)
            # return self.send_response()
        else:
            return self.send_error_response(data={'detail': "User Already exists"})

        html_content=f'Welcome, you have successfully signed up <br> Your signed up details are: <br> Full Name: {name} <br> Email Id: {email} <br> Password: {password}'
        success, message = send_welcome_email(email, 'Welcome', html_content)

        if success:
            return self.send_response(data={'detail': message})
        else:
            return self.send_error_response(data={'detail': message})
    
class UpdateEmployerAPIView(AppAPIView):
    """This class provides edit the user Details from Admin"""

    class _EmployerSerializer(AppWriteOnlyModelSerializer):

        class Meta(AppWriteOnlyModelSerializer.Meta):
            model = EmployerDetail
            fields = [
                "identity", 
                "description",
                "logo_image", 
                "contact_email_id", 
                "alternative_conatct_email_id", 
                "contact_number",
                "locality_street_address",
                "country",
                "state",
                "city",
                "pincode",
            ]

        def update(self, instance, validated_data):
            instance = super().update(validated_data=validated_data, instance=instance)
            return instance

    serializer_class = _EmployerSerializer


    def post(self, *args, **kwargs):
        employer = EmployerDetail.objects.get(id=kwargs['id'])
        serializer = self.get_valid_serializer(instance=employer)
        serializer.save()
        return self.send_response()

class CreateInterviewPanelAPIView(AppAPIView):
    """
    API to Create Employer from CMS.
    """

    class _Serializer(AppWriteOnlyModelSerializer):

        class Meta(AppWriteOnlyModelSerializer.Meta):
            fields = ["first_name", "middle_name", "last_name", "alternative_email", "job_role", "experience_years", "industry_type", "address", "country", "state", "city","pincode"]
            model = User

    serializer_class = _Serializer

    def post(self, request, *args, **kwargs):
        """Use IDP to handle the same."""

        serializer = self.get_valid_serializer()
        # idp_response = valid_idp_response(
        #     url_path="/api/access/v1/simple-signup/",
        #     request=self.get_request(),
        #     method="POST",
        # )
        headers = get_admin_headers()
        email = self.request.data["email"]
        password = self.request.data["password"]
        name = self.request.data["first_name"]
        payload = {
            "userId": 0,
            "tenantId": settings.IDP_TENANT_ID,
            "tenantDisplayName": name,
            "tenantName": settings.IDP_TENANT_NAME,
            "role": "TenantUser",
            "email": email,
            "name": name,
            "surname": name,
            "configJson": "string",
            "password": password,
            "businessUnitName": "test",
            "userIdNumber": "string",
            "userGrade": "string",
            "isOnsiteUser": "yes",
            "managerName": "test",
            "managerEmail": "test@gmail.com",
            "managerId": 0,
            "organizationUnitId": 0
        }

        idp_response = requests.post(settings.IDP_CONFIG['host'] + settings.IDP_CONFIG['user_create_url'], json=payload, headers=headers)
        data = idp_response.json()
        user_id = User.objects.filter(idp_user_id=data.get('userId')).first()
        # full_name = data.get('name') + data.get('surname')
        if user_id is None:
        # full_name = data.get('name') + data.get('surname')
            corporate = EmployerDetail.objects.get(representative=self.get_user())
            role = UserRole.objects.get(identity__icontains="Interview Panel Member")
            serializer.save(idp_user_id=data.get('userId'), password=data.get('password'), idp_email=data.get('email'), user_name=data.get('email'), first_name=data.get('name'), last_name=data.get('surname'), full_name=name,corporate=corporate, user_role=role)
            return self.send_response()
        else:
            return self.send_error_response(data={'detail': "User Already exists"})

        # serializer.save(idp_user_id=idp_response["user"]["uuid"], corporate=corporate,user_role=role) # set user role here
        # idp_response["user"] = {**idp_response["user"], **serializer.data}

        # return self.send_response()
    
class UpdateInterviewPanelAPIView(AppAPIView):
    """This class provides edit the user Details from Admin"""

    class _Serializer(AppWriteOnlyModelSerializer):

        class Meta(AppWriteOnlyModelSerializer.Meta):
            model = User
            fields = ["first_name", "middle_name", "last_name", "alternative_email", "job_role", "experience_years", "industry_type", "address", "country", "state", "city", "pincode"]

        def update(self, instance, validated_data):
            instance = super().update(validated_data=validated_data, instance=instance)
            return instance

    serializer_class = _Serializer

    def post(self, *args, **kwargs):
        interview_panel = User.objects.get(id=kwargs['id'])
        serializer = self.get_valid_serializer(instance=interview_panel)
        serializer.save()
        return self.send_response(serializer.data)
    
class MetaInterviewScheduleAPIView(AppAPIView):

    def get(self, request, *args, **kwargs):
        applied_candidate_ids=[]
        job_round_ids=[]
        job = Job.objects.filter(created_by=self.get_user())
        if job:
            applied_candidate_ids = JobAppliedList.objects.filter(job__in=job).values_list('created_by_id', flat=True)
            job_round_ids = Job.objects.filter(id__in=job).values_list('job_round_details', flat=True)

        # Retrieve the User objects and serialize them
        candidate = User.objects.filter(id__in=applied_candidate_ids).distinct()
        candidate_serializer = read_serializer(
            User,
            meta_fields=['id', 'uuid', 'first_name', "middle_name", "last_name"]
        )
        serialized_candidates = candidate_serializer(candidate, many=True).data

        # Retrieve the Job objects and serialize them
        jobs = JobAppliedList.objects.filter(created_by_id__in=applied_candidate_ids, job__in=job).exclude(status="pending_assessment")
        jobs_serializer = read_serializer(
            JobAppliedList,
            meta_fields=['id', 'uuid', 'created_by'],
            init_fields_config={
                "job_detail": read_serializer(
                    meta_model=Job, meta_fields=['id', 'identity', 'job_role'],
                    init_fields_config={
                        "round_details": read_serializer(
                            meta_model=JobRoundDetails, meta_fields=['id', 'title']
                        )(source="job_round_details", many=True),
                    }
                )(source="job"),
            }
        )
        serialized_jobs = jobs_serializer(jobs, many=True).data

        # Retrieve the Job Round Detail objects and serialize them
        job_round = JobRoundDetails.objects.filter(id__in=job_round_ids)
        job_round_serializer = read_serializer(
            JobRoundDetails,
            meta_fields=['id', 'uuid', 'title', 'description', 'assessment_id', 'hackathon_id'],
        )
        serialized_job_round = job_round_serializer(job_round, many=True).data

        # Retrieve the Job Feedback Template objects and serialize them
        feedback_template = JobFeedbackTemplate.objects.filter(created_by=self.get_user())
        feedback_template_serializer = read_serializer(
            JobFeedbackTemplate,
            meta_fields=['id', 'uuid', 'identity'],
        )
        serialized_feedback_template = feedback_template_serializer(feedback_template, many=True).data

        # Retrieve the Interview Panel Member objects and serialize them
        interview_panel = User.objects.filter(user_role__identity="Interview Panel Member", created_by=self.get_user())
        interview_panel_serializer = read_serializer(
            User,
            meta_fields=['id', 'uuid', 'first_name', "middle_name", "last_name"],
        )
        serialized_interview_panel = interview_panel_serializer(interview_panel, many=True).data

        data = {
            "applicant": serialized_candidates,
            "job": serialized_jobs,
            "job_round": serialized_job_round,
            "interview_feedback_template": serialized_feedback_template,
            "interview_panel": serialized_interview_panel
        }
        return self.send_response(data=data)

class EmployerDashboardAPIView(AppAPIView):
    """Sends out data for the website home/landing page."""

    class _ApplicantListSerializer(AppReadOnlyModelSerializer):
        created_by = read_serializer(User, meta_fields=["id","uuid","first_name"])(User.objects.all())
        job = read_serializer(Job, meta_fields=["id","uuid","identity"])(Job.objects.all())
        class Meta(AppReadOnlyModelSerializer.Meta):
            fields = ["id", "created_by","job", "status"]
            model = JobAppliedList
        
    class _WebinarSerializer(AppReadOnlyModelSerializer):
        image = get_app_read_only_serializer(WebinarImage, meta_fields="__all__")()

        class Meta(AppReadOnlyModelSerializer.Meta):
            model = Webinar
            fields = ["id","uuid", "identity", "image", "description", "participant_limit", "start_date"]

    class _HackathonSerializer(AppReadOnlyModelSerializer):
        image = HackathonImageSerializer()

        class Meta(AppReadOnlyModelSerializer.Meta):
            model = hackathon_models.Hackathon
            fields = ['id','uuid','identity','image','description','no_of_participants_limit','start_date']
        
    def get(self, *args, **kwargs):
        """Handle on get method."""

        user = self.get_user()

        today = date.today()

        jobs_count =  Job.objects.filter(created_by=user).count()
        applied_positions = JobAppliedList.objects.filter(job__created_by=user,status="applied_for_job").count()
        shortlisted_positions = JobAppliedList.objects.filter(job__created_by=user,status="shortlist").count()
        rejected_positions = JobAppliedList.objects.filter(job__created_by=user,status="rejected").count()

        # Job Top List
        jobs_list = Job.objects.values('job_role').annotate(count=Count('job_role')).order_by('-count')[:10]
        
        applicant_list = self._ApplicantListSerializer(JobAppliedList.objects.filter(job__created_by=user).order_by("created")[:10], many=True).data

        jobs={
            "total_jobs": jobs_count,
            "applied_positions": applied_positions,
            "shortlisted_positions": shortlisted_positions,
            "rejected_positions": rejected_positions
        }
        upcoming_events = {
            "webinars":self._WebinarSerializer(Webinar.objects.filter(start_date__gte=today), many=True).data,
            "hackathons":self._HackathonSerializer(hackathon_models.Hackathon.objects.filter(start_date__gte=today), many=True).data
        }
        return self.send_response(
            data={
                "jobs": jobs,
                "trending_jobs": jobs_list,
                "applicant_list": applicant_list,
                "upcoming_events":upcoming_events
            }
        )
