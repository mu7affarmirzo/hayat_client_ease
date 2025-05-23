from django.contrib import admin
from core.models import *
from core.models.services import ServiceTypeModel, ServiceModel


admin.site.register(Account)
admin.site.register(PatientModel)
admin.site.register(ServiceTypeModel)
admin.site.register(ServiceModel)
# admin.site.register(PaymentModel)
admin.site.register(SessionBookingModel)
admin.site.register(IndividualSessionModel)
admin.site.register(RolesModel)
admin.site.register(AccountRoleModel)
admin.site.register(ReferralDoctorModel)
admin.site.register(TherapistModel)


class PaymentAdmin(admin.ModelAdmin):
    list_display = ['session', 'amount', 'method', 'created_at', 'created_by', 'updated_at', 'updated_by']


admin.site.register(PaymentModel, PaymentAdmin)

