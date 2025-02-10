from django.db import models
from django.db.models import Sum
from django.utils import timezone

from core.models import PatientModel, ServiceModel, Account


class SessionModel(models.Model):
    patient = models.ForeignKey(PatientModel, on_delete=models.CASCADE, related_name="sessions")
    massage = models.ForeignKey(ServiceModel, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    discount = models.PositiveIntegerField(default=0, blank=True, null=True)
    total_price = models.PositiveIntegerField(default=0, blank=True, null=True)
    pre_discount_price = models.PositiveIntegerField(default=0, blank=True, null=True)
    is_paid = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    created_by = models.ForeignKey(Account, on_delete=models.SET_NULL, blank=True, null=True, related_name="created_sessions")
    updated_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_by = models.ForeignKey(Account, on_delete=models.SET_NULL, blank=True, null=True, related_name="updated_sessions")

    def save(self, *args, **kwargs):
        # Calculate total price before saving
        self.total_price = int((self.massage.price * self.quantity) * (100 - self.discount)/100)
        self.pre_discount_price = self.massage.price * self.quantity
        super().save(*args, **kwargs)

    @property
    def overall_payed_amount(self):
        return self.payments.aggregate(total=Sum('amount'))['total']

    def __str__(self):
        return f"{self.patient.full_name} - {self.massage.name} ({self.quantity})"

    class Meta:
        ordering = ['-created_at']


class PaymentModel(models.Model):
    session = models.ForeignKey(SessionModel, on_delete=models.CASCADE, related_name="payments")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    method = models.CharField(max_length=50, choices=[("наличка", "Наличка"), ("карта", "Карта"), ("online", "Online")])

    created_at = models.DateTimeField(auto_now_add=True, null=True)
    created_by = models.ForeignKey(Account, on_delete=models.SET_NULL, blank=True, null=True,
                                   related_name="created_payments")
    updated_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_by = models.ForeignKey(Account, on_delete=models.SET_NULL, blank=True, null=True,
                                   related_name="updated_payments")

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.update_session_payment_status()

    def update_session_payment_status(self):
        total_paid = self.session.payments.aggregate(total=models.Sum('amount'))['total'] or 0
        if total_paid >= self.session.total_price:
            self.session.is_paid = True
            self.session.save()

    def __str__(self):
        return f"Payment of {self.amount} for {self.session.patient.full_name}"

