from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import MinValueValidator
import uuid
from django.db.models.signals import post_save
from django.dispatch import receiver

class Restaurant(models.Model):
    CUISINE_CHOICES = [
        ('korean','Korean'),
        ('italian', 'Italian'),
        ('japanese','Japanese'),
        ('mexican','Mexican'),
        ('chinese', 'Chinese'),
        ('thai', 'Thai'),
        ('spanish','Spanish'),
        ('indian', 'Indian'),
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
    # Instead of directly using ManyToManyField, we'll access items through OrderItem
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    total_price = models.DecimalField(max_digits=8, decimal_places=2, default=0.00, editable=False)
    discount_applied = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    coupon = models.ForeignKey(Coupon, null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.skip_price_calculation = False

    def save(self, *args, **kwargs):
        # Calculate total price if we're not skipping calculation
        if not hasattr(self, 'skip_price_calculation') or not self.skip_price_calculation:
            calculated_total = self.calculate_total
            if calculated_total > 0:
                self.total_price = calculated_total
            
        if not self.user and not self.guest_id:
            self.guest_id = uuid.uuid4()
        super().save(*args, **kwargs)
        
    @property
    def calculate_total(self):
        """Calculate current total from order items"""
        total = sum(item.quantity * item.menu_item.price for item in self.items.all())
        return total if total > 0 else 0  # Ensure we never return None or negative

    def apply_coupon(self):
        if self.coupon and self.coupon.is_valid():
            # Recalculate total price first to ensure it's up to date
            total = sum(
                order_item.quantity * order_item.menu_item.price 
                for order_item in self.items.all()
            )
            self.total_price = total
            
            # Calculate discount
            discount_amount = (self.total_price * self.coupon.discount_percentage) / 100
            self.discount_applied = discount_amount
            
            # Set the skip_price_calculation flag to avoid recalculating in save()
            self.skip_price_calculation = True
            self.save()
            # Reset the flag after saving
            self.skip_price_calculation = False

    def __str__(self):
        return f"Order {self.id} by {self.user if self.user else 'Guest'}"

    @property
    def get_total_items(self):
        """Return the total number of items in this order"""
        return sum(item.quantity for item in self.items.all())

    @property
    def get_order_items(self):
        """Return all order items for this order"""
        return self.items.all()

    @property
    def get_total_after_discount(self):
        """Return the total price after applying any discounts"""
        total = self.calculate_total  # Use calculated total instead of stored total_price
        if self.coupon and self.coupon.is_valid():
            return total - self.discount_applied
        return total


class OrderItem(models.Model):
    """Model for individual items in an order with quantity"""
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1, validators=[MinValueValidator(1)])
    
    def __str__(self):
        return f"{self.quantity} × {self.menu_item.name}"
    
    @property
    def name(self):
        """Return the name of the menu item for template convenience"""
        return self.menu_item.name
    
    @property
    def price(self):
        """Return the price of this line item (price × quantity)"""
        return self.menu_item.price * self.quantity
    
    @property
    def description(self):
        """Return the menu item description for template convenience"""
        return self.menu_item.description


class Review(models.Model):
    """Model for customer reviews of restaurants"""
    RATING_CHOICES = [
        (1, '1 - Poor'),
        (2, '2 - Fair'),
        (3, '3 - Good'),
        (4, '4 - Very Good'),
        (5, '5 - Excellent'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, 
                           related_name='reviews')
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, 
                                 related_name='reviews')
    name = models.CharField(max_length=100, blank=True, help_text="Name for non-logged in users")
    rating = models.IntegerField(choices=RATING_CHOICES, default=5)
    review_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        
    def __str__(self):
        return f"Review for {self.restaurant.name} by {self.get_reviewer_name()}"
    
    def get_reviewer_name(self):
        """Return the name of the reviewer, prioritizing user name if available"""
        if self.user:
            return self.user.username
        return self.name or "Anonymous"
    
    @property
    def star_rating(self):
        """Return a string of stars representing the rating"""
        return '★' * self.rating + '☆' * (5 - self.rating)
