from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Main routes
    path('', views.home, name='home'),
    path('restaurants/', views.restaurant_list, name='restaurant_list'),
    path('restaurants/<int:id>/', views.restaurant_detail, name='restaurant_detail'),
    path('menu/', views.menu_view, name='menu'),
    
    # Authentication routes
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register, name='register'),
    path('profile/', views.user_profile, name='user_profile'),
    
    # Order routes
    path('order-history/', views.order_history, name='order_history'),
    path('place-order/<int:restaurant_id>/', views.place_order, name='place_order'),
    path('order-summary/<int:order_id>/', views.order_summary, name='order_summary'),
    path('checkout/<int:order_id>/', views.checkout, name='checkout'),
    
    # Marketing and information pages
    path('reviews/', views.reviews, name='reviews'),
    path('demo/', views.demo, name='demo'),
    path('for-restaurants/', views.for_restaurants, name='for_restaurants'),
    path('get-started/', views.get_started, name='get_started'),
    path('schedule-demo/', views.schedule_demo, name='schedule_demo'),
    path('contact/', views.contact, name='contact'),
    path('aboutus/', views.aboutus, name='aboutus'),
    
    # Owner routes
    path('owner/dashboard/', views.owner_dashboard, name='owner_dashboard'),
    path('owner/menu/edit/', views.owner_menu_edit, name='owner_menu_edit'),
    path('owner/orders/', views.owner_orders, name='owner_orders'),
    path('owner/settings/', views.owner_settings, name='owner_settings'),
]

# Password reset URLs
urlpatterns += [
    path('password_reset/', auth_views.PasswordResetView.as_view(
        template_name='main/password/password_reset.html',
        email_template_name='main/password/password_reset_email.html',
        subject_template_name='main/password/password_reset_subject.txt'
    ), name='password_reset'),
    
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='main/password/password_reset_done.html'
    ), name='password_reset_done'),
    
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='main/password/password_reset_confirm.html'
    ), name='password_reset_confirm'),
    
    path('checkout/<int:order_id>/', views.checkout, name='checkout'),
    path('orders/<int:order_id>/review/', views.submit_review, name='submit_review'),
    
    # Marketing and information pages
]

# Add media serving in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
