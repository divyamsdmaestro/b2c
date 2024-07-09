from apps.access.models import User
from apps.common.views.api import AppAPIView
import requests
from apps.common.views.api.base import NonAuthenticatedAPIMixin
from apps.learning.models.course import Course
from apps.learning.models.linkages import JobEligibleSkill
from apps.web_portal.models import UserAssessmentResult, JobAssessmentResult
from apps.web_portal.models.assessment import JobEligibleSkillAssessment
from apps.web_portal.serializers.assessment import UserAssessmentResultSerializer
from config import settings
from apps.access.authentication import get_user_headers
from apps.jobs.models import Job, JobAppliedList

# def get_headers(user):
#     data_token = get_token(user)
#     header = {
#         'Content-Type' : 'application/json',
#         'Authorization': f'Bearer {data_token}'
#     }
#     return header

# def get_token(user):
#     try:
#         payload = {
#             "userNameOrEmailAddress": user.idp_email,
#             "password": user.password,
#             "rememberClient": True,
#             "tenancyName": settings.IDP_TENANT_NAME
#         }
       
#         response = requests.post(settings.IDP_CONFIG['host'] + settings.IDP_CONFIG['authenticate_url'], json=payload)
#         data = response.json()
#         return data.get('accessToken')
#     except Exception as e:
#         raise e
    
class GetAssessmentURLAsync(AppAPIView):


    def post(self, request, *args, **kwargs):
       
        """Use IDP to handle the same."""
        user = self.get_user()
        headers = get_user_headers(user)
        email = self.request.data["idp_email"]
        first_name = self.request.data["first_name"]
        last_name = self.request.data["last_name"]
        assessment_id = self.request.data["assessment_id"]
        payload = {
                    "tenantId": 119,
                    "assessmentIdNumber": assessment_id,
                    "userEmailAddress": email,
                    "firstName": first_name,
                    "lastName": last_name,
                    "resultShareMode": [],
                    "scheduleConfig": {
                        "totalAttempts": 2,
                        "passPercentage": 50,
                        "duration": 60,
                        "externalScheduleConfigArgs": None,
                        "assessmentConfig": {
                            "enableShuffling": True,
                            "resultType": 2,
                            "redirectURL": ""
                        }
                    }
                }
        #idp_user_url
        idp_response = requests.post(settings.IDP_CONFIG['yaksha_host'] + settings.IDP_CONFIG['yaksha_assessment_url'], json=payload, headers=headers)
        # print(idp_response.status_code)
        # breakpoint()
        data = idp_response.json()
        # print(idp_response.json())
        # breakpoint()
        return self.send_response(data=data)
    

class GetUserAssessmentResult(AppAPIView):

    def post(self, request, *args, **kwargs):
       
        user = self.get_user()
        email = user.idp_email
        headers = get_user_headers(user)
        assessment_id = self.request.data["assessment_id"]
        course_uuid = self.request.data["course"]
        course = Course.objects.get(uuid=course_uuid)

        idp_response = requests.get(settings.IDP_CONFIG['yaksha_host'] + settings.IDP_CONFIG['yaksha_user_assessment_result_url'] + f"?tenantId={settings.IDP_TENANT_ID}&userEmailAddress={email}&AssessmentIdNumber={assessment_id}", headers=headers)
        data = idp_response.json()
        result_data = data.get("result", {})
        assessment_name = result_data.get("assessmentName", "")
        actual_start = result_data.get("schedules", [])[0].get("attempts", [])[0].get("actualStart", "")
        status = result_data.get("schedules", [])[0].get("attempts", [])[0].get("status", "")
        score_percentage = result_data.get("schedules", [])[0].get("attempts", [])[0].get("scorePercentage", 0.0)
        email_address = result_data.get("userEmailAddress", "")

        user_details = User.objects.get(idp_email = email_address)
        unique_criteria = {
            'user': user_details,
            'assessment_id': assessment_id,
        }

        defaults = {
            'result': data,
            'user': user_details,
            'assessment_name': assessment_name,
            'assessment_id': assessment_id,
            'assessment_date': actual_start,
            'result_status': status,
            'score_percentage': score_percentage,
            'course': course,
        }
        user_assessment_result, created = UserAssessmentResult.objects.update_or_create(
            **unique_criteria, defaults = defaults   
        )
        return self.send_response()

