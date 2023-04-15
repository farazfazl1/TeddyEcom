from django.urls import path
from carts import views

app_name = 'cart'

urlpatterns = [
    path('', views.cart, name='cart'),
    path('add-to-cart/<int:product_id>/',
         views.add_to_cart, name='add-to-cart'),
    path('sub-from-cart/<int:product_id>/',
         views.sub_from_cart, name='sub_from_cart'),
    path('remove_full_cart/<int:product_id>/',
         views.remove_full_cart, name='remove_full_cart'),
]
