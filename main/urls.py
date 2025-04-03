from django.urls import path
from . import views
from django.contrib.auth import views as auth_views # Built-in Django authentication views
from .views import menu_view

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='main/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    path('restaurants/', views.restaurant_list, name='restaurant_list'),
    path('restaurant/<int:restaurant_id>/', views.restaurant_detail, name='restaurant_detail'),
    path('restaurant/<int:restaurant_id>/order/', views.place_order, name='place_order'),
    path('orders/', views.order_history, name='order_history'),
    path('order/<int:order_id>/', views.order_summary, name='order_summary'),
    path('menu/', views.menu_view, name='menu'),
    path('place_order/<int:restaurant_id>/', views.place_order, name='place_order'),
]
