from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth.models import User  # Import User model
from django.db import IntegrityError, transaction # For database transactions
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum, Avg
from django.db.models import Count, Sum, Avg
from django.db.models.functions import TruncDate
from .models import Restaurant, MenuItem, Coupon, Order, OrderItem, Review, Owner
from .forms import LoginForm, RegisterForm, CouponApplyForm, ContactForm, RestaurantSignupForm, ReviewForm

# Validation utility functions
def is_valid_email(email):
    """
    Validate email format using regex pattern.
    
    Args:
        email (str): Email address to validate
        
    Returns:
        bool: True if email format is valid, False otherwise
    """
    if not email or not isinstance(email, str):
        return False
    
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def is_valid_phone(phone):
    """
    Validate phone number format.
    
    Args:
        phone (str): Phone number to validate
        
    Returns:
        bool: True if phone format is valid, False otherwise
    """
    if not phone or not isinstance(phone, str):
        return False
    
    # Remove common separators and spaces
    digits = ''.join(c for c in phone if c.isdigit())
    
    # Most countries have phone numbers between 8 and 15 digits
    return 8 <= len(digits) <= 15

def home(request):
    """Home page view"""
    try:
        return render(request, 'main/home.html')
    except Exception as e:
        messages.error(request, f'Error loading home page: {str(e)}')
        return render(request, 'main/home.html')

def restaurant_list(request):
    """Display list of all restaurants"""
    try:
        restaurants = Restaurant.objects.all()
        context = {
            'restaurants': restaurants
        }
        return render(request, 'main/restaurant_list.html', context)
    except Exception as e:
        messages.error(request, f'Error loading restaurants: {str(e)}')
        return redirect('home')

def restaurant_detail(request, id):
    """Display details of a specific restaurant"""
    try:
        restaurant = get_object_or_404(Restaurant, id=id)
        menu_items = MenuItem.objects.filter(restaurant=restaurant)
        context = {
            'restaurant': restaurant,
            'menu_items': menu_items
        }
        return render(request, 'main/restaurant_detail.html', context)
    except Exception as e:
        messages.error(request, f'Error loading restaurant details: {str(e)}')
        return redirect('restaurant_list')

def menu_view(request):
    """Display menu items with filtering options"""
    try:
        # Get all restaurants for filter dropdown
        restaurants = Restaurant.objects.all()
        
        # Get filter parameters
        restaurant_id = request.GET.get('restaurant')
        cuisine = request.GET.get('cuisine')
        
        # Start with all menu items
        menu_items = MenuItem.objects.select_related('restaurant').all()
        
        # Apply filters if provided
        filtered_restaurant = None
        if restaurant_id:
            try:
                filtered_restaurant = Restaurant.objects.get(id=restaurant_id)
                menu_items = menu_items.filter(restaurant=filtered_restaurant)
            except Restaurant.DoesNotExist:
                messages.warning(request, "Restaurant not found.")
        
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
    except Exception as e:
        messages.error(request, f'Error loading menu: {str(e)}')
        return redirect('home')

# Authentication views
def login_view(request):
    """Handle user login with user type verification"""
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            # Get the user type from form (fixed in 2025-04-29 to correctly handle 'customer' and 'owner')
            user_type = form.cleaned_data.get('user_type')
            user = authenticate(username=username, password=password)
            
            if user is not None:
                # Check if user type matches
                is_owner = Owner.objects.filter(user=user).exists()
                
                if user_type == 'owner' and not is_owner:
                    messages.error(request, 'This account is not registered as a restaurant owner.')
                    return render(request, 'main/login.html', {'form': form})
                elif user_type == 'customer' and is_owner:
                    messages.error(request, 'Please login as an owner with this account.')
                    return render(request, 'main/login.html', {'form': form})
                
                login(request, user)
                messages.success(request, f'Welcome back, {username}!')
                
                # Redirect based on user type
                if user_type == 'owner':
                    return redirect('owner_dashboard')
                return redirect('home')
            else:
                messages.error(request, 'Invalid username or password.')
    else:
        form = LoginForm()
    return render(request, 'main/login.html', {'form': form})

