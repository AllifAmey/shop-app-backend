"""
Views for the shop API
"""

from rest_framework import authentication
from rest_framework import viewsets
from rest_framework.views import APIView
from shop.serializers import (
    ProductSerializer,
    CartSerializer,
    CartItemSerializer,
    OrderSerializer,
    OrderItemSerializer,
    OrderListSerializer,
    UserDeliveryInfoSerializer
)
from rest_framework.response import Response
from rest_framework import status
from rest_framework.renderers import JSONRenderer
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from shop import permissions
from shop import models
from drf_spectacular.utils import extend_schema,\
    inline_serializer, PolymorphicProxySerializer
from rest_framework import serializers
from django.db.models import Sum, Count
from django.db.models.functions import ExtractMonth
from django.db import connection


class DataAnalysisShopAPIView(APIView):
    """Analysis of the backend data and returns result"""
    queryset = models.Order.objects.all()
    renderer_classes = [JSONRenderer]
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        return models.Order.objects.all()

    def get(self, request):
        sales_per_month = [{"month": "Jan",
                            "sale": 0},
                           {"month": "Feb",
                            "sale": 0},
                           {"month": "Mar",
                            "sale": 0},
                           {"month": "Apr",
                            "sale": 0},
                           {"month": "May",
                            "sale": 0},
                           {"month": "Jun",
                            "sale": 0},
                           {"month": "Jul",
                            "sale": 0},
                           {"month": "Aug",
                            "sale": 0},
                           {"month": "Sep",
                            "sale": 0},
                           {"month": "Oct",
                            "sale": 0},
                           {"month": "Nov",
                            "sale": 0},
                           {"month": "Dec",
                            "sale": 0},
                           ]

        """
        Problem with current solution:

        Product Popularity Algorithm problem -
        I keep looping over the same queryset when I could
        get my answer in 2 operations 0(2)
        Current logic:
        Loop over order models in database ( imagine 1000x )
        Then perform python's max function o(n^2)
        Extremely inefficient

        Solution:
        most_popular = models.Product.objects\
            .annotate(num_orderItem=Count('orderitem'))\
                .order_by("-num_orderItem")[0]
        least_popular = models.Product.objects\
            .annotate(num_orderItem=Count('orderitem'))\
                .order_by("num_orderItem")[0]
        count_most = models.OrderItem.objects\
            .filter(product=most_popular).count()
        count_most = models.OrderItem.objects\
            .filter(product=least_popular).count()
        4 queries. 0(4) Much more efficient long term.

        Problem with current solution:

        Sales for each month algorithim problem -
        I keep looping over the query set and many operations on each loop
        Overtime as the application scales the operation would be 0(n^2)
        Imagine 1000x rows
        In theory I could probably do 12 queries.

        Solution:
        models.Order.objects.annotate(month=ExtractMonth('date_ordered'))
        .values('month').annotate(total_sales=Sum('total_price'))
        After:
        Database gets hit 5 times ( Not reliant on data expanding )
        Before:
        Database gets hit 8 times ( based on data expanded )
        Improve is seen as api scales.
        """
        monthly_sales = models.Order.objects.annotate(
            month=ExtractMonth('date_ordered'))\
            .values('month').annotate(total_sales=Sum('total_price'))
        for sale in monthly_sales:
            sales_per_month[sale['month']-1]['sale'] = sale['total_sales']
        print(len(connection.queries))  # hits database
        print(connection.queries[-1]['sql'])
        most_popular = models.Product.objects.annotate(
            num_orderItem=Count('orderitem')).order_by("-num_orderItem")[0]
        print(len(connection.queries))  # hits database
        print(connection.queries[-1]['sql'])
        least_popular = models.Product.objects.annotate(
            num_orderItem=Count('orderitem')).order_by("num_orderItem")[0]
        print(len(connection.queries))  # hits database
        print(connection.queries[-1]['sql'])
        count_most = models.OrderItem.objects.filter(
            product=most_popular).count()
        print(len(connection.queries))  # hits database
        print(connection.queries[-1]['sql'])
        count_least = models.OrderItem.objects.filter(
            product=least_popular).count()
        print(len(connection.queries))  # hits database
        print(connection.queries[-1]['sql'])
        serializer_most_popular_product = ProductSerializer(
            most_popular
            )
        serializer_least_popular_product = ProductSerializer(
            least_popular
            )
        most_popular_data = {
            'most_popular': serializer_most_popular_product.data,
            'occurance': count_most
            }
        least_popular_data = {
            'least_popular': serializer_least_popular_product.data,
            'occurance': count_least
            }
        popularity_metric = [most_popular_data, least_popular_data]
        return Response({"sales_per_month": sales_per_month,
                         'popularity_metric': popularity_metric})


class ListProductViewset(viewsets.ModelViewSet):
    """List the products available at the shop"""
    serializer_class = ProductSerializer
    queryset = models.Product.objects.all()
    renderer_classes = [JSONRenderer]
    http_method_names = ['get']

    def get_queryset(self):
        return models.Product.objects.all()

    def list(self, request):
        products = self.get_queryset().order_by("id")
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)


class DestroyProductViewSet(viewsets.ModelViewSet):
    """Allows admin to destroy products"""
    serializer_class = ProductSerializer
    queryset = models.Product.objects.all()
    renderer_classes = [JSONRenderer]
    http_method_names = ['delete']
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [IsAdminUser]

    def destroy(self, request, pk):
        if request.user.is_staff:
            product = models.Product.objects.get(id=pk)
            product.delete()
            return Response(
                {"Message": "Successful deletion"},
                status=status.HTTP_204_NO_CONTENT
                )
        else:
            # scare off the hackers
            return Response(
                {"Message": "You will be reported to the police if you try"},
                status=status.HTTP_403_FORBIDDEN
                )


class CreateProduct(APIView):
    """Create product if staff"""
    serializer_class = ProductSerializer
    queryset = models.Product.objects.all()
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [IsAdminUser]

    def post(self, request):
        """Create product"""
        # for some odd reason this logic works here
        # but not in ListProductViewset

        user = request.user
        if user.is_staff:
            serializer = ProductSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(
                    {"Message": "serializer works"},
                    status=status.HTTP_201_CREATED
                    )
            else:
                return Response(
                    serializer.errors,
                    status=status.HTTP_400_BAD_REQUEST
                    )
        else:
            return Response(
                {"message": "You are not authorised."},
                status=status.HTTP_401_UNAUTHORIZED
                )


class ListCartView(viewsets.ModelViewSet):
    """Users can view items in cart and edit cart"""
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
        # json = JSONRenderer().render(serializer.data)
        products = serializer.data[0]['products']
        user_cart_products = models.Product.objects.filter(pk__in=products)
        products_serialized = ProductSerializer(user_cart_products, many=True)

        return products_serialized.data

    def list(self, request):
        """Returns the list of products in the user's cart"""
        products = self.grab_product_from_cart(request)
        user_cart = models.Cart.objects.filter(user=request.user)
        serializer = self.serializer_class(user_cart, many=True)

        return Response({'id': serializer.data[0]['id'], 'products': products})

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
        # TODO: Join a table then filter it.
        serializer = CartSerializer(user_cart)
        products = serializer.data['products']
        products = models.CartItem.objects.filter(pk__in=products)
        serializer = self.serializer_class(products, many=True)
        user_cart = []

        for product in products:

            serializer = ProductSerializer(product.product)
            user_cart.append({'cart_item_id': product.id,
                              'product': serializer.data,
                              'quantity': product.quantity,
                              })
        return Response(user_cart)

    def create(self, request):
        """Allows user to post user cart items"""
        user = request.user
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            recent_cart_item = serializer.save()
            user_cart = models.Cart.objects.get(user=user)
            user_cart.products.add(recent_cart_item)
            product = models.Product.objects.get(
                pk=recent_cart_item.product.pk
                )
            serializer = ProductSerializer(product)
            res = {'cart_item_id': recent_cart_item.id,
                   'product': serializer.data,
                   'quantity': recent_cart_item.quantity}
            return Response(res, status=status.HTTP_201_CREATED)
        else:
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
                )


class OrderItemViewset(viewsets.ModelViewSet):
    """Users can see their list of orders items """
    serializer_class = OrderItemSerializer
    queryset = models.OrderItem.objects.all()
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.UpdateOwnCart]
    http_method_names = ['get', 'post', 'delete']


class OrderViewset(viewsets.ModelViewSet):
    """Users can see their list of orders """
    serializer_class = OrderSerializer
    queryset = models.Order.objects.all()
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.UpdateOwnOrder]
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_queryset(self):
        return models.Order.objects.all()

    def list(self, request):
        """Display user's list of orders"""
        user = request.user#
        
        # TODO: Find a way to join the order table, the order item table and the product table.
        # Use that fat table and query it. 
        if user.is_staff:
            # if staff return all orders in the data base.
            # maybe change the logic in the future if the amount of orders ,
            # is too much for servers.
            all_orders = models.Order.objects.prefetch_related('order__product').order_by("id")
            serializer = self.serializer_class(
                all_orders,
                many=True
                )
            for order in serializer.data:
                order_item = models.OrderItem.objects.filter(
                    pk__in=order["order"]
                    )
                order_item_serializer = OrderItemSerializer(
                    order_item,
                    many=True
                    )
                order_item_list = []
                for order_item_model in order_item_serializer.data:
                    product_id = order_item_model["product"]
                    product = models.Product.objects.get(id=product_id)
                    product_serializer = ProductSerializer(product)
                    quantity = order_item_model["quantity"]
                    order_item_obj = {
                        "order_item_id": order_item_model["id"],
                        "product": product_serializer.data,
                        "quantity": quantity
                    }
                    order_item_list.append(order_item_obj)
                order.update({"order": order_item_list})
                personal_info_used = models.UserDeliveryInfo.objects.get(
                    pk=order["personal_info_used"]
                    )
                Infoserializer = UserDeliveryInfoSerializer(personal_info_used)
                order.update({"personal_info_used": Infoserializer.data})
            print(len(connection.queries))
            return Response(serializer.data)

        user_order_list = models.OrderList.objects.get(user=user)
        serializer = OrderListSerializer(user_order_list)
        orders = serializer.data["order_list"]
        order = models.Order.objects.filter(pk__in=orders)
        serializer = OrderSerializer(order, many=True)
        for order in serializer.data:
            order_item = models.OrderItem.objects.filter(pk__in=order["order"])
            order_item_serializer = OrderItemSerializer(order_item, many=True)
            order_item_list = []
            for order_item_model in order_item_serializer.data:
                product_id = order_item_model["product"]
                product = models.Product.objects.get(id=product_id)
                product_serializer = ProductSerializer(product)
                quantity = order_item_model["quantity"]
                order_item_obj = {
                    "product": product_serializer.data,
                    "quantity": quantity
                }
                order_item_list.append(order_item_obj)
            order.update({"order": order_item_list})
            personal_info_used = models.UserDeliveryInfo.objects.get(
                pk=order["personal_info_used"]
                )
            Infoserializer = UserDeliveryInfoSerializer(personal_info_used)
            order.update({"personal_info_used": Infoserializer.data})
        """
        {
            "id": 20,
            "user": 2,
            "email": "allifamey487@gmail.com",
            "order": [
            26
            ],
            "personal_info_used": 25,
            "delivery_instructions": "awefawefawef",
            "delivery_status": "Processing Order",
            "date_ordered": "2022-12-24",
            "total_price": "5.99"
        },
        """
        print(len(connection.queries))
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

    @extend_schema(
        request=inline_serializer(
            name="Mass_delete",
            fields={
                "object_type": serializers.CharField(),
                "ids": serializers.ListField(
                    child=serializers.IntegerField(min_value=1)
                    )
                }
            ),
        responses={
            '2XX': inline_serializer(
                name='Success',
                fields={"message": serializers.CharField()}
                )
            }
    )
    def post(self, request):
        """Deletes objects on mass"""
        user = request.user
        object_type = request.data.get("object_type")
        ids = request.data.get("ids")

        if object_type == "cart":
            # TODO: check addition things
            # such as whether those ids listed are related to the user.
            cart_items = models.CartItem.objects.filter(pk__in=ids)
            print(user)
            cart_items.delete()
        return Response({"Message": "Items successfully deleted"})


class UserDeliveryInfoViewset(viewsets.ModelViewSet):
    """Users can see their list of orders items """
    serializer_class = UserDeliveryInfoSerializer
    queryset = models.UserDeliveryInfo.objects.all()
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.UpdateOwnCart]
    http_method_names = ['get', 'post', 'patch', 'delete']

    @extend_schema(
        request=PolymorphicProxySerializer(
            component_name='user_delivery_info',
            serializers=[
                UserDeliveryInfoSerializer,
                inline_serializer(name="user_orders",
                                  fields={
                                      "delivery_msg":
                                          serializers.CharField(
                                              allow_blank=True
                                              ),
                                      "total_price":
                                          serializers.DecimalField(
                                              max_digits=5,
                                              decimal_places=2
                                              ),
                                          }
                                  ),
                ],
            resource_type_field_name='type',
            many=True
            ),
        responses={
            '2XX': inline_serializer(
                name='Order_success',
                fields={
                    "message": serializers.CharField()
                    }
                )
            }
    )
    def create(self, request):
        """Create delivery info and order"""
        user_exist = "Don't know"

        # establish if anonymous user.
        try:
            user = request.user
            user_exist = True
        except:
            user_exist = False
        # process the data and check if user inputted right data
        serializer = self.serializer_class(data=request.data[0])
        if serializer.is_valid():
            # create the deliveryInfo
            # new_deliveryInfo = serializer.save()
            # create the order items by grabbing the user's cart
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
                serializer = OrderItemSerializer(
                    data={
                        "user": user.id,
                        "email": email,
                        "product": product,
                        "quantity": quantity
                        }
                    )
                if serializer.is_valid():
                    new_OrderItem = serializer.save()
                    store_orders.append(new_OrderItem.id)
                else:
                    return Response(
                        serializer.errors,
                        status=status.HTTP_400_BAD_REQUEST
                        )
            # here is where the order
            email = request.data[0]['email']
            serializer = self.serializer_class(data=request.data[0])
            new_delivery_info = None
            if serializer.is_valid():
                new_delivery_info = serializer.save()
            else:
                return Response(
                    serializer.errors,
                    status=status.HTTP_400_BAD_REQUEST
                    )

            serializer = OrderSerializer(
                data={
                    "user": user.id,
                    "email": email,
                    "personal_info_used": new_delivery_info.id,
                    "order": store_orders,
                    "delivery_instructions": request.data[1]["delivery_msg"],
                    "total_price": request.data[1]["total_price"]
                    }
                )
            if serializer.is_valid():
                # lastly attach the user's order to the order list
                # so they can view it and all the necessary information
                new_order = serializer.save()
                if serializer.is_valid():
                    old_OrderList = models.OrderList.objects.get(user=user)
                    old_OrderList.order_list.add(new_order)
                    # now the order is added, delete the cart items.
                    print(user)
                    old_cartItems = models.CartItem.objects.filter(user=user)
                    old_cartItems.delete()
                else:
                    return Response(
                        serializer.errors,
                        status=status.HTTP_400_BAD_REQUEST
                        )
            else:
                return Response(
                    serializer.errors,
                    status=status.HTTP_400_BAD_REQUEST
                    )
            return Response(
                {"message": "order is valid"},
                status=status.HTTP_200_OK
                )
        else:
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
                )


class PostOrderAnonymousAPIView(APIView):
    """Allows users to post orders anonymously"""
    serializer_class = UserDeliveryInfoSerializer

    @extend_schema(
        request=PolymorphicProxySerializer(
            component_name='user_delivery_info_anonymous',
            serializers=[
                UserDeliveryInfoSerializer,
                inline_serializer(
                    name="user_orders_anonymous",
                    fields={
                        "delivery_msg":
                            serializers.CharField(allow_blank=True),
                        "total_price": serializers.DecimalField(
                            max_digits=5,
                            decimal_places=2
                            ),
                        }
                    ),
                inline_serializer(
                    name="user_cart",
                    fields={
                        "products": serializers.ListField(
                            child=inline_serializer(
                                name="user_items_anonymous",
                                fields={
                                    "product_ids":
                                        serializers.IntegerField(min_value=1),
                                    "quantity":
                                        serializers.IntegerField(min_value=1),
                                        }
                                )
                            )
                        }
                    )
                ],
            resource_type_field_name='type',
            many=True,
            ),
        responses={
            '2XX':
                inline_serializer(
                    name='Order_success',
                    fields={
                        "message":
                            serializers.CharField()
                            }
                    )
                }
    )
    def post(self, request):
        """Post orders anonymously."""

        email = request.data[0]['email']
        user_cartItems = request.data[2]['products']
        serializer = self.serializer_class(data=request.data[0])
        if serializer.is_valid():
            # now that the delivery info is valid
            # create the orderitems and attach the email to it.
            # a email is required so issues with their order can be heard
            # email can be used to find their order.
            store_orders = []
            for cartItem in user_cartItems:
                product = cartItem['product_id']
                quantity = cartItem['quantity']
                serializer = OrderItemSerializer(
                    data={
                        "email": email,
                        "product": product,
                        "quantity": quantity
                        }
                    )
                if serializer.is_valid():
                    new_orderItem = serializer.save()
                    store_orders.append(new_orderItem.id)
                else:
                    return Response(
                        serializer.errors,
                        status=status.HTTP_400_BAD_REQUEST
                        )
            serializer = self.serializer_class(data=request.data[0])
            if serializer.is_valid():
                new_delivery_info = serializer.save()
                serializer = OrderSerializer(
                    data={
                        "email": email,
                        "personal_info_used": new_delivery_info.id,
                        "order": store_orders,
                        "delivery_instructions":
                            request.data[1]["delivery_msg"],
                        "total_price":
                            request.data[1]["total_price"]
                        }
                    )
                if serializer.is_valid():
                    serializer.save()
                    return Response({"message": "Order Successful"})
                else:
                    return Response(
                        serializer.errors,
                        status=status.HTTP_400_BAD_REQUEST
                        )
        else:
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
                )
        return Response({"message": "hello"})
