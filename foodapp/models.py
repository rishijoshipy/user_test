from django.contrib.auth.models import AbstractBaseUser,PermissionsMixin
from django.db import models
from django.utils.translation import gettext_lazy as _

from .managers import CustomUserManager

class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255,null=True,blank=True)

    first_name = models.CharField(max_length=255,null=True,blank=True)
    last_name = models.CharField(max_length=255,blank=True,null=True)
    image = models.ImageField(upload_to='images')

    age=models.IntegerField(blank=True,null=True)
    city_name=models.CharField(max_length=50,  blank=True,null=True)
    state_name =models.CharField(max_length=50,  blank=True,null=True)
    country_name =models.CharField(max_length=50,  blank=True,null=True)
    profession=models.CharField(max_length=50,  blank=True,null=True)
    hobbies=models.CharField(max_length=50,  blank=True,null=True)

    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    """User TWO-Auth"""
    is_auth=models.BooleanField(default=False)
    is_email_verify=models.BooleanField(default=False)
    is_sms_verify=models.BooleanField(default=False)
    is_verify=models.BooleanField(default=False)
    
    is_login=models.BooleanField(default=False)
    
    mob_number=models.CharField(max_length=10,null=True)
    county_code=models.CharField(max_length=3,null=True)

    number = models.CharField(max_length=5,blank=True)#OTP
    otp_expiry_time = models.DateTimeField(null=True)

   

    
    """user login as email"""
    USERNAME_FIELD = 'email'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def get_absolute_url(self):
        return "/users/%i/" % (self.pk)
    def get_email(self):
        return self.email
    def __str__(self):
        return self.email

    class Meta:
        db_table = 'users'

class userlog(models.Model):
    user = models.ForeignKey(CustomUser,on_delete=models.CASCADE)
    status = models.IntegerField(null=True)
    session_id= models.CharField(max_length=50,  blank=True,null=True)
    session_create=models.DateTimeField(null=True)
    session_updated=models.DateTimeField(null=True)

    def __str__(self):
        return str(self.user)
  