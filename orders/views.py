import datetime
from django.shortcuts import render, redirect
from carts.models import CartItem
from .models import Order
from .forms import OrderForm


def payments(req):
    return render(req, 'orders/payment.html')


def place_order(req, total=0, quantity=0):
    current_user = req.user

    # if the cart count is less than or equal to 0, then redirect back to home page
    cart_items = CartItem.objects.filter(user=current_user)
    print(f'cart items {cart_items}')

    cart_count = cart_items.count()

    if cart_count <= 0:
        return redirect('store:store')

    grand_total = 0
    tax = 0

    for cart_item in cart_items:
        total += (cart_item.product.price * cart_item.cart_quantity)
        quantity += cart_item.cart_quantity

    tax = (2 * total)/100
    grand_total = total + tax

    if req.method == 'POST':
        form = OrderForm(req.POST)

        if form.is_valid():

            # store al the billing info inside Order Table
            data = Order()
            data.user = current_user
            data.first_name = form.cleaned_data['first_name']
            data.last_name = form.cleaned_data['last_name']
            data.phone_number = form.cleaned_data['phone_number']
            data.email = form.cleaned_data['email']
            data.address_line_1 = form.cleaned_data['address_line_1']
            data.address_line_2 = form.cleaned_data['address_line_2']
            data.country = form.cleaned_data['country']
            data.state = form.cleaned_data['state']
            data.city = form.cleaned_data['city']
            data.order_note = form.cleaned_data['order_note']
            data.order_total = grand_total
            data.tax = tax
            # Gives you the user IP Address
            data.ip = req.META.get('REMOTE_ADDR')
            data.save()

            # To generate our order ID, we'll take current day,month,year and add it to order id
            yr = int(datetime.date.today().strftime('%Y'))
            dt = int(datetime.date.today().strftime('%d'))
            mt = int(datetime.date.today().strftime('%m'))
            d = datetime.date(yr, mt, dt)
            current_date = d.strftime("%Y%m%d")  # 20230502
            order_number = current_date + str(data.id)
            data.order_number = order_number

            data.save()

            order = Order.objects.get(
                user=current_user, is_ordered=False, order_number=order_number)

            context = {
                'order': order,
                'cart_items': cart_items,
                'total': total,
                'tax': tax,
                'grand_total': grand_total
            }
            return render(req, 'orders/payment.html', context)
    else:
        return redirect('cart:checkout')

    return render(req, 'pages/home.html')
