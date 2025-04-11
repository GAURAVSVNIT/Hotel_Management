from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from .models import Restaurant

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
    return render(request, 'main/restaurant_list.html', {'restaurants': restaurants})

def restaurant_detail(request, restaurant_id):
    restaurant = get_object_or_404(Restaurant, id=restaurant_id)
    return render(request, 'main/restaurant_detail.html', {'restaurant': restaurant})

@login_required
def place_order(request, restaurant_id):
    restaurant = get_object_or_404(Restaurant, id=restaurant_id)
    # For now, just redirect to restaurant detail page
    messages.info(request, 'Order placement will be implemented soon!')
    return redirect('restaurant_detail', restaurant_id=restaurant_id)
