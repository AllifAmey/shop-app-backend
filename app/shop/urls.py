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
    basename="user cart items"
    )
router.register(
    'orders',
    views.OrderViewset,
    basename="user orders"
    )
router.register(
    'deliveryinfo',
    views.UserDeliveryInfoViewset,
    basename="user delivery info"
    )
router.register(
    'individual_order',
    views.OrderItemViewset,
    basename="user order item"
    )
router.register(
    'products',
    views.ListProductViewset,
    basename='products'
    )
router.register(
    'products/delete',
    views.DestroyProductViewSet,
    basename='delete products'
    )

urlpatterns = [
    path(
        'post_orders/anonymous',
        views.PostOrderAnonymousAPIView.as_view(),
        name='post orders anonymously'
        ),
    path(
        'user/orders/',
        views.OrderListView.as_view(),
        name='user list of orders'
        ),
    path(
        'user/mass_delete',
        views.MassDeleteAPIView.as_view(),
        name='Deletes objects on mass'
        ),
    path(
        'create/product',
        views.CreateProduct.as_view(),
        name='create_product'
        ),
    path(
        'analysis',
        views.DataAnalysisShopAPIView.as_view(),
        name='data analysis'
        ),
    path('', include(router.urls)),
]
