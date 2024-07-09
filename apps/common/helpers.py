import datetime, inflect
import json
import random
import secrets
import string
import time
import typing
import requests

from dateutil import tz
from django.conf import settings
from requests import request
from django.core import validators
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content
from django.template.loader import render_to_string
import sendgrid
import os
from icalendar import Calendar, Event
from sendgrid.helpers.mail.attachment import Attachment
from sendgrid.helpers.mail.file_content import FileContent
from sendgrid.helpers.mail.file_name import FileName
from sendgrid.helpers.mail.disposition import Disposition
from sendgrid.helpers.mail.content_id import ContentId
from sendgrid.helpers.mail.file_type import FileType
import pytz

def create_log(data: typing.Any, category: str):
    """
    A centralized function to create the app logs. Just in case some
    extra pre-processing are to be added in the future.
    """

    # assert data and category, "The passed parameters cannot be None while creating log."
    # apps.get_model("common.Log").objects.create(data=data, category=category)

    if settings.DEBUG:
        print("Log: ", data, category)  # noqa


def get_display_name_for_slug(slug: str):
    """
    For a given string slug this generates the display name for the given slug.
    This generated display name will be displayed on the front end.
    """

    try:
        return slug.replace("_", " ").title()
    except:  # noqa
        return slug


def flatten(value):
    return [item for sublist in value for item in sublist]


def random_n_digits(n):
    """Returns a random number with `n` length."""

    range_start = 10 ** (n - 1)
    range_end = (10**n) - 1
    return str(random.randint(range_start, range_end))


def random_n_token(n=10):
    """Generate a random string with numbers and characters with `n` length."""

    allowed_characters = (
        string.ascii_letters + string.digits
    )  # contains char and digits
    return "".join(secrets.choice(allowed_characters) for _ in range(n))


def make_http_request(
    url: str, method="GET", headers={}, data={}, params={}, auth=None, **kwargs  # noqa
):
    """
    Function that makes a third party http request to any given url based on the passed params.
    This is similar to triggerSimpleAjax/Axios function. This is defined here just to make things DRY.
    """

    response = request(
        method=method,
        url=url,
        headers=headers,
        data=stringify(data),
        params=params,
        auth=auth,
        **kwargs,
    )

    try:
        response_data = response.json()
    except json.decoder.JSONDecodeError:
        response_data = None

    _output = {
        "data": response_data,
        "status_code": response.status_code,
        "reason": None if response_data else response.text,  # fallback for the data
    }

    # logging action
    log = {
        "request_data": data,
        "params": params,
        "headers": headers,
        "method": method,
        "response_data": _output,
    }
    # log_outbound_message(stringify(log), url, "make_http_request")

    if settings.DEBUG:
        print(log)  # noqa

    return _output


def stringify(data, fallback=None):  # noqa
    """Stringify a given data."""

    try:
        return json.dumps(data)
    except:  # noqa
        return fallback


def convert_utc_to_local_timezone(
    input_datetime: datetime.date | datetime.datetime,
    inbound_request,  # noqa
):
    """
    Given a UTC datetime or date object, this will convert it to the
    user's local timezone based on the request.
    """

    from_zone = tz.gettz(settings.TIME_ZONE)

    # TODO: from `inbound_request`
    to_zone = tz.gettz("Asia/Kolkata")

    input_datetime = input_datetime.replace(tzinfo=from_zone)

    return input_datetime.astimezone(to_zone)


def is_any_or_list1_in_list2(list1: list, list2: list):
    """Given two lists, this will check if any element of list1 is in list2."""

    return any(v in list2 for v in list1)

def is_list2_in_list1(list1, list2):
    """Given two lsits, this will check if list1 contains all the items of list2"""
    
    return all(item in list1 for item in list2)

def get_first_of(*args):
    """For _ in args, returns the first value whose value is valid."""

    for _ in args:
        if _:
            return _

    return None


def get_file_field_url(instance, field="image"):
    """Given any instance and a linked File or Image field, returns the url."""

    if getattr(instance, field, None):
        return getattr(instance, field).file.url

    return None


def pause_thread(seconds):
    """Pause the tread for the given seconds."""

    time.sleep(seconds)

def validate_rating(value):
    if value > 0 and value > 5:
        raise validators.ValidationError("Rating must be less than or equal to 5 and it should be a positive value.")

def validate_pincode(value):
    if value > 999999 or value <= 100000: #check if it has 6 digits or not
        raise validators.ValidationError("Pincode must have only 6 digits.")
    
def validate_image(image):
    if image.size > 1024 * 1024:  # 1 MB
        raise validators.ValidationError("File size should be less than 1 MB.")
    
