from django.db import models
from django.db.models import Sum
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _

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


class IndividualSessionModel(models.Model):
    """Model for tracking individual therapy sessions"""

    STATUS_CHOICES = (
        ('pending', _('Ожидает')),
        ('completed', _('Проведен')),
        ('canceled', _('Отменен')),
    )

    booking = models.ForeignKey('SessionBookingModel', on_delete=models.CASCADE,
                                related_name='individual_sessions',
                                verbose_name=_('Бронирование'))

    session_number = models.PositiveIntegerField(verbose_name=_('Номер сеанса'))

    status = models.CharField(max_length=20, choices=STATUS_CHOICES,
                              default='pending', verbose_name=_('Статус'))

    therapist = models.ForeignKey('TherapistModel', on_delete=models.SET_NULL,
                                  related_name='conducted_sessions', null=True, blank=True,
                                  verbose_name=_('Терапевт'))

    completed_at = models.DateTimeField(null=True, blank=True,
                                        verbose_name=_('Дата проведения'))

    notes = models.TextField(blank=True, null=True, verbose_name=_('Примечания'))

    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Создано'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Обновлено'))

    class Meta:
        ordering = ['session_number']
        verbose_name = _('Индивидуальный сеанс')
        verbose_name_plural = _('Индивидуальные сеансы')
        unique_together = ['booking', 'session_number']  # Ensure no duplicate session numbers

    def __str__(self):
        return f"{self.booking.patient.full_name} - Сеанс #{self.session_number}"


class SessionBookingModel(models.Model):
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
    session = models.ForeignKey(SessionBookingModel, on_delete=models.CASCADE, related_name="payments")
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


@receiver(post_save, sender=SessionBookingModel)
def create_individual_sessions(sender, instance, created, **kwargs):
    """
    Signal to create or update individual sessions when a booking is saved
    """

    # Get current number of individual sessions
    current_sessions = instance.individual_sessions.count()

    # If this is a new booking, create all sessions
    if created:
        for i in range(1, instance.quantity + 1):
            IndividualSessionModel.objects.create(
                booking=instance,
                session_number=i,
                therapist=instance.therapist,
                status='pending'
            )
        # Update proceeded_sessions to 0 (should already be 0, but just in case)
        instance.proceeded_sessions = 0
        instance.save(update_fields=['proceeded_sessions'])
        return

    # Handle existing booking with changed quantity
    if hasattr(instance, '_original_quantity') and instance._original_quantity != instance.quantity:
        # If quantity increased, add new sessions
        if instance.quantity > instance._original_quantity:
            for i in range(instance._original_quantity + 1, instance.quantity + 1):
                IndividualSessionModel.objects.create(
                    booking=instance,
                    session_number=i,
                    therapist=instance.therapist,
                    status='pending'
                )

        # If quantity decreased, remove excess sessions
        elif instance.quantity < instance._original_quantity:
            # Only remove sessions that haven't been completed
            for session in instance.individual_sessions.filter(
                    session_number__gt=instance.quantity
            ).order_by('-session_number'):
                if session.status != 'completed':
                    session.delete()
                else:
                    # If a completed session would be removed, adjust quantity to keep it
                    if instance.quantity < session.session_number:
                        instance.quantity = session.session_number
                        instance.save(update_fields=['quantity'])
                        break

    # Sync proceeded_sessions count with completed individual sessions
    completed_count = instance.proceeded_sessions
    if instance.proceeded_sessions != completed_count:
        instance.proceeded_sessions = completed_count
        instance.save(update_fields=['proceeded_sessions'])


# Signal for updating proceeded_sessions when an individual session is saved
@receiver(post_save, sender=IndividualSessionModel)
def update_booking_proceeded_sessions(sender, instance, **kwargs):
    """
    Update the proceeded_sessions count in the booking model
    when an individual session is saved
    """
    # Get the booking
    booking = instance.booking

    # Calculate the new count of completed sessions
    completed_count = booking.individual_sessions.filter(status='completed').count()

    # Update the booking's proceeded_sessions field if it's different
    if booking.proceeded_sessions != completed_count:
        booking.proceeded_sessions = completed_count
        # Use update_fields to avoid triggering other signals
        booking.save(update_fields=['proceeded_sessions'])


