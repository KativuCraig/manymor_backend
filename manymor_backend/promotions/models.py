from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from products.models import Product


class CarouselPromotion(models.Model):
    """
    Promotional banners for the homepage carousel
    """
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='promotions/carousel/')
    link_url = models.URLField(blank=True, null=True, help_text="Optional link when banner is clicked")
    button_text = models.CharField(max_length=50, blank=True, help_text="Text for CTA button")
    is_active = models.BooleanField(default=True)
    display_order = models.PositiveIntegerField(
        default=0,
        help_text="Lower numbers appear first in carousel"
    )
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['display_order', '-created_at']
        verbose_name = "Carousel Promotion"
        verbose_name_plural = "Carousel Promotions"

    def __str__(self):
        return self.title

    def is_currently_active(self):
        """Check if promotion is active and within date range"""
        from django.utils import timezone
        now = timezone.now()
        return self.is_active and self.start_date <= now <= self.end_date


class ProductPromotion(models.Model):
    """
    Promotions that can be applied to specific products
    """
    DISCOUNT_TYPE_CHOICES = [
        ('percentage', 'Percentage'),
        ('fixed', 'Fixed Amount'),
    ]

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    discount_type = models.CharField(max_length=20, choices=DISCOUNT_TYPE_CHOICES, default='percentage')
    discount_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    products = models.ManyToManyField(Product, related_name='promotions', blank=True)
    badge_text = models.CharField(
        max_length=50,
        blank=True,
        help_text="Text to display on product badge (e.g., 'SALE', '20% OFF')"
    )
    badge_color = models.CharField(
        max_length=7,
        default='#FF0000',
        help_text="Hex color code for badge background"
    )
    is_active = models.BooleanField(default=True)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Product Promotion"
        verbose_name_plural = "Product Promotions"

    def __str__(self):
        return self.name

    def is_currently_active(self):
        """Check if promotion is active and within date range"""
        from django.utils import timezone
        now = timezone.now()
        return self.is_active and self.start_date <= now <= self.end_date

    def calculate_discounted_price(self, original_price):
        """Calculate the discounted price based on promotion type"""
        if self.discount_type == 'percentage':
            discount_amount = original_price * (self.discount_value / 100)
            return original_price - discount_amount
        else:  # fixed amount
            return max(original_price - self.discount_value, 0)

    def get_discount_percentage(self, original_price):
        """Get discount as percentage for display"""
        if self.discount_type == 'percentage':
            return self.discount_value
        else:
            if original_price > 0:
                return (self.discount_value / original_price) * 100
            return 0
