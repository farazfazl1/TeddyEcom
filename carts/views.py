
from django.shortcuts import render, redirect, get_object_or_404
from store.models import Product
from .models import Cart, CartItem
from store.models import Variation
from django.contrib.auth.decorators import login_required

# This function generates a unique cart ID based on the user's session ID


def _cart_id(req):
    cart = req.session.session_key
    if not cart:
        cart = req.session.create()
    return cart


# This function adds a product to the user's cart when the 'Add to Cart' button is clicked
def add_to_cart(req, product_id):
    current_user = req.user
    # Get the product object from the database using the product ID provided
    product = Product.objects.get(id=product_id)

    # if user is authenticated
    if current_user.is_authenticated:
        product_variation = []

        # Check if the form has been submitted using the POST method
        if req.method == 'POST':
            # Loop through all the form input elements submitted in the POST request
            for item in req.POST:
                # Get the name of the form input element that was submitted
                key = item

                # Get the selected value for the form input element
                value = req.POST[key]

                # Attempt to retrieve a Variation object with the corresponding category and value
                try:
                    variation = Variation.objects.get(
                        product=product,
                        variation_category__iexact=key,
                        variation_value__iexact=value)
                    # Append the retrieved Variation object to the product_variation list
                    product_variation.append(variation)
                except:
                    # If a Variation object with the corresponding category and value cannot be found, ignore it
                    pass

        # Check if the product is already in the cart
        does_cart_item_exist = CartItem.objects.filter(
            product=product, user=current_user).exists()

        if does_cart_item_exist:
            # If the cart item already exists, get the existing cart item and update its quantity
            cart_item = CartItem.objects.filter(
                product=product, user=current_user)
            existing_variation_list = []
            id = []

            for item in cart_item:
                # Get a list of all the variations associated with the existing cart item
                existing_variation = item.variations.all()
                existing_variation_list.append(list(existing_variation))
                id.append(item.id)

            if product_variation in existing_variation_list:
                # If the new product variation matches an existing cart item's variations, increase or decrease its quantity
                index = existing_variation_list.index(product_variation)
                item_id = id[index]
                item = CartItem.objects.get(product=product, id=item_id)
                item.cart_quantity += 1
                item.save()
            else:
                # If the new product variation doesn't match any existing cart item's variations, update the cart item's variations
                item = CartItem.objects.create(
                    product=product, cart_quantity=1, user=current_user)
                if len(product_variation) > 0:
                    item.variations.clear()
                    item.variations.add(*product_variation)

                # Increment the cart item's quantity by 1 and save it
                item.save()
        else:
            # If the cart item doesn't exist, create a new one with a quantity of 1 and save it
            cart_item = CartItem.objects.create(
                product=product, cart_quantity=1, user=current_user)

            if len(product_variation) > 0:
                cart_item.variations.clear()
                cart_item.variations.add(*product_variation)

            # Save the cart item
            cart_item.save()

        # Redirect the user to the 'cart' page after the product is added to the cart
        return redirect('cart:cart')

    # if user is not authenticated
    else:
        product_variation = []

        # Check if the form has been submitted using the POST method
        if req.method == 'POST':
            # Loop through all the form input elements submitted in the POST request
            for item in req.POST:
                # Get the name of the form input element that was submitted
                key = item

                # Get the selected value for the form input element
                value = req.POST[key]

                # Attempt to retrieve a Variation object with the corresponding category and value
                try:
                    variation = Variation.objects.get(
                        product=product,
                        variation_category__iexact=key,
                        variation_value__iexact=value)
                    # Append the retrieved Variation object to the product_variation list
                    product_variation.append(variation)
                except:
                    # If a Variation object with the corresponding category and value cannot be found, ignore it
                    pass

        try:
            # Try to get the cart object associated with the user's session ID
            cart = Cart.objects.get(cart_id=_cart_id(req))
        except Cart.DoesNotExist:
            # If the cart doesn't exist, create a new one with the session ID
            cart = Cart.objects.create(cart_id=_cart_id(req))

        # Save the cart object
        cart.save()

        # Check if the product is already in the cart
        does_cart_item_exist = CartItem.objects.filter(
            product=product, cart=cart).exists()

        if does_cart_item_exist:
            # If the cart item already exists, get the existing cart item and update its quantity
            cart_item = CartItem.objects.filter(product=product, cart=cart)
            existing_variation_list = []
            id = []

            for item in cart_item:
                # Get a list of all the variations associated with the existing cart item
                existing_variation = item.variations.all()
                existing_variation_list.append(list(existing_variation))
                id.append(item.id)

            if product_variation in existing_variation_list:
                # If the new product variation matches an existing cart item's variations, increase or decrease its quantity
                index = existing_variation_list.index(product_variation)
                item_id = id[index]
                item = CartItem.objects.get(product=product, id=item_id)
                item.cart_quantity += 1
                item.save()
            else:
                # If the new product variation doesn't match any existing cart item's variations, update the cart item's variations
                item = CartItem.objects.create(
                    product=product, cart_quantity=1, cart=cart)
                if len(product_variation) > 0:
                    item.variations.clear()
                    item.variations.add(*product_variation)

                # Increment the cart item's quantity by 1 and save it
                item.save()
        else:
            # If the cart item doesn't exist, create a new one with a quantity of 1 and save it
            cart_item = CartItem.objects.create(
                product=product, cart_quantity=1, cart=cart)

            if len(product_variation) > 0:
                cart_item.variations.clear()
                cart_item.variations.add(*product_variation)

            # Save the cart item
            cart_item.save()

        # Redirect the user to the 'cart' page after the product is added to the cart
        return redirect('cart:cart')


