from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from .models import Restaurant, Order, MenuItem, Coupon
from django.contrib.auth.decorators import login_required
from .forms import CouponApplyForm
from django.contrib import messages

def home(request):
    return render(request, 'main/home.html')

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Auto-login after registration
            return redirect('home')
    else:
        form = UserCreationForm()
    
    return render(request, 'main/register.html', {'form': form})

def restaurant_list(request):
    restaurants = Restaurant.objects.all()  # Get all fields
    return render(request, 'main/restaurant_list.html', {'restaurants': restaurants})

def restaurant_detail(request, restaurant_id):
    restaurant = get_object_or_404(Restaurant, id=restaurant_id)
    return render(request, 'main/restaurant_detail.html', {'restaurant': restaurant})

@login_required
def place_order(request, restaurant_id):
    restaurant = get_object_or_404(Restaurant, id=restaurant_id)

    if request.method == "POST":
        # Find all items with quantities > 0
        selected_items = []
        total_price = 0
        
        # Look for all quantity inputs in the form
        for key, value in request.POST.items():
            if key.startswith('quantity_') and int(value) > 0:
                item_id = key.split('_')[1]
                quantity = int(value)
                
                try:
                    menu_item = MenuItem.objects.get(id=item_id)
                    selected_items.append((menu_item, quantity))
                    total_price += menu_item.price * quantity
                except MenuItem.DoesNotExist:
                    continue
        
        if not selected_items:
            messages.error(request, "Please select at least one item to place an order.")
            return redirect("menu", restaurant_id=restaurant_id)
            
        try:
            # Create the order with pre-calculated total price
            order = Order(
                user=request.user,
                restaurant=restaurant,
                total_price=total_price
            )
            # Save first to get an ID
            order.save()
            
            # Now add items to the order with a valid ID
            for item, quantity in selected_items:
                for _ in range(quantity):
                    order.items.add(item)
            
            messages.success(request, "Order placed successfully!")
            return redirect("order_history")
        except Exception as e:
            messages.error(request, f"Error placing order: {str(e)}")
            return redirect("menu", restaurant_id=restaurant_id)
    
    # If not POST, redirect to menu
    return redirect("menu", restaurant_id=restaurant_id)

@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'main/order_history.html', {'orders': orders})

@login_required
def order_summary(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)  # Secure lookup

    form = CouponApplyForm(request.POST or None)
    
    if request.method == 'POST' and form.is_valid():
        code = form.cleaned_data['code']
        try:
            coupon = Coupon.objects.get(code=code, is_active=True)
            if coupon.is_valid():
                order.coupon = coupon
                order.save()  # Save the order with the coupon first
                order.apply_coupon()  # Then apply the coupon
                messages.success(request, f"Coupon '{coupon.code}' applied! Discount: {coupon.discount_percentage}%")
            else:
                messages.error(request, "Coupon expired or invalid.")
        except Coupon.DoesNotExist:
            messages.error(request, "Invalid coupon code.")

    return render(request, 'main/order_summary.html', {'order': order, 'form': form})

def menu_view(request, restaurant_id):
    # Always expects a restaurant_id in the URL
    restaurant = get_object_or_404(Restaurant, id=restaurant_id)
    menu_items = restaurant.menu_items.all()

    return render(request, 'main/menu.html', {'restaurant': restaurant, 'menu_items': menu_items})

@login_required
def checkout(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    if request.method == 'POST':
        # Simple implementation - mark as paid
        order.status = 'Completed'
        order.save()
        messages.success(request, "Payment successful! Your order has been completed.")
        return redirect('order_history')
    
    return render(request, 'main/checkout.html', {'order': order})