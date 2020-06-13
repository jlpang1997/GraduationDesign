from django.contrib import admin
from TestModel.models import *
# Register your models here.

class ContactAdmin(admin.ModelAdmin):
    fields = ('name', 'email')
 
admin.site.register(Contact, ContactAdmin)

admin.site.register([Test,Tag])
