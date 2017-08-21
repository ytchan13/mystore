from django import forms

from .models import OrderInfo


class OrderInfoForm(forms.ModelForm):
    class Meta:
        model = OrderInfo
        fields = ['billing_name', 'billing_address', 'shipping_name', 'shipping_address']