def register(request):
    """Handle user registration"""
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}! You can now log in.')
            return redirect('login')
    else:
        form = RegisterForm()
    return render(request, 'main/register.html', {'form': form})

def logout_view(request):
    """Handle user logout"""
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('home')

@login_required
def user_profile(request):
    """Display and update user profile information"""
    try:
        # Get recent orders for the user (limit to 5)
        recent_orders = Order.objects.filter(user=request.user).order_by('-created_at')[:5]
        
        # Get user's reviews if any
        user_reviews = Review.objects.filter(user=request.user).select_related('restaurant').order_by('-created_at')[:3]
        
        # Handle profile update form submission
        if request.method == 'POST':
            # Get form data
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            email = request.POST.get('email')
            
            # Validate inputs
            if email and not is_valid_email(email):
                messages.error(request, 'Please provide a valid email address.')
            else:
                # Update user profile
                request.user.first_name = first_name
                request.user.last_name = last_name
                if email:
                    request.user.email = email
                request.user.save()
                
                messages.success(request, 'Profile updated successfully!')
                return redirect('user_profile')
        
        context = {
            'user': request.user,
            'recent_orders': recent_orders,
            'user_reviews': user_reviews,
        }
        
        return render(request, 'main/user_profile.html', context)
    except Exception as e:
        messages.error(request, f'Error loading profile: {str(e)}')
        return redirect('home')

# Order management views
@login_required
def place_order(request, restaurant_id):
    """Handle placing a new order"""
    try:
        restaurant = get_object_or_404(Restaurant, id=restaurant_id)
        
        if request.method == 'POST':
            # Process items from the form
            items_to_add = []
            total_items = 0
            
            for key, value in request.POST.items():
                if key.startswith('quantity_'):
                    try:
                        quantity = int(value)
                        if quantity < 0:
                            messages.error(request, 'Invalid quantity specified.')
                            return redirect('restaurant_detail', id=restaurant_id)
                        elif quantity > 0:
                            item_id = key.replace('quantity_', '')
                            try:
                                menu_item = MenuItem.objects.get(id=item_id, restaurant=restaurant)
                                items_to_add.append((menu_item, quantity))
                                total_items += quantity
                            except MenuItem.DoesNotExist:
                                messages.error(request, f'Menu item not found or not available in this restaurant.')
                                return redirect('restaurant_detail', id=restaurant_id)
                    except ValueError:
                        messages.error(request, 'Invalid quantity format.')
                        return redirect('restaurant_detail', id=restaurant_id)
            
            # Check if order is empty or too large
            if not items_to_add:
                messages.warning(request, 'Please select at least one item to place an order.')
                return redirect('restaurant_detail', id=restaurant_id)
            
            if total_items > 50:  # Set a reasonable maximum order size
                messages.error(request, 'Order quantity exceeds maximum limit.')
                return redirect('restaurant_detail', id=restaurant_id)
            
            if items_to_add:
                # Create the order
                order = Order(
                    user=request.user,
                    restaurant=restaurant,
                    status='Pending'
                )
                # Set skip_price_calculation for initial save since we don't have items yet
                order.skip_price_calculation = True
                order.save()
                
                # Add items to the order
                for menu_item, quantity in items_to_add:
                    OrderItem.objects.create(
                        order=order,
                        menu_item=menu_item,
                        quantity=quantity
                    )
                
                # Now calculate the total with all items
                order.skip_price_calculation = False
                order.save()  # This will trigger total calculation in save()
                
                messages.success(request, f'Your order from {restaurant.name} has been placed.')
                return redirect('order_summary', order_id=order.id)
            else:
                messages.warning(request, 'Please select at least one item to place an order.')
        
        return redirect('restaurant_detail', id=restaurant_id)
    except Exception as e:
        messages.error(request, f'Error placing order: {str(e)}')
        return redirect('restaurant_detail', id=restaurant_id)

