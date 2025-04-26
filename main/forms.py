from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.validators import RegexValidator, EmailValidator
from .models import Coupon

class LoginForm(forms.Form):
    """Form for user login"""
    username = forms.CharField(
        max_length=150,
        label="Username",
        widget=forms.TextInput(attrs={
            'class': 'form-input border p-2 rounded',
            'placeholder': 'Enter your username'
        })
    )
    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={
            'class': 'form-input border p-2 rounded',
            'placeholder': 'Enter your password'
        })
    )

class RegisterForm(UserCreationForm):
    """Form for user registration extending Django's UserCreationForm"""
    email = forms.EmailField(
        max_length=254,
        help_text="Required. Enter a valid email address.",
        validators=[EmailValidator()],
        widget=forms.EmailInput(attrs={
            'class': 'form-input border p-2 rounded',
            'placeholder': 'Enter your email'
        })
    )
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add styling to the default UserCreationForm fields
        for fieldname in ['username', 'password1', 'password2']:
            self.fields[fieldname].widget.attrs.update({
                'class': 'form-input border p-2 rounded'
            })

class CouponApplyForm(forms.Form):
    """Form for applying coupon codes to orders"""
    code = forms.CharField(
        max_length=20,
        label="Coupon Code",
        required=False,  # Allow orders without a coupon
        widget=forms.TextInput(attrs={
            'class': 'form-input border p-2 rounded',  # Tailwind-friendly
            'placeholder': 'Enter coupon code (if any)'
        })
    )

class ContactForm(forms.Form):
    """Form for contact page"""
    name = forms.CharField(
        max_length=100,
        label="Your Name",
        widget=forms.TextInput(attrs={
            'class': 'form-input border p-2 rounded',
            'placeholder': 'Enter your name'
        })
    )
    email = forms.EmailField(
        label="Email Address",
        validators=[EmailValidator()],
        widget=forms.EmailInput(attrs={
            'class': 'form-input border p-2 rounded',
            'placeholder': 'Enter your email'
        })
    )
    subject = forms.CharField(
        max_length=200,
        label="Subject",
        widget=forms.TextInput(attrs={
            'class': 'form-input border p-2 rounded',
            'placeholder': 'Enter message subject'
        })
    )
    message = forms.CharField(
        label="Message",
        widget=forms.Textarea(attrs={
            'class': 'form-textarea border p-2 rounded',
            'placeholder': 'Enter your message',
            'rows': 5
        })
    )
    
    def clean_subject(self):
        subject = self.cleaned_data.get('subject')
        if len(subject.strip()) < 3:
            raise forms.ValidationError("Please provide a more descriptive subject line")
        return subject
        
    def clean_message(self):
        message = self.cleaned_data.get('message')
        if len(message.strip()) < 20:
            raise forms.ValidationError("Please provide a more detailed message (minimum 20 characters)")
        return message

class RestaurantSignupForm(forms.Form):
    """Form for restaurant owners to register"""
    restaurant_name = forms.CharField(
        max_length=255,
        label="Restaurant Name",
        widget=forms.TextInput(attrs={
            'class': 'form-input border p-2 rounded',
            'placeholder': 'Restaurant name'
        })
    )
    owner_name = forms.CharField(
        max_length=100,
        label="Owner Name",
        widget=forms.TextInput(attrs={
            'class': 'form-input border p-2 rounded',
            'placeholder': 'Your name'
        })
    )
    email = forms.EmailField(
        label="Email",
        validators=[EmailValidator()],
        widget=forms.EmailInput(attrs={
            'class': 'form-input border p-2 rounded',
            'placeholder': 'Contact email'
        })
    )
    phone = forms.CharField(
        max_length=20,
        label="Phone Number",
        validators=[
            RegexValidator(
                regex=r'^\+?1?\d{9,15}$',
                message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
            ),
        ],
        widget=forms.TextInput(attrs={
            'class': 'form-input border p-2 rounded',
            'placeholder': 'Phone number'
        })
    )
    address = forms.CharField(
        max_length=255,
        label="Restaurant Address",
        widget=forms.TextInput(attrs={
            'class': 'form-input border p-2 rounded',
            'placeholder': 'Restaurant address'
        })
    )
    city = forms.CharField(
        max_length=100,
        label="City",
        widget=forms.TextInput(attrs={
            'class': 'form-input border p-2 rounded',
            'placeholder': 'City'
        })
    )
    cuisine_type = forms.ChoiceField(
        label="Cuisine Type",
        choices=[
            ('korean', 'Korean'),
            ('italian', 'Italian'),
            ('japanese', 'Japanese'),
            ('mexican', 'Mexican'),
            ('chinese', 'Chinese'),
            ('thai', 'Thai'),
            ('spanish', 'Spanish'),
            ('indian', 'Indian'),
            ('other', 'Other (please specify)'),
        ],
        widget=forms.Select(attrs={
            'class': 'form-select border p-2 rounded'
        })
    )
    other_cuisine = forms.CharField(
        max_length=100,
        label="If Other, please specify",
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-input border p-2 rounded',
            'placeholder': 'Specify cuisine type'
        })
    )
    seating_capacity = forms.IntegerField(
        label="Seating Capacity",
        min_value=1,
        widget=forms.NumberInput(attrs={
            'class': 'form-input border p-2 rounded',
            'placeholder': 'Number of seats'
        })
    )
    subscription_plan = forms.ChoiceField(
        label="Subscription Plan",
        choices=[
            ('basic', 'Basic: QR Code Menu ($59/month)'),
            ('standard', 'Standard: QR Code Menu + Order Management ($99/month)'),
            ('premium', 'Premium: Full POS Integration ($149/month)'),
        ],
        widget=forms.RadioSelect(attrs={
            'class': 'form-radio'
        })
    )
    additional_info = forms.CharField(
        label="Additional Information",
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-textarea border p-2 rounded',
            'placeholder': 'Any additional information you would like to share',
            'rows': 3
        })
    )
    terms_accepted = forms.BooleanField(
        label="I agree to the Terms and Conditions",
        widget=forms.CheckboxInput(attrs={
            'class': 'form-checkbox'
        })
    )
    
    def clean(self):
        cleaned_data = super().clean()
        cuisine_type = cleaned_data.get('cuisine_type')
        other_cuisine = cleaned_data.get('other_cuisine')
        
        # Validate other cuisine field if 'other' is selected
        if cuisine_type == 'other' and not other_cuisine:
            self.add_error('other_cuisine', "Please specify the cuisine type.")
            
        return cleaned_data
