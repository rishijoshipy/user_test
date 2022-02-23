import re
import json
from urllib import response
from wsgiref.util import request_uri
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
        serializer = UserRegisterSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            print("User Created SuccessFully but not Authenticated")
        else:
            code = status.HTTP_404_NOT_FOUND
            return Response(unsuccess(code,serializer.errors),code)        

        user_data=CustomUser.objects.get(email=email)
        exp_time_save(user_data)
        random_number_OTP(user_data)
        user = authenticate(email=email, password=password)
        if user:
            token_pair = TokenObtainPairSerializer()
            refresh = token_pair.get_token(user)
            access = refresh.access_token
            if user_data.is_auth:
                #user_mail_send(user_data)
                print("mail send")
                code = status.HTTP_201_CREATED
                return Response(success_login(code, "2-FA is On and OTP send to mail.Please Verify.", serializer.data,str(access),str(refresh)),code)      
            else:
                code = status.HTTP_201_CREATED
                return Response(success_login(code, "2-FA is Off and User is created.", serializer.data,str(access),str(refresh)),code)
        else:
            return Response("user not found")

"""USer TWo-auth email verify"""
class User_EmailVerify_VIEW(APIView):
    permission_classes = (IsAuthenticated,)

    def patch(self,request,format=None):
        user=request.user
        user_otp=request.data["OTP"]
        user_data=CustomUser.objects.get(email=user)
        if user_data.is_auth:
            time = datetime.now()
            current_time = time.replace(tzinfo=utc)
            if current_time < user_data.otp_expiry_time:
                gen_otp=user_data.number
                if user_otp==gen_otp:
                    try:
                        user_mail_verified(user_data)
                        code = status.HTTP_200_OK
                        return Response("User Email Verified Successfully",code)
                    except Exception as e :
                        print(e)              
                else:
                    return HttpResponse("Wrong OTP")
            else:
                return Response("OTP Expire")
        else:
            code = status.HTTP_200_OK
            return Response(success(code, "2-FA is Off",user),code)

"""Mobile details add"""
class MobileDetails_VIEW(APIView):
    permission_classes = [IsAuthenticated,]

    def patch(self, request, format=None):
        user=request.user
        data=request.data
        user_data = CustomUser.objects.get(email=user)
        print(user_data)
        exp_time_save(user_data)
        random_number_OTP(user_data)
        serializer = mobileSerializer(user_data,data=data,partial=True)
        if serializer.is_valid():
            serializer.save()
            #user_send_sms(user_data)
            codes = status.HTTP_201_CREATED
            return Response(success(codes, "Mobile Details Added and OTP send to mobile.Please Verify.",serializer.data),codes)
        else:    
            code = status.HTTP_404_NOT_FOUND
            return Response(unsuccess(code,serializer.errors),code)
        
"""USer TWo-auth sms verify"""
class User_Mobile_Verify_VIEW(APIView):
    permission_classes = (IsAuthenticated,)

    def patch(self,request,format=None):
        user=request.user
        user_otp=request.data["OTP"]
        user_data=CustomUser.objects.get(email=user)
        if user_data.is_auth:
            time = datetime.now()
            current_time = time.replace(tzinfo=utc)
            if current_time < user_data.otp_expiry_time:
                gen_otp=user_data.number
                if user_otp==gen_otp:
                    try:
                        user_mobile_verified(user_data)
                        code = status.HTTP_200_OK
                        return Response("User Mobile Verified and User Registration Successfully.",code)
                    
                    except Exception as e :
                        print(e)              
                else:                  
                    return Response("wrong OTP")
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
            time = datetime.now()
            current_time = time.replace(tzinfo=utc)
            user_data=CustomUser.objects.get(email=user)
            if current_time>user_data.otp_expiry_time:
                try:
                    exp_time_save(user_data)
                    random_number_OTP(user_data)
                    #user_mail_send(user_data)
                    #user_send_sms(user_data)
                    code = status.HTTP_200_OK
                    return Response("OTP Resend Successfully",code)
                except Exception as e :
                    print(e)              
            else:
                return Response("Try Afer Some Time,OTP not expired")
        else:
            code = status.HTTP_200_OK
            return Response(success(code, "Two-Factor-Auth not Avaliable ",user),code)