@login_required
def order_summary(request, order_id):
    """Display order summary and handle coupon application"""
    try:
        order = get_object_or_404(Order, id=order_id, user=request.user)
        
        # Handle coupon application
        if request.method == 'POST' and 'code' in request.POST:
            coupon_code = request.POST.get('code')
            try:
                coupon = Coupon.objects.get(code=coupon_code, is_active=True)
                # In a real app, you'd check if coupon is valid
                order.coupon = coupon
                order.save()
                messages.success(request, f'Coupon {coupon_code} applied successfully!')
            except Coupon.DoesNotExist:
                messages.error(request, 'Invalid coupon code.')
            return redirect('order_summary', order_id=order.id)
        
        return render(request, 'main/order_summary.html', {'order': order})
    except Exception as e:
        messages.error(request, f'Error viewing order summary: {str(e)}')
        return redirect('order_history')

# Marketing and information pages
def demo(request):
    """Demo page showing how the QR code menu system works"""
    try:
        return render(request, 'main/demo.html')
    except Exception as e:
        messages.error(request, f'Error loading demo page: {str(e)}')
        return redirect('home')

def for_restaurants(request):
    """Information page for restaurant owners"""
    try:
        return render(request, 'main/for_restaurants.html')
    except Exception as e:
        messages.error(request, f'Error loading restaurant information: {str(e)}')
        return redirect('home')

def get_started(request):
    """Sign-up page for restaurant owners, creates User, Restaurant, Owner"""
    try:
        if request.method == 'POST':
            form = RestaurantSignupForm(request.POST)
            if form.is_valid():
                # Get form data
                data = form.cleaned_data
                
                # -- START: Implement Object Creation --
                try:
                    # Use a transaction to ensure all objects are created or none are
                    with transaction.atomic():
                        # 1. Create the User account
                        new_user = User.objects.create_user(
                            username=data['username'],
                            password=data['password'],
                            email=data['email'],
                            # Add owner's name if desired
                            first_name=data['owner_name'].split(' ')[0] if data['owner_name'] else '',
                            last_name=' '.join(data['owner_name'].split(' ')[1:]) if ' ' in data['owner_name'] else '',
                        )

                        # 2. Create the Restaurant
                        # Determine cuisine - handle 'other'
                        cuisine = data['cuisine_type']
                        if cuisine == 'other':
                            cuisine = data.get('other_cuisine', 'Other') # Use specified or default to 'Other'

                        new_restaurant = Restaurant.objects.create(
                            name=data['restaurant_name'],
                            location=f"{data['address']}, {data['city']}", # Combine address/city
                            cuisine=cuisine,
                            # description can be added later if needed
                        )

                        # 3. Create the Owner profile and link User and Restaurant
                        new_owner = Owner.objects.create(
                            user=new_user,
                            restaurant=new_restaurant,
                            phone_number=data['phone'],
                            # address is now stored in Restaurant, could duplicate if needed
                        )

                    # Send confirmation emails, create CRM tasks etc. (Placeholder)
                    # send_owner_confirmation_email(new_user.email, new_restaurant.name)
                    # notify_sales_team(new_restaurant.name)

                    messages.success(request, f'Restaurant "{new_restaurant.name}" and owner account "{new_user.username}" created! You can now log in.')
                    return redirect('login') # Redirect to login after successful signup

                except IntegrityError as e:
                    # Handle case where username might already exist
                    if 'auth_user_username_key' in str(e) or 'UNIQUE constraint failed: auth_user.username' in str(e):
                         form.add_error('username', 'This username is already taken. Please choose another.')
                    else:
                         messages.error(request, f'An unexpected database error occurred: {str(e)}')
                    # Re-render form with errors
                    return render(request, 'main/get_started.html', {'form': form})
                except Exception as e:
                     # Catch any other unexpected errors during creation
                     messages.error(request, f'An error occurred during signup: {str(e)}')
                     return render(request, 'main/get_started.html', {'form': form})
                # -- END: Implement Object Creation --
        else:
            form = RestaurantSignupForm()
            
        return render(request, 'main/get_started.html', {'form': form})
    except Exception as e:
        messages.error(request, f'Error loading signup page: {str(e)}')
        return redirect('home')

