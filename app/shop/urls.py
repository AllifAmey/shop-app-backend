"""
Urls for the shop API
"""
from rest_framework.routers import DefaultRouter

from django.urls import path, include

from shop import views



app_name = 'shop'

router = DefaultRouter()


router.register('cart/items', views.CartItemViewset, basename="user cart items")
router.register('orders', views.OrderViewset, basename="user orders")
router.register('individual_order', views.OrderItemViewset, basename="user order item")

urlpatterns = [
    path('products/', views.ListProductView.as_view(), name='products'),
   
    path('user/orders/', views.OrderListView.as_view(), name='user list of orders'),
    path('', include(router.urls))
]