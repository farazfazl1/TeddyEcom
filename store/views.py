from django.shortcuts import render, get_object_or_404, redirect

from orders.models import OrderProduct
from .models import Product, ReviewRating
from django.contrib import messages
from category.models import Category
from carts.models import CartItem
from django.core.paginator import Paginator
from carts.views import _cart_id
from django.db.models import Q
from .forms import ReviewForm


def store(req, category_slug=None):
    categories = None
    products = None

    # If a category slug is specified, get the Category object for that slug
    if category_slug != None:
        categories = get_object_or_404(
            Category, slug=category_slug)

        # Get all products that belong to the specified category and are available
        products = Product.objects.filter(
            category=categories, is_avalible=True).order_by('id')
        # order-by here will remove the error that compiler tells about there's no order

        # Pagination
        paginator = Paginator(products, 3)
        page = req.GET.get('page')
        paged_products = paginator.get_page(page)

        # Count the number of products in the category
        product_count = products.count()

    # If no category slug is specified, get all products that are available
    else:
        products = Product.objects.order_by(
            '-created_date').filter(is_avalible=True)

        paginator = Paginator(products, 6)
        page = req.GET.get('page')

        paged_products = paginator.get_page(page)

        # Count the number of products
        product_count = products.count()

    # Create a dictionary of variables to be used in the template
    context = {
        'Category': categories,
        'Product': paged_products,
        'product_count': product_count,
    }

    # Render the template with the dictionary of variables
    return render(req, 'pages/store.html', context)


def product_detail(req, category_slug, product_slug):
    try:
        # Get the single Product object that matches the specified category and product slugs
        single_product = Product.objects.get(
            category__slug=category_slug, slug=product_slug)

        # Check if the product is already in the user's cart
        in_cart = CartItem.objects.filter(
            cart__cart_id=_cart_id(req), product=single_product).exists()

    except Exception as e:
        raise e

    if req.user.is_authenticated:
        try:
            ordered_product = OrderProduct.objects.filter(
                user=req.user, product_id=single_product.id).exists()

        except OrderProduct.DoesNotExist:
            ordered_product = None
    else:
        ordered_product = None

    # Get all the reviews
    # When admin doesnt want to show a particular reivew, they can turn status False to make reivew dissapear
    reviews = ReviewRating.objects.filter(
        product_id=single_product.id, status=True)

    # Create a dictionary of variables to be used in the template
    context = {
        'product': single_product,
        'in_cart': in_cart,  # Add the in_cart variable to the context dictionary,
        'ordered_product': ordered_product,
        'reviews': reviews
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


# SEARCH BASED ON PROUDCT DESCRIPTION
def search(req):
    if 'keyword' in req.GET:
        # Retrieve the search keyword from the query string
        keyword = req.GET['keyword']

        if keyword:
            # Filter the Product objects based on the search keyword
            # Use the `Q` object to make a complex query with multiple filters
            # The `icontains` lookup retrieves objects where the description field contains the keyword, case-insensitive
            # The `iexact` lookup retrieves objects where the product_name field matches the keyword exactly, case-insensitive
            products = Product.objects.order_by('-created_date').filter(
                Q(description__icontains=keyword) | Q(product_name__iexact=keyword))
            # Get the count of products that match the search keyword
            product_count = products.count()

        # Print the search keyword to the console
        print(keyword)

    # Create a dictionary of variables to be used in the template
    context = {
        'Product': products,  # Add the products variable to the context dictionary
        'product_count': product_count
    }

    # Render the template with the dictionary of variables
    return render(req, 'pages/store.html', context)


def submit_review(req, product_id):
    url = req.META.get('HTTP_REFERER')  # store the already existing URL
    if req.method == 'POST':
        try:
            review = ReviewRating.objects.get(
                user__id=req.user.id, product__id=product_id)
            form = ReviewForm(req.POST, instance=review)

            if form.is_valid():
                form.save()  # Save the updated form

                messages.success(
                    req, 'Thank you. Your review has been updated')
            else:
                messages.error(req, 'Failed to update the review')

            return redirect(url)

        except ReviewRating.DoesNotExist:
            form = ReviewForm(req.POST)

            if form.is_valid():
                data = form.save(commit=False)
                data.ip_address = req.META.get('REMOTE_ADDR')
                data.product_id = product_id
                data.user_id = req.user.id
                data.save()

                messages.success(
                    req, 'Thank you. Your review has been submitted')
            else:
                messages.error(req, 'Failed to submit the review')

            return redirect(url)
