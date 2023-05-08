"""
Tests for order api
"""
from decimal import Decimal

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from shop.models import Product, Cart, CartItem, OrderList, Order, OrderItem, UserDeliveryInfo

LIST_ORDER_URL = reverse('shop:user_orders-list')
CREATE_ORDER_URL = reverse('shop:user_delivery_info-list')

def get_order_specific_url(order_id):
    """Create and return get specific order URL"""
    return reverse('shop:user_orders-detail', args=[order_id])#

def delete_order_specific_url(order_id):
    """Create and return delete specific order URL"""
    return reverse('shop:user_orders-detail', args=[order_id])

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

class OrderUserApiTest(TestCase):
    """Test authenticated user order API request"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = create_user(email='user@example.com', password='test123')
        self.hacker = create_user(email='hackerr@example.com', password='31337H4X0R')
        self.client.force_authenticate(user=self.user)
    
    def test_list_orders(self):
        """Test authenticated users can recieve their orders"""
        create_order(self.user)
        
        res = self.client.get(LIST_ORDER_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
    
    def test_list_specific_order(self):
        """Test Authenticated users can retrieve specific order"""
        
        order = create_order(self.user)
        
        url = get_order_specific_url(order.id)
        
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
    
    def test_list_orders_hacker(self):
        """Test hackers can't get other user orders"""
        order = create_order(self.user)
        self.client.force_authenticate(user=self.hacker)
        
        url = get_order_specific_url(order.id)
        
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        
    
    def test_post_orders(self):
        """Test Authenticated users can post their orders"""
        payload = [
            {
                "user": self.user.id,
                'first_name': "Test",
                "last_name": "Boy",
                "email": "test@admin.com",
                "phone_number": "+44 7700 900077",
                "address": "Marylebone, London",
                "city": "London",
                "country": "United Kingdom",
                "post_code": "NW10 4UX",
                "delivery_type": "Standard",
            },
            {
                "delivery_msg": "Sample Delivery Message",
                "total_price": Decimal('5.25'),   
            }
            ]
        product = create_product()
        cartItemData_test = {
            "user": self.user,
            "product": product,
            "quantity": 1
        }
        cart = Cart.objects.get(user=self.user)
        cart_item = CartItem.objects.create(**cartItemData_test)
        cart.products.add(cart_item)
        self.client.force_authenticate(user=self.user)
        res = self.client.post(CREATE_ORDER_URL, data=payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        
    def test_post_order_hacker(self):
        """Test hacker can't post order in others name"""
        payload = [
            {
                "user": self.user.id,
                'first_name': "Test",
                "last_name": "Boy",
                "email": "test@admin.com",
                "phone_number": "+44 7700 900077",
                "address": "Marylebone, London",
                "city": "London",
                "country": "United Kingdom",
                "post_code": "NW10 4UX",
                "delivery_type": "Standard",
            },
            {
                "delivery_msg": "Sample Delivery Message",
                "total_price": Decimal('5.25'),   
            }
            ]
        product = create_product()
        cartItemData_test = {
            "user": self.user,
            "product": product,
            "quantity": 1
        }
        cart = Cart.objects.get(user=self.user)
        cart_item = CartItem.objects.create(**cartItemData_test)
        cart.products.add(cart_item)
        self.client.force_authenticate(user=self.hacker)
        res = self.client.post(CREATE_ORDER_URL, data=payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
