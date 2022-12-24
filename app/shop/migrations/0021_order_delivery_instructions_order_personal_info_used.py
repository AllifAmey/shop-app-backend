# Generated by Django 4.1.3 on 2022-12-21 21:25

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0020_alter_defaultuserdeliveryinfo_default_info'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='delivery_instructions',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='order',
            name='personal_info_used',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to='shop.userdeliveryinfo'),
        ),
    ]