"""
Tests for analysis api
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

LIST_ANALYSIS_URL = reverse('shop:data_analysis')


def create_admin_user(**params):
    """Create and return a admin user."""
    user = get_user_model().objects.create_user(**params)
    user.is_staff = True
    user.save()
    return user


class AnalysisAPIApiTest(TestCase):
    """Test authenticated user order API request"""

    def setUp(self):
        self.client = APIClient()
        self.admin_user = create_admin_user(
            email='user@example.com',
            password='test123')

    def test_get_analysis_hacker(self):
        """Test unauthenticated user can't get analysis"""

        res = self.client.get(LIST_ANALYSIS_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_analysis_admin(self):
        """Test admin can get analysis"""
        self.client.force_authenticate(user=self.admin_user)
        res = self.client.get(LIST_ANALYSIS_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
