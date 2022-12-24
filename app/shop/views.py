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
    UserDeliveryInfoSerializer
)
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import status
from rest_framework.renderers import JSONRenderer
from rest_framework.permissions import IsAuthenticated
from shop import permissions
from shop import models
from drf_spectacular.utils import extend_schema, inline_serializer, PolymorphicProxySerializer
from rest_framework import serializers


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
        
# new apis involving the new models

# this is now the standard
# TODO: Make sure when cart item is created attach to user - change post method

class CartItemViewset(viewsets.ModelViewSet):
    """Users can create cart items"""
    serializer_class = CartItemSerializer
    queryset = models.CartItem.objects.all()
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = (permissions.UpdateOwnCart, )
    
    def list(self, request):
        """Displays user's cart"""
        user = request.user
        user_cart = models.Cart.objects.get(user=user)
        # CartItemSerializer
        serializer = CartSerializer(user_cart)
        products = serializer.data['products']
        products = models.CartItem.objects.filter(pk__in=products)
        serializer = self.serializer_class(products, many=True)
        user_cart = {}
        
        for product in products:
            
            serializer = ProductSerializer(product.product)
            user_cart[f'cart id {product.id}'] = {'product': serializer.data,
                                                 'quantity': product.quantity}
            
        
        return Response(user_cart)
    
    def create(self, request):
        """Allows user to post user cart items"""
        user = request.user
        
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            recent_cart_item = serializer.save()
            user_cart = models.Cart.objects.get(user=user)
            user_cart.products.add(recent_cart_item)
            return Response({"message": "Cart item added successfully!"}, status=status.HTTP_200_OK)
        else:
            
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        


class OrderItemViewset(viewsets.ModelViewSet):
    """Users can see their list of orders items """
    serializer_class = OrderItemSerializer
    queryset = models.OrderItem.objects.all()
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.UpdateOwnCart,]
    http_method_names = ['get', 'post', 'delete']
    


class OrderViewset(viewsets.ModelViewSet):
    """Users can see their list of orders """
    serializer_class = OrderSerializer
    queryset = models.Order.objects.all()
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.UpdateOwnCart,]
    http_method_names = ['get', 'post', 'delete']
    
    def list(self, request):
        """Display user's list of orders"""
        user = request.user
        user_order_list = models.OrderList.objects.get(user=user)
        serializer = OrderListSerializer(user_order_list)
        print(serializer.data["order_list"])
        orders = serializer.data["order_list"]
        order = models.Order.objects.filter(pk__in=orders)
        serializer = OrderSerializer(order, many=True)
        
        
        return Response(serializer.data)

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
    

    
class MassDeleteAPIView(APIView):
    """Allows the deletion of different objects on mass"""
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    @extend_schema(request=inline_serializer(name="Mass_delete",fields={
        "object_type": serializers.CharField(), 
        "ids": serializers.ListField(
            child=serializers.IntegerField(min_value=1))
        }),responses={
            '2XX': inline_serializer(name='Success', fields={"message": serializers.CharField()})
        })
    def post(self,request):
        """Deletes objects on mass"""
        
        user = request.user
        object_type = request.data.get("object_type")
        ids = request.data.get("ids")
        
        if object_type == "cart":
            # TODO: check addition things such as whether those ids listed are related to the user.
            cart_items = models.CartItem.objects.filter(pk__in=ids)
            print(user)
            cart_items.delete()
            
        
        return Response({"Message": "Items successfully deleted"})

