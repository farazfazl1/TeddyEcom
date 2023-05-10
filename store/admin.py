from django.contrib import admin
from .models import Product, Variation, ReviewRating
from django.utils.html import format_html


class ProductAdmin(admin.ModelAdmin):
    list_display = ('thumbnail', 'product_name', 'category', 'stock',
                    'price', 'modified_date', 'is_avalible')
    prepopulated_fields = {
        'slug': ('product_name',)
    }
    list_display_links = ('product_name', 'thumbnail',)
    search_fields = ('id', 'product_name', 'description',
                     'price', 'stock', 'category__category_name',)

    list_filter = ('category',)

    def thumbnail(self, object):
        return format_html(f'<img src="{object.images.url}" width = "40" style="border-radius: 50%"/>')

    thumbnail.short_description = 'Photo'


class VariationAdmin(admin.ModelAdmin):
    list_display = ('product', 'variation_category',
                    'variation_value', 'is_active',)
    list_editable = ('is_active',)
    list_filter = (
        'product',
        'variation_category',
        'variation_value',
        'is_active',
    )

# class ReviewRatingAdmin(admin.ModelAdmin):


admin.site.register(Product, ProductAdmin)
admin.site.register(Variation, VariationAdmin)
admin.site.register(ReviewRating)
