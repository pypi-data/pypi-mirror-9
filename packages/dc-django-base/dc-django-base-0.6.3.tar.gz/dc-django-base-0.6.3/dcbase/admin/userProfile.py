from dcbase.models import UserProfile
from django.contrib import admin


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user']
    search_fields = ['user__username']
