from django.db import models
from django.urls import reverse


class Category(models.Model):
    category_name = models.CharField(max_length=90, unique=True)

    # slug -> URL OF category and should be unique
    slug = models.SlugField(max_length=255, unique=True)

    description = models.TextField(max_length=350, blank=True)
    image = models.ImageField(upload_to='photos/categories', blank=True)

    class Meta:
        verbose_name = 'category'
        verbose_name_plural = 'categories'

    def __str__(self):
        return self.category_name

    def get_url(self):
        return reverse('store:products_by_category', args=[self.slug])
        # products_by_category is name of the url in urls.py for categories
