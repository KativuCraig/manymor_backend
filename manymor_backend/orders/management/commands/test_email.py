"""
Management command to test email functionality.
Usage: python manage.py test_email <order_id>
"""
from django.core.management.base import BaseCommand
from orders.models import Order
from orders.emails import send_order_confirmation_email, send_order_status_update_email


class Command(BaseCommand):
    help = 'Test email sending functionality for orders'

    def add_arguments(self, parser):
        parser.add_argument(
            'order_id',
            type=int,
            help='Order ID to send test email for'
        )
        parser.add_argument(
            '--type',
            type=str,
            default='confirmation',
            choices=['confirmation', 'status'],
            help='Type of email to send (confirmation or status)'
        )
        parser.add_argument(
            '--status',
            type=str,
            default='PACKED',
            help='Status for status update email (e.g., PACKED, DISPATCHED, IN_TRANSIT, DELIVERED)'
        )

    def handle(self, *args, **options):
        order_id = options['order_id']
        email_type = options['type']
        
        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'Order #{order_id} does not exist'))
            return
        
        self.stdout.write(f'Testing email for Order #{order_id}')
        self.stdout.write(f'Customer: {order.user.email}')
        self.stdout.write(f'Total: ${order.total_amount}')
        self.stdout.write('')
        
        if email_type == 'confirmation':
            self.stdout.write('Sending order confirmation email...')
            success = send_order_confirmation_email(order)
        else:
            status_value = options['status'].upper()
            self.stdout.write(f'Sending status update email (Status: {status_value})...')
            success = send_order_status_update_email(order, status_value)
        
        if success:
            self.stdout.write(self.style.SUCCESS('✓ Email sent successfully!'))
            self.stdout.write('')
            self.stdout.write('Note: If using console backend, check your terminal output above.')
            self.stdout.write('If using SMTP, check the recipient email inbox.')
        else:
            self.stdout.write(self.style.ERROR('✗ Failed to send email'))
