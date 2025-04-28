from django.urls import path
from . import views

urlpatterns = [
    # Other URL patterns
    path('capture-emotion/', views.capture_emotion, name='capture_emotion'),
]