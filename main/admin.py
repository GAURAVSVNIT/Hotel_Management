from django.contrib import admin
from .models import Restaurant, MenuItem, Order, Coupon

@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    list_display = ("name", "location")  # Display more details in the list view
    search_fields = ("name", "location")  # Enable search by name & location
    list_filter = ("location",)  # Add a location filter

@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ("name", "restaurant", "price")  # Show restaurant name in the list
    search_fields = ("name", "restaurant__name")  # Allow searching menu items by name or restaurant
    list_filter = ("restaurant",)  # Filter by restaurant

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "restaurant", "total_price", "status", "created_at")
    search_fields = ("id", "user__username", "restaurant__name")  # Allow searching orders by ID, user, or restaurant
    list_filter = ("status", "restaurant")  # Add filters for order status and restaurant
    readonly_fields = ("total_price", "discount_applied", "created_at")  # Prevent manual edits

@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ("code", "discount_percentage", "valid_from", "valid_to", "is_active")
    search_fields = ("code",)
    list_filter = ("is_active",)

# @admin.register(Owner)
# class OwnerAdmin(admin.ModelAdmin):
#     list_display = ("user", "restaurant", "phone_number")  # Added phone_number for more detail
#     search_fields = ("user__username", "restaurant__name", "phone_number")  # Allow searching by phone number too
#     list_filter = ("restaurant",)  # Filter by restaurant
#     # readonly_fields removed to allow selection of user and restaurant
