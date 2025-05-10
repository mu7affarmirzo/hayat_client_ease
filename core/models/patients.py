import datetime

from django.db import models

from core.models import Account


class PatientModel(models.Model):
    f_name = models.CharField(max_length=255)
    mid_name = models.CharField(max_length=255, null=True, blank=True)
    l_name = models.CharField(max_length=255)
    email = models.EmailField(null=True, blank=True)
    date_of_birth = models.DateField(auto_now=False)
    home_phone_number = models.CharField(max_length=255, blank=True, null=True)
    mobile_phone_number = models.CharField(max_length=255, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    country = models.CharField(max_length=255, blank=True, null=True)
    last_visit_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    modified_by = models.ForeignKey(Account, related_name="modf_patient_by_user", on_delete=models.SET_NULL, null=True, blank=True)
    gender = models.BooleanField()

    @property
    def age(self):
        return datetime.date.today().year - self.date_of_birth.year

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
            try:
                mid_name = self.mid_name
            except:
                mid_name = ''

            return f"{self.f_name} {self.l_name} {mid_name}"
        except:
            return ""

    def __str__(self):

        try:
            mid_name = self.mid_name
        except:
            mid_name = ''

        return f"{self.f_name} {self.l_name} {mid_name}"

    class Meta:
        ordering = ('-created_at', )