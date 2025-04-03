from django import forms
from core.models import ServiceModel, ServiceTypeModel

class ServiceTypeForm(forms.ModelForm):
    class Meta:
        model = ServiceTypeModel
        fields = ['type']
        labels = {
            'type': 'Тип услуги'
        }
        widgets = {
            'type': forms.TextInput(attrs={'class': 'form-control'})
        }

class ServiceForm(forms.ModelForm):
    class Meta:
        model = ServiceModel
        fields = ['type', 'name', 'price']
        labels = {
            'type': 'Тип услуги',
            'name': 'Название',
            'price': 'Цена'
        }
        widgets = {
            'type': forms.Select(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control'})
        }