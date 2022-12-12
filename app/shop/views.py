"""
Views for the shop API
"""

from rest_framework import generics, authentication
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework import filters
from shop import models
from shop.serializers import (
    ProductSerializer,
    CartSerializer,
    OrderSerializer,
    DeliverySerializer
)
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import status
from rest_framework.renderers import JSONRenderer
from rest_framework.permissions import IsAuthenticated
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


#Order and delivery APIView

class RetrievePostOrderView(APIView):
    """Retrieves the order to the shop the user made and allows posting orders"""
    serializer_class = OrderSerializer
    queryset = models.Order.objects.all()
    renderer_classes = [JSONRenderer]
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Returns the list of products in the user's order"""
        
        queryset_order = models.Order.objects.filter(user=request.user)
        
        # checks if user has orders else return no orders
        if queryset_order:
            order_serialized = self.serializer_class(queryset_order, many=True)
            return Response(order_serialized.data, status=status.HTTP_200_OK)
        else:
            error_msg = {"You have no orders"}
            return Response(error_msg , status=status.HTTP_404_NOT_FOUND)

       
    
    def post(self, request):
        """Edits the order upon successful transaction"""
        user = request.user
        print(user)
        print(request.data)
        user_cart = models.Cart.objects.get(user=request.user)
        
        serializer = CartSerializer(user_cart)
       
        products = serializer.data['products']
        
        if products == []:
            print(user_cart)
            error_msg = {"You can't make a order with no products in your cart."}
            return Response(error_msg , status=status.HTTP_404_NOT_FOUND)
        
        else:
            user_cart_products = models.Product.objects.filter(pk__in=products)
            products_serialized = ProductSerializer(user_cart_products, many=True)
            new_order = models.Order.objects.create(user=request.user)
            new_order.products.set(products)
            new_delivery_msg = models.Delivery.objects.create(order=new_order, delivery_status="")
            delivery_serialized = DeliverySerializer(new_delivery_msg)
            user_cart.products.set('') 
            user_cart.save()
            
         
            success_msg = {"You have successfully placed an order"}
            return Response({
                'message': success_msg, 
                'products ordered': products_serialized.data, 
                'delivery status': delivery_serialized.data}, status=status.HTTP_201_CREATED)
            
            
        
        
    
class RetrieveDeliveryView(APIView):
    """Retrieves the delivery status of the user's order"""
    serializer_class = DeliverySerializer
    queryset = models.Delivery.objects.all()
    renderer_classes = [JSONRenderer]
  
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Returns the list of products in the user's cart"""
        user = request.user
        user_delivery = models.Delivery.objects.filter(user=user)
        serializer = self.serializer_class(user_delivery, many=True)
        
        return Response({'delivery status':serializer.data[0]['delivery_status']})
    
    def post(self, request):
        """Allows the delivery status to be edited by admin"""
        user = request.user
        
        if user.is_staff:
            serializer = DeliverySerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            error_msg = {"You are not authorised to edit other user's delivery status"}
            return Response(error_msg, status=status.HTTP_403_FORBIDDEN)
    
    
    
