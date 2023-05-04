from django.db import models
from accounts.models import Account
from store.models import Product, Variation

"""
Payment Model
    user (ForeignKey User)
    payment_id
    payment_method
    amount_paid
    status
    created_at
"""


class Payment(models.Model):
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    payment_id = models.CharField(max_length=100)
    payment_method = models.CharField(
        max_length=100)  # paypal for this project
    amount_paid = models.CharField(max_length=100)
    status = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.payment_id


"""
Order Model
    user (ForeignKey User)
    payment (ForeignKey Payment)
    order_number
    first_name
    last_name
    phone_number
    email
    address_line_1
    address_line_2
    country
    state
    city
    total
    tax
    status (dropdown New, Accepted, Completed, Cancelled)
    ip_address
    order_note
    is_ordered (Default=False)
    created_at
    updated_at
    
    
user <-
the ForeignKey field in your example specifies that the current model has a many-to-one
relationship with the Account model, and that when an Account instance
is deleted, the foreign key field in the current model will be set to NULL. Additionally,
the user field in the current model can be left blank.
"""


class Order(models.Model):
    STATUS = (
        ('New', 'New'),
        ('Accepted', 'Accepted'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    )

    user = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True)
    payment = models.ForeignKey(
        Payment, on_delete=models.SET_NULL, blank=True, null=True)
    order_number = models.CharField(max_length=20)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone_number = models.CharField(max_length=15)
    email = models.EmailField(max_length=50)
    address_line_1 = models.CharField(max_length=50)
    address_line_2 = models.CharField(max_length=50, blank=True)
    country = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    city = models.CharField(max_length=50)
    order_note = models.CharField(max_length=100, blank=True)
    order_total = models.FloatField()
    tax = models.FloatField()
    status = models.CharField(max_length=10, choices=STATUS, default='New')
    ip = models.CharField(blank=True, max_length=20)
    is_ordered = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def full_name(self):
        return f'{self.first_name} {self.last_name}'

    def full_address(self):
        return f'{self.address_line_1} {self.address_line_2}'

    def __str__(self):
        return self.first_name


"""
Order Product
    order (ForeignKey Order)
    payment (ForeignKey Payment)
    user (ForeignKey User)
    product (ForeignKey Product)
    variation (ForeignKey Variation)
    color
    size
    quantity
    product_price
    is_ordered
    created_at
    updated_at
"""


class OrderProduct(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    payment = models.ForeignKey(
        Payment, on_delete=models.SET_NULL, blank=True, null=True)
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variations = models.ManyToManyField(Variation, blank=True)
    quantity = models.IntegerField()
    product_price = models.FloatField()
    ordered = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.product.product_name
