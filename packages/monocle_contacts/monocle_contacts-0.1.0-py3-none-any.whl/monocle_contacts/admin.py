from django.contrib import admin
from .models import *

class SampleModelAdmin(admin.ModelAdmin):
    list_display = ('name','position','isShown',)
    list_editable = ('position','isShown',)



admin.site.register(SampleModel, SampleModelAdmin)
