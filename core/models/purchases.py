from django.db import models
from django.db.models import Sum
from django.utils import timezone
import datetime


from core.models import PatientModel, ServiceModel, Account, TherapistModel


class ReferralDoctorModel(models.Model):
    f_name = models.CharField(max_length=255)
    mid_name = models.CharField(max_length=255, null=True, blank=True)
    l_name = models.CharField(max_length=255)
    email = models.EmailField(null=True, blank=True)

    is_active = models.BooleanField(default=True)

    created_by = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    modified_by = models.ForeignKey(Account, related_name="modf_docs_by_user", on_delete=models.SET_NULL, null=True, blank=True)
    gender = models.BooleanField()

    rate = models.IntegerField(null=True, blank=True, default=15)

    @property
    def formatted_gender(self):
        return 'Мужской' if self.gender is True else 'Женскый'

    def to_result(self):
        return {
            'age': self.age,
            'name': self.full_name,
            'gender': self.gender
        }

    @property
    def full_name(self):
        try:
            mid_name = self.mid_name
        except:
            mid_name = ''

        return f"{self.f_name} {self.l_name} {mid_name}"

    def __str__(self):
        try:
            mid_name = self.mid_name
        except:
            mid_name = ''

        return f"{self.f_name} {self.l_name} {mid_name}"

    class Meta:
        ordering = ('-created_at',)


class SessionModel(models.Model):
    patient = models.ForeignKey(PatientModel, on_delete=models.SET_NULL, related_name="sessions", null=True, blank=True)
    massage = models.ForeignKey(ServiceModel, on_delete=models.SET_NULL, related_name="sessions", null=True, blank=True)
    therapist = models.ForeignKey(TherapistModel, on_delete=models.SET_NULL, related_name="sessions", null=True, blank=True)

    referral_doctor = models.ForeignKey(ReferralDoctorModel, on_delete=models.SET_NULL, related_name="sessions", null=True, blank=True)

    quantity = models.PositiveIntegerField(default=1, null=True, blank=True)
    proceeded_sessions = models.PositiveIntegerField(default=0, null=True, blank=True)

    discount = models.PositiveIntegerField(default=0, blank=True, null=True)
    start_date = models.DateTimeField(auto_now_add=True, null=True)

    total_price = models.PositiveIntegerField(default=0, blank=True, null=True)
    pre_discount_price = models.PositiveIntegerField(default=0, blank=True, null=True)
    is_paid = models.BooleanField(default=False)

    is_reported = models.BooleanField(default=False)

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
        try:
            return int(self.payments.aggregate(total=Sum('amount'))['total'])
        except:
            return 0

    @property
    def remaining_payed_amount(self):
        return int(self.total_price-self.overall_payed_amount)

    def __str__(self):
        return f"{self.patient.full_name} - {self.massage.name} ({self.quantity})"

    class Meta:
        ordering = ['-created_at']


class PaymentModel(models.Model):
    session = models.ForeignKey(SessionModel, on_delete=models.CASCADE, related_name="payments")
    amount = models.PositiveBigIntegerField(null=True, blank=True, default=0)
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

    class Meta:
        ordering = ('-created_at',)
