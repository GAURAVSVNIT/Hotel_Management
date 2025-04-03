from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from .models import Restaurant, Order, MenuItem, Coupon
from django.contrib.auth.decorators import login_required
from .forms import CouponApplyForm
from django.contrib import messages

# Create your views here.

def home(request):
    return render(request, 'main/home.html')

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Automatically login after registration
            return redirect('home')
    else:
        form = UserCreationForm()
    
    return render(request, 'main/register.html', {'form': form})

def restaurant_list(request):
    restaurants = Restaurant.objects.all()
    return render(request, 'main/restaurant_list.html', {'restaurants': restaurants})

def restaurant_detail(request, restaurant_id):
    restaurant = get_object_or_404(Restaurant, id=restaurant_id)
    return render(request, 'main/restaurant_detail.html', {'restaurant': restaurant})

@login_required
def place_order(request, restaurant_id):
    if request.method == "POST":
        restaurant = Restaurant.objects.get(id=restaurant_id)
        item_ids = request.POST.getlist("items")  # Get selected menu items
        items = MenuItem.objects.filter(id__in=item_ids)
        total_price = sum(item.price for item in items)

        order = Order.objects.create(
            user=request.user,
            restaurant=restaurant,
            total_price=total_price,
        )
        order.items.set(items)
        order.save()

        messages.success(request, "Order placed successfully!")
        return redirect("order_history")  # Redirect to order history page

    return redirect("menu", restaurant_id=restaurant_id)

@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'main/order_history.html', {'orders': orders})

def order_summary(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    if order.user and order.user != request.user:
        return redirect('restaurant_list')

    form = CouponApplyForm(request.POST or None)
    
    if request.method == 'POST' and form.is_valid():
        code = form.cleaned_data['code']
        try:
            coupon = Coupon.objects.get(code=code, is_active=True)
            if coupon.is_valid():
                order.coupon = coupon
                order.apply_coupon()
                messages.success(request, f"Coupon '{coupon.code}' applied! Discount: {coupon.discount_percentage}%")
            else:
                messages.error(request, "Coupon expired or invalid.")
        except Coupon.DoesNotExist:
            messages.error(request, "Invalid coupon code.")

    return render(request, 'main/order_summary.html', {'order': order, 'form': form})


def menu_view(request):
    # Get the first restaurant (temporary fix)
    restaurant = Restaurant.objects.first()  

    if not restaurant:
        return render(request, "main/menu.html", {"error": "No restaurant found."})

    menu_items = MenuItem.objects.filter(restaurant=restaurant)

    return render(request, "main/menu.html", {"menu_items": menu_items, "restaurant": restaurant})