class GetAssessmentResult(AppAPIView):
    
    def get(self, request, assessment_id, *args, **kwargs):
        user = self.get_user()
        user_assessment_results = UserAssessmentResult.objects.filter(
            assessment_id = assessment_id, user = user
        )
        serializer = UserAssessmentResultSerializer(user_assessment_results, many=True)

        result_data = serializer.data
        return self.send_response(data={'result': result_data})
    
class GetJobAssessmentResult(AppAPIView):

    def post(self, request, *args, **kwargs):
       
        user = self.get_user()
        email = user.idp_email
        headers = get_user_headers(user)
        assessment_id = self.request.data["assessment_id"]
        job_uuid = self.request.data["job"]
        job = Job.objects.get(uuid=job_uuid)

        idp_response = requests.get(settings.IDP_CONFIG['yaksha_host'] + settings.IDP_CONFIG['yaksha_user_assessment_result_url'] + f"?tenantId={settings.IDP_TENANT_ID}&userEmailAddress={email}&AssessmentIdNumber={assessment_id}", headers=headers)
        try:
            data = idp_response.json()
            result_data = data.get("result", {})
            assessment_name = result_data.get("assessmentName", "")
            actual_start = result_data.get("schedules", [])[0].get("attempts", [])[0].get("actualStart", "")
            status = result_data.get("schedules", [])[0].get("attempts", [])[0].get("status", "")
            score_percentage = result_data.get("schedules", [])[0].get("attempts", [])[0].get("scorePercentage", 0.0)
            email_address = result_data.get("userEmailAddress", "")

            user_details = User.objects.get(idp_email = email_address)
            unique_criteria = {
                'user': user_details,
                'assessment_id': assessment_id,
            }

            defaults = {
                'result': data,
                'user': user_details,
                'assessment_name': assessment_name,
                'assessment_id': assessment_id,
                'assessment_date': actual_start,
                'result_status': status,
                'score_percentage': score_percentage,
                'job': job,
            }
            user_assessment_result, created = JobAssessmentResult.objects.update_or_create(
                **unique_criteria, defaults = defaults
            )

            if user_assessment_result:
                if user_assessment_result.result_status == "Passed":
                    applied_job = JobAppliedList.objects.filter(job=job, created_by=user).first()
                    applied_job.status = "applied_for_job"
                    applied_job.save()
                    return self.send_response(data={"result_status":status})
                else:
                    first_name = user.first_name
                    last_name = user.last_name
                    payload = {
                        "tenantId": 119,
                        "assessmentIdNumber": assessment_id,
                        "userEmailAddress": email,
                        "firstName": first_name,
                        "lastName": last_name,
                        "resultShareMode": [],
                        "scheduleConfig": {
                            "totalAttempts": 2,
                            "passPercentage": 50,
                            "duration": 60,
                            "externalScheduleConfigArgs": None,
                            "assessmentConfig": {
                                "enableShuffling": True,
                                "resultType": 2,
                                "redirectURL": ""
                            }
                        }
                    }
                    #idp_user_url
                    idp_response = requests.post(settings.IDP_CONFIG['yaksha_host'] + settings.IDP_CONFIG['yaksha_assessment_url'], json=payload, headers=headers)
                    data = idp_response.json()
                    return self.send_response(data=data)
        except:
            first_name = user.first_name
            last_name = user.last_name
            payload = {
                "tenantId": 119,
                "assessmentIdNumber": assessment_id,
                "userEmailAddress": email,
                "firstName": first_name,
                "lastName": last_name,
                "resultShareMode": [],
                "scheduleConfig": {
                    "totalAttempts": 2,
                    "passPercentage": 50,
                    "duration": 60,
                    "externalScheduleConfigArgs": None,
                    "assessmentConfig": {
                        "enableShuffling": True,
                        "resultType": 2,
                        "redirectURL": ""
                    }
                }
            }
            #idp_user_url
            idp_response = requests.post(settings.IDP_CONFIG['yaksha_host'] + settings.IDP_CONFIG['yaksha_assessment_url'], json=payload, headers=headers)
            data = idp_response.json()
            return self.send_response(data=data)


