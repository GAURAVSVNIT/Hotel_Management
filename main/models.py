from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import MinValueValidator
import uuid

class Restaurant(models.Model):
    CUISINE_CHOICES = [
        ('indian', 'Indian'),
        ('chinese', 'Chinese'),
        ('thai', 'Thai'),
        ('italian', 'Italian'),
    ]
    
    name = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to="restaurants/", blank=True, null=True)
    cuisine = models.CharField(
        max_length=20,
        choices=CUISINE_CHOICES,
        default='indian'
    )

    def __str__(self):
        return self.name

class MenuItem(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name="menu_items")
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.01)])
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to="menu_items/", blank=True, null=True)

    def __str__(self):
        return f"{self.name} - {self.restaurant.name}"

class Coupon(models.Model):
    code = models.CharField(max_length=20, unique=True, blank=True)
    discount_percentage = models.IntegerField(default=10)
    valid_from = models.DateTimeField()
    valid_to = models.DateTimeField()
    is_active = models.BooleanField(default=True)
        
    def save(self, *args, **kwargs):
        if not self.code:
            self.code = str(uuid.uuid4())[:8].upper()
        super().save(*args, **kwargs)
    
    def is_valid(self):
        now = timezone.now()
        return self.is_active and self.valid_from <= now <= self.valid_to

    def __str__(self):
        return f"{self.code} - {self.discount_percentage}%"

class Order(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Preparing', 'Preparing'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    guest_id = models.UUIDField(default=uuid.uuid4, editable=False, null=True, blank=True)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    items = models.ManyToManyField(MenuItem)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    total_price = models.DecimalField(max_digits=8, decimal_places=2, default=0.00, editable=False)
    discount_applied = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    coupon = models.ForeignKey(Coupon, null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.skip_price_calculation = False

    def save(self, *args, **kwargs):
        # Only calculate total price if we're not skipping price calculation
        if not hasattr(self, 'skip_price_calculation') or not self.skip_price_calculation:
            self.total_price = sum(item.price for item in self.items.all())
        if not self.user and not self.guest_id:
            self.guest_id = uuid.uuid4()
        super().save(*args, **kwargs)

    def apply_coupon(self):
        if self.coupon and self.coupon.is_valid():
            discount_amount = (self.total_price * self.coupon.discount_percentage) / 100
            self.discount_applied = discount_amount
            self.total_price -= discount_amount
            self.save()

    def __str__(self):
        return f"Order {self.id} by {self.user if self.user else 'Guest'}"
