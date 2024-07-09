from authlib.integrations.requests_client import OAuth2Session
from django.shortcuts import redirect
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from config import settings
import requests, hashlib
from apps.access.models import User, UserRole
from rest_framework.authtoken.models import Token as AuthToken
from rest_framework.response import Response
from django.http import HttpResponse
from django.contrib.auth.hashers import make_password
from apps.ecash.reward_points import trigger_reward_points
from apps.common.helpers import send_welcome_email

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

def idp_function(user_info, provider):
    password = hashlib.md5(user_info['email'].encode()).hexdigest()
    headers = get_admin_headers()
    email = user_info["email"]
    name = user_info["name"]
    first_name = user_info["given_name"]
    if "family_name" in user_info:
        last_name = user_info["family_name"]
    else:
        last_name = "null"
    payload = {
        "userId": 0,
        "tenantId": settings.IDP_TENANT_ID,
        "tenantDisplayName": name,
        "tenantName": settings.IDP_TENANT_NAME,
        "role": "TenantUser",
        "email": email,
        "name": first_name,
        "surname": last_name,
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
    if user_id is None and data.get('password') is not None:
        role = UserRole.objects.get(identity__icontains="Learner")
        User.objects.create(idp_user_id=data.get('userId'), password=data.get('password'), idp_email=data.get('email'), user_name=data.get('email'), first_name=data.get('name'), last_name=data.get('surname'), user_role=role, full_name=name, socail_oauth=True, social_provider=provider)
        get_user = User.objects.get(idp_email=data.get('email'))
        trigger_reward_points(get_user, action="New User")
        html_content=f'Welcome, you have successfully signed up <br> Your signed up details are: <br> Full Name: {name} <br> Email Id: {email} <br> Password: {password}'
        success, message = send_welcome_email(email, 'Welcome', html_content)

    elif user_id is None and data.get('password') is None:
        return {"error": "User already exists"}

    user_id = User.objects.filter(idp_user_id=data.get('userId')).first()
    payload = {
        "userNameOrEmailAddress": user_id.user_name,
        "password": user_id.password,
        "rememberClient": True,
        "tenancyName": settings.IDP_TENANT_NAME,
    }
    idp_response = requests.post(settings.IDP_CONFIG['host'] + settings.IDP_CONFIG['authenticate_url'], json=payload)
    data = idp_response.json()

    if user_id.onboarding_area_of_interests.exists():
        onboarding=True
    else:
        onboarding=False

    token ,_= AuthToken.objects.get_or_create(user=user_id)
    response_data = {
        'full_name': user_id.full_name,
        'first_name': user_id.first_name,
        'last_name': user_id.last_name,
        'uuid': user_id.uuid,
        'role': user_id.user_role.identity,
        'email': user_id.idp_email,
        'token': token.key,
        'idp_token': data.get("accessToken"),
        'encryptedAccessToken': data.get("encryptedAccessToken"),
        'expireInSeconds': data.get("expireInSeconds"),
        'userId': data.get("userId"),
        'onboarding': onboarding
    }
    return response_data

def get_user_data(provider, access_token):
    oauth_settings = settings.AUTHLIB_OAUTH_CLIENTS.get(provider, {})

    response = requests.get(
        oauth_settings.get('userinfo_url'),
        headers={'Authorization': f'Bearer {access_token}'}
    )

    if response.status_code == 200:
        return response.json()
    else:
        return None

# Google Login
@api_view(['GET'])
@permission_classes([AllowAny])
def oauth_login(request, provider):

    oauth_settings = settings.AUTHLIB_OAUTH_CLIENTS.get(provider, {})

    oauth = OAuth2Session(
        client_id=oauth_settings.get('client_id'),
        redirect_uri=oauth_settings.get('redirect_uri')
    )

    authorization_url, _ = oauth.create_authorization_url(
        oauth_settings.get('authorize_url'),
        scope=oauth_settings.get('client_kwargs', {}).get('scope', '')
    )

    return Response({"social login":authorization_url})

@api_view(['GET'])
@permission_classes([AllowAny])
def oauth_callback(request, provider):
    code = request.GET.get('code')
    if not code:
        return HttpResponse(f'Error: Authorization code not received for {provider.capitalize()}')

    oauth_settings = settings.AUTHLIB_OAUTH_CLIENTS.get(provider, {})

    oauth = OAuth2Session(
        client_id=oauth_settings.get('client_id'),
        redirect_uri=oauth_settings.get('redirect_uri')
    )

    token = oauth.fetch_access_token(
        oauth_settings.get('token_url'),
        code=code,
        client_secret=oauth_settings.get('client_secret')
    )

    user_data = get_user_data(provider, token['access_token'])
    response_data = None
    if user_data:
        response_data=idp_function(user_data, provider)
    return Response(response_data, status=200)