def schedule_demo(request):
    """Handle scheduling a demonstration for potential restaurant clients"""
    try:
        if request.method == 'POST':
            # Process form data
            restaurant_name = request.POST.get('restaurant_name')
            contact_name = request.POST.get('contact_name')
            email = request.POST.get('email')
            phone = request.POST.get('phone')
            preferred_date = request.POST.get('preferred_date')
            preferred_time = request.POST.get('preferred_time')
            notes = request.POST.get('notes', '')
            
            # Validate inputs
            if not restaurant_name or not contact_name or not email or not phone or not preferred_date or not preferred_time:
                messages.error(request, 'Please fill in all required fields.')
                return redirect('schedule_demo')
            
            if not is_valid_email(email):
                messages.error(request, 'Please provide a valid email address.')
                return redirect('schedule_demo')
                
            if not is_valid_phone(phone):
                messages.error(request, 'Please provide a valid phone number.')
                return redirect('schedule_demo')
            
            # Database operations in a production environment would include:
            # 1. Create DemoRequest record
            #    - Store restaurant information
            #    - Contact details
            #    - Requested date/time
            #    - Special requirements
            # 2. Check staff availability for requested time
            #    - Query calendar/scheduling system
            #    - Reserve time slot if available
            # 3. Send confirmation email to restaurant
            #    - Meeting details (time, date, format)
            #    - Calendar invitation (.ics attachment)
            #    - Preparation instructions
            # 4. Create internal notification
            #    - Alert assigned sales representative
            #    - Add to demo calendar
            
            messages.success(request, 'Demo scheduled successfully! We will send you a confirmation email shortly.')
            return redirect('home')
        
        # Add today's date for the date input min attribute
        context = {
            'today': timezone.now().date()
        }
        return render(request, 'main/schedule_demo.html', context)
    except Exception as e:
        messages.error(request, f'Error scheduling demo: {str(e)}')
        return redirect('home')
def contact(request):
    """Contact page with form handling"""
    try:
        if request.method == 'POST':
            form = ContactForm(request.POST)
            if form.is_valid():
                # Form is valid, get the cleaned data
                data = form.cleaned_data
                
                # Database operations in a production environment would include:
                # 1. Create ContactMessage record
                #    - Store sender details and message content
                #    - Assign unique reference number
                #    - Set initial status (unread, pending)
                # 2. Send confirmation email to user
                #    - Include reference number for follow-up
                #    - Expected response time
                # 3. Create notification for support team
                #    - Add to support queue
                #    - Send email alert to support staff
                # 4. Log interaction in CRM system
                #    - Link to existing customer record if applicable
                #    - Create new prospect record if new contact
                
                messages.success(request, 'Message sent successfully! We will get back to you soon.')
                return redirect('home')
        else:
            form = ContactForm()
            
        return render(request, 'main/contact.html', {'form': form})
    except Exception as e:
        messages.error(request, f'Error sending message: {str(e)}')
        return redirect('home')

def reviews(request):
    """Display a paginated list of reviews from all restaurants"""
    try:
        # Get filter parameter for restaurant
        restaurant_id = request.GET.get('restaurant')
        
        # Start with all reviews
        reviews_list = Review.objects.select_related('restaurant', 'user').all()
        
        # Apply filter if provided
        filtered_restaurant = None
        if restaurant_id:
            try:
                filtered_restaurant = Restaurant.objects.get(id=restaurant_id)
                reviews_list = reviews_list.filter(restaurant=filtered_restaurant)
            except Restaurant.DoesNotExist:
                messages.warning(request, "Restaurant not found.")
        
        # Get all restaurants for filter dropdown
        restaurants = Restaurant.objects.all()
        
        # Pagination
        page = request.GET.get('page', 1)
        paginator = Paginator(reviews_list, 5)  # Show 5 reviews per page
        
        try:
            reviews = paginator.page(page)
        except PageNotAnInteger:
            reviews = paginator.page(1)
        except EmptyPage:
            reviews = paginator.page(paginator.num_pages)
            
        context = {
            'reviews': reviews,
            'restaurants': restaurants,
            'filtered_restaurant': filtered_restaurant
        }
        
        return render(request, 'main/reviews.html', context)
    except Exception as e:
        messages.error(request, f'Error loading reviews: {str(e)}')
        return redirect('home')

