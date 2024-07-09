from apps.common.views.api import AppAPIView
import requests
from config import settings
import json

def get_headers(user):
    data_auth_new_token = get_auth_response_new(user)
    header = {
        'Content-Type' : 'application/json',
        'Authorization': data_auth_new_token["accessToken"],
        'tenant': data_auth_new_token["localTenantId"],
        'role': data_auth_new_token["role"],
        'authType': data_auth_new_token["auth_type"],
    }
    return header

def get_auth_response_new(user):
    data_token = get_token(user)
    try:
        payload = {
            "token": data_token,
            "tenant_id": settings.MML_TENANT_ID
        }
        response = requests.post(settings.IDP_CONFIG['mml_host'] + settings.IDP_CONFIG['mml_validate_token_url'], json=payload, verify=False)
        data = response.json()
        response_data = {
            "accessToken" : data.get('success').get('accessToken'),
            "auth_type" : data.get('success').get('auth_type'),
            "localTenantId" : data.get('success').get('localTenantId'),
            "role" : data.get('success').get('role'),
        }
        return response_data
    except Exception as e:
        raise e

def get_token(user):
    try:
        payload = {
            "userNameOrEmailAddress": user.idp_email,
            "password": user.password,
            "rememberClient": True,
            "tenancyName": settings.IDP_TENANT_NAME
        }
        response = requests.post(settings.IDP_CONFIG['host'] + settings.IDP_CONFIG['authenticate_url'], json=payload)
        data = response.json()
        return data.get('accessToken')
    except Exception as e:
        raise e
    
class GetVmProvisioningRequestAPIView(AppAPIView):
    def post(self, *args, **kwargs):
       
        """Use IDP to handle the same."""
        user = self.get_user()
        headers = get_headers(user)
        sku = self.request.data["sku"]
        vm_name = self.request.data["vm_name"]
        payload = {
                    "sku": sku,
                    "vm_name": vm_name,
                    "status": 5
                  }
        #idp_user_url
        mml_response = requests.post("https://laas.makemylabs.in/v1/requests",json=payload,verify=False, headers=headers)
        data = mml_response.json()
        # print(data)
        provision_request_id = data.get("id")
        # print(provision_request_id)
        # breakpoint()
        mml_provision_details_response = []
        if provision_request_id:
            mml_provision_details_response = requests.get(settings.IDP_CONFIG['mml_host'] + f"/v1/vm?provision_request={provision_request_id}", verify=False, headers=headers)
            return self.send_response(data=mml_provision_details_response.json())
        else:
            return self.send_error_response(data=data)

class GetVmStartAPIView(AppAPIView):
    def get(self, *args, **kwargs):
        vm_id = kwargs.get("id")
        user = self.get_user()
        headers = get_headers(user)
        # vm_response = requests.get("https://laas.makemylabs.in/v1/vm/09f2a26c-77bc-43d2-bbb4-5d470e43f70e", verify=False, headers=headers)
        vm_response = requests.get(settings.IDP_CONFIG['mml_host'] + settings.IDP_CONFIG['mml_status_url'] + f"/{vm_id}", verify=False, headers=headers)
        # print(vm_response)
        # breakpoint()
        if vm_response:
            # print("hgvdcgh")
            # breakpoint()
            data = vm_response.json()
            if data:
                vm_status_id = data.get('id')
                # vm_name = data.get('vm_name')
                if vm_status_id:
                    payload = {
                        "action":1, 
                        # "soft":False, 
                        # "vm_name":vm_name
                    }
                    vm_start_response = requests.patch(settings.IDP_CONFIG['mml_host'] + settings.IDP_CONFIG['mml_power_start_url'] + f"/{vm_status_id}", json=payload, verify=False,headers=headers)
                    # print(vm_start_response)
                    # breakpoint()
                    vm_start_response = vm_start_response.json()
                    return self.send_response(vm_start_response)
                else:
                    return self.send_error_response({'message': "1"})
            else:
                return self.send_error_response({'message': "2"})
        else:
            return self.send_error_response({'message': "3"})