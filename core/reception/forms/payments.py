from django import forms
from core.models import PaymentModel


class SingularPaymentCreateSerializer(forms.ModelForm):

    class Meta:
        model = PaymentModel
        fields = [
            'method', 'amount'
        ]


class WholePaymentCreateSerializer(forms.ModelForm):

    class Meta:
        model = PaymentModel
        fields = [
            'method'
        ]
