from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

class CustomerRating(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    rating = models.IntegerField()  # 1-5 stars
    dominant_emotion = models.CharField(max_length=20)
    emotion_scores = models.JSONField(default=dict)  # Store detailed emotion values
    table_number = models.IntegerField(null=True, blank=True)
    timestamp = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return f"Rating: {self.rating}/5 - {self.timestamp.strftime('%Y-%m-%d %H:%M')}"