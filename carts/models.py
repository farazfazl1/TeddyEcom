from django.db import models
from store.models import Product, Variation
from accounts.models import Account


class Cart(models.Model):
    cart_id = models.CharField(max_length=250, blank=True)
    date_added = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.cart_id


class CartItem(models.Model):
    # if user is deleted, so as the cart
    user = models.ForeignKey(Account, on_delete=models.CASCADE, null=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variations = models.ManyToManyField(Variation, blank=True)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, null=True)
    cart_quantity = models.IntegerField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f'{self.cart_quantity} x {self.product.product_name}'

    def sub_total(self):
        return self.product.price * self.cart_quantity
