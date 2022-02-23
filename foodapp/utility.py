from time import time
import random
from django.conf import settings

from .models import *
from django.db.models import Q

from django.core.mail import send_mail

from twilio.rest import Client
account_sid =settings.TWILLIO_ACCOUNT_SID
auth_token =settings.TWILIO_AUTH_TOKEN

from datetime import  datetime, timedelta

import pytz

def random_number_OTP(user):
    number_list=[x for x in range(10)]
    code_items=[]
    for i in range(4):
        num=random.choice(number_list)
        code_items.append(num)
    code_string="".join(str(item) for item in code_items)
    user.number=code_string
    user.save()

utc=pytz.UTC
def exp_time_save(user):
    time = datetime.now()
    current_time = time.replace(tzinfo=utc)
    user.otp_expiry_time = current_time+timedelta(seconds=60)
    user.save()

def user_mail_send(user):
    """SEND EMAIL"""
    try:
        otp=user.number
        username=user.name
        email=user.email
        subject = "Email Verification."
        message =f'Hi ,{username}'+"\n"+ f'Here your ID :"{email}" and OTP:"{otp}".'
        email_from = settings.EMAIL_HOST_USER
        recipient_list = [email, ]
        send_mail(subject, message, email_from, recipient_list)
        print("Email Send",message)
    
    except Exception as e:
        print(e)

def user_send_sms(user_data):
    """SEND SMS"""
    username=user_data.name
    email=user_data.email
    message =f'Hi {username},SMS Verification...'+"\n"+ f'Here your ID :"{email}" and OTP:"{user_data.number}".'
    send_to=user_data.county_code+user_data.mob_number
    client = Client(account_sid, auth_token) 
    message = client.messages.create(  
                    messaging_service_sid=settings.TWILIO_SERVICE_SID, 
                    body=message,      
                    to=send_to 
                ) 
    print("SMS Send")

def user_mail_verified(user):
    user.number=""
    user.is_email_verify="True"
    user.save()
    print("mail verified save")


def user_mobile_verified(user):
    user.number=""
    user.is_sms_verify="True"
    user.save()
    print("Mobile verified save")

def user_verified(user):
    user.number=""
    user.is_login="True"
    user.is_verify="True"
    user.save()
    print("User verified")

def statuslogin(user,access_token):
    time = datetime.now()
    current_time = time.replace(tzinfo=utc)
    user.session_id=access_token
    user.session_create=current_time
    user.save()


def statuslogout(user,access_token):
    time = datetime.now()
    current_time = time.replace(tzinfo=utc)
    user.is_login="False"
    user.is_verify="False"
    user.session_id=""
    user.session_updated=current_time
    user.save()

def success(code,message,dataser):
    return {"code":code,"message":message,"data":dataser}

def unsuccess(code,dataser):
    message = "Data Error...Bad Reuest!"
    return {"code":code,"message":message,"data":dataser}

def success_login(code,message,dataser,access,refresh):
    data = {
        "user" : dataser,
        "access_token":access,
        "refresh_token":refresh
    }
    return {"code":code,"message":message,"data":data}

def success_logout(code,message):
    return {"code":code,"message":message}