def validate_resume(resume):
    if resume.size > 1024 * 1024 * 5:  # 5 MB
        raise validators.ValidationError("File size should be less than 5 MB.")
    
class EmailNotification:

    def __init__(
        self,
        email_to: str | list,
        template_code: str = None,
        **kwargs,
    ):

        assert template_code

        self.input = kwargs.get('kwargs')
        self.email_to = email_to
        self.template_code = template_code
        self.send_email()

    def get_subject(self):
        if self.template_code == "student_signup":
            subject = f"Welcome to Techademy via {self.input.get('institute_name')}"
        
        elif self.template_code == "support_to_admin":
            subject = "Leaner need your support"
        
        elif self.template_code == "interview_scheduled_learner":
            subject = "An Interview Scheduled"

        elif self.template_code == "interview_scheduled_interviewer":
            subject = "A new interview has been scheduled"

        elif self.template_code == "offer_letter_initiate":
            subject = "An offer letter has been initiated"
        
        elif self.template_code == "webinar_registration":
            subject = "Webinar registration"

        elif self.template_code == "webinar_reminder_email":
            subject = "Friendly Reminder: Join Our Webinar!"

        else:
            subject = ""

        return subject

    def get_body(self):
        template_name = self.template_code
        if not template_name:
            raise ValueError(f"Invalid template code: {self.template_code}")

        body = render_to_string(f'email/{template_name}.html', self.input)
        return body

    def send_email(self):
        message = Mail(
            from_email='welcome@techademy.com',
            to_emails=self.email_to,
            subject=self.get_subject(),
            html_content=self.get_body()
        )
        try:
            sg = SendGridAPIClient(api_key=settings.ANYMAIL["SENDGRID_API_KEY"])                
            response = sg.send(message)
            print(response)
            if response.status_code == 202:
                return True, 'Email sent.'
            else:
                return False, 'Failed to send email.'
        except Exception as e:
            return False, f'An error occurred: {str(e)}'
    
def send_welcome_email(email, subject, html_content):
    message = Mail(
        from_email='welcome@techademy.com',
        to_emails=email,
        subject=subject,
        html_content=html_content
    )
    
    try:
        sg = SendGridAPIClient(api_key=settings.ANYMAIL["SENDGRID_API_KEY"])
        response = sg.send(message)
        if response.status_code == 202:
            return True, 'Email sent.'
        else:
            return False, 'Failed to send email.'
    except Exception as e:
        return False, f'An error occurred: {str(e)}'

def send_webinar_reminder_email(email, subject, html_content, webinar_title, start_date, end_date):
    import base64
    try:
        start_datetime = datetime.datetime.strptime(start_date, '%Y-%m-%dT%H:%M:%S.%fZ')
        end_datetime = datetime.datetime.strptime(end_date, '%Y-%m-%dT%H:%M:%S.%fZ')

        # Convert UTC datetime objects to IST
        ist_timezone = pytz.timezone('Asia/Kolkata')  # IST timezone
        start_datetime_ist = start_datetime.astimezone(ist_timezone)
        end_datetime_ist = end_datetime.astimezone(ist_timezone)

        # Format datetime objects into the desired string format
        formatted_start_datetime = start_datetime_ist.strftime('%Y%m%dT%H%M%SZ')
        formatted_end_datetime = end_datetime_ist.strftime('%Y%m%dT%H%M%SZ')

        ical_content = f"""
            BEGIN:VCALENDAR\r\n
            VERSION:2.0\r\n
            PRODID:-//Example Corp//iCal4j 1.0//EN\r\n
            BEGIN:VEVENT\r\n
            UID:1234567890@example.com\r\n
            DTSTAMP:{formatted_start_datetime}\r\n
            DTSTART:{formatted_start_datetime}\r\n
            DTEND:{formatted_end_datetime}\r\n
            SUMMARY:Webinar reminder email\r\n
            DESCRIPTION:This is a {webinar_title} event.\r\n
            LOCATION:Virtual\r\n
            END:VEVENT\r\n
            END:VCALENDAR\r\n
            """
        ical_content_encoded = base64.b64encode(ical_content.encode()).decode()        
        message = Mail(
            from_email='welcome@techademy.com',
            to_emails=email,
            subject=subject,
            html_content=html_content
        )
        # Create attachment file
        attachment = Attachment()
        attachment.file_content = FileContent(ical_content_encoded)
        attachment.file_name = FileName('meeting.ics')
        attachment.file_type = FileType('text/calendar')        
        attachment.disposition = Disposition('attachment')
        attachment.content_id = ContentId('Calendar')
        # Attach the calendar event
        message.attachment = attachment
        sg = SendGridAPIClient(api_key=settings.ANYMAIL["SENDGRID_API_KEY"])
        response = sg.send(message)
        if response.status_code == 202:
            return True, 'Email sent.'
        else:
            return False, 'Failed to send email.'
    except Exception as e:
        print(f'An error occurred: {str(e)}')
        return False, f'An error occurred: {str(e)}'
        
    
