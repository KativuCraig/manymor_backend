from django.db import models
from django.conf import settings
from products.models import Product

User = settings.AUTH_USER_MODEL


class Order(models.Model):
    class Status(models.TextChoices):
        PLACED = 'PLACED', 'Placed'
        PACKED = 'PACKED', 'Packed'
        DISPATCHED = 'DISATCHED', 'Dispatched'
        IN_TRANSIT = 'IN_TRANSIT', 'In Transit'
        DELIVERED = 'DELIVERED', 'Delivered'
        CANCELLED = 'CANCELLED', 'Cancelled'

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='orders'
    )
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PLACED
    )
    payment_status = models.CharField(
        max_length=20,
        default='PAID'  # mocked for MVP
    )
    shipping_address = models.TextField(blank=True)  # ADD THIS FIELD
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.id}"


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        related_name='items',
        on_delete=models.CASCADE
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT
    )
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"
