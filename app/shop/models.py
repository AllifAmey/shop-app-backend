"""
Models for the shop
"""
from django.db import models
from django.conf import settings
from django.core.validators import RegexValidator
"""
Model name:
Product
Model fields:
Id: 1
Name: Charfield
ImageUrl: URLfield
price: decimalfield
longDescription: Textfield
shortDescription: Textfield (use #) as a separator for frontend

keep the below in mind as the product model relies on the id to generate the card1 and card2 id.
python manage.py sqlsequencereset myapp1 myapp2 myapp3
"""

class Product(models.Model):
    """individual product in the shop"""
    name = models.CharField(max_length=255)
    image_url = models.URLField(max_length=255)
    price = models.DecimalField(max_digits=5, decimal_places=2)
    description_short = models.TextField()
    description_long = models.TextField()
    catagory = models.CharField(max_length=255, default="Ring")

    def __str__(self):
        """Return the model as a string"""
        return self.name

class CartItem(models.Model):
    """Individual product with quantity in Cart"""
    user = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		on_delete=models.CASCADE
		)
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE
    )
    quantity = models.IntegerField(
    )
    
    def __str__(self):
         """Return the model as a string"""
         return f'{self.user} wants {self.product} {self.quantity} times'

class Cart(models.Model):
    """Cart for each user"""
    user = models.OneToOneField(
		settings.AUTH_USER_MODEL,
		on_delete=models.CASCADE
		)
    
    products = models.ManyToManyField(
        CartItem,
        blank=True,
    )

    def __str__(self):
        """Return the model as a string"""
        return f'{self.user}\'s cart'



class OrderItem(models.Model):
    """Individual product ordered by the User/anonymous user"""
    user = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		on_delete=models.CASCADE,
        blank=True,
        null=True
		)
    email = models.EmailField(max_length=255, blank=True, null=True)
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE
    )
    quantity = models.IntegerField()
    date_ordered = models.DateField(
        auto_now=True
    )
    
    
    def __str__(self):
         """Return the model as a string"""
         return f'{self.email if self.user == None else self.user} ordered {self.product} {self.quantity} times at {self.date_ordered}'
     
class UserDeliveryInfo(models.Model):
    """User info to help delivering items"""
    # email is not optional here but user is. Anonymous orders dont need users
    # anonymous orders need emails and every order does by default to establish,
    # to connect the data to the database.
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=True, null=True)
    first_name= models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField(max_length=255)
    phone_number = models.CharField(max_length=255)
    address = models.TextField()
    city = models.CharField(max_length=255)
    country = models.CharField(max_length=255)
    post_code = models.CharField(max_length=255)
    delivery_type = models.CharField(max_length=255)
    
    def __str__(self):
        """Return the model as a string"""
        return f'{self.email if self.user == None else self.user}\'s User Delivery Info'

class Order(models.Model):
    """Orders for each user/anonymous user"""
    # for future referance user and email are both optional when creating an order.
    # users 
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=True, null=True)
    email = models.EmailField(max_length=255, blank=True, null=True)
    order = models.ManyToManyField(
        OrderItem,
    )
    personal_info_used = models.OneToOneField(
        UserDeliveryInfo,
        on_delete=models.CASCADE,
        null=True
    )
    delivery_instructions = models.TextField(null=True, blank=True)
    delivery_status = models.CharField(max_length=255, blank=True, default="Processing Order")
    date_ordered = models.DateField(
        auto_now=True
    )
    total_price = models.DecimalField(max_digits=5, decimal_places=2)
    
    
    def __str__(self):
        """Return the model as a string"""
        return f'{self.email if self.user == None else self.user}\'s order posted at {self.date_ordered} with delivery status of {self.delivery_status}'
    
class OrderList(models.Model):
    "Complete list of Orders for each User"
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
		on_delete=models.CASCADE,
    )
    order_list = models.ManyToManyField(
        Order,
    )
    
    def __str__(self):
        """Return the model as a string"""
        return f'{self.user}\'s list of orders'
    

class DefaultUserDeliveryInfo(models.Model):
    """Default User info for delivering items"""
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
		on_delete=models.CASCADE,
        blank=True,
        null=True
    )
    
    default_info = models.OneToOneField(
        UserDeliveryInfo,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    def __str__(self):
        """Return the model as a string"""
        return f'{self.user}\'s default User Delivery Info'

