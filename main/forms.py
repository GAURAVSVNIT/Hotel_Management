from django import forms
from .models import Coupon

class CouponApplyForm(forms.Form):
    code = forms.CharField(
        max_length=20,
        label="Coupon Code",
        required=False,  # Allow orders without a coupon
        widget=forms.TextInput(attrs={
            'class': 'form-input border p-2 rounded',  # Tailwind-friendly
            'placeholder': 'Enter coupon code (if any)'
        })
    )