class GetJobEligibleSkillAssessmentResult(AppAPIView):
    def post(self, request, *args, **kwargs):
       
        user = self.get_user()
        email = user.idp_email
        headers = get_user_headers(user)
        assessment_id = self.request.data["assessment_id"]
        job_eligible_skill_uuid = self.request.data["job_eligible_skill"]
        job_eligible_skill = JobEligibleSkill.objects.get(uuid=job_eligible_skill_uuid)

        idp_response = requests.get(settings.IDP_CONFIG['yaksha_host'] + settings.IDP_CONFIG['yaksha_user_assessment_result_url'] + f"?tenantId={settings.IDP_TENANT_ID}&userEmailAddress={email}&AssessmentIdNumber={assessment_id}", headers=headers)
        try:
            data = idp_response.json()
            result_data = data.get("result", {})
            assessment_name = result_data.get("assessmentName", "")
            actual_start = result_data.get("schedules", [])[0].get("attempts", [])[0].get("actualStart", "")
            status = result_data.get("schedules", [])[0].get("attempts", [])[0].get("status", "")
            score_percentage = result_data.get("schedules", [])[0].get("attempts", [])[0].get("scorePercentage", 0.0)
            email_address = result_data.get("userEmailAddress", "")

            user_details = User.objects.get(idp_email = email_address)
            unique_criteria = {
                'user': user_details,
                'assessment_id': assessment_id,
            }

            defaults = {
                'result': data,
                'user': user_details,
                'assessment_name': assessment_name,
                'assessment_id': assessment_id,
                'assessment_date': actual_start,
                'result_status': status,
                'score_percentage': score_percentage,
                'job_eligible_skill': job_eligible_skill,
            }
            user_assessment_result, created = JobEligibleSkillAssessment.objects.update_or_create(
                **unique_criteria, defaults = defaults
            )

            if user_assessment_result:
                if user_assessment_result.result_status == "Passed":
                    return self.send_response(data={"result_status":status})
                else:
                    first_name = user.first_name
                    last_name = user.last_name
                    payload = {
                        "tenantId": 119,
                        "assessmentIdNumber": assessment_id,
                        "userEmailAddress": email,
                        "firstName": first_name,
                        "lastName": last_name,
                        "resultShareMode": [],
                        "scheduleConfig": {
                            "totalAttempts": 2,
                            "passPercentage": 50,
                            "duration": 60,
                            "externalScheduleConfigArgs": None,
                            "assessmentConfig": {
                                "enableShuffling": True,
                                "resultType": 2,
                                "redirectURL": ""
                            }
                        }
                    }
                    #idp_user_url
                    idp_response = requests.post(settings.IDP_CONFIG['yaksha_host'] + settings.IDP_CONFIG['yaksha_assessment_url'], json=payload, headers=headers)
                    data = idp_response.json()
                    return self.send_response(data=data)
        except:
            first_name = user.first_name
            last_name = user.last_name
            payload = {
                "tenantId": 119,
                "assessmentIdNumber": assessment_id,
                "userEmailAddress": email,
                "firstName": first_name,
                "lastName": last_name,
                "resultShareMode": [],
                "scheduleConfig": {
                    "totalAttempts": 2,
                    "passPercentage": 50,
                    "duration": 60,
                    "externalScheduleConfigArgs": None,
                    "assessmentConfig": {
                        "enableShuffling": True,
                        "resultType": 2,
                        "redirectURL": ""
                    }
                }
            }
            #idp_user_url
            idp_response = requests.post(settings.IDP_CONFIG['yaksha_host'] + settings.IDP_CONFIG['yaksha_assessment_url'], json=payload, headers=headers)
            data = idp_response.json()
            return self.send_response(data=data)