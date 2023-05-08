import datetime
import json
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from carts.models import CartItem
from store.models import Product
from .models import Order, OrderProduct, Payment
from .forms import OrderForm
from django.db import transaction

from django.template.loader import render_to_string
from django.core.mail import send_mail


@transaction.atomic  # makes stock go down when order takes place
def payments(req):
    body = json.loads(req.body)
    order = get_object_or_404(Order, user=req.user,
                              is_ordered=False, order_number=body['orderID'])

    payment = Payment(
        user=req.user,
        payment_id=body['transID'],
        payment_method=body['payment_method'],
        amount_paid=order.order_total,
        status=body['status'],
    )
    payment.save()
    print(payment.status)

    # updating the order model's payment
    order.payment = payment

    # Now order is successful
    order.is_ordered = True
    order.save()

    # Move the cart items to OrderProduct Table
    cart_items = CartItem.objects.filter(user=req.user)

    for item in cart_items:
        ordered_product = OrderProduct()
        ordered_product.order_id = order.id
        ordered_product.payment = payment
        ordered_product.user_id = req.user.id
        ordered_product.product_id = item.product_id
        ordered_product.quantity = item.cart_quantity
        ordered_product.product_price = item.product.price
        ordered_product.ordered = True
        ordered_product.save()

        # Fetch Variations to the products ordered that have variation included
        cart_item = CartItem.objects.get(id=item.id)

        product_variation = cart_item.variations.all()

        ordered_product = OrderProduct.objects.get(id=ordered_product.id)
        ordered_product.variations.set(product_variation)

        ordered_product.save()

    # Reduce the quantity of the sold products
        product = Product.objects.get(id=item.product.id)
        product.stock -= item.cart_quantity
        product.save()

    # Clear Cart
    CartItem.objects.filter(user=req.user).delete()

    # Send order recieved email to customer
    mail_subject = f'From TeddyEcom: ORDER #{order.order_number} RECIEVED'
    message = render_to_string('emails/order_recieved.html', {
        'user': req.user,
        'orders': order,
    })
    to_email = req.user.email
    # send_email = EmailMessage(mail_subject, message, to=[to_email])
    send_mail(mail_subject, message, 'TeddyEcom <faraztestingdeveloper@gmail.com>   ',
              [to_email], fail_silently=False)

    # Send order number and transaction id back to JSON
    # this is for the send data functun in payments.html javascript section
    data = {
        'order_number': order.order_number,
        'transID': payment.payment_id,
    }

    return JsonResponse(data)


# ------------
def place_order(req, total=0, quantity=0):

    current_user = req.user

    # if the cart count is less than or equal to 0, then redirect back to home page
    cart_items = CartItem.objects.filter(user=current_user)

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


def successful_payments(req):

    order_number = req.GET.get('order_number')
    transID = req.GET.get('payment_id')

    try:
        order = Order.objects.get(order_number=order_number, is_ordered=True)
        ordered_products = OrderProduct.objects.filter(order_id=order.id)
        
        subtotal = 0
        
        for i in ordered_products:
            subtotal += i.product_price * i.quantity
        payment = Payment.objects.get(payment_id = transID)

        context = {
            'order': order,
            'ordered_products': ordered_products,
            'order_number': order.order_number,
            'transaction': transID,
            'payment': payment, #FOR STATUS OF PAYMENT COMING FROM PAYPAL WHEN COMPLETED,
            'subtotal': subtotal
            
            
            
        }
    except (Payment.DoesNotExist, Order.DoesNotExist):
        return redirect('store:store')

    return render(req, 'orders/successful.html', context)
