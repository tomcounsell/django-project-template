from django.contrib import admin
from apps.common.models import User

admin.register(User)


class UserAdmin(admin.ModelAdmin):
    pass
