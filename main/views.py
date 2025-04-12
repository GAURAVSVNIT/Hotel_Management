from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.http import HttpResponseBadRequest
from .models import Restaurant, MenuItem, Order, Coupon
def home(request):
    return render(request, 'main/home.html')

def logout_view(request):
    """
    Custom logout view that handles both GET and POST requests.
    """
    logout(request)
    return redirect('home')

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}. You can now log in.')
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'main/register.html', {'form': form})

def restaurant_list(request):
    restaurants = Restaurant.objects.all()
    
    # Handle cuisine filtering
    cuisine = request.GET.get('cuisine')
    if cuisine:
        restaurants = restaurants.filter(cuisine=cuisine)
    
    context = {
        'restaurants': restaurants,
        'cuisines': Restaurant.CUISINE_CHOICES,
        'selected_cuisine': cuisine
    }
    return render(request, 'main/restaurant_list.html', context)

def restaurant_detail(request, restaurant_id):
    restaurant = get_object_or_404(Restaurant, id=restaurant_id)
    menu_items = restaurant.menu_items.all()
    return render(request, 'main/restaurant_detail.html', {
        'restaurant': restaurant,
        'menu_items': menu_items
    })
@login_required
def place_order(request, restaurant_id):
    restaurant = get_object_or_404(Restaurant, id=restaurant_id)
    
    if request.method == 'POST':
        # First, check if there are any items to add
        items_to_add = []
        for key, value in request.POST.items():
            if key.startswith('quantity_') and int(value) > 0:
                item_id = key.replace('quantity_', '')
                try:
                    menu_item = MenuItem.objects.get(id=item_id)
                    items_to_add.append(menu_item)
                except MenuItem.DoesNotExist:
                    pass
        
        if items_to_add:
            # Create and save the order first to get an ID
            order = Order(
                user=request.user,
                restaurant=restaurant,
                status='Pending'
            )
            # Save without calculating total price yet
            order.skip_price_calculation = True
            order.save()
            
            # Now add items to the many-to-many relationship
            order.items.add(*items_to_add)
            
            # Calculate the total price and save again
            order.skip_price_calculation = False
            order.save()
            
            messages.success(request, f'Your order from {restaurant.name} has been placed.')
            return redirect('order_summary', order_id=order.id)
        else:
            messages.warning(request, 'Please select at least one item to place an order.')
            return redirect('restaurant_detail', restaurant_id=restaurant_id)
    
    # If not POST, redirect to restaurant detail page
    return redirect('restaurant_detail', restaurant_id=restaurant_id)

@login_required
def order_summary(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    # Apply coupon if provided
    if request.method == 'POST' and 'code' in request.POST:
        coupon_code = request.POST.get('code')
        try:
            coupon = Coupon.objects.get(code=coupon_code, is_active=True)
            if coupon.is_valid():
                order.coupon = coupon
                order.apply_coupon()
                messages.success(request, f'Coupon {coupon_code} applied successfully!')
            else:
                messages.error(request, 'This coupon has expired.')
        except Coupon.DoesNotExist:
            messages.error(request, 'Invalid coupon code.')
        
        return redirect('order_summary', order_id=order.id)
    
    return render(request, 'main/order_summary.html', {'order': order})

@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'main/order_history.html', {'orders': orders})

@login_required
def checkout(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    if request.method == 'POST':
        # Simple simulation of payment processing
        # In a real application, you would integrate with a payment gateway here
        
        # Update order status
        order.status = 'Preparing'
        order.save()
        
        messages.success(request, 'Payment successful! Your order is being prepared.')
        return redirect('order_history')
    
    return render(request, 'main/checkout.html', {'order': order})

def menu_view(request):
    """
    View that shows all menu items from all restaurants in one place.
    Allows filtering by restaurant and cuisine.
    """
    # Get all restaurants for filtering dropdown
    restaurants = Restaurant.objects.all()
    
    # Handle restaurant and cuisine filtering
    restaurant_id = request.GET.get('restaurant')
    cuisine = request.GET.get('cuisine')
    
    # Start with all menu items
    menu_items = MenuItem.objects.select_related('restaurant').all()
    
    # Apply restaurant filter
    if restaurant_id:
        try:
            restaurant = Restaurant.objects.get(id=restaurant_id)
            menu_items = menu_items.filter(restaurant=restaurant)
            filtered_restaurant = restaurant
        except Restaurant.DoesNotExist:
            filtered_restaurant = None
    else:
        filtered_restaurant = None
    
    # Apply cuisine filter
    if cuisine:
        menu_items = menu_items.filter(restaurant__cuisine=cuisine)
    
    # Group menu items by restaurant
    menu_by_restaurant = {}
    for item in menu_items:
        if item.restaurant not in menu_by_restaurant:
            menu_by_restaurant[item.restaurant] = []
        menu_by_restaurant[item.restaurant].append(item)
    
    context = {
        'menu_by_restaurant': menu_by_restaurant,
        'restaurants': restaurants,
        'cuisines': Restaurant.CUISINE_CHOICES,
        'filtered_restaurant': filtered_restaurant,
        'selected_cuisine': cuisine
    }
    return render(request, 'main/menu.html', context)
