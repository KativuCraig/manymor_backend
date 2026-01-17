from django.db.models.signals import post_save
from django.dispatch import receiver
from orders.models import Order
from .models import Delivery, DeliveryStatusLog

@receiver(post_save, sender=Order)
def create_delivery_on_order(sender, instance, created, **kwargs):
    """Automatically create delivery record when order is created"""
    if created:
        delivery = Delivery.objects.create(order=instance)
        DeliveryStatusLog.objects.create(
            delivery=delivery,
            status=Delivery.Status.PLACED,
            notes='Order placed'
        )
        print(f"Created delivery record for Order #{instance.id}")