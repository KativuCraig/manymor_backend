from django.db.models.signals import post_save
from django.dispatch import receiver
from orders.models import Order
from orders.emails import send_delivery_status_update_email
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


@receiver(post_save, sender=Delivery)
def delivery_status_changed(sender, instance, created, **kwargs):
    """
    Send email notification when delivery status changes.
    Skip email on creation since order confirmation already sent.
    """
    if not created:
        # Delivery status was updated, send email notification
        try:
            # Get the most recent status log entry for notes
            latest_log = instance.status_logs.first()
            notes = latest_log.notes if latest_log else None
            
            # Send email notification
            send_delivery_status_update_email(instance, notes)
        except Exception as e:
            print(f"Failed to send delivery status email: {str(e)}")
