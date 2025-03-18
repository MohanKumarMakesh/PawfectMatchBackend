from django.urls import path
from .views import get_dogs, add_dog, delete_dog

urlpatterns = [
    path('dogs/', get_dogs, name='get_dogs'),
    path('dogs/add/', add_dog, name='add_dog'),
    path('dogs/delete/<int:dog_id>/', delete_dog, name='delete_dog')
]
