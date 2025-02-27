import logging
import os
from firebase_admin import credentials, auth, initialize_app, get_app
from .serializers import UserSerializer
from django.contrib.auth.models import User
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

# Initialize Firebase Admin SDK
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
cred = credentials.Certificate(
    os.path.join(BASE_DIR, 'pawfectmatch-1a858-firebase-adminsdk-fbsvc-789e8e1919.json'))

# Check if the default app is already initialized
try:
    get_app()
except ValueError:
    initialize_app(cred)

# Set up logging
logger = logging.getLogger(__name__)


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


@api_view(['POST'])
def signup(request):
    logger.info("Signup API called")
    username = request.data.get('username')
    email = request.data.get('email')
    password = request.data.get('password')
    id_token = request.data.get('idToken')

    try:
        # Verify the ID token
        decoded_token = auth.verify_id_token(id_token)
        uid = decoded_token['uid']

        # Create user in Django
        user = User.objects.create_user(
            username=username, email=email, password=password)
        user.save()

        # Serialize user data
        serializer = UserSerializer(user)
        tokens = get_tokens_for_user(user)
        return Response({"message": "Signup successful", "user": serializer.data, "tokens": tokens}, status=status.HTTP_201_CREATED)
    except auth.InvalidIdTokenError:
        logger.error("Invalid ID token")
        return Response({"error": "Invalid ID token"}, status=status.HTTP_401_UNAUTHORIZED)
    except User.DoesNotExist:
        logger.error("User already exists")
        return Response({"error": "User already exists"}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.error(f"Signup failed: {str(e)}")
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def login(request):
    logger.info("Login API called")
    id_token = request.data.get('idToken')
    try:
        decoded_token = auth.verify_id_token(id_token)
        uid = decoded_token['uid']
        user = User.objects.get(username=uid)
        logger.info(f"User logged in: {user.username}")
        tokens = get_tokens_for_user(user)
        return Response({"message": "Login successful", "tokens": tokens}, status=status.HTTP_200_OK)
    except auth.InvalidIdTokenError:
        logger.error("Invalid ID token")
        return Response({"error": "Invalid ID token"}, status=status.HTTP_401_UNAUTHORIZED)
    except User.DoesNotExist:
        logger.error("User does not exist")
        return Response({"error": "User does not exist"}, status=status.HTTP_404_NOT_FOUND)
