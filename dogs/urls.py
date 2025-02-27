from django.urls import path
from .views import get_dogs

urlpatterns = [
    path('dogs/', get_dogs, name='get_dogs'),
]
