# forms.py
from django import forms
from core.models import PaymentModel, SessionBookingModel, Account


class PaymentFilterForm(forms.Form):
    """Form for filtering payments in the dashboard"""

    PAYMENT_TYPE_CHOICES = [
        ('', 'All'),
        ('payment', 'Payments Only'),
        ('withdrawal', 'Withdrawals Only'),
    ]

    start_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control',
        }),
        label='Start Date'
    )

    end_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control',
        }),
        label='End Date'
    )

    method = forms.ChoiceField(
        required=False,
        choices=[('', 'All Methods')] + PaymentModel.method.field.choices,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Payment Method'
    )

    payment_type = forms.ChoiceField(
        required=False,
        choices=PAYMENT_TYPE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Payment Type'
    )

    min_amount = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Minimum amount'
        }),
        label='Min Amount'
    )

    max_amount = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Maximum amount'
        }),
        label='Max Amount'
    )

    patient_search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search by patient name or phone'
        }),
        label='Patient Search'
    )

    created_by = forms.ModelChoiceField(
        required=False,
        queryset=Account.objects.filter(created_payments__isnull=False).distinct(),
        empty_label='All Users',
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Created By'
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Update created_by queryset to only show users who have created payments
        self.fields['created_by'].queryset = Account.objects.filter(
            created_payments__isnull=False
        ).distinct().order_by('username')


class PaymentCreateForm(forms.ModelForm):
    """Form for creating new payments"""

    class Meta:
        model = PaymentModel
        fields = ['session', 'amount', 'method']
        widgets = {
            'session': forms.Select(attrs={
                'class': 'form-control',
                'required': True,
            }),
            'amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'required': True,
                'step': '1',
                'placeholder': 'Enter amount (use negative for refunds)'
            }),
            'method': forms.Select(attrs={
                'class': 'form-control',
                'required': True,
            }),
        }
        labels = {
            'session': 'Session',
            'amount': 'Amount (сум)',
            'method': 'Payment Method',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Order sessions by most recent first
        self.fields['session'].queryset = SessionBookingModel.objects.select_related(
            'patient'
        ).order_by('-created_at')

        # Customize session display
        self.fields['session'].empty_label = 'Select a session'

    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if amount == 0:
            raise forms.ValidationError('Amount cannot be zero.')
        return amount


class PaymentEditForm(forms.ModelForm):
    """Form for editing existing payments"""

    class Meta:
        model = PaymentModel
        fields = ['amount', 'method']
        widgets = {
            'amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'required': True,
                'step': '1',
            }),
            'method': forms.Select(attrs={
                'class': 'form-control',
                'required': True,
            }),
        }
        labels = {
            'amount': 'Amount (сум)',
            'method': 'Payment Method',
        }

    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if amount == 0:
            raise forms.ValidationError('Amount cannot be zero.')
        return amount


class DateRangeForm(forms.Form):
    """Simple form for date range selection (used in analytics)"""

    start_date = forms.DateField(
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control',
        }),
        label='Start Date'
    )

    end_date = forms.DateField(
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control',
        }),
        label='End Date'
    )

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')

        if start_date and end_date and start_date > end_date:
            raise forms.ValidationError('Start date must be before end date.')

        return cleaned_data