@login_required
def order_history(request):
    """Display the order history for the logged-in user"""
    try:
        # Get all orders for the current user, ordered by most recent first
        orders = Order.objects.filter(user=request.user).order_by('-created_at')
        
        context = {
            'orders': orders
        }
        return render(request, 'main/order_history.html', context)
    except Exception as e:
        messages.error(request, f'Error retrieving order history: {str(e)}')
        return redirect('home')

@login_required
def checkout(request, order_id):
    """Process payment and checkout for an order"""
    try:
        order = get_object_or_404(Order, id=order_id, user=request.user)
        
        # Force recalculation of total
        order.skip_price_calculation = False
        order.save()
        
        # Check if order is already completed
        if order.status == 'Completed':
            messages.info(request, 'This order has already been processed.')
            return redirect('order_history')
            
        if request.method == 'POST':
            # Process payment (mock implementation for demo)
            payment_method = request.POST.get('payment_method')
            
            if not payment_method:
                messages.error(request, 'Please select a payment method.')
                return redirect('checkout', order_id=order.id)
                
            # In a real application, you would:
            # 1. Validate payment details
            # 2. Process payment through a payment gateway
            # 3. Handle success/failure responses
            # 4. Update order status based on payment result
            
            # Mock successful payment for demo
            order.status = 'Completed'
            order.save()
            
            messages.success(request, 'Payment successful! Your order has been confirmed.')
            return redirect('order_history')
            
        context = {
            'order': order
        }
        return render(request, 'main/checkout.html', context)
    except Exception as e:
        messages.error(request, f'Error during checkout: {str(e)}')
        return redirect('order_history')

@login_required
def owner_dashboard(request):
    """Dashboard view for restaurant owners"""
    try:
        # Verify the user is an owner
        owner = get_object_or_404(Owner, user=request.user)
        restaurant = owner.restaurant
        
        # Calculate statistics directly with querysets
        total_orders = Order.objects.filter(restaurant=restaurant).count()
        
        # Calculate total revenue from completed orders
        revenue_result = Order.objects.filter(
            restaurant=restaurant,
            status='Completed'
        ).aggregate(
            total=Sum('total_price')
        )
        total_revenue = revenue_result['total'] or 0
        
        # Calculate average rating
        rating_result = Review.objects.filter(
            restaurant=restaurant
        ).aggregate(
            avg=Avg('rating')
        )
        average_rating = rating_result['avg'] or 0
        
        # Get recent orders for the restaurant
        recent_orders = Order.objects.filter(
            restaurant=restaurant
        ).order_by('-created_at')[:5]
        
        # Get recent reviews
        recent_reviews = Review.objects.filter(
            restaurant=restaurant
        ).order_by('-created_at')[:3]
        
        # Get best-selling items
        bestsellers = OrderItem.objects.filter(
            order__restaurant=restaurant,
            order__status='Completed'
        ).values(
            'menu_item__name'
        ).annotate(
            total_ordered=Count('id')
        ).order_by('-total_ordered')[:5]
        
        # Get daily orders for current month
        daily_orders = Order.objects.filter(
            restaurant=restaurant,
            created_at__month=timezone.now().month
        ).annotate(
            date=TruncDate('created_at')
        ).values('date').annotate(
            count=Count('id'),
            revenue=Sum('total_price')
        ).order_by('-date')[:30]
        
        context = {
            'owner': owner,
            'restaurant': restaurant,
            'total_orders': total_orders,
            'total_revenue': total_revenue,
            'average_rating': average_rating,
            'recent_orders': recent_orders,
            'recent_reviews': recent_reviews,
            'bestsellers': bestsellers,
            'daily_orders': daily_orders,
            # Add statistics for the dashboard
            'stats': {
                'pending_orders': Order.objects.filter(restaurant=restaurant, status='Pending').count(),
                'completed_orders': Order.objects.filter(restaurant=restaurant, status='Completed').count(),
                'menu_items': MenuItem.objects.filter(restaurant=restaurant).count(),
                'total_reviews': restaurant.reviews.count(),
            }
        }
        return render(request, 'main/owner_dashboard.html', context)
    except Owner.DoesNotExist:
        # Redirect to login page with appropriate message
        messages.warning(request, 'Owner profile not found for this user. Please log in with an owner account.') 
        return redirect('login')
    except Exception as e:
        # Print the actual exception to the console for debugging
        import traceback
        print(f"!!! ERROR IN OWNER DASHBOARD VIEW: {type(e).__name__} - {e}")
        traceback.print_exc()
        messages.error(request, 'An unexpected error occurred while loading the dashboard. Please try again.')
        return redirect('home')
    
