from django.contrib import admin
from core.models import *
from core.models.services import ServiceTypeModel, ServiceModel

# Register your models here.


admin.site.register(Account)
admin.site.register(PatientModel)
admin.site.register(ServiceTypeModel)
admin.site.register(ServiceModel)
admin.site.register(PaymentModel)
admin.site.register(SessionModel)
