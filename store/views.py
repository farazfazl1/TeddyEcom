from django.shortcuts import render, get_object_or_404
from .models import Product
from category.models import Category


def store(req, category_slug=None):
    categories = None
    products = None

    if category_slug != None:
        categories = get_object_or_404(
            Category, slug=category_slug)  # gets categories
        # will being us all products from particualr category
        products = Product.objects.filter(
            category=categories, is_avalible=True)
        # A feature is asking how many products are in there, so we use the count to count the product amount
        product_count = products.count()

    else:
        products = Product.objects.order_by(
            '-created_date').filter(is_avalible=True)
        # A feature is asking how many products are in there, so we use the count to count the product amount
        product_count = products.count()

    context = {
        'Category': categories,
        'Product': products,
        'product_count': product_count,
    }
    return render(req, 'pages/store.html', context)


def product_detail(req, category_slug, product_slug):
    #category __ slug is the syntax for product's Category that in Category it has slug
    try:
        single_product = Product.objects.get(category__slug=category_slug, slug=product_slug)
    except Exception as e:
        raise e
    context = {
        'product': single_product
    }
        
    return render(req, 'pages/productPage.html', context)
