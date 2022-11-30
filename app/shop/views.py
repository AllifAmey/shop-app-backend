"""
Views for the shop API
"""

from rest_framework import generics, authentication
from rest_framework import viewsets
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework import filters
from shop import models
from shop.serializers import (
    ProductSerializer,
    CartSerializer,
)
from rest_framework.response import Response
from rest_framework import status
from rest_framework.renderers import JSONRenderer
from shop import permissions
from shop import models

class ListProductView(generics.ListAPIView):
    """List the products available at the shop"""
    serializer_class = ProductSerializer
    queryset = models.Product.objects.all()
    renderer_classes = [JSONRenderer]
   
#viewsets.ModelViewSet

class ListCartView(viewsets.ModelViewSet):
    """List items in shopping cart for user and allows user to edit shopping cart"""
    serializer_class = CartSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = (permissions.UpdateOwnCart, )
    queryset = models.Cart.objects.all()
    http_method_names = ['get',  'patch']
    renderer_classes = [JSONRenderer]
    
    def grab_product_from_cart(self, request):
        """This returns products from cart."""
        user_cart = models.Cart.objects.filter(user=request.user)
        serializer = self.serializer_class(user_cart, many=True)
        # maybe use the below for later, it just looks extremely weird.
        #json = JSONRenderer().render(serializer.data)
        products = serializer.data[0]['products']
        user_cart_products = models.Product.objects.filter(pk__in=products)
        products_serialized = ProductSerializer(user_cart_products, many=True)
        return products_serialized.data
    
    def list(self, request):
        """Returns the list of products in the user's cart"""
        products = self.grab_product_from_cart(request)
        user_cart = models.Cart.objects.filter(user=request.user)
        serializer = self.serializer_class(user_cart, many=True)
        print(serializer.data[0]['id'])
        
        
        
        return Response({'id':serializer.data[0]['id'],'products': products} )
    
    
    
    
    
    
