"""
Urls for the shop API
"""
from rest_framework.routers import DefaultRouter

from django.urls import path, include

from shop import views



app_name = 'shop'

router = DefaultRouter()

router.register('cart', views.ListCartView, basename="cart")
# path('cart/', views.ListCartView.as_view(), name='cart'),
# products/

urlpatterns = [
    path('products/', views.ListProductView.as_view(), name='products'),
    path('orders/', views.RetrievePostOrderView.as_view(), name='orders'),
    path('delivery/', views.RetrieveDeliveryView.as_view(), name='delivery'),
    path('experiment/', views.ExperimentView.as_view(), name="experiment"),
    path('', include(router.urls))
]