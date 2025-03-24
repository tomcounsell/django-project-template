from django.contrib import admin
from unfold.admin import ModelAdmin

class BaseAdmin(ModelAdmin):
  exclude = ('created_at', 'modified_at',)
