from django.contrib import admin
from core.models import *
from core.models.services import ServiceTypeModel, ServiceMode

# Register your models here.


admin.site.register(Account)
admin.site.register(PatientModel)
admin.site.register(ServiceTypeModel)
admin.site.register(ServiceMode)