def number_to_words(number):
    p = inflect.engine()
    return p.number_to_words(number)

def capture_blp_enquiry_to_lsq(enquiry):
    """helper to upload Blended Learning Path Customer Enquiry data to Leadsquared"""
    try:
        data = [
            {
            "Attribute": "FirstName",
            "Value": enquiry.name
            },
            {
                "Attribute": "EmailAddress",
                "Value": enquiry.email
            },
            {
                "Attribute": "SearchBy",
                "Value": "Phone" 
            },
            {
                "Attribute": "Phone",
                "Value": enquiry.phone_number
            },
            {
                "Attribute": "Source",
                "Value": "Website" 
            },
            {
                "Attribute": "mx_Interested_In",
                "Value": enquiry.blp_name
            }
        ]
        
        response = requests.post(f'{settings.LEAD_SQUARE_HOST}LeadManagement.svc/Lead.Capture?accessKey={settings.LEAD_SQUARED_ACCESS_KEY}&secretKey={settings.LEAD_SQUARED_SECRET_KEY}',json=data)
        response = response.json()
        if response["Status"] == "Success":
            enquiry.lead_squared_id = response["Message"]["Id"] if response["Message"] else None
            enquiry.save()
            capture_opportunities_blp_enquiry_to_lsq(enquiry)
    except Exception as e:
        pass


def capture_opportunities_blp_enquiry_to_lsq(enquiry):
    """helper to upload Blended Learning Path Customer Enquiry data to Leadsquared Opportunities"""
    try:
        data ={
                "LeadDetails":[
                    {
                        "Attribute":"EmailAddress",
                        "Value":enquiry.email
                    },
                    {
                        "Attribute":"ProspectID",
                        "Value":enquiry.uuid.hex
                    },
                    {
                        "Attribute":"SearchBy",
                        "Value":"ProspectId"
                    },
                    {
                        "Attribute":"__UseUserDefinedGuid__",
                        "Value":"true"
                    }
                ],
                "Opportunity":{
                    "OpportunityEventCode":12000,
                    "OpportunityNote":"Opportunity capture api overwrite",
                    "UpdateEmptyFields":True,
                    "DoNotPostDuplicateActivity":True,
                    "DoNotChangeOwner":True,
                    "Fields":[
                        {
                            "SchemaName":"mx_Custom_1",
                            "Value":f"{enquiry.name}-{enquiry.blp_name}"
                        },
                        {
                            "SchemaName":"mx_Custom_2",
                            "Value":"Prospecting"
                        },
                        {
                            "SchemaName":"mx_Custom_5",
                            "Value":"Prospecting"
                        },
                        {
                            "SchemaName":"Status",
                            "Value":"Open"
                        }
                    ]
                }
            }
        response = requests.post(f'{settings.LEAD_SQUARE_HOST}OpportunityManagement.svc/Capture?accessKey={settings.LEAD_SQUARED_ACCESS_KEY}&secretKey={settings.LEAD_SQUARED_SECRET_KEY}',json=data)
        response = response.json()
    except Exception as e:
        pass

# def capture_blp_enquiry_auto_pop_up_to_lsq(enquiry):
#     """helper to upload Blended Learning Path Customer Enquiry data to Leadsquared"""
#     try:
#         data = [
#             {
#             "Attribute": "FirstName",
#             "Value": enquiry.name
#             },
#             {
#                 "Attribute": "EmailAddress",
#                 "Value": enquiry.email
#             },
#             {
#                 "Attribute": "SearchBy",
#                 "Value": "Phone" 
#             },
#             {
#                 "Attribute": "Phone",
#                 "Value": enquiry.phone_number
#             },
#             {
#                 "Attribute": "Source",
#                 "Value": "Website" 
#             },
#             {
#                 "Attribute": "mx_Interested_In",
#                 "Value": "Java Full Stack"
#             }
#         ]
        
#         response = requests.post(f'{settings.LEAD_SQUARE_HOST}LeadManagement.svc/Lead.Capture?accessKey={settings.LEAD_SQUARED_ACCESS_KEY}&secretKey={settings.LEAD_SQUARED_SECRET_KEY}',json=data)
#         response = response.json()
#         if response["Status"] == "Success":
#             enquiry.lead_squared_id = response["Message"]["Id"] if response["Message"] else None
#             enquiry.save()
#             # capture_opportunities_blp_enquiry_auto_pop_up_to_lsq(enquiry)
#     except Exception as e:
#         pass

