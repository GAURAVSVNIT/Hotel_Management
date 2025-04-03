from django import forms
from .models import Coupon

class CouponApplyForm(forms.Form):
    code = forms.CharField(max_length=20, label="Coupon Code")
