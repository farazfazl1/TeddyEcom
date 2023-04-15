from .models import Cart, CartItem
from .views import _cart_id


def counter(req):
    # Initialize the cart count to zero
    cart_count = 0

    # Check if 'admin' is in the request path, and return an empty dictionary if true
    if 'admin' in req.path:
        return {}
    # Otherwise, continue with the cart count calculation
    else:
        try:
            # Get the cart associated with the current request
            cart = Cart.objects.filter(cart_id=_cart_id(req))

            # Get all cart items associated with the cart and sum their quantities
            cart_items = CartItem.objects.all().filter(cart=cart[:1])
            for item in cart_items:
                cart_count += item.cart_quantity

        # If the cart doesn't exist, set the cart count to zero
        except Cart.DoesNotExist:
            cart_count = 0

    # Return a dictionary containing the calculated cart count
    return dict(cart_count=cart_count)
