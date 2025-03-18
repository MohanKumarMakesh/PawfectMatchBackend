import io
import logging
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
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
    serializer = DogSerializer(dogs, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['POST'])
def add_dog(request):
    image = request.FILES.get('image')
    if not image:
        return Response({"error": "Image is required"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        if image.size > (1024 * 1024):  # Check if image size is greater than 1 MB
            img = Image.open(image)
<<<<<<< HEAD
            if img.size > (1024 * 1024):  # Check if image size is greater than 1 MB
                output = io.BytesIO()
                img.save(output, format='JPEG', quality=85)
                output.seek(0)
                image = output
            print(settings.AWS_STORAGE_BUCKET_NAME)
            s3 = boto3.client('s3')
            s3.upload_fileobj(
                image, settings.AWS_STORAGE_BUCKET_NAME, f'dogs/{image.name}')
            image_url = f'https://{settings.AWS_S3_CUSTOM_DOMAIN}/dogs/{image.name}'
            serializer.validated_data['image'] = image_url

        serializer.save()
        # Fetch the updated list of dogs
        dogs = Dog.objects.all()
        updated_serializer = DogSerializer(dogs, many=True)
        return Response(updated_serializer.data, status=status.HTTP_201_CREATED)
    else:
        logger.error(f"Serializer errors: {serializer.errors}")
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
=======
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
        request.data['user'] = request.user.id

        # Validate data
        serializer = DogSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            # Fetch the updated list of dogs
            dogs = Dog.objects.all()
            updated_serializer = DogSerializer(dogs, many=True)
            return Response(updated_serializer.data, status=status.HTTP_201_CREATED)
        else:
            # Remove the uploaded image from S3 if data is not valid
            s3.delete_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=f'dogs/{image.name}')
            logger.error(f"Serializer errors: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.error(f"Error uploading image: {str(e)}")
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
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

        # Add image URL to request data
        request.data['image'] = image_url

        # Validate data
        serializer = DogSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            # Fetch the updated list of dogs
            dogs = Dog.objects.all()
            updated_serializer = DogSerializer(dogs, many=True)
            return Response(updated_serializer.data, status=status.HTTP_201_CREATED)
        else:
            # Remove the uploaded image from S3 if data is not valid
            s3.delete_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=f'dogs/{image.name}')
            logger.error(f"Serializer errors: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.error(f"Error uploading image: {str(e)}")
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@api_view(['DELETE'])
def delete_dog(request, dog_id):
    try:
        dog = Dog.objects.get(id=dog_id, user=request.user)
        s3 = boto3.client('s3')
        s3.delete_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=f'dogs/{dog.image.split("/")[-1]}')
        dog.delete()
        return Response({"message": "Dog and image deleted successfully"}, status=status.HTTP_200_OK)
    except Dog.DoesNotExist:
        return Response({"error": "Dog not found or you do not have permission to delete this dog"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Error deleting dog: {str(e)}")
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
>>>>>>> 81c0dc896250eca6fae3d8b845e58284410d800b
