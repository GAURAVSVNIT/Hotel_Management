from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.home, name='home'),
    path('restaurants/', views.restaurant_list, name='restaurant_list'),
    path('restaurants/<int:id>/', views.restaurant_detail, name='restaurant_detail'),
    path('menu/', views.menu_view, name='menu'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register, name='register'),
    path('profile/', views.user_profile, name='user_profile'),
    path('order-history/', views.order_history, name='order_history'),
    path('place-order/<int:restaurant_id>/', views.place_order, name='place_order'),
    path('order-summary/<int:order_id>/', views.order_summary, name='order_summary'),
    path('checkout/<int:order_id>/', views.checkout, name='checkout'),
    
    # New routes for the updated website
    path('reviews/', views.reviews, name='reviews'),
    path('demo/', views.demo, name='demo'),
    path('for-restaurants/', views.for_restaurants, name='for_restaurants'),
    path('get-started/', views.get_started, name='get_started'),
    path('schedule-demo/', views.schedule_demo, name='schedule_demo'),
    path('contact/', views.contact, name='contact'),
]

# Add media serving in development
# Note: In production, media files should be served by a proper web server
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
