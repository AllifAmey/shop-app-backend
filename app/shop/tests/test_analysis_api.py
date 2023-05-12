"""
Tests for analysis api
"""
from decimal import Decimal

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from shop.models import (
    Product,
    OrderList,
    Order,
    OrderItem,
    UserDeliveryInfo)

LIST_ANALYSIS_URL = reverse('shop:data_analysis')


def create_product(**params):
    """Create and return a sample product."""
    defaults = {
        'name': 'Sample product title',
        'image_url': 'http://example.com/product.png',
        'price': Decimal('5.25'),
        'description_short': "Sample Short Description",
        'description_long': "Sample long description",
        'catagory': "Ring",
    }
    defaults.update(params)

    product = Product.objects.create(**defaults)
    return product


def create_order(user, **params):
    defaults = {
        'user': user,
        'first_name': "Test",
        "last_name": "Boy",
        "email": "test@admin.com",
        "phone_number": "+44 7700 900077",
        "address": "Marylebone, London",
        "city": "London",
        "country": "United Kingdom",
        "post_code": "NW10 4UX",
        "delivery_type": "Standard",
    }
    defaults.update(params)
    user_deliveryInfo_test = UserDeliveryInfo.objects.create(**defaults)
    product = create_product()
    orderItemData_test = {
        "user": user,
        "email": defaults['email'],
        "product": product,
        "quantity": 1,
    }
    orderItem_obj = OrderItem.objects.create(**orderItemData_test)
    OrderData_test = {
        "user": user,
        "email": defaults['email'],
        "personal_info_used": user_deliveryInfo_test,
        "delivery_instructions": "Leave by door",
        "total_price":  Decimal('5.25'),
        }
    order_obj = Order.objects.create(**OrderData_test)
    order_obj.order.add(orderItem_obj)
    orderList = OrderList.objects.get(user=user)
    orderList.order_list.add(order_obj)
    return order_obj


def create_user(**params):
    """Create and return a new user."""
    return get_user_model().objects.create_user(**params)


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
        self.user = create_user(
            email='user@example.com',
            password='test123')
        self.admin_user = create_admin_user(
            email='admin@example.com',
            password='test123')

    def test_get_analysis_hacker(self):
        """Test unauthenticated user can't get analysis"""

        res = self.client.get(LIST_ANALYSIS_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_analysis_admin(self):
        """Test admin can get analysis"""
        self.client.force_authenticate(user=self.admin_user)
        create_order(self.user)
        res = self.client.get(LIST_ANALYSIS_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
