from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', auth_views.LoginView.as_view(template_name='main/login.html'), name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register, name='register'),
    path('restaurants/', views.restaurant_list, name='restaurant_list'),
    path('restaurants/<int:restaurant_id>/', views.restaurant_detail, name='restaurant_detail'),
    path('restaurants/<int:restaurant_id>/order/', views.place_order, name='place_order'),
    path('orders/', views.order_history, name='order_history'),
    path('orders/<int:order_id>/', views.order_summary, name='order_summary'),
    path('orders/<int:order_id>/checkout/', views.checkout, name='checkout'),
    path('menu/', views.menu_view, name='menu'),
]

# Add media serving in development
# Note: In production, media files should be served by a proper web server
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
