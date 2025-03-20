from django.urls import path
from .views import get_dogs, add_dog, delete_dog, update_dog  # Import the new update_dog view

urlpatterns = [
    path('dogs/', get_dogs, name='get_dogs'),
    path('dogs/add/', add_dog, name='add_dog'),
    path('dogs/update/<int:dog_id>/', update_dog, name='update_dog'),  # New endpoint

    path('dogs/delete/<int:dog_id>/', delete_dog, name='delete_dog')
]
