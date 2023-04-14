from django.shortcuts import render
from store.models import Product


def home(req):
    product_data = Product.objects.order_by(
        '-created_date').filter(is_avalible=True)

    context = {
        'Product': product_data
    }
    return render(req, 'pages/home.html', context)