# def capture_opportunities_blp_enquiry_auto_pop_up_to_lsq(enquiry):
#     """helper to upload Blended Learning Path Customer Enquiry data to Leadsquared Opportunities"""
#     try:
#         data ={
#                 "LeadDetails":[
#                     {
#                         "Attribute": "FirstName",
#                         "Value": enquiry.name
#                     },
#                     {
#                         "Attribute":"EmailAddress",
#                         "Value":enquiry.email
#                     },
#                     {
#                         "Attribute":"ProspectID",
#                         "Value":enquiry.uuid.hex
#                     },
#                     {
#                         "Attribute":"SearchBy",
#                         "Value":"ProspectId"
#                     },
#                     {
#                         "Attribute": "Phone",
#                         "Value": enquiry.phone_number
#                     },
#                     {
#                         "Attribute":"__UseUserDefinedGuid__",
#                         "Value":"true"
#                     }
#                 ],
#                 "Opportunity":{
#                     "OpportunityEventCode":12000,
#                     "OpportunityNote":"Opportunity capture api overwrite",
#                     "UpdateEmptyFields":True,
#                     "DoNotPostDuplicateActivity":True,
#                     "DoNotChangeOwner":True,
#                     "Fields":[
#                         {
#                             "SchemaName":"mx_Custom_1",
#                             "Value":f"{enquiry.name}-{enquiry.blp_name}"
#                         },
#                         {
#                             "SchemaName":"mx_Custom_2",
#                             "Value":"Prospecting"
#                         },
#                         {
#                             "SchemaName":"mx_Custom_5",
#                             "Value":"Prospecting"
#                         },
#                         {
#                             "SchemaName":"Status",
#                             "Value":"Open"
#                         }
#                     ]
#                 }
#             }
#         response = requests.post(f'{settings.LEAD_SQUARE_HOST}OpportunityManagement.svc/Capture?accessKey={settings.LEAD_SQUARED_ACCESS_KEY}&secretKey={settings.LEAD_SQUARED_SECRET_KEY}',json=data)
#         response = response.json()
#     except Exception as e:
#         pass


def search_opportunity_by_email_and_phone(email):
    url = f"{settings.LEAD_SQUARE_HOST}LeadManagement.svc/Leads.GetByEmailaddress?accessKey={settings.LEAD_SQUARED_ACCESS_KEY}&secretKey={settings.LEAD_SQUARED_SECRET_KEY}&emailaddress={email}"
    response = requests.get(url)
    if response.status_code == 200:
        opportunities = response.json()
        if opportunities:
            for opportunity in opportunities:
                if opportunity["Status"] == "Open":
                    return opportunity  # Return the first matching open opportunity
    return None

def capture_opportunities_blp_enquiry_auto_pop_up_to_lsq(enquiry):
    """Helper to upload Blended Learning Path Customer Enquiry data to Leadsquared Opportunities"""
    try:
        # Check if an open opportunity already exists for the lead
        existing_opportunity = search_opportunity_by_email_and_phone(enquiry.email)
        
        if existing_opportunity:
            print("An open opportunity already exists for this lead.")
            return None

        data = {
            "LeadDetails": [
                {
                    "Attribute": "FirstName",
                    "Value": enquiry.name
                },
                {
                    "Attribute": "EmailAddress",
                    "Value": enquiry.email
                },
                {
                    "Attribute": "Phone",
                    "Value": enquiry.phone_number
                },
                {
                    "Attribute": "ProspectID",
                    "Value": enquiry.lead_squared_id
                },
                {
                    "Attribute": "SearchBy",
                    "Value": "ProspectId"
                },
                {
                    "Attribute": "__UseUserDefinedGuid__",
                    "Value": "true"
                }
            ],
            "Opportunity": {
                "OpportunityEventCode": 12000,
                "OpportunityNote": "Opportunity capture api overwrite",
                "UpdateEmptyFields": True,
                "DoNotPostDuplicateActivity": True,
                "DoNotChangeOwner": True,
                "Fields": [
                    {
                        "SchemaName": "mx_Custom_1",
                        "Value": f"{enquiry.name}-{enquiry.blp_name}"
                    },
                    {
                        "SchemaName": "mx_Custom_2",
                        "Value": "Prospecting"
                    },
                    {
                        "SchemaName": "mx_Custom_5",
                        "Value": "Prospecting"
                    },
                    {
                        "SchemaName": "Status",
                        "Value": "Open"
                    }
                ]
            }
        }
        response = requests.post(f'{settings.LEAD_SQUARE_HOST}OpportunityManagement.svc/Capture?accessKey={settings.LEAD_SQUARED_ACCESS_KEY}&secretKey={settings.LEAD_SQUARED_SECRET_KEY}', json=data)
        response = response.json()
    except Exception as e:
        pass
