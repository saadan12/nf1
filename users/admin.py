# src/users/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.db import models

from tinymce.widgets import TinyMCE
from .models import CustomUser, Privacy_Policy, Cookies_Policy, API_KEY, AllLogin, UserActivity, AuthCode


class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('email', 'is_staff', 'is_active',)
    list_filter = ('email', 'is_staff', 'is_active',)
    fieldsets = (
        (None, {'fields': ('email', 'password', 'username')}),
        ('Permissions', {'fields': ('is_staff', 'is_active')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'is_staff', 'is_active')}
         ),
    )
    search_fields = ('email',)
    ordering = ('email',)


class textEditorAdmin1(admin.ModelAdmin):
    list_display = ["privacy_content"]
    formfield_overrides = {
        models.TextField: {'widget': TinyMCE()}
    }


class textEditorAdmin2(admin.ModelAdmin):
    list_display = ["cookies_content"]
    formfield_overrides = {
        models.TextField: {'widget': TinyMCE()}
    }


admin.site.register(Privacy_Policy, textEditorAdmin1)
admin.site.register(Cookies_Policy, textEditorAdmin2)
admin.site.register(CustomUser)
admin.site.register(API_KEY)
admin.site.register(AllLogin)
admin.site.register(UserActivity)
admin.site.register(AuthCode)
