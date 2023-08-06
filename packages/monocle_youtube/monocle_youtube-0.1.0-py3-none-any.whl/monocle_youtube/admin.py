from django.contrib import admin
from .models import *

class VideoAdmin(admin.ModelAdmin):
    list_display = ('channel_id',)



admin.site.register(Video, VideoAdmin)
