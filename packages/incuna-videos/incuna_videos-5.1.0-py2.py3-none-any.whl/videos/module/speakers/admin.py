from django.contrib import admin
from .models import Speaker


class SpeakerAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}


admin.site.register(Speaker, SpeakerAdmin)
