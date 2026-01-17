from rest_framework import serializers
from .models import CarouselPromotion, ProductPromotion
from django.utils import timezone


class CarouselPromotionSerializer(serializers.ModelSerializer):
    is_currently_active = serializers.SerializerMethodField()

    class Meta:
        model = CarouselPromotion
        fields = [
            'id',
            'title',
            'description',
            'image',
            'link_url',
            'button_text',
            'is_active',
            'display_order',
            'start_date',
            'end_date',
            'is_currently_active',
        ]

    def get_is_currently_active(self, obj):
        return obj.is_currently_active()


class ProductPromotionSerializer(serializers.ModelSerializer):
    is_currently_active = serializers.SerializerMethodField()
    products_count = serializers.SerializerMethodField()

    class Meta:
        model = ProductPromotion
        fields = [
            'id',
            'name',
            'description',
            'discount_type',
            'discount_value',
            'badge_text',
            'badge_color',
            'is_active',
            'start_date',
            'end_date',
            'is_currently_active',
            'products_count',
        ]

    def get_is_currently_active(self, obj):
        return obj.is_currently_active()

    def get_products_count(self, obj):
        return obj.products.count()


class ProductPromotionDetailSerializer(serializers.ModelSerializer):
    """Serializer for embedding promotion info in product responses"""
    discount_percentage = serializers.SerializerMethodField()
    discounted_price = serializers.SerializerMethodField()

    class Meta:
        model = ProductPromotion
        fields = [
            'id',
            'name',
            'badge_text',
            'badge_color',
            'discount_type',
            'discount_value',
            'discount_percentage',
            'discounted_price',
        ]

    def get_discount_percentage(self, obj):
        """Calculate discount percentage for display"""
        product = self.context.get('product')
        if product:
            return obj.get_discount_percentage(product.price)
        return 0

    def get_discounted_price(self, obj):
        """Calculate discounted price"""
        product = self.context.get('product')
        if product:
            return obj.calculate_discounted_price(product.price)
        return None
