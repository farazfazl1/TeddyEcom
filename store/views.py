from django.shortcuts import render, get_object_or_404
from .models import Product
from category.models import Category
from carts.models import CartItem
from carts.views import _cart_id


def store(req, category_slug=None):
    categories = None
    products = None

    # If a category slug is specified, get the Category object for that slug
    if category_slug != None:
        categories = get_object_or_404(
            Category, slug=category_slug)

        # Get all products that belong to the specified category and are available
        products = Product.objects.filter(
            category=categories, is_avalible=True)

        # Count the number of products in the category
        product_count = products.count()

    # If no category slug is specified, get all products that are available
    else:
        products = Product.objects.order_by(
            '-created_date').filter(is_avalible=True)

        # Count the number of products
        product_count = products.count()

    # Create a dictionary of variables to be used in the template
    context = {
        'Category': categories,
        'Product': products,
        'product_count': product_count,
    }

    # Render the template with the dictionary of variables
    return render(req, 'pages/store.html', context)



def product_detail(req, category_slug, product_slug):
    try:
        # Get the single Product object that matches the specified category and product slugs
        single_product = Product.objects.get(category__slug=category_slug, slug=product_slug)

        # Check if the product is already in the user's cart
        in_cart = CartItem.objects.filter(cart__cart_id=_cart_id(req), product=single_product).exists()

    except Exception as e:
        raise e

    # Create a dictionary of variables to be used in the template
    context = {
        'product': single_product,
        'in_cart': in_cart, # Add the in_cart variable to the context dictionary
    }

    # Render the template with the dictionary of variables
    return render(req, 'pages/productPage.html', context)

# The in_cart variable checks whether the product is already in the user's 
# cart or not. It does this by using the CartItem.objects.filter() method to 
# look for a CartItem object that has a cart attribute with the same cart_id as the user's current
# cart (as obtained by calling _cart_id(req)), and a product attribute that matches the single_product
# object that we just obtained.

# The exists() method is then called on the resulting queryset to return a boolean
# value indicating whether such a CartItem object exists or not. If it exists, that
# means the product is already in the user's cart, and in_cart is set to True. Otherwise, in_cart 
# is set to False. This in_cart variable is then added to the context dictionary and
# passed to the productPage.html template for use in the template.