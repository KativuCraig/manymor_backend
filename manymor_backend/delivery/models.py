from django.db import models
from orders.models import Order

class Delivery(models.Model):
    class Status(models.TextChoices):
        PLACED = 'PLACED', 'Placed'
        PACKED = 'PACKED', 'Packed'
        DISPATCHED = 'DISPATCHED', 'Dispatched'
        IN_TRANSIT = 'IN_TRANSIT', 'In Transit'
        DELIVERED = 'DELIVERED', 'Delivered'

    order = models.OneToOneField(
        Order,
        related_name='delivery',
        on_delete=models.CASCADE
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PLACED
    )
    estimated_delivery = models.DateField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Delivery for Order #{self.order.id}"


class DeliveryStatusLog(models.Model):
    """Tracks every status change for audit trail"""
    delivery = models.ForeignKey(
        Delivery,
        related_name='status_logs',
        on_delete=models.CASCADE
    )
    status = models.CharField(
        max_length=20,
        choices=Delivery.Status.choices
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True
    )

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.delivery.order.id} -> {self.status}"