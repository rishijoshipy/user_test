from rest_framework import serializers, status
from foodapp.models import *
from rest_framework.validators import UniqueValidator
from foodapp.utility import success,unsuccess
from django.db.models import Q
import random

"""Signup or Register Enduser/Owneruser"""
class UserRegisterSerializer(serializers.ModelSerializer):
    
    email=serializers.EmailField(required=True,validators=[UniqueValidator(queryset=CustomUser.objects.all())])
    name = serializers.CharField(required=True,min_length=4,max_length=50)
    password = serializers.CharField(required=True,min_length=6,write_only= True)
    confirm_password = serializers.CharField(required=True,write_only= True)
    
    class Meta:
        model= CustomUser
        fields = ('email','name','password','confirm_password','is_auth')
    
    def create(self, validated_data):
        password = validated_data['password']  
        num = self.context["number"]
        time=self.context["time"]
        user=CustomUser.objects.create_user(email=validated_data['email'],
                                    name=validated_data['name'],
                                    is_auth=validated_data['is_auth'],
                                    number=num,
                                    otp_expiry_time=time,
                                    )
        user.set_password(password)
        user.save()
        return user

    def validate(self, data):
        email=data.get('email')
        name =  data.get('name')
        last_name = data.get('last_name')
        password = data.get('password')
        confirm_password = data.get('confirm_password')
        
        if not email[0].isalpha():
            raise serializers.ValidationError({"email" : ["Enter a valid email address."]})
        
        if password != confirm_password:
            raise serializers.ValidationError({"confirm_password":["Those passwords don't match."]})

        return data

"""TWO-auth Email_Verify"""
class Email_VerifySerializer(serializers.ModelSerializer):
    
    class Meta:
        model=CustomUser
        fields=("is_email_verify","number","otp_expiry_time",)

    def update(self, instance, validated_data):
        instance.number = validated_data.get('number', instance.number)
        instance.otp_expiry_time = validated_data.get('otp_expiry_time', instance.otp_expiry_time)        
        instance.is_email_verify = validated_data.get('is_email_verify', instance.is_verify)
        instance.save()
        return instance

"""User Mobile and code serializer"""
class mobileSerializer(serializers.ModelSerializer):
     
    class Meta:
        model=CustomUser
        fields=('mob_number','county_code')

    def update(self, instance, validated_data):
        instance.mob_number = validated_data.get('mob_number', instance.mob_number)
        instance.county_code = validated_data.get('county_code', instance.county_code)
        instance.save()
        return instance

"""TWO-auth mobile_Verify"""
class SMS_VerifySerializer(serializers.ModelSerializer):
    
    class Meta:
        model=CustomUser
        fields=("is_sms_verify","number","otp_expiry_time",)

    def update(self, instance, validated_data):
        instance.number = validated_data.get('number', instance.number)
        instance.otp_expiry_time = validated_data.get('otp_expiry_time', instance.otp_expiry_time)        
        instance.is_sms_verify = validated_data.get('is_sms_verify', instance.is_sms_verify)
        instance.save()
        return instance

class Login_VerifySerializer(serializers.ModelSerializer):
    
    class Meta:
        model=CustomUser
        fields=("is_verify","number","otp_expiry_time",)

    def update(self, instance, validated_data):
        instance.number = validated_data.get('number', instance.number)
        instance.otp_expiry_time = validated_data.get('otp_expiry_time', instance.otp_expiry_time)        
        instance.is_verify = validated_data.get('is_verify', instance.is_verify)
        instance.save()
        return instance

"""Resend OTP"""
class ResendOTPSerializer(serializers.ModelSerializer):
    
    class Meta:
        model=CustomUser
        fields=("number","otp_expiry_time",)

    def update(self, instance, validated_data):
        instance.number = validated_data.get('number', instance.number)
        instance.otp_expiry_time = validated_data.get('otp_expiry_time', instance.otp_expiry_time)
        instance.save()
        return instance



"""Owner User update res_name,city,res_address"""
class userSerializer(serializers.ModelSerializer):
     
    class Meta:
        model=CustomUser
        fields=('first_name','last_name','age','city_name','state_name','country_name','profession','hobbies')

    def update(self, instance, validated_data):
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.age = validated_data.get('age', instance.age)
        
        instance.city_name = validated_data.get('city_name', instance.city_name)
        instance.state_name = validated_data.get('state_name', instance.state_name)
        instance.country_name = validated_data.get('country_name', instance.country_name)
        instance.profession = validated_data.get('profession', instance.profession)
        instance.profession = validated_data.get('profession', instance.profession)
        instance.hobbies = validated_data.get('hobbies', instance.hobbies)
        instance.save()
        return instance

"""ADMIN SIGNUP"""
class AdminUserRegisterSerializer(serializers.ModelSerializer):
    email=serializers.EmailField(required=True,validators=[UniqueValidator(queryset=CustomUser.objects.all())])
    name = serializers.CharField(required=True,min_length=4,max_length=50)
    password = serializers.CharField(required=True,min_length=6,write_only= True)
    confirm_password = serializers.CharField(required=True,write_only= True)
    
    class Meta:
        model= CustomUser
        fields = ('email','name','password','confirm_password')

    def validate(self, data):
        email=data.get('email')
        name =  data.get('name')
        password = data.get('password')
        confirm_password = data.get('confirm_password')
        
        if not email[0].isalpha():
            raise serializers.ValidationError({"email" : ["Enter a valid email address."]})
 
        if password != confirm_password:
            raise serializers.ValidationError({"confirm_password":["Those passwords don't match."]})

        return data
        
    def create(self, validated_data):
        password = validated_data['password']
        user=CustomUser.objects.create_superuser(email=validated_data['email'],
                                    password = validated_data['password'],
                                    name=validated_data['name'],
                                    )
        user.set_password(password)
        user.save()
        return user

"""ADMIN MANAGER---- USER ---UPDATE,DELETE SERIALIZER"""
class AdminUserManagerSerializer(serializers.ModelSerializer):
    
    class Meta:
        model= CustomUser
        fields = "__all__"

    def update(self, instance, validated_data):
        instance.is_active = validated_data.get('is_active', instance.is_active)
        instance.save()
        return instance

    def delete(self,instance):
        instance.delete()