def cart(req, total=0, quantity=0, cart_items=None):
    tax = 0
    grand_total = 0
    # Try to get the cart based on the cart id stored in the session
    try:
        if req.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=req.user, is_active=True)

        else:
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
        'grand_total': grand_total,
    }

    # Render the cart template with the context data
    return render(req, 'cart/cart.html', context)


# Function to subtract one quantity from the cart item for a given product
def sub_from_cart(req, product_id, cart_item_id):

    # Get the product that is being modified
    product = get_object_or_404(Product, id=product_id)

    try:
        if req.user.is_authenticated:
            # Get the cart item for the product in the cart
            cart_item = CartItem.objects.get(
                product=product, user=req.user, id=cart_item_id)
        else:
            # Get the cart associated with the user
            cart = Cart.objects.get(cart_id=_cart_id(req))
        # If the cart item quantity is greater than 1, subtract 1 and save the item
        if cart_item.cart_quantity > 1:
            cart_item.cart_quantity -= 1
            cart_item.save()
        else:
            # If the quantity is 1 or less, delete the item from the cart
            cart_item.delete()
    except:
        pass

    # Redirect to the cart page
    return redirect('cart:cart')


# Function to remove a product's entire cart
def remove_full_cart(req, product_id, cart_item_id):    

    # Get the product that is being removed
    product = get_object_or_404(Product, id=product_id)
    
    if req.user.is_authenticated:
        # Get the cart item for the product in the cart
        cart_item = CartItem.objects.get(
            product=product, user=req.user, id=cart_item_id)
    else:
        # Get the cart associated with the user
        cart = Cart.objects.get(cart_id=_cart_id(req))
        cart_item = CartItem.objects.get(
            product=product, cart=cart, id=cart_item_id)

    # Delete the cart item from the cart
    cart_item.delete()

    # Redirect to the cart page
    return redirect('cart:cart')


@login_required(login_url='users:login-user')
def checkout(req, total=0, quantity=0, cart_items=None):
    tax = 0
    grand_total = 0
    # Try to get the cart based on the cart id stored in the session
    try:
        if req.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=req.user, is_active=True)

        else:
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
        print("ERROR")
        pass

    # Create a dictionary of data to pass to the template
    context = {
        'total': total,
        'cart_quantity': quantity,
        'cart_items': cart_items,
        'tax': tax,
        'grand_total': grand_total,
    }
    return render(req, 'cart/checkout.html', context)
