# Generated by Django 4.1.3 on 2022-12-11 15:22

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0004_alter_cart_products_order_delivery'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order',
            name='orders',
        ),
        migrations.AddField(
            model_name='order',
            name='orders',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to='shop.cart'),
        ),
    ]
