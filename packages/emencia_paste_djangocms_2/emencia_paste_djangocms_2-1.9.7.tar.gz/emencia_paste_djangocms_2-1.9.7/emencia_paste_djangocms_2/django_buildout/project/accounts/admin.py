from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from .models import UserInfo

class UserInfoAdmin(admin.ModelAdmin):
    list_display = ('user', 'lastname', 'firstname', 'company', 'function',)
    raw_id_fields = ['user']
    search_fields = ('user__username', 'firstname', 'lastname', 'company',)

admin.site.register(UserInfo, UserInfoAdmin)
