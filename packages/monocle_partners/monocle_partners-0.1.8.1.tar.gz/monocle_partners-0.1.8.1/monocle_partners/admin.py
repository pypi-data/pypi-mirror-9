from django.contrib import admin
from .models import *

class PartnerAdmin(admin.ModelAdmin):
    list_display = ('name','image_admin','position')
    list_editable = ['position']
    fields = ['name','image','position']
    sortable_field_name = "position"


admin.site.register(Partner, PartnerAdmin)
