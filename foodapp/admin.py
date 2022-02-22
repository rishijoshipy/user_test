
# Register your models here.
from django.contrib import admin
from .models import *


class CustomUserAdmin(admin.ModelAdmin):
    model = CustomUser
    list_display = ('email', 'is_staff', 'is_active','is_auth','is_verify','number','is_email_verify','is_sms_verify','is_login','county_code','mob_number','otp_expiry_time','session_id','session_create','session_updated')
    list_filter  = ('email', 'is_staff', 'is_active',)
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Permissions', {'fields': ('is_staff','is_active','is_superuser','is_owner','is_enduser')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'is_staff', 'is_active')}
        ),
    )
    search_fields = ('email',)
    ordering = ('email',)


admin.site.register(CustomUser, CustomUserAdmin)

# admin.site.register(Cuisine)
# admin.site.register(dishe)
# admin.site.register(Order)
