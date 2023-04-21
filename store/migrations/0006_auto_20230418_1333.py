# Generated by Django 3.2.15 on 2023-04-18 20:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0005_variation'),
    ]

    operations = [
        migrations.AlterField(
            model_name='variation',
            name='variation_category',
            field=models.CharField(choices=[('material', 'material'), ('color', 'color')], max_length=100),
        ),
        migrations.AlterField(
            model_name='variation',
            name='variation_value',
            field=models.CharField(max_length=100, unique=True),
        ),
    ]
