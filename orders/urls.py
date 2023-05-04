from django.urls import path
from orders import views

app_name = 'order'

urlpatterns = [
    path('place-order/', views.place_order, name='place-order'),
    path('place-order/payments/', views.payments, name='payments'),
]
