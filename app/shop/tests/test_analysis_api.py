"""
Tests for analysis api
"""
from decimal import Decimal

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from shop.models import Product, Cart, CartItem, OrderList, Order, OrderItem, UserDeliveryInfo

