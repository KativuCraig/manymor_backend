from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from promotions.models import ProductPromotion
from products.models import Product


class Command(BaseCommand):
    help = 'Create sample product promotions for testing'

    def handle(self, *args, **options):
        # Get some products to apply promotions to
        products = Product.objects.all()[:5]
        
        if not products:
            self.stdout.write(self.style.ERROR('No products found. Please create products first.'))
            return

        now = timezone.now()
        
        # Create a percentage discount promotion
        promo1, created = ProductPromotion.objects.get_or_create(
            name='Summer Sale 2026',
            defaults={
                'description': '20% off selected summer items',
                'discount_type': 'percentage',
                'discount_value': 20.00,
                'badge_text': '20% OFF',
                'badge_color': '#FF4444',
                'is_active': True,
                'start_date': now,
                'end_date': now + timedelta(days=30),
            }
        )
        
        if created:
            promo1.products.add(*products[:3])
            self.stdout.write(self.style.SUCCESS(f'Created promotion: {promo1.name}'))
        else:
            self.stdout.write(self.style.WARNING(f'Promotion already exists: {promo1.name}'))

        # Create a fixed discount promotion
        promo2, created = ProductPromotion.objects.get_or_create(
            name='New Year Clearance',
            defaults={
                'description': '$10 off selected items',
                'discount_type': 'fixed',
                'discount_value': 10.00,
                'badge_text': 'SAVE $10',
                'badge_color': '#00AA00',
                'is_active': True,
                'start_date': now,
                'end_date': now + timedelta(days=14),
            }
        )
        
        if created:
            promo2.products.add(*products[2:5])
            self.stdout.write(self.style.SUCCESS(f'Created promotion: {promo2.name}'))
        else:
            self.stdout.write(self.style.WARNING(f'Promotion already exists: {promo2.name}'))

        self.stdout.write(self.style.SUCCESS('\nSample promotions created successfully!'))
        self.stdout.write(self.style.SUCCESS('You can view them in the admin panel or via the API.'))