class UserDeliveryInfoViewset(viewsets.ModelViewSet):
    """Users can see their list of orders items """
    serializer_class = UserDeliveryInfoSerializer
    queryset = models.UserDeliveryInfo.objects.all()
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.UpdateOwnCart,]
    http_method_names = ['get', 'post', 'patch','delete']
    
    
    @extend_schema(
    request=PolymorphicProxySerializer(
        component_name='user_delivery_info',
        serializers=[
            UserDeliveryInfoSerializer, inline_serializer(name="user_orders",fields={
                "delivery_msg": serializers.CharField(allow_blank=True), 
                "total_price": serializers.DecimalField(max_digits=5, decimal_places=2), 
        }),
        ],
        resource_type_field_name='type',
        many=True
    ),
    responses={
            '2XX': inline_serializer(name='Order_success', fields={"message": serializers.CharField()})
        }
    )
    def create(self, request):
        """Create delivery info and order"""
        user_exist = "Don't know"
        
        #establish if anonymous user.
        try:
            user = request.user
            user_exist = True
        except:
            user_exist = False
            
        # process the data and check if user inputted right data
        serializer = self.serializer_class(data=request.data[0])
        if serializer.is_valid():
            #create the deliveryInfo
            #new_deliveryInfo = serializer.save()
            #create the order items by grabbing the user's cart
            user_cart = "empty"
            if user_exist:
                user_cart = models.Cart.objects.get(user=user)
            
            serializer = CartSerializer(user_cart)
            
            user_cart_cartItems = serializer.data['products']
            store_orders = []
            for cartItem in user_cart_cartItems:
                single_cartItem = models.CartItem.objects.get(id=cartItem)
                serializer = CartItemSerializer(single_cartItem)
                product = serializer.data['product']
                quantity = serializer.data['quantity']
                email = request.data[0]['email']
                serializer = OrderItemSerializer(data={"user":user.id,"email":email,"product":product, "quantity":quantity})
                if serializer.is_valid():
                    new_OrderItem = serializer.save()
                    store_orders.append(new_OrderItem.id)
                else:
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                
            
            #here is where the order
            email = request.data[0]['email']
            serializer = self.serializer_class(data=request.data[0])
            new_delivery_info = None
            if serializer.is_valid():
                new_delivery_info = serializer.save()
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            serializer = OrderSerializer(data={"user": user.id, 
                                               "email": email, 
                                               "personal_info_used":new_delivery_info.id,
                                               "order": store_orders,
                                               "delivery_instructions": request.data[1]["delivery_msg"],
                                               "total_price": request.data[1]["total_price"]})
            if serializer.is_valid():
                # lastly attach the user's order to the order list so they can view it and all the necessary information
                
                new_order = serializer.save()
                
                if serializer.is_valid():
                    print("hello")
                    old_OrderList = models.OrderList.objects.get(user=user)
                    old_OrderList.order_list.add(new_order)
                    # now the order is added, delete the cart items.                 
                    print(user)
                    old_cartItems = models.CartItem.objects.filter(user=user)
                    
                    
                    old_cartItems.delete()
                else:
                    print(serializer.errors)
                    print("there's an error")
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            else:
                
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            return Response({"message": "order is valid"},  status=status.HTTP_200_OK)
        else:
            
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        
class PostOrderAnonymousAPIView(APIView):
    """Allows users to post orders anonymously"""
    serializer_class = UserDeliveryInfoSerializer
    
    @extend_schema(
    request=PolymorphicProxySerializer(
        component_name='user_delivery_info_anonymous',
        serializers=[
            UserDeliveryInfoSerializer, inline_serializer(name="user_orders_anonymous",fields={
                "delivery_msg": serializers.CharField(allow_blank=True), 
                "total_price": serializers.DecimalField(max_digits=5, decimal_places=2), 
        }),inline_serializer(name="user_cart",fields={
            "products": serializers.ListField(child=inline_serializer(name="user_items_anonymous",fields={
                "product_ids": serializers.IntegerField(min_value=1), 
                "quantity": serializers.IntegerField(min_value=1), }))
        })  
        ],
        resource_type_field_name='type',
        many=True
    ),
    responses={
            '2XX': inline_serializer(name='Order_success', fields={"message": serializers.CharField()})
        }
    )
    def post(self,request):
        """Post orders anonymously."""
        
        email = request.data[0]['email']
        user_cartItems = request.data[2]['products']
        serializer = self.serializer_class(data=request.data[0])
        if serializer.is_valid():
            # now that the delivery info is valid
            # create the orderitems and attach the email to it.
            # this is so that if the user gives us a email to complain of orders
            # we can look at their email to see what orders are attached to it.
            store_orders = []
            for cartItem in user_cartItems:
                product = cartItem['product_id']
                quantity = cartItem['quantity']
                serializer = OrderItemSerializer(data={"email":email,"product":product, "quantity":quantity})
                if serializer.is_valid():
                    new_orderItem = serializer.save()
                    store_orders.append(new_orderItem.id)
                else:
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            serializer = self.serializer_class(data=request.data[0])
            if serializer.is_valid():
                new_delivery_info = serializer.save()
                serializer = OrderSerializer(data={
                                                "email": email, 
                                                "personal_info_used":new_delivery_info.id,
                                                "order": store_orders,
                                                "delivery_instructions": request.data[1]["delivery_msg"],
                                                "total_price": request.data[1]["total_price"]})
                if serializer.is_valid():
                    
                    serializer.save()
                    return Response({"message": "Order Successful"})
                else:
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({"message": "hello"})    
    