def aboutus(request):
    try:
        return render(request, 'main/aboutus.html')
    except Exception as e:
        messages.error(request, f'Error loading about us page: {str(e)}')
        return render(request, 'main/aboutus.html')
    
@login_required
def owner_menu_edit(request):
    """View for restaurant owners to edit their menu items"""
    try:
        # Verify the user is an owner
        owner = get_object_or_404(Owner, user=request.user)
        restaurant = owner.restaurant
        
        if request.method == 'POST':
            action = request.POST.get('action')
            
            if action == 'add':
                # Add new menu item
                name = request.POST.get('name')
                price = request.POST.get('price')
                description = request.POST.get('description')
                image = request.FILES.get('image')
                
                if name and price:
                    try:
                        MenuItem.objects.create(
                            restaurant=restaurant,
                            name=name,
                            price=price,
                            description=description,
                            image=image if image else None
                        )
                        messages.success(request, 'Menu item added successfully!')
                    except ValueError:
                        messages.error(request, 'Invalid price format.')
                else:
                    messages.error(request, 'Please provide both name and price.')
            
            elif action == 'edit':
                # Edit existing menu item
                item_id = request.POST.get('item_id')
                item = get_object_or_404(MenuItem, id=item_id, restaurant=restaurant)
                
                name = request.POST.get('name')
                price = request.POST.get('price')
                description = request.POST.get('description')
                image = request.FILES.get('image')
                
                if name and price:
                    try:
                        item.name = name
                        item.price = price
                        item.description = description
                        if image:
                            item.image = image
                        item.save()
                        messages.success(request, 'Menu item updated successfully!')
                    except ValueError:
                        messages.error(request, 'Invalid price format.')
                else:
                    messages.error(request, 'Please provide both name and price.')
            
            elif action == 'delete':
                # Delete menu item
                item_id = request.POST.get('item_id')
                item = get_object_or_404(MenuItem, id=item_id, restaurant=restaurant)
                item.delete()
                messages.success(request, 'Menu item deleted successfully!')
            
            return redirect('owner_menu_edit')
        
        # Get all menu items for this restaurant
        menu_items = MenuItem.objects.filter(restaurant=restaurant)
        
        context = {
            'restaurant': restaurant,
            'menu_items': menu_items,
        }
        return render(request, 'main/owner_menu_edit.html', context)
    except Exception as e:
        messages.error(request, 'An error occurred while managing menu items.')
        return redirect('owner_dashboard')

@login_required
def owner_orders(request):
    """View for restaurant owners to manage their orders"""
    try:
        # Verify the user is an owner
        owner = get_object_or_404(Owner, user=request.user)
        restaurant = owner.restaurant
        
        if request.method == 'POST':
            order_id = request.POST.get('order_id')
            new_status = request.POST.get('status')
            
            if order_id and new_status:
                order = get_object_or_404(Order, id=order_id, restaurant=restaurant)
                if new_status in [status[0] for status in Order.STATUS_CHOICES]:
                    order.status = new_status
                    order.save()
                    messages.success(request, f'Order #{order.id} status updated to {new_status}')
                else:
                    messages.error(request, 'Invalid status selected.')
            return redirect('owner_orders')
        
        # Get orders with optional filters
        status_filter = request.GET.get('status')
        date_filter = request.GET.get('date')
        
        orders = Order.objects.filter(restaurant=restaurant)
        
        if status_filter:
            orders = orders.filter(status=status_filter)
        if date_filter:
            orders = orders.filter(created_at__date=date_filter)
            
        orders = orders.order_by('-created_at')
        
        context = {
            'restaurant': restaurant,
            'orders': orders,
            'status_choices': Order.STATUS_CHOICES,
            'current_status': status_filter,
        }
        return render(request, 'main/owner_orders.html', context)
    except Exception as e:
        messages.error(request, 'An error occurred while managing orders.')
        return redirect('owner_dashboard')

@login_required
def owner_settings(request):
    """View for restaurant owners to manage their restaurant settings"""
    try:
        # Verify the user is an owner
        owner = get_object_or_404(Owner, user=request.user)
        restaurant = owner.restaurant
        
        if request.method == 'POST':
            # Update restaurant information
            name = request.POST.get('name')
            location = request.POST.get('location')
            description = request.POST.get('description')
            cuisine = request.POST.get('cuisine')
            image = request.FILES.get('image')
            phone = request.POST.get('phone')
            
            if name and location and cuisine:
                restaurant.name = name
                restaurant.location = location
                restaurant.description = description
                restaurant.cuisine = cuisine
                if image:
                    restaurant.image = image
                restaurant.save()
                
                if phone:
                    owner.phone_number = phone
                    owner.save()
                
                messages.success(request, 'Restaurant settings updated successfully!')
            else:
                messages.error(request, 'Please fill in all required fields.')
            
            return redirect('owner_settings')
        
        context = {
            'owner': owner,
            'restaurant': restaurant,
            'cuisine_choices': Restaurant.CUISINE_CHOICES,
        }
        return render(request, 'main/owner_settings.html', context)
    except Exception as e:
        messages.error(request, 'An error occurred while updating settings.')
        return redirect('owner_dashboard')

@login_required
def submit_review(request, order_id):
    """Handle submission of restaurant reviews after order completion"""
    try:
        # Get the order and verify it belongs to the current user
        order = get_object_or_404(Order, id=order_id, user=request.user)
        
        # Check if order is completed
        if order.status != 'Completed':
            messages.error(request, 'You can only review completed orders.')
            return redirect('order_summary', order_id=order.id)
        
        # Check if order has already been reviewed
        if order.has_been_reviewed:
            messages.info(request, 'You have already reviewed this order.')
            return redirect('order_summary', order_id=order.id)
        
        # Get the restaurant from the order
        restaurant = order.restaurant
        
        if request.method == 'POST':
            form = ReviewForm(request.POST)
            if form.is_valid():
                # Create and save the review
                review = Review(
                    user=request.user,
                    restaurant=restaurant,
                    rating=form.cleaned_data['rating'],
                    review_text=form.cleaned_data['review_text']
                )
                
                # Add name if provided (shouldn't be needed for logged-in users but just in case)
                if 'name' in form.cleaned_data and form.cleaned_data['name']:
                    review.name = form.cleaned_data['name']
                    
                review.save()
                
                # Mark the order as reviewed
                order.has_been_reviewed = True
                order.save()
                
                messages.success(request, 'Thank you for your review!')
                return redirect('order_history')
        else:
            # Initialize the form
            form = ReviewForm()
        
        context = {
            'form': form,
            'order': order,
            'restaurant': restaurant
        }
        return render(request, 'main/review_form.html', context)
    except Exception as e:
        messages.error(request, f'Error submitting review: {str(e)}')
        return redirect('order_history')
