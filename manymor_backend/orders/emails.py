"""
Email utility functions for sending order-related emails.
"""
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.html import strip_tags


def send_order_confirmation_email(order):
    """
    Send order confirmation email to customer when order is placed.
    
    Args:
        order: Order instance
    """
    try:
        # Prepare context data
        order_items = []
        for item in order.items.all():
            order_items.append({
                'product_name': item.product.name,
                'quantity': item.quantity,
                'unit_price': f"{item.unit_price:.2f}",
                'subtotal': f"{(item.unit_price * item.quantity):.2f}"
            })
        
        context = {
            'order_id': order.id,
            'order_date': order.created_at.strftime('%B %d, %Y at %I:%M %p'),
            'order_status': order.get_status_display(),
            'customer_email': order.user.email,
            'shipping_address': order.shipping_address or 'Not provided',
            'order_items': order_items,
            'total_amount': f"{order.total_amount:.2f}",
            'company_name': settings.COMPANY_NAME,
            'support_email': settings.COMPANY_SUPPORT_EMAIL,
        }
        
        # Render email templates
        html_content = render_to_string('emails/order_confirmation.html', context)
        text_content = render_to_string('emails/order_confirmation.txt', context)
        
        # Create email
        subject = f'Order Confirmation - Order #{order.id}'
        from_email = settings.DEFAULT_FROM_EMAIL
        to_email = [order.user.email]
        
        # Create email message with both HTML and plain text
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=from_email,
            to=to_email
        )
        email.attach_alternative(html_content, "text/html")
        
        # Send email
        email.send(fail_silently=False)
        
        print(f"✓ Order confirmation email sent to {order.user.email} for Order #{order.id}")
        return True
        
    except Exception as e:
        print(f"✗ Failed to send order confirmation email: {str(e)}")
        return False


def send_order_status_update_email(order, new_status, status_message=None):
    """
    Send order status update email to customer when order status changes.
    
    Args:
        order: Order instance
        new_status: New status value
        status_message: Optional custom message about the status change
    """
    try:
        # Map status to CSS class
        status_class_map = {
            'PLACED': 'placed',
            'PACKED': 'packed',
            'DISPATCHED': 'dispatched',
            'DISATCHED': 'dispatched',  # Handle typo in model
            'IN_TRANSIT': 'in_transit',
            'DELIVERED': 'delivered',
            'CANCELLED': 'cancelled',
        }
        
        # Default status messages
        default_messages = {
            'PLACED': 'Your order has been received and is being prepared.',
            'PACKED': 'Your order has been packed and is ready for dispatch.',
            'DISPATCHED': 'Your order has been dispatched and is on its way to you!',
            'DISATCHED': 'Your order has been dispatched and is on its way to you!',
            'IN_TRANSIT': 'Your order is currently in transit and will arrive soon.',
            'DELIVERED': 'Your order has been delivered successfully. Enjoy your purchase!',
            'CANCELLED': 'Your order has been cancelled. If you have any questions, please contact support.',
        }
        
        # Get delivery info if exists
        estimated_delivery = None
        if hasattr(order, 'delivery'):
            estimated_delivery = order.delivery.estimated_delivery
        
        context = {
            'order_id': order.id,
            'order_date': order.created_at.strftime('%B %d, %Y'),
            'customer_email': order.user.email,
            'new_status': order.get_status_display(),
            'current_status': new_status,
            'status_class': status_class_map.get(new_status, 'placed'),
            'status_message': status_message or default_messages.get(new_status, ''),
            'total_amount': f"{order.total_amount:.2f}",
            'estimated_delivery': estimated_delivery.strftime('%B %d, %Y') if estimated_delivery else None,
            'company_name': settings.COMPANY_NAME,
            'support_email': settings.COMPANY_SUPPORT_EMAIL,
        }
        
        # Render email templates
        html_content = render_to_string('emails/order_status_update.html', context)
        text_content = render_to_string('emails/order_status_update.txt', context)
        
        # Create email
        subject = f'Order Status Update - Order #{order.id} is now {order.get_status_display()}'
        from_email = settings.DEFAULT_FROM_EMAIL
        to_email = [order.user.email]
        
        # Create email message with both HTML and plain text
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=from_email,
            to=to_email
        )
        email.attach_alternative(html_content, "text/html")
        
        # Send email
        email.send(fail_silently=False)
        
        print(f"✓ Status update email sent to {order.user.email} for Order #{order.id} (Status: {new_status})")
        return True
        
    except Exception as e:
        print(f"✗ Failed to send status update email: {str(e)}")
        return False


def send_delivery_status_update_email(delivery, notes=None):
    """
    Send delivery status update email based on delivery object.
    
    Args:
        delivery: Delivery instance
        notes: Optional notes about the status change
    """
    return send_order_status_update_email(
        order=delivery.order,
        new_status=delivery.status,
        status_message=notes
    )
