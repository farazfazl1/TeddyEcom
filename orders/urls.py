from django.urls import path, include
from orders import views

app_name = 'order'

urlpatterns = [
    path('place-order/', views.place_order, name='place-order'),

    # PAYMENT
    path('place-order/payments/',
         views.payments, name='payments'),

    path('place-order/payments/successful', views.successful_payments, name='successful-payments')

]
