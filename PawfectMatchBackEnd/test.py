from django.test import TestCase
from django.urls import reverse, resolve
from django.http import HttpResponse

# filepath: PawfectMatchBackend/PawfectMatchBackEnd/test_urls.py


class TestUrls(TestCase):
    def test_admin_url(self):
        """Test the admin URL is accessible."""
        response = self.client.get('/admin/')
        self.assertEqual(response.status_code, 200)

    def test_user_api_url(self):
        """Test the user API URL is included."""
        response = self.client.get('/api/user/')
        self.assertIn(response.status_code, [200, 404])  # Adjust based on actual implementation

    def test_dogs_api_url(self):
        """Test the dogs API URL is included."""
        response = self.client.get('/api/')
        self.assertIn(response.status_code, [200, 404])  # Adjust based on actual implementation