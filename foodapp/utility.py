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
utc=pytz.UTC
time=datetime.now()
current_time = time.replace(tzinfo=utc)

def exp_time(now):
    expired = now+timedelta(seconds=120)
    return expired

def exp_time_session(now):
    expired= now+timedelta(minutes=5)
    return expired

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

def user_mail_send(subject,message,Email):
    """SEND EMAIL"""
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [Email, ]
    send_mail(subject, message, email_from, recipient_list)
    print("Email Send")
            
def user_send_sms(message,send_to):
    """SEND SMS"""
    client = Client(account_sid, auth_token) 
    message = client.messages.create(  
                    messaging_service_sid=settings.TWILIO_SERVICE_SID, 
                    body=message,      
                    to=send_to 
                ) 
    print("SMS Send")

def random_number_OTP():
    number_list=[x for x in range(10)]
    code_items=[]
    for i in range(4):
        num=random.choice(number_list)
        code_items.append(num)
    code_string="".join(str(item) for item in code_items)
    numbers=code_string
    return numbers

def statuslogin(user,exp_time,access_token,time,num):
    user.is_login="True"
    user.otp_expiry_time=exp_time
    user.session_id=access_token
    user.session_create=time
    user.number=num
    user.save()

def statuslogout(user,time):
    user.is_login="False"
    user.session_id=""
    user.session_updated=time
    user.save()
