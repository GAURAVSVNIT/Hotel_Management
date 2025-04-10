from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Home & Authentication
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='main/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),

    # Restaurant & Menu
    path('restaurants/', views.restaurant_list, name='restaurant_list'),
    path('restaurant/<int:restaurant_id>/', views.restaurant_detail, name='restaurant_detail'),
    #path('menu/', views.menu_view, name='menu_without_restaurant'),  # Allows accessing menu without restaurant_id
    path('restaurant/<int:restaurant_id>/menu/', views.menu_view, name='menu'),
    

    # Ordering System
    path('restaurant/<int:restaurant_id>/order/', views.place_order, name='place_order'),
    #path('order/', views.place_order, name='order_without_restaurant'),  # Allows placing orders without a restaurant
    path('orders/', views.order_history, name='order_history'),
    path('order/<int:order_id>/', views.order_summary, name='order_summary'),

    # Password Reset
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
]