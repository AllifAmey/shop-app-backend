"""
Models for the shop
"""
from django.db import models
from django.conf import settings

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
    """Individual product ordered by the User"""
    user = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		on_delete=models.CASCADE
		)
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
         return f'{self.user} ordered {self.product} {self.quantity} times at {self.date_ordered}'

class Order(models.Model):
    """Orders for each user"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    order = models.ManyToManyField(
        OrderItem,
        
    )
    delivery_status = models.CharField(max_length=255, blank=True, default="Processing Order")
    date_ordered = models.DateField(
        auto_now=True
    )
    total_price = models.DecimalField(max_digits=5, decimal_places=2)
    
    
    def __str__(self):
        """Return the model as a string"""
        return f'{self.user}\'s order posted at {self.date_ordered} with delivery status of {self.delivery_status}'
    
class OrderList(models.Model):
    "Complete list of Orders for each User"
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
		on_delete=models.CASCADE
    )
    order_list = models.ManyToManyField(
        Order,
    )
    
    def __str__(self):
        """Return the model as a string"""
        return f'{self.user}\'s list of orders'
    