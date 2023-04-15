from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from store.models import Product
from .models import Cart, CartItem


# This function generates a unique cart ID based on the user's session ID
def _cart_id(req):
    cart = req.session.session_key
    if not cart:
        cart = req.session.create()
    return cart


# This function adds a product to the user's cart when the 'Add to Cart' button is clicked
def add_to_cart(req, product_id):
    # Get the product object from the database using the product ID provided
    product = Product.objects.get(id=product_id)

    try:
        # Try to get the cart object associated with the user's session ID
        cart = Cart.objects.get(cart_id=_cart_id(req))
    except Cart.DoesNotExist:
        # If the cart doesn't exist, create a new one with the session ID
        cart = Cart.objects.create(cart_id=_cart_id(req))

    # Save the cart object
    cart.save()

    try:
        # Try to get the cart item associated with the product and cart objects
        cart_item = CartItem.objects.get(product=product, cart=cart)
        # If the cart item already exists, increment the quantity by 1 and save
        cart_item.cart_quantity += 1
        cart_item.save()
    except CartItem.DoesNotExist:
        # If the cart item doesn't exist, create a new one with a quantity of 1 and save
        cart_item = CartItem.objects.create(
            product=product, cart=cart, cart_quantity=1)
        cart_item.save()

    # Redirect the user to the 'cart' page after the product is added to the cart
    return redirect('cart:cart')


def cart(req, total=0, quantity=0, cart_items=None):
    # Try to get the cart based on the cart id stored in the session
    try:
        cart = Cart.objects.get(cart_id=_cart_id(req))
        # Get all the cart items for this cart that are still active
        cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        # Loop through all the cart items and calculate the total cost and quantity
        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.cart_quantity)
            quantity += cart_item.cart_quantity

        # Calculate 8% tax similar to Cali sales tax
        tax = (8 * total)/100
        grand_total = total + tax
    # If the cart does not exist, do nothing (i.e. no items in cart)
    except Cart.DoesNotExist:
        pass

    # Create a dictionary of data to pass to the template
    context = {
        'total': total,
        'cart_quantity': quantity,
        'cart_items': cart_items,
        'tax': tax,
        'grand_total': grand_total
    }

    # Render the cart template with the context data
    return render(req, 'cart/cart.html', context)


# Function to subtract one quantity from the cart item for a given product
def sub_from_cart(req, product_id):
    # Get the cart associated with the user
    cart = Cart.objects.get(cart_id=_cart_id(req))

    # Get the product that is being modified
    product = get_object_or_404(Product, id=product_id)

    # Get the cart item for the product in the cart
    cart_item = CartItem.objects.get(product=product, cart=cart)

    # If the cart item quantity is greater than 1, subtract 1 and save the item
    if cart_item.cart_quantity > 1:
        cart_item.cart_quantity -= 1
        cart_item.save()
    else:
        # If the quantity is 1 or less, delete the item from the cart
        cart_item.delete()

    # Redirect to the cart page
    return redirect('cart:cart')


# Function to remove a product's entire cart
def remove_full_cart(req, product_id):
    # Get the cart associated with the user
    cart = Cart.objects.get(cart_id=_cart_id(req))

    # Get the product that is being removed
    product = get_object_or_404(Product, id=product_id)

    # Get the cart item for the product in the cart
    cart_item = CartItem.objects.get(product=product, cart=cart)

    # Delete the cart item from the cart
    cart_item.delete()

    # Redirect to the cart page
    return redirect('cart:cart')
