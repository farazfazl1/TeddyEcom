from django.contrib import admin
from .models import Order, OrderProduct, Payment


class OrderProductInline(admin.TabularInline):
    model = OrderProduct
    readonly_fields = [
        'payment',
        'user',
        'product',
        'variations',
        'quantity',
        'product_price',
        'ordered',
    ]
    extra = 0


class OrderAdmin(admin.ModelAdmin):
    list_display = [
        'order_number',
        'full_name',
        'email',
        'city',
        'ip',
        'status',
        'is_ordered',
        'created_at',
    ]

    list_filter = [
        'status',
        'is_ordered',
    ]

    search_fields = [
        'order_number',
        'first_name',
        'last_name',
        'phone_number',
        'email',
        'ip',
        'payment__payment_id',
    ]

    list_per_page = 15
    inlines = [OrderProductInline]


class PaymentAdmin(admin.ModelAdmin):
    readonly_fields = [
        'user',
        'payment_id',
        'payment_method',
        'amount_paid',
        'status',
    ]

    list_display = [
        'user',
        'payment_id',
        'payment_method',
        'amount_paid',
        'status',
    ]

    list_display_links = [
        'user',
        'payment_id',
    ]


admin.site.register(Order, OrderAdmin)
admin.site.register(OrderProduct)
admin.site.register(Payment, PaymentAdmin)
