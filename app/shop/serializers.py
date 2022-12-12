"""
Serializers for the shop API View.
"""
from rest_framework import serializers

from shop import models

"""
 name = models.CharField(max_length=255)
    image_url = models.URLField(max_length=255)
    price = models.DecimalField(..., max_digits=5, decimal_places=2)
    description_short = models.TextField()
    description_long = models.TextField()

"""

class ProductSerializer(serializers.ModelSerializer):
    """Serializes Product Model"""
    class Meta:
        model = models.Product
        fields = ['id', 'name', 'image_url', 'price', 'description_short', 'description_long']

class CartSerializer(serializers.ModelSerializer):
    """Serializes Cart Model"""
    class Meta:
        model = models.Cart
        fields = ['id', 'user', 'products']
        
class OrderSerializer(serializers.ModelSerializer)  :
    """Serializes Order Model"""
    class Meta:
        model = models.Order
        fields = ['id', 'user', 'products']
        
class DeliverySerializer(serializers.ModelSerializer):
    """Serializes Delivery Model"""
    class Meta:
        model = models.Delivery
        fields = ['id', 'order', 'delivery_status']
        