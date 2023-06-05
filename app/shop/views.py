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
    UserDeliveryInfoSerializer,
    ExternalSerializer
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
import requests
import json


class DataAnalysisShopAPIView(APIView):
    """Analysis of the backend data and returns result"""
    queryset = models.Order.objects.all()
    renderer_classes = [JSONRenderer]
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        return models.Order.objects.all()

    def get(self, request):
        """Calculate and retrieve backend analysis."""
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
        monthly_sales = models.Order.objects.annotate(
            month=ExtractMonth('date_ordered'))\
            .values('month').annotate(total_sales=Sum('total_price'))
        for sale in monthly_sales:
            sales_per_month[sale['month']-1]['sale'] = sale['total_sales']
        most_popular = models.Product.objects.annotate(
            num_orderItem=Count('orderitem')).order_by("-num_orderItem")[0]
        least_popular = models.Product.objects.annotate(
            num_orderItem=Count('orderitem')).order_by("num_orderItem")[0]
        count_most = models.OrderItem.objects.filter(
            product=most_popular).count()
        count_least = models.OrderItem.objects.filter(
            product=least_popular).count()
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
        # from O(n+1) to O(6) - achievement note.
        for sql in enumerate(connection.queries):
            if sql[0] != 0:
                print(f'SQL Number {sql[0]}')
                print(sql[1]['sql'])
                print("\n")

        return Response({"sales_per_month": sales_per_month,
                         'popularity_metric': popularity_metric},
                        status=status.HTTP_200_OK)


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
        """Destroys product according to PK given."""
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


class CartItemViewset(viewsets.ModelViewSet):
    """Users can create cart items"""
    serializer_class = CartItemSerializer
    queryset = models.CartItem.objects.all()
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = (permissions.UpdateOwnCart, )

    def list(self, request):
        """Displays user's cart"""
        # this should be the optimal way only 1 query is done to get user data.
        # query reduced rom 6 to 2 - achievement note.
        products = models.CartItem.objects.select_related('product')\
            .filter(user=request.user)
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
        # check if user requesting is user
        if request.user.id != request.data['user']:
            return Response({'Message': "Unauthorised"},
                            status=status.HTTP_401_UNAUTHORIZED)
        # check request.data is validated
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            # get product id
            new_product_id = serializer.validated_data['product'].id
            # this checks if the product already exist in user cart.
            user_cart = models.CartItem.objects\
                .select_related('product')\
                .filter(user=request.user)\
                .values_list('product')\
                .filter(product__id=new_product_id)\
                .count()
            # if an existing product is found in cart
            if user_cart >= 1:
                # do a patch
                existing_cartItem = models.CartItem.objects\
                    .select_related('product')\
                    .filter(user=request.user, product__id=new_product_id)
                existing_cartItem.update(
                    quantity=existing_cartItem[0]
                    .quantity+request.data['quantity'])
                product = models.Product.objects.get(
                    pk=existing_cartItem[0].product.pk
                    )
                serializer = ProductSerializer(product)
                return Response(
                    {'cart_item_id': existing_cartItem[0].id,
                     'product': serializer.data,
                     'quantity': existing_cartItem[0].quantity},
                    status=status.HTTP_201_CREATED)
            else:
                # do a post
                recent_cart_item = serializer.save()
                print('Queries performed:', len(connection.queries))
                product = models.Product.objects.get(
                    pk=recent_cart_item.product.pk
                    )
                print('Queries performed:', len(connection.queries))
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
    http_method_names = ['get', 'post', 'patch']

    def get_queryset(self):
        return models.Order.objects.all()

    def list(self, request):
        """Display user's list of orders"""
        user = request.user

        # TODO: Find a way to join the order table,
        # the order item table and the product table.
        # Use that fat table and query it.
        if user.is_staff:
            # if staff return all orders in the data base.
            # maybe change the logic in the future if the amount of orders ,
            # is too much for servers.
            all_orders = models.Order.objects\
                .prefetch_related('order__product').order_by("id")
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
                name='Order_success_user',
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
        except Exception:
            user_exist = False
        # process the data and check if user inputted right data
        serializer = self.serializer_class(data=request.data[0])
        if serializer.is_valid():
            # create the deliveryInfo
            # new_deliveryInfo = serializer.save()
            # create the order items by grabbing the user's cart
            if request.user.id != request.data[0]['user']:
                # stop request if not user.
                return Response(
                    {"Message": "You have been reported to the police"},
                    status=status.HTTP_403_FORBIDDEN
                    )
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
                status=status.HTTP_201_CREATED
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
                    name='Order_success_anonymous',
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


class ExternalAPIView(APIView):
    """Handles external stuff"""
    serializer_class = ExternalSerializer

    def post(self, request):
        """Recieves and handles"""
        # note:
        # I am not sure if I should use environmental variables
        # no one is going to see this codebase anyway.
        if request.data['type'] == "weather":
            weather_api_key = "d5f13bf4e6778a1974946a9ce14e7428"
            r = requests.get(
                "https://api.openweathermap.org"
                "/data/2.5/weather?q=London,"
                f"uk&APPID={weather_api_key}")
            res = r.json()
            weather_icon = res["weather"][0]["icon"]
            return Response({"message": f"{weather_icon}"})
        if request.data['type'] == "email":
            email_params = json.loads(request.data["content"])
            emailjs_api_key = "yuixfm0RKnxAsx74W"
            service_id = "service_cwfc9gm"
            template_id = "template_2406ad3"
            data = {
                "service_id": service_id,
                "template_id": template_id,
                "user_id": emailjs_api_key,
                "template_params": {
                    "first_name": email_params["first_name"],
                    "last_name": email_params["last_name"],
                    "your_name": email_params["your_name"],
                    "email": email_params["email"],
                    "phone_number": email_params["phone_number"],
                    "message": email_params["message"]
                    },
                "accessToken": "wBzl314qFvQ5CKZOrk7wL",
                }
            r = requests.post(
                'https://api.emailjs.com/api/v1.0/email/send',
                json=data)
            if r.status_code != 200:
                return Response(
                    {"Message": "Error"}, status=status.HTTP_400_BAD_REQUEST)
            return Response({"Message": "Success"}, status=status.HTTP_200_OK)
        return Response({"Message": "Hello there wonderer"})
