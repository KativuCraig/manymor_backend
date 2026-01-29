# Email Configuration Guide

This document explains the email notification system for customer orders in the ManyMor e-commerce backend.

## Overview

The system automatically sends emails to customers in two scenarios:
1. **Order Confirmation** - When a customer places an order
2. **Status Updates** - When the order/delivery status changes (Placed → Packed → Dispatched → In Transit → Delivered)

## Setup Instructions

### 1. Configure Email Settings

The email configuration is in `manymor_backend/settings.py`. You can configure it using environment variables:

```python
# Development: Emails print to console (default)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Production: Use SMTP (e.g., Gmail, SendGrid, AWS SES)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-app-password'
DEFAULT_FROM_EMAIL = 'noreply@manymor.com'
```

### 2. Environment Variables (Recommended for Production)

Create a `.env` file:

```env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-specific-password
DEFAULT_FROM_EMAIL=noreply@manymor.com
```

### 3. Gmail Setup (if using Gmail)

1. Enable 2-Factor Authentication on your Google account
2. Generate an App Password:
   - Go to Google Account Settings → Security → 2-Step Verification → App passwords
   - Create a new app password for "Mail"
   - Use this password in `EMAIL_HOST_PASSWORD`

### 4. Alternative Email Services

**SendGrid:**
```python
EMAIL_HOST = 'smtp.sendgrid.net'
EMAIL_HOST_USER = 'apikey'
EMAIL_HOST_PASSWORD = 'your-sendgrid-api-key'
EMAIL_PORT = 587
```

**AWS SES:**
```python
EMAIL_BACKEND = 'django_ses.SESBackend'
AWS_ACCESS_KEY_ID = 'your-access-key'
AWS_SECRET_ACCESS_KEY = 'your-secret-key'
AWS_SES_REGION_NAME = 'us-east-1'
```

**Mailgun:**
```python
EMAIL_HOST = 'smtp.mailgun.org'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'postmaster@your-domain.mailgun.org'
EMAIL_HOST_PASSWORD = 'your-mailgun-password'
```

## Email Templates

### Template Location
- HTML Templates: `templates/emails/*.html`
- Plain Text Templates: `templates/emails/*.txt`

### Available Templates

1. **order_confirmation.html/txt** - Sent when order is placed
2. **order_status_update.html/txt** - Sent when order status changes

### Customizing Templates

Edit the HTML/TXT files in `templates/emails/`. Available context variables:

**Order Confirmation:**
- `order_id` - Order number
- `order_date` - Date order was placed
- `order_status` - Current order status
- `customer_email` - Customer's email
- `shipping_address` - Delivery address
- `order_items` - List of items with product name, quantity, price
- `total_amount` - Order total
- `company_name` - Your company name
- `support_email` - Support contact email

**Status Update:**
- `order_id` - Order number
- `new_status` - New status display name
- `current_status` - Raw status value
- `status_message` - Custom message about the change
- `estimated_delivery` - Expected delivery date
- All order confirmation variables

## How It Works

### Automatic Email Triggers

**Order Placement:**
```python
# When customer checks out (orders/views.py)
order = Order.objects.create(...)  # Email sent automatically via signal
```

**Status Update:**
```python
# When admin updates delivery status (delivery/views.py)
delivery.status = 'DISPATCHED'
delivery.save()  # Email sent automatically via signal
```

### Signals

The system uses Django signals to automatically send emails:

- `orders/signals.py` - Handles order creation and status changes
- `delivery/signals.py` - Handles delivery status changes

### Manual Email Sending

If you need to manually send an email:

```python
from orders.emails import send_order_confirmation_email, send_order_status_update_email
from orders.models import Order

# Send confirmation
order = Order.objects.get(id=1)
send_order_confirmation_email(order)

# Send status update
send_order_status_update_email(order, 'DISPATCHED', 'Your package is on the way!')
```

## Testing Emails

### Test Command

Test email functionality without placing real orders:

```bash
# Test order confirmation email
python manage.py test_email 1 --type=confirmation

# Test status update email
python manage.py test_email 1 --type=status --status=DISPATCHED
```

### Console Backend (Development)

During development, emails print to the console:

```bash
python manage.py runserver
# Place an order via API
# Check terminal output for email content
```

### Testing with Real SMTP

1. Configure SMTP settings
2. Place a test order
3. Check recipient inbox

## Order Status Flow

The system sends emails for each status transition:

```
PLACED → Email: "Order Confirmed"
   ↓
PACKED → Email: "Order Packed"
   ↓
DISPATCHED → Email: "Order Dispatched"
   ↓
IN_TRANSIT → Email: "Order In Transit"
   ↓
DELIVERED → Email: "Order Delivered"
```

**Cancelled Status:** Also triggers an email notification

## API Integration

### Place Order (Triggers Confirmation Email)
```http
POST /api/orders/checkout/
Authorization: Bearer <token>
Content-Type: application/json

{
  "shipping_address": "123 Main St, City, Country"
}
```

### Update Delivery Status (Triggers Status Email)
```http
PUT /api/delivery/{order_id}/update_status/
Authorization: Bearer <admin-token>
Content-Type: application/json

{
  "status": "DISPATCHED",
  "notes": "Package handed to courier service"
}
```

## Troubleshooting

### Emails Not Sending

1. **Check email backend:**
   ```python
   # In settings.py
   print(EMAIL_BACKEND)  # Should be smtp.EmailBackend for real emails
   ```

2. **Verify SMTP credentials:**
   - Test with `python manage.py shell`:
   ```python
   from django.core.mail import send_mail
   send_mail('Test', 'Message', 'from@example.com', ['to@example.com'])
   ```

3. **Check firewall/network:**
   - Ensure port 587 (or 465) is open
   - Check if ISP blocks SMTP ports

4. **Gmail specific:**
   - Use App Password, not regular password
   - Enable "Less secure app access" if needed

### Emails Going to Spam

1. Configure SPF, DKIM, and DMARC records for your domain
2. Use a reputable SMTP service (SendGrid, AWS SES)
3. Include plain text version (already implemented)
4. Add unsubscribe link in production

### Missing Context Variables

Check that Order has related data:
```python
order = Order.objects.get(id=1)
print(order.user.email)  # Must exist
print(order.items.all())  # Should have items
```

## Production Checklist

- [ ] Configure proper SMTP service (not Gmail)
- [ ] Set up domain authentication (SPF, DKIM, DMARC)
- [ ] Use environment variables for credentials
- [ ] Update `DEFAULT_FROM_EMAIL` to your domain
- [ ] Update `COMPANY_NAME` and `COMPANY_SUPPORT_EMAIL`
- [ ] Test email delivery to various providers
- [ ] Set up email logging/monitoring
- [ ] Add email rate limiting if needed
- [ ] Customize email templates with branding
- [ ] Add unsubscribe functionality (if required)

## File Structure

```
manymor_backend/
├── settings.py                    # Email configuration
├── templates/
│   └── emails/
│       ├── order_confirmation.html
│       ├── order_confirmation.txt
│       ├── order_status_update.html
│       └── order_status_update.txt
├── orders/
│   ├── emails.py                  # Email sending functions
│   ├── signals.py                 # Auto-send on order events
│   ├── views.py                   # Order creation
│   └── management/
│       └── commands/
│           └── test_email.py      # Testing command
└── delivery/
    ├── signals.py                 # Auto-send on status changes
    └── views.py                   # Status updates
```

## Support

For issues or questions:
- Check Django email documentation: https://docs.djangoproject.com/en/stable/topics/email/
- Review signal documentation: https://docs.djangoproject.com/en/stable/topics/signals/
