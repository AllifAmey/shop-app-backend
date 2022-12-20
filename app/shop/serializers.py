"""
Serializers for the shop API View.
"""
from rest_framework import serializers

from shop import models

class ProductSerializer(serializers.ModelSerializer):
    """Serializes Product Model"""
    class Meta:
        model = models.Product
        fields = ['id', 'name', 'image_url', 'price', 'description_short', 'description_long']

class CartItemSerializer(serializers.ModelSerializer):
    """Serializes the Cart Item Model"""
    class Meta:
        model = models.CartItem
        fields = ['id', 'user', 'product', 'quantity']

class CartSerializer(serializers.ModelSerializer):
    """Serializes Cart Model"""
    class Meta:
        model = models.Cart
        fields = ['id', 'user', 'products']
        
class OrderItemSerializer(serializers.ModelSerializer)  :
    """Serializes Order Model"""
    class Meta:
        model = models.OrderItem
        fields = ['id', 'user', 'product', 'quantity', 'date_ordered']
        
class OrderSerializer(serializers.ModelSerializer)  :
    """Serializes Order Model"""
    class Meta:
        model = models.Order
        fields = ['id', 'user', 'order', 'delivery_status', 'date_ordered', 'total_price']
        
class OrderListSerializer(serializers.ModelSerializer)  :
    """Serializes OrderList Model"""
    class Meta:
        model = models.OrderList
        fields = ['id', 'user', 'order_list']
        

        