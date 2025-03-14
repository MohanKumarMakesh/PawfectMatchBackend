from django.urls import path
from .views import get_dogs, add_dog

urlpatterns = [
    path('dogs/', get_dogs, name='get_dogs'),
    path('dogs/add/', add_dog, name='add_dog'),
]
