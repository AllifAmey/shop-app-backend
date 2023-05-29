"""
Serializers for the shop API View.
"""
from rest_framework import serializers

from shop import models


class ProductSerializer(serializers.ModelSerializer):
    """Serializes Product Model"""
    class Meta:
        model = models.Product
        fields = ['id', 'name', 'image_url', 'price',
                  'description_short', 'description_long', 'catagory']


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


class OrderItemSerializer(serializers.ModelSerializer):
    """Serializes Order Model"""
    class Meta:
        model = models.OrderItem
        fields = ['id', 'user', 'email', 'product', 'quantity', 'date_ordered']


class OrderSerializer(serializers.ModelSerializer):
    """Serializes Order Model"""
    class Meta:
        model = models.Order
        fields = ['id', 'user', 'email', 'order',
                  'personal_info_used', 'delivery_instructions',
                  'delivery_status', 'date_ordered', 'total_price']


class OrderListSerializer(serializers.ModelSerializer):
    """Serializes OrderList Model"""
    class Meta:
        model = models.OrderList
        fields = ['id', 'user', 'order_list']


class UserDeliveryInfoSerializer(serializers.ModelSerializer):
    """Serializes OrderList Model"""
    class Meta:
        model = models.UserDeliveryInfo
        fields = ['id', 'user', 'first_name', 'last_name', 'email',
                  'phone_number', 'address', 'city', 'country',
                  'post_code', 'delivery_type']


class DefaultUserDeliveryInfoSerializer(serializers.ModelSerializer):
    """Serializes OrderList Model"""
    class Meta:
        model = models.DefaultUserDeliveryInfo
        fields = ['id', 'user', 'default_info']


class ExternalSerializer(serializers.Serializer):
    """Serializes External APi"""
    type = serializers.CharField(max_length=200)
    content = serializers.CharField(allow_blank=True)
