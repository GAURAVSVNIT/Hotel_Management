from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.validators import RegexValidator, EmailValidator
from .models import Coupon, Review
class LoginForm(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-orange-500 focus:ring-orange-500',
            'placeholder': 'Username'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-orange-500 focus:ring-orange-500',
            'placeholder': 'Password'
        })
    )
    user_type = forms.ChoiceField(
        choices=[('customer', 'Customer'), ('owner', 'Restaurant Owner')],
        widget=forms.RadioSelect(attrs={
            'class': 'form-radio text-orange-600'
        }),
        initial='customer'
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = "Username"
        self.fields['password'].label = "Password"
        self.fields['user_type'].label = "Login as"

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
            'class': 'form-input border p-2 rounded',
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

    username = forms.CharField(
        max_length=150,
        label="Choose a Username",
        widget=forms.TextInput(attrs={
            'class': 'form-input border p-2 rounded',
            'placeholder': 'Create a username for login'
        })
    )

    password = forms.CharField(
        label="Choose a Password",
        widget=forms.PasswordInput(attrs={
            'class': 'form-input border p-2 rounded',
            'placeholder': 'Create a secure password'
        })
    )

    confirm_password = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(attrs={
            'class': 'form-input border p-2 rounded',
            'placeholder': 'Enter password again'
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
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', "Passwords do not match.")
            
        # Call the original clean method's logic for other fields
        # (e.g., cuisine type validation)
        cuisine_type = cleaned_data.get('cuisine_type')
        other_cuisine = cleaned_data.get('other_cuisine')
        
        # Validate other cuisine field if 'other' is selected
        if cuisine_type == 'other' and not other_cuisine:
            self.add_error('other_cuisine', "Please specify the cuisine type.")
            
        return cleaned_data

class ReviewForm(forms.Form):
    """Form for submitting restaurant reviews"""
    rating = forms.ChoiceField(
        label="Rating",
        choices=Review.RATING_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-select border p-2 rounded'
        })
    )
    
    review_text = forms.CharField(
        label="Your Review",
        widget=forms.Textarea(attrs={
            'class': 'form-textarea border p-2 rounded',
            'placeholder': 'Share your experience with this restaurant...',
            'rows': 5
        })
    )
    
    name = forms.CharField(
        label="Your Name (optional if logged in)",
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-input border p-2 rounded',
            'placeholder': 'Enter your name'
        })
    )
    
    def clean_review_text(self):
        review_text = self.cleaned_data.get('review_text')
        if len(review_text.strip()) < 10:
            raise forms.ValidationError("Please provide a more detailed review (minimum 10 characters)")
        return review_text
