"""
Django signals for Order model to send emails on order events.
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import transaction
from .models import Order
from .emails import send_order_confirmation_email, send_order_status_update_email


@receiver(post_save, sender=Order)
def order_post_save(sender, instance, created, **kwargs):
    """
    Signal handler that triggers when an Order is saved.
    - Sends confirmation email when order is created (after transaction commits)
    - Sends status update email when status changes
    """
    if created:
        # New order created - send confirmation email after transaction commits
        # This ensures all order items are saved first
        transaction.on_commit(lambda: send_order_confirmation_email(instance))
    else:
        # Order updated - check if status changed
        if kwargs.get('update_fields') is None or 'status' in kwargs.get('update_fields', []):
            # Status might have changed, send update email
            # We need to check if status actually changed
            try:
                # Get the old instance from database
                old_instance = Order.objects.get(pk=instance.pk)
                if old_instance.status != instance.status:
                    send_order_status_update_email(instance, instance.status)
            except Order.DoesNotExist:
                # This shouldn't happen, but handle gracefully
                pass
