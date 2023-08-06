from django.contrib import admin
from .models import *

class SocialButtonAdmin(admin.ModelAdmin):
    list_display = ('name','position',)
    list_editable = ('position',)


admin.site.register(SocialButton, SocialButtonAdmin)
