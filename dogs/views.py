import io
import logging
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import permission_classes
from PIL import Image
import boto3
from django.conf import settings
from .models import Dog
from .serializers import DogSerializer

# Set up logging
logger = logging.getLogger(__name__)


@api_view(['GET'])
def get_dogs(request):
    dogs = Dog.objects.all()
    print("Dogs:", dogs)
    serializer = DogSerializer(dogs, many=True)
    dogs_with_user = [
        {**dog, "user_id": dog["user"]} for dog in serializer.data
    ]
    return Response(dogs_with_user, status=status.HTTP_200_OK)


@api_view(['POST'])
def add_dog(request):
    image = request.FILES.get('image')
    if not image:
        return Response({"error": "Image is required"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        if image.size > (1024 * 1024):  # Check if image size is greater than 1 MB
            img = Image.open(image)
            output = io.BytesIO()
            img.save(output, format='JPEG', quality=85)
            output.seek(0)
            image = output

        # Upload image to S3
        s3 = boto3.client('s3')
        s3.upload_fileobj(
            image, settings.AWS_STORAGE_BUCKET_NAME, f'dogs/{image.name}')
        image_url = f'https://{settings.AWS_S3_CUSTOM_DOMAIN}/dogs/{image.name}'
        logger.info(f"Image URL: {image_url}")

        # Add image URL and user to request data
        request.data['image'] = image_url
        user_id = request.data.get('user')  # Access the user field from request.data
        if not user_id:
            return Response({"error": "User is required"}, status=status.HTTP_400_BAD_REQUEST)
        request.data['user'] = user_id

        # Validate data
        serializer = DogSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            # Fetch the updated list of dogs
            dogs = Dog.objects.all()
            print("Dogs:", dogs)
            updated_serializer = DogSerializer(dogs, many=True)
            return Response(updated_serializer.data, status=status.HTTP_201_CREATED)
        else:
            # Remove the uploaded image from S3 if data is not valid
            s3.delete_object(
                Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=f'dogs/{image.name}')
            logger.error(f"Serializer errors: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.error(f"Error uploading image: {str(e)}")
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@api_view(['PUT'])
@permission_classes([IsAuthenticated])  # Ensure the user is authenticated
def update_dog(request, dog_id):
    try:
        # Fetch the dog object and ensure it belongs to the authenticated user
        dog = Dog.objects.get(id=dog_id, user=request.user)

        # Update the dog's details
        data = request.data
        if 'name' in data:
            dog.name = data['name']
        if 'image' in request.FILES:
            # Delete the old image from S3 if it exists
            if dog.image:
                s3 = boto3.client('s3')
                s3.delete_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME,
                                 Key=f'dogs/{dog.image.split("/")[-1]}')

            # Upload the new image to S3
            image = request.FILES['image']
            s3.upload_fileobj(
                image, settings.AWS_STORAGE_BUCKET_NAME, f'dogs/{image.name}')
            dog.image = f'https://{settings.AWS_S3_CUSTOM_DOMAIN}/dogs/{image.name}'

        dog.save()
        serializer = DogSerializer(dog)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Dog.DoesNotExist:
        return Response({"error": "Dog not found or you do not have permission to update this dog"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Error updating dog: {str(e)}")
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])  # Ensure the user is authenticated
def delete_dog(request, dog_id):
    try:
        # Check if the user is authenticated
        if not request.user.is_authenticated:
            return Response({"error": "Authentication required"}, status=status.HTTP_401_UNAUTHORIZED)

        # Fetch the dog object and ensure it belongs to the authenticated user
        dog = Dog.objects.get(id=dog_id, user=request.user)
        
        # Delete the image from S3
        s3 = boto3.client('s3')
        s3.delete_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME,
                         Key=f'dogs/{dog.image.split("/")[-1]}')
        dog.delete()
        return Response({"message": "Dog and image deleted successfully"}, status=status.HTTP_200_OK)
    except Dog.DoesNotExist:
        return Response({"error": "Dog not found or you do not have permission to delete this dog"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Error deleting dog: {str(e)}")
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
