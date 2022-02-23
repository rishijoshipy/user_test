from django.urls import path, include

from django.contrib import admin

from foodapp import views

from rest_framework_simplejwt import views as jv

urlpatterns = [
  path('admin/',admin.site.urls),
    #"""SIGNUp ENDUSER AND OWNER"""
    #"""First Phase"""
    path('signup',views.UserSignupVIEW.as_view()),
    path('email_two_Auth',views.User_EmailVerify_VIEW.as_view()),
  
    #"""Second Phase"""
    path('mobiledetails',views.MobileDetails_VIEW.as_view()),
    path('sms_two_Auth',views.User_Mobile_Verify_VIEW.as_view()),
    

    # #LOGIN AND LOGOUT FOR ANY USER
    path('login',views.LoginVIEW.as_view(),name="login"),
    path('login_verify_twoauth',views.User_Login_Verify_VIEW.as_view()),
    path('logout',views.LogoutVIEW.as_view()),

    path('ResendOtp',views.Resend_OtpVIEW.as_view()),
  
    #"""user profile"""
    path('profile',views.User_DetailsVIEW.as_view()),
   

    #""ADMIN PANEL SIGNUP AND MANAGER""
    path('adminsignup',views.AdminUserSign.as_view()),
    path('adminmanager', views.AdminUserManager.as_view()),
  ]