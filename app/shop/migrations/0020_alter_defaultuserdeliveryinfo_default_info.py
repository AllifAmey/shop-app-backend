# Generated by Django 4.1.3 on 2022-12-21 21:15

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0019_userdeliveryinfo_defaultuserdeliveryinfo'),
    ]

    operations = [
        migrations.AlterField(
            model_name='defaultuserdeliveryinfo',
            name='default_info',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='shop.userdeliveryinfo'),
        ),
    ]
