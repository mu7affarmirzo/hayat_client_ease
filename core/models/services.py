from django.db import models

from core.models import Account


class ServiceTypeModel(models.Model):
    type = models.CharField(max_length=100)

    created_by = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    modified_by = models.ForeignKey(
        Account, related_name="modf_service_type_by_user",
        on_delete=models.SET_NULL, null=True, blank=True
    )

    def __str__(self):
        return str(self.type)


class ServiceMode(models.Model):
    type = models.ForeignKey(ServiceTypeModel, on_delete=models.SET_NULL, null=True, blank=True, related_name='services')
    name = models.CharField(max_length=255)

    price = models.DecimalField(max_digits=10, decimal_places=2)

    created_by = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    modified_by = models.ForeignKey(
        Account, related_name="modf_service_by_user",
        on_delete=models.SET_NULL, null=True, blank=True
    )

    def __str__(self):
        return str(self.name)
