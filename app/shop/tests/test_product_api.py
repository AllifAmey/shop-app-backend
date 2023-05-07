"""
Tests for shop api
"""
from decimal import Decimal


from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from shop.models import Product
from shop.serializers import ProductSerializer

LIST_PRODUCTS_URL = reverse('shop:products-list')
CREATE_PRODUCTS_URL = reverse('shop:create_product')

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

def product_specific_url(product_id):
    """Create and return a product detail URL."""
    return reverse('shop:products-detail', args=[product_id])

def product_delete_url(product_id):
    """Delete and return a product delete URL."""
    return reverse('shop:delete_products-detail', args=[product_id])

def create_user(**params):
    """Create and return a new user."""
    return get_user_model().objects.create_user(**params)

def create_admin_user(**params):
    """Create and return a admin user."""
    user = get_user_model().objects.create_user(**params)
    user.is_staff = True
    user.save()
    return user

class PublicApiTestProduct(TestCase):
    """Test the public features of the shop API"""
    
    def setUp(self):
        self.client = APIClient()
        
    def test_list_products(self):
        """Test products can be listed"""
        create_product()
        
        res = self.client.get(LIST_PRODUCTS_URL)

        recipes = Product.objects.all().order_by('-id')
        serializer = ProductSerializer(recipes, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_specific_product(self):
        """Test specific products gets retrieved"""
        
        product = create_product()

        url = product_specific_url(product.id)
        res = self.client.get(url)

        serializer = ProductSerializer(product)
        self.assertEqual(res.data, serializer.data)

class ProductCreateUserApiTests(TestCase):
    """Test authenticated user Product Create API requests."""
    
    def setUp(self):
        self.client = APIClient()
        self.user = create_user(email='user@example.com', password='test123')
    
    def test_product_create_anon(self):
        """Test anon can't create product"""
        payload = {
        'name': 'Sample product title',
        'image_url': 'http://example.com/product.png',
        'price': Decimal('5.25'),
        'description_short': "Sample Short Description",
        'description_long': "Sample long description",
        'catagory': "Ring",
        }
        res = self.client.post(CREATE_PRODUCTS_URL, payload)
        
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_product_create_user(self):
        """Test authenticated user can't create product"""
        payload = {
        'name': 'Sample product title',
        'image_url': 'http://example.com/product.png',
        'price': Decimal('5.25'),
        'description_short': "Sample Short Description",
        'description_long': "Sample long description",
        'catagory': "Ring",
        }
        self.client.force_authenticate(user=self.user)
        res = self.client.post(CREATE_PRODUCTS_URL, payload)
        
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

class ProductCreateAdminApiTests(TestCase):
    """Test Admin Product Create API requests."""
    
    def setUp(self):
        self.client = APIClient()
        self.admin_user = create_admin_user(email='user@example.com', password='test123')
        self.client.force_authenticate(user=self.admin_user)
    
    def test_product_create_admin(self):
        """Test Admin can create Product"""
        payload = {
        'name': 'Sample product title',
        'image_url': 'http://example.com/product.png',
        'price': Decimal('5.25'),
        'description_short': "Sample Short Description",
        'description_long': "Sample long description",
        'catagory': "Ring",
        }
        res = self.client.post(CREATE_PRODUCTS_URL, payload)
        
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

class ProductDeleteUserApiTests(TestCase):
    """Test authenticated user Product Delete API requests."""
    
    def setUp(self):
        self.client = APIClient()
        self.user = create_user(email='user@example.com', password='test123')
    
    def test_product_delete_anon(self):
        """Test anon can't delete product"""
        product = create_product()
        url = product_delete_url(product.id)
        res = self.client.delete(url)
        
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_product_create_user(self):
        """Test authenticated user can't delete product"""
        product = create_product()
        url = product_delete_url(product.id)
        res = self.client.delete(url)
        self.client.force_authenticate(user=self.user)
        res = self.client.delete(url)
        
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

class ProductDeleteAdminApiTests(TestCase):
    """Test Admin Product Create API requests."""
    
    def setUp(self):
        self.client = APIClient()
        self.admin_user = create_admin_user(email='user@example.com', password='test123')
        self.client.force_authenticate(user=self.admin_user)
    
    def test_product_delete_admin(self):
        """Test Admin can delete Product"""

        product = create_product()
        url = product_delete_url(product.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