"""USer Login API"""
class LoginVIEW(APIView):
    
    def post(self,request,format=None):
        data = request.data
        user_req=request.user
        email = request.data['email']
        password = request.data['password']
        user = authenticate(email=email, password=password)
        print(user)
        if user and user.is_email_verify and user.is_sms_verify and user.is_active:
            if user.is_login:
                return Response(f"User already login."+"\n"+f"session id:{user.session_id}.")
            else:
                token_pair = TokenObtainPairSerializer()
                refresh = token_pair.get_token(user)
                access = refresh.access_token
                exp_time_save(user)
                random_number_OTP(user)
                statuslogin(user,access)
                if user.is_auth:
                    try:  
                        #user_mail_send(user)
                        #user_send_sms(user)
                        auth_login(request,user)
                        code = status.HTTP_201_CREATED
                        return Response(success_login(code, "2-FA Login is On. Please Verify.", data,str(access),str(refresh)),code)      
                    except Exception as e:
                        print(e)
                else:
                    try:
                        user_mail_send(user)
                        code = status.HTTP_201_CREATED
                        return Response(success_login(code, "2-FA Login is Off. Please Verify.", data,str(access),str(refresh)),code)      
                    except Exception as e:
                        print(e)            
        else:
            return Response("User not found/verified with mail/mobile") 

"""USer TWo-auth sms verify"""
class User_Login_Verify_VIEW(APIView):
    permission_classes = (IsAuthenticated,)

    def patch(self,request,format=None):
        user_data=request.user
        user_otp=request.data["OTP"]
        time = datetime.now()
        current_time = time.replace(tzinfo=utc)
        if current_time< user_data.otp_expiry_time:
            gen_otp=user_data.number
            if user_otp==gen_otp:
                try:
                    user_verified(user_data)
                    #add login details{session}
                    
                    code = status.HTTP_200_OK
                    return Response("Verified and Login Successfully",code)
                except Exception as e:
                    print(e)
            else:
                return Response("wrong OTP")
        else:
            return Response("OTP Expire")

"""User logout API"""
class LogoutVIEW(APIView):
    permission_classes = (IsAuthenticated,)
    def post(self, request):
        user=request.user
        if user.is_login and user.is_verify :
            if user.is_active:
                try:
                    statuslogout(user,user.session_id)
                    auth_logout(request)
                    code = status.HTTP_200_OK
                    return Response("Logout SuccessFull",code)
                except Exception as e:
                    print(e)
            else:
                return Response("user is block")
        else:
            return Response("Please, Login")
            
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
        if user.is_login and user.is_verify:
            serializer = userSerializer(user,data=data,partial=True)
            if serializer.is_valid():
                serializer.save()
                code = status.HTTP_200_OK
                return Response(success(code, "user details added",serializer.data),code)
        else:    
            code = status.HTTP_404_NOT_FOUND
            return Response(unsuccess(code,"Login required"),code)

class User_ProfilePicVIEW(APIView):
    permission_classes = [IsAuthenticated,]
    def get(self, request, format=None):
        user=request.user
        user_data = CustomUser.objects.get(email=user)
        serializer =  userprofileSerializer(user_data)
        return Response(serializer.data)

    def patch(self, request, format=None):
        file_uploaded = request.FILES.get('image')
        user=request.user
        data={"image":file_uploaded}
        if user.is_login and user.is_verify:
            serializer =  userprofileSerializer(user,data=data,partial=True)
            if serializer.is_valid():
                serializer.save()
                code = status.HTTP_200_OK
                return Response(success(code, "user profile pic added",serializer.data),code)
        else:    
            code = status.HTTP_404_NOT_FOUND
            return Response(unsuccess(code,"Login required"),code)


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
        searched=request.data["Active"]
        if searched=="True":
            Emp1 = CustomUser.objects.filter(Q(is_active=True))
            serializer = AdminUserManagerSerializer(Emp1,many=True)
            return Response(serializer.data)

        elif searched=="False":
            Emp1 = CustomUser.objects.filter(Q(is_active=False))
            serializer = AdminUserManagerSerializer(Emp1,many=True)
            return Response(serializer.data)

    def post(self, request,format=None):
        searched=request.data["Active"]
        if searched=="True":
            isadmin= CustomUser.objects.filter(Q(is_login=True))
            serializers = AdminUserManagerSerializer(isadmin,many=True)
            return Response(serializers.data)
        elif searched=="False":
            isadmin= CustomUser.objects.filter(Q(is_login=False))
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
