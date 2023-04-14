from django.contrib import admin
from .models import Product
from django.utils.html import format_html


class ProductAdmin(admin.ModelAdmin):
    list_display = ('thumbnail', 'product_name', 'category', 'stock',
                    'price', 'modified_date', 'is_avalible')
    prepopulated_fields = {
        'slug': ('product_name',)
    }
    list_display_links = ('product_name', 'thumbnail',)
    search_fields = ('id', 'category', 'product_name',
                     'description', 'price', 'stock',)
    list_filter = ('category',)

    def thumbnail(self, object):
        return format_html(f'<img src="{object.images.url}" width = "40" style="border-radius: 50%"/>')

    thumbnail.short_description = 'Photo'


admin.site.register(Product, ProductAdmin)
