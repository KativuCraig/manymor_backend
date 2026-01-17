from rest_framework import serializers
from .models import Category, Product, ProductImage
from django.utils import timezone


class CategorySerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ('id', 'name', 'parent', 'children')

    def get_children(self, obj):
        return CategorySerializer(obj.children.all(), many=True).data


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ('id', 'image')


class ProductSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)
    uploaded_images = serializers.ListField(
        child=serializers.ImageField(max_length=1000000, allow_empty_file=False, use_url=False),
        write_only=True,
        required=False
    )
    category_name = serializers.CharField(source='category.name', read_only=True)
    
    # Promotion fields
    active_promotion = serializers.SerializerMethodField()
    promotional_price = serializers.SerializerMethodField()
    discount_percentage = serializers.SerializerMethodField()
    has_promotion = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = (
            'id',
            'name',
            'description',
            'price',
            'stock_quantity',
            'is_active',
            'category',
            'category_name',
            'images',
            'uploaded_images',
            'created_at',
            'has_promotion',
            'active_promotion',
            'promotional_price',
            'discount_percentage',
        )

    def get_active_promotion(self, obj):
        """Get the first active promotion for this product"""
        now = timezone.now()
        active_promotion = obj.promotions.filter(
            is_active=True,
            start_date__lte=now,
            end_date__gte=now
        ).first()
        
        if active_promotion:
            return {
                'id': active_promotion.id,
                'name': active_promotion.name,
                'badge_text': active_promotion.badge_text,
                'badge_color': active_promotion.badge_color,
            }
        return None

    def get_promotional_price(self, obj):
        """Calculate promotional price if promotion exists"""
        now = timezone.now()
        active_promotion = obj.promotions.filter(
            is_active=True,
            start_date__lte=now,
            end_date__gte=now
        ).first()
        
        if active_promotion:
            return active_promotion.calculate_discounted_price(obj.price)
        return None

    def get_discount_percentage(self, obj):
        """Get discount percentage for display"""
        now = timezone.now()
        active_promotion = obj.promotions.filter(
            is_active=True,
            start_date__lte=now,
            end_date__gte=now
        ).first()
        
        if active_promotion:
            return active_promotion.get_discount_percentage(obj.price)
        return None

    def get_has_promotion(self, obj):
        """Check if product has any active promotion"""
        now = timezone.now()
        return obj.promotions.filter(
            is_active=True,
            start_date__lte=now,
            end_date__gte=now
        ).exists()

    def create(self, validated_data):
        uploaded_images = validated_data.pop('uploaded_images', [])
        product = Product.objects.create(**validated_data)
        
        # Create ProductImage instances for each uploaded image
        for image in uploaded_images:
            ProductImage.objects.create(product=product, image=image)
        
        return product

    def update(self, instance, validated_data):
        uploaded_images = validated_data.pop('uploaded_images', [])
        
        # Update product fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Add new images if provided
        for image in uploaded_images:
            ProductImage.objects.create(product=instance, image=image)
        
        return instance
