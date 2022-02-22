import re
import json
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect

from rest_framework import status
from rest_framework.views import APIView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import *
from django.db.models import Q

from .serializers import *

from .utility import *

from .permissions import *

import stripe
stripe.api_key=settings.STRIPE_SECRET_KEY

from django.contrib.auth import authenticate,login as auth_login,logout as auth_logout

from datetime import  datetime, timedelta
"""User registrations API with Two_AUTH On/OFF"""
class UserSignupVIEW(APIView):
    def get(self, request, format=None):  
        Emp1 = CustomUser.objects.all()
        serializer = UserRegisterSerializer(Emp1, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        data=request.data
        email = request.data['email']
        password = request.data['password']
        num=random_number_OTP()
        time = datetime.now()
        current_time = time.replace(tzinfo=utc)
        otp_expiry_time = exp_time(current_time)
        serializer = UserRegisterSerializer(data=data,context={"number":num,"time":otp_expiry_time})
        if serializer.is_valid():
            serializer.save()
            print("User Created SuccessFully")
        else:
            code = status.HTTP_404_NOT_FOUND
            return Response(unsuccess(code,serializer.errors),code)        
        User_data=CustomUser.objects.get(email=email)
        user = authenticate(email=email, password=password)
        if user:
            token_pair = TokenObtainPairSerializer()
            refresh = token_pair.get_token(user)
            access = refresh.access_token
            #auth_login(request,user)
            if User_data.is_auth:
                otp=User_data.number
                username=User_data.name
                #send_to=User_data.county_code+User_data.mob_number
                Email=User_data.email
                subject = "Greetingsss...."
                message =f'Hi {username},Email Verification.'+"\n"+ f'Here your ID :"{user}" and OTP:"{otp}".'
                print(message)
                #user_mail_send(subject,message,Email)
                code = status.HTTP_201_CREATED
                return Response(success_login(code, "User OTP send to mail successfully)", serializer.data,str(access),str(refresh)),code)      
            else:
                code = status.HTTP_201_CREATED
                return Response(success_login(code, "Two-Factor is Off", serializer.data,str(access),str(refresh)),code)
        else:
            return Response("user not found")

"""USer TWo-auth email verify"""
class User_EmailVerify_VIEW(APIView):
    permission_classes = (IsAuthenticated,)

    def patch(self,request,format=None):
        user=request.user
        user_otp=request.data["OTP"]
        code=CustomUser.objects.get(email=user)
        
        if code.is_auth:
            time = datetime.now()
            current_time = time.replace(tzinfo=utc)
            session_expiry_time=exp_time_session(current_time)  
            if current_time < code.otp_expiry_time:
                gen_otp=code.number
                if user_otp==gen_otp:
                    data={"number":"","is_email_verify":"True"}
                    serializer = Email_VerifySerializer(code,data=data,context={'user':request.user},partial=True)
                    if serializer.is_valid():
                        serializer.save()
                        subject="User Activations"
                        username=code.name
                        message=f'{username} is Email Verified and user created Successfully'
                        Email=code.email
                        #user_mail_send(subject,message,Email)
                        code = status.HTTP_200_OK
                        return Response(success(code,"User Email Verified Successfully",serializer.data),code)
                    else:    
                        code = status.HTTP_404_NOT_FOUND
                        return Response(unsuccess(code,serializer.errors),code)
                else:
                    if current_time< session_expiry_time:
                        code.delete()
                        return HttpResponse("User not created Because OTP not validated for long time")
                    else:
                        return HttpResponse("wrong OTP")
            else:
                return Response("OTP Expire")
        else:
            code = status.HTTP_200_OK
            return Response(success(code, "Two-Factor-Auth not Avaliable ",user),code)

"""Mobile details add"""
class MobileDetails_VIEW(APIView):
    permission_classes = [IsAuthenticated,]

    def patch(self, request, format=None):
        user=request.user
        data=request.data
        code = CustomUser.objects.get(email=user)
        print(code)
        num=random_number_OTP()
        time = datetime.now()
        current_time = time.replace(tzinfo=utc)
        otp_expiry_time = exp_time(current_time)
        serializer = mobileSerializer(code,data=data,context={'user':request.user},partial=True)
        if serializer.is_valid():
            code.number=num
            code.otp_expiry_time=otp_expiry_time
            code.save()

            serializer.save()
            username=code.name
            message =f'Hi {username},SMS Verification...'+"\n"+ f'Here your ID :"{user}" and OTP:"{code.number}".'
            send_to=code.county_code+code.mob_number
            Email=code.email
            #user_send_sms(message,send_to)
            print(message)
            codes = status.HTTP_201_CREATED
            return Response(success(codes, "Owner details added",serializer.data),codes)
        else:    
            code = status.HTTP_404_NOT_FOUND
            return Response(unsuccess(code,serializer.errors),code)
        
"""USer TWo-auth sms verify"""
class User_SMS_Verify_VIEW(APIView):
    permission_classes = (IsAuthenticated,)

    def patch(self,request,format=None):
        user=request.user
        user_otp=request.data["OTP"]
        code=CustomUser.objects.get(email=user)
        if code.is_auth:
            time = datetime.now()
            current_time = time.replace(tzinfo=utc)
            session_expiry_time=exp_time_session(code.otp_expiry_time)
            if current_time < code.otp_expiry_time:
                gen_otp=code.number
                if user_otp==gen_otp:
                    data={"number":"","is_sms_verify":"True"}
                    serializer = SMS_VerifySerializer(code,data=data,context={'user':request.user},partial=True)
                    if serializer.is_valid():
                        serializer.save()
                        subject="User Activations"
                        username=code.name
                        message=f'{username} is Verified Successfully'
                        send_to=code.county_code+code.mob_number
                        Email=code.email
                        #user_send_sms(message,send_to)
                        code = status.HTTP_200_OK
                        return Response(success(code,"User SMS Verified Successfully User Registrations Done..",serializer.data),code)
                    else:    
                        code = status.HTTP_404_NOT_FOUND
                        return Response(unsuccess(code,serializer.errors),code)
                else:
                     if current_time< session_expiry_time:
                        code.delete()
                        return HttpResponse("User not created Because OTP not validated for long time")
                     else:
                        return HttpResponse("wrong OTP")
            else:
                return Response("OTP Expire")     
        else:
            code = status.HTTP_200_OK
            return Response(success(code, "Two-Factor-Auth not Avaliable ",user),code)

"""OTP Resend"""
class Resend_OtpVIEW(APIView):
    permission_classes = [IsAuthenticated,]

    def patch(self,request,format=None):        
        user=request.user
        if user.is_auth:
            num=random_number_OTP()
            time = datetime.now()
            current_time = time.replace(tzinfo=utc)
            T_time = exp_time(current_time)
            code=CustomUser.objects.get(email=user)
            if current_time > code.otp_expiry_time:
                data={"number":num,"otp_expiry_time":T_time}
                serializer = ResendOTPSerializer(code,data=data,partial=True)
                if serializer.is_valid():
                    serializer.save()
                else: 
                    code = status.HTTP_404_NOT_FOUND
                    return Response(unsuccess(code,serializer.errors),code)
                number=code.number
                subject="Resend OTP"
                message=f'Resend OTP:{number}'
                Email=code.email
                #send_to=code.county_code+code.mob_number
                #user_mail_send(subject,message,Email)
                #user_send_sms(message,send_to)
                print(message)
                code = status.HTTP_200_OK
                return Response(success(code,"OTP Resend Successfully",serializer.data),code)
            else:
                return Response("Try Afer Some Time")
        else:
            code = status.HTTP_200_OK
            return Response(success(code, "Two-Factor-Auth not Avaliable ",user),code)

"""USer Login API"""
class LoginVIEW(APIView):
    
    def post(self,request,format=None):
        data = request.data

        email = request.data['email']
        password = request.data['password']
        time = datetime.now()
        current_time = time.replace(tzinfo=utc)
        otp_expiry_time = exp_time(current_time)
        user = authenticate(email=email, password=password)
        print(user)
        if user:    
            if user.is_login:
                return Response("Please loging after some time because User already loging..")
            
            elif user.is_auth==1:
                token_pair = TokenObtainPairSerializer()
                refresh = token_pair.get_token(user)
                access = refresh.access_token

                user_data=CustomUser.objects.get(email=user)
                num=random_number_OTP() 
                time = datetime.now()
                current_time = time.replace(tzinfo=utc)
                otp_expiry_time = exp_time(current_time)

                statuslogin(user,otp_expiry_time,access,current_time,num)

                username=user_data.name
                send_to=user_data.county_code+user_data.mob_number
                Email=user_data.email
                subject = "Greetingsss...."
                message =f'Hi {username},Thank you for Registrations.'+"\n"+ f'Here your ID :"{user}" and OTP:"{user_data.number}".'
                print(message)
                #user_mail_send(subject,message,Email)
                #user_send_sms(message,send_to)

                code = status.HTTP_201_CREATED
                return Response(success_login(code, "OTP send to MAIL,SMS. Please Verify OTP For Login.)", data,str(access),str(refresh)),code)      


            elif user.is_auth==0:
                token_pair = TokenObtainPairSerializer()
                refresh = token_pair.get_token(user)
                access = refresh.access_token
                statusloging(user,current_time,access)

                user_data=CustomUser.objects.get(email=user)
                num=random_number_OTP() 
                time = datetime.now()
                current_time = time.replace(tzinfo=utc)
                otp_expiry_time = exp_time(current_time)
                user_data.save()

                otp=user_data.number
                username=user_data.name
                Email=user_data.email
                subject = "Greetingsss...."
                message =f'Hi {username},Thank you for Registrations.'+"\n"+ f'Here your ID :"{user}" and OTP:"{otp}".'
                print(message)
                #user_mail_send(subject,message,Email)
                code = status.HTTP_201_CREATED
                return Response(success_login(code, "OTP send to MAIL Only. Please Verify OTP...)", serializer.data,str(access),str(refresh)),code)      

            else:
                return Response("zero codition match")
        else:
            code = status.HTTP_404_NOT_FOUND
            return Response(unsuccess(code,"Fail"),code)

"""USer TWo-auth sms verify"""
class User_Login_Verify_VIEW(APIView):
    permission_classes = (IsAuthenticated,)

    def patch(self,request,format=None):
        user=request.user
        user_otp=request.data["OTP"]
        code=CustomUser.objects.get(email=user)
           
        time = datetime.now()
        current_time = time.replace(tzinfo=utc)
        session_expiry_time=exp_time_session(code.otp_expiry_time)
        if current_time< code.otp_expiry_time:
            gen_otp=code.number
            if user_otp==gen_otp:
                data={"number":"","is_verify":"True"}
                serializer = Login_VerifySerializer(code,data=data,context={'user':request.user},partial=True)
                if serializer.is_valid():
                    serializer.save()
                    access=code.session_id
                    #auth_login(request,user)
                    code = status.HTTP_200_OK
                    return Response(success_login(code, "Verified and Login SuccessFull", serializer.data,str(access),str("HII")),code)
                else:    
                    code = status.HTTP_404_NOT_FOUND
                    return Response(unsuccess(code,serializer.errors),code)
            else:
                return HttpResponse("wrong OTP")
        else:
            if current_time<session_expiry_time:
                data={"session_id":"","is_verify":"False","is_login":"False"}
                serializer = Login_VerifySerializer(code,data=data,context={'user':request.user},partial=True)
                if serializer.is_valid():
                    serializer.save()
                    code = status.HTTP_200_OK
                    return Response(success_login(code, "Not Verified and Login UnsuccessFull", serializer.data,str(access),str("HII")),code)
            else:
                return Response("OTP Expire")

"""User logout API"""
class LogoutVIEW(APIView):
    permission_classes = (IsAuthenticated,)
    def post(self, request):

        user=request.user
        if user.is_login and user.is_verify:
            time = datetime.now()
            current_time = time.replace(tzinfo=utc)
            statuslogout(user,current_time)
            auth_logout(request)
            code = status.HTTP_200_OK
            return Response(success_logout(code, "Logout SuccessFull"))
        else:
            return Response("not logout")
            
"""Profile Update"""
class User_DetailsVIEW(APIView):
    permission_classes = [IsAuthenticated,]
    def get(self, request, format=None):
        user=request.user
        user1 = CustomUser.objects.get(email=user)
        serializer = userSerializer(user1)
        return Response(serializer.data)

    def patch(self, request, format=None):
        data = request.data
        user=request.user
        user1 = CustomUser.objects.get(email=user)
        print(user1)
        serializer = userSerializer(user1,data=data,context={'user':request.user},partial=True)
        if serializer.is_valid():
            serializer.save()
            code = status.HTTP_200_OK
            return Response(success(code, "Owner details added",serializer.data),code)
        else:    
            code = status.HTTP_404_NOT_FOUND
            return Response(unsuccess(code,serializer.errors),code)

"""Admin User Signup"""
class AdminUserSign(APIView):
    def get(self, request, format=None):  
        Emp1 = CustomUser.objects.all()
        serializer = AdminUserRegisterSerializer(Emp1, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        data=request.data
        serializer = AdminUserRegisterSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            code = status.HTTP_201_CREATED
            return Response(success(code, "Admin Created", serializer.data),code)
        code = status.HTTP_404_NOT_FOUND
        return Response(unsuccess(code,serializer.errors),code) 

"""ADMIN MANAGER FOR  GET,POST,UPDATE"""
class AdminUserManager(APIView):
    permission_classes = (IsAuthenticated,adminuserAuthenticationPermission)
    def get(self, request, format=None):  
        user=request.user
        searched=request.data["Active"]

        if searched==True:
            Emp1 = CustomUser.objects.filter(Q(is_active=True))
            serializer = AdminUserManagerSerializer(Emp1,many=True,context={'request': request})
            return Response(serializer.data)

        elif searched==False:
            Emp1 = CustomUser.objects.filter(Q(is_active=False))
            serializer = AdminUserManagerSerializer(Emp1,many=True,context={'request': request})
            return Response(serializer.data)

    def post(self, request,format=None):
        isadmin= CustomUser.objects.filter(Q(is_login=True))
        serializers = AdminUserManagerSerializer(isadmin,many=True)
        return Response(serializers.data)

    def patch(self, request, format=None):
        emails=request.data["email"]
        user= CustomUser.objects.filter(Q(email=emails))
        if user:
            data={"is_active":"False"}
            serializer = AdminUserManagerSerializer(user,data=data,context={'user':request.user},partial=True)
            if serializer.is_valid():
                serializer.save()
                code = status.HTTP_200_OK
                return Response(success(code, "User is Blocked",serializer.data),code)
            else:
                return Response("data not valid")
        else:
            return Response("user not found")
    