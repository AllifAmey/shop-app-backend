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

class Cart(models.Model):
    """Cart for each user"""
    user = models.OneToOneField(
		settings.AUTH_USER_MODEL,
		on_delete=models.CASCADE
		)
    products = models.ManyToManyField(
        Product
    )

    def __str__(self):
        """Return the model as a string"""
        return f'{self.user}\'s cart'