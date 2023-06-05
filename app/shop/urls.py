"""
Urls for the shop API
"""
from rest_framework.routers import DefaultRouter

from django.urls import path, include

from shop import views
app_name = 'shop'

router = DefaultRouter()


router.register(
    'cart/items',
    views.CartItemViewset,
    basename="user_cart_items"
    )
router.register(
    'orders',
    views.OrderViewset,
    basename="user_orders"
    )
router.register(
    'deliveryinfo',
    views.UserDeliveryInfoViewset,
    basename="user_delivery_info"
    )
router.register(
    'individual_order',
    views.OrderItemViewset,
    basename="user_order_item"
    )
router.register(
    'products',
    views.ListProductViewset,
    basename='products'
    )
router.register(
    'products/delete',
    views.DestroyProductViewSet,
    basename='delete_products'
    )

urlpatterns = [
    path(
        'post_orders/anonymous',
        views.PostOrderAnonymousAPIView.as_view(),
        name='post_orders_anonymously'
        ),
    path(
        'create/product',
        views.CreateProduct.as_view(),
        name='create_product'
        ),
    path(
        'analysis',
        views.DataAnalysisShopAPIView.as_view(),
        name='data_analysis'
        ),
    path('external',
         views.ExternalAPIView.as_view(),
         name="external"),
    path('', include(router.urls)),
]
