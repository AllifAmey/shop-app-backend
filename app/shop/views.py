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
    CartItemSerializer,
    OrderSerializer,
    OrderItemSerializer,
    OrderListSerializer,
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
"""
class RetrievePostOrderView(APIView):
    \"""Retrieves the order to the shop the user made and allows posting orders\"""
    serializer_class = OrderSerializer
    queryset = models.Order.objects.all()
    renderer_classes = [JSONRenderer]
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        \"""Returns the list of products in the user's order\"""
        
        queryset_order = models.Order.objects.filter(user=request.user)
        
        #queryset_delivery = models.Delivery.objects.filter(user=request.user)
        
        # checks if user has orders else return no orders
        if queryset_order:
            
            entire_order = {'orders': []}
       
            for order_obj in queryset_order:
                delivery_obj = models.Delivery.objects.get(order=order_obj)
                serializer = DeliverySerializer(delivery_obj)
                order_serialized = self.serializer_class(order_obj)
                products = order_serialized.data['products']
                user_cart_products = models.Product.objects.filter(pk__in=products)
                products_serialized = ProductSerializer(user_cart_products, many=True)
                
                individual_order = {
                    'order' : products_serialized.data,
                    'delivery status': serializer.data['delivery_status']}
                
                entire_order['orders'].append(individual_order)
            
            return Response(entire_order, status=status.HTTP_200_OK)
        else:
            error_msg = {"You have no orders"}
            return Response(error_msg , status=status.HTTP_404_NOT_FOUND)

       
    
    def post(self, request):
        \"""Edits the order upon successful transaction\"""
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
"""            
            
        
        
"""
class RetrieveDeliveryView(APIView):
    \"""Retrieves the delivery status of the user's order\"""
    serializer_class = DeliverySerializer
    queryset = models.Delivery.objects.all()
    renderer_classes = [JSONRenderer]
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        \"""Allows the delivery status to be edited by admin\"""
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
"""
        
# new apis involving the new models

class CartView(APIView):
    """Users can see and post cart items"""
    
    serializer_class = CartSerializer
    queryset = models.Cart.objects.all()
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Displays user's cart"""
        user = request.user
        user_cart = models.Cart.objects.get(user=user)
        # CartItemSerializer
        serializer = self.serializer_class(user_cart)
        products = serializer.data['products']
        products = models.CartItem.objects.filter(pk__in=products)
        serializer = CartItemSerializer(products, many=True)
        user_cart = {}
        counter = 1
        for product in products:
            print(product)
            serializer = ProductSerializer(product.product)
            user_cart[f'cart item {counter}'] = {'product': serializer.data,
                                                 'quantity': product.quantity}
            counter += 1
        
        return Response(user_cart)

class OrderListView(APIView):
    """Users can see their list of orders """
    serializer_class = OrderListSerializer
    queryset = models.OrderList.objects.all()
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Display user's list of orders"""
        user = request.user
        user_order_list = models.OrderList.objects.get(user=user)
        serializer = self.serializer_class(user_order_list)
        print(serializer.data["order_list"])
        orders = serializer.data["order_list"]
        order = models.Order.objects.filter(pk__in=orders)
        serializer = OrderSerializer(order, many=True)
        
        
        return Response(serializer.data)
    

