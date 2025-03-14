import io
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from PIL import Image
import boto3
from django.conf import settings
from .models import Dog
from .serializers import DogSerializer


@api_view(['GET'])
def get_dogs(request):
    dogs = Dog.objects.all()
    serializer = DogSerializer(dogs, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
def add_dog(request):
    serializer = DogSerializer(data=request.data)
    if serializer.is_valid():
        image = request.FILES.get('image')
        if image:
            img = Image.open(image)
            if img.size > (1024 * 1024):  # Check if image size is greater than 1 MB
                output = io.BytesIO()
                img.save(output, format='JPEG', quality=85)
                output.seek(0)
                image = output

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
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
