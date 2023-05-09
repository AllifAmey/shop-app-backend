"""
Tests for cart api
"""
from decimal import Decimal


from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from shop.models import Product, CartItem


LIST_CART_Items_URL = reverse('shop:user_cart_items-list')


def cartItem_delete_url(cartItem_id):
    """Create and return a cart delete URL."""
    return reverse('shop:user_cart_items-detail', args=[cartItem_id])


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


def create_user(**params):
    """Create and return a new user."""
    return get_user_model().objects.create_user(**params)


class CartUserApiTest(TestCase):
    """Test authenticated user cart API request"""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user(email='user@example.com', password='test123')
        self.hacker = create_user(
            email='hackerr@example.com',
            password='31337H4X0R')
        self.client.force_authenticate(user=self.user)

    def test_list_cartItems(self):
        """Test cart can be listed"""

        res = self.client.get(LIST_CART_Items_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_post_cartItems(self):
        """Test cart items can be posted"""
        product = create_product()
        payload = {
            "user": self.user.id,
            "product": product.id,
            "quantity": 1
        }
        res = self.client.post(LIST_CART_Items_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_delete_cartItems(self):
        """Test cart items can be deleted"""

        product = create_product()
        test_cartItemData = {
            "user": self.user,
            "product": product,
            "quantity": 1
        }
        test_cartItem = CartItem.objects.create(**test_cartItemData)

        url = cartItem_delete_url(test_cartItem.id)

        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_cartItems_hacker(self):
        """Test cart items can't be deleted by hacker"""

        product = create_product()
        test_cartItemData = {
            "user": self.user,
            "product": product,
            "quantity": 1
        }
        test_cartItem = CartItem.objects.create(**test_cartItemData)
        self.client.force_authenticate(user=self.hacker)

        url = cartItem_delete_url(test_cartItem.id)

        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
