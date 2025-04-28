import cv2
import numpy as np
import json
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import base64
from .models import CustomerRating

# Load pre-trained models for face detection and emotion recognition
def load_models():
    # Face detection model - comes with OpenCV
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    
    # For emotion recognition, we'll use a simpler approach
    # In a production environment, you'd want to download and use a dedicated emotion recognition model
    # For example, a pre-trained FER (Facial Emotion Recognition) model
    
    return face_cascade

# Function for emotion detection and rating conversion
def detect_emotion_and_rate(image):
    """
    Detect emotions in an image and convert to a 5-star rating using OpenCV
    
    Args:
        image: OpenCV image
        
    Returns:
        tuple: (rating, dominant_emotion, emotion_scores)
    """
    try:
        # Convert to grayscale for face detection
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Load face detection model
        face_cascade = load_models()
        
        # Detect faces
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)
        
        if len(faces) == 0:
            # No face detected
            return 3, "unknown", {"neutral": 100}
        
        # For simplicity, we'll analyze the largest face (closest to camera)
        largest_face = sorted(faces, key=lambda x: x[2] * x[3], reverse=True)[0]
        x, y, w, h = largest_face
        
        # Extract face region
        face_roi = gray[y:y+h, x:x+w]
        
        # In a real implementation, you would feed this face to an emotion recognition model
        # For this example, we'll use a mock "analysis" based on simple image properties
        # This is just a placeholder - you'd replace this with a proper model
        
        # Simple brightness-based mock analysis (not a real emotion detector)
        brightness = np.mean(face_roi)
        
        # Mock emotion mapping based on brightness
        # This is just a demonstration - in a real scenario, use a proper emotion model
        if brightness > 150:
            dominant_emotion = "happy"
            emotion_scores = {"happy": 70, "neutral": 20, "surprised": 10}
            rating = 5
        elif brightness > 125:
            dominant_emotion = "neutral"
            emotion_scores = {"neutral": 60, "happy": 30, "surprised": 10}
            rating = 4
        elif brightness > 100:
            dominant_emotion = "neutral"
            emotion_scores = {"neutral": 80, "sad": 15, "angry": 5}
            rating = 3
        elif brightness > 75:
            dominant_emotion = "sad"
            emotion_scores = {"sad": 60, "neutral": 30, "angry": 10}
            rating = 2
        else:
            dominant_emotion = "angry"
            emotion_scores = {"angry": 70, "sad": 20, "neutral": 10}
            rating = 1
        
        # In a real implementation, you would:
        # 1. Use a proper facial emotion recognition model (like FER2013 model)
        # 2. Get real emotion probabilities from the model
        # 3. Map these to appropriate star ratings
            
        return rating, dominant_emotion, emotion_scores
        
    except Exception as e:
        print(f"Error in emotion detection: {e}")
        return 3, "unknown", {"neutral": 100}  # Default to neutral/3 stars if detection fails

@csrf_exempt
def capture_emotion(request):
    """View to receive image data, analyze emotion, and store rating"""
    if request.method == 'GET':
        return render(request, 'ratings/capture_emotion.html')
        
    if request.method == 'POST':
        try:
            # Get image data from POST request
            image_data = request.POST.get('image_data')
            table_number = request.POST.get('table_number')
            
            # Convert base64 image to OpenCV format
            image_data = image_data.split(',')[1] if ',' in image_data else image_data
            image_bytes = base64.b64decode(image_data)
            np_arr = np.frombuffer(image_bytes, np.uint8)
            img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
            
            # Detect emotion and get rating
            rating, dominant_emotion, emotion_scores = detect_emotion_and_rate(img)
            
            # Store in database
            emotion_rating = CustomerRating(
                rating=rating,
                dominant_emotion=dominant_emotion,
                emotion_scores=emotion_scores,
                table_number=int(table_number) if table_number else None
            )
            emotion_rating.save()
            
            return JsonResponse({
                'success': True,
                'rating': rating,
                'dominant_emotion': dominant_emotion,
                'emotion_scores': emotion_scores
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=400)
