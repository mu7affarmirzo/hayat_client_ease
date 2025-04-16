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


class WithdrawalPaymentForm(forms.ModelForm):
    """Form for processing refunds/withdrawals when clients don't use all sessions"""
    amount = forms.IntegerField(
        min_value=1,  # Ensure the displayed amount is positive
        label="Сумма возврата",
        help_text="Введите положительное значение, система автоматически обработает его как возврат"
    )

    class Meta:
        model = PaymentModel
        fields = ['method', 'amount']

    def save(self, commit=True):
        """Convert positive input amount to negative for database storage"""
        instance = super().save(commit=False)

        # Make sure the amount is stored as negative for withdrawals
        instance.amount = -abs(instance.amount)

        if commit:
            instance.save()
        return instance
