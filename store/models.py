from django.db import models
from category.models import Category
from django.urls import reverse


class Product(models.Model):

    product_name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField(max_length=500, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    images = models.ImageField(upload_to='photos/products')
    stock = models.IntegerField(blank=False)
    is_avalible = models.BooleanField(default=True)

    # models.CASCADE will delete all products attached to a category if that category is deleted
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.product_name

    def get_url(self):
        # this time we take 2 arguments because in our link, we have 2 slugs necessary
        return reverse('store:product_detail_url', args=[self.category.slug, self.slug])


class VariationManager(models.Manager):
    def colors(self):
        return super(VariationManager, self).filter(variation_category='color', is_active=True)

    def materials(self):
        return super(VariationManager, self).filter(variation_category='material', is_active=True)


class Variation(models.Model):
    variation_category_choice = (
        ('material', 'material'),
        ('color', 'color')
    )

    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variation_category = models.CharField(
        max_length=100, choices=variation_category_choice)
    variation_value = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    created_date = models.DateTimeField(auto_now=True)

    objects = VariationManager()

    def __str__(self):
        return self.variation_value
