from django.contrib import admin
from .models import CarouselPromotion, ProductPromotion


@admin.register(CarouselPromotion)
class CarouselPromotionAdmin(admin.ModelAdmin):
    list_display = ['title', 'is_active', 'display_order', 'start_date', 'end_date', 'created_at']
    list_filter = ['is_active', 'start_date', 'end_date']
    search_fields = ['title', 'description']
    list_editable = ['is_active', 'display_order']
    ordering = ['display_order', '-created_at']
    date_hierarchy = 'start_date'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'image')
        }),
        ('Call to Action', {
            'fields': ('button_text', 'link_url')
        }),
        ('Display Settings', {
            'fields': ('is_active', 'display_order')
        }),
        ('Schedule', {
            'fields': ('start_date', 'end_date')
        }),
    )


@admin.register(ProductPromotion)
class ProductPromotionAdmin(admin.ModelAdmin):
    list_display = ['name', 'discount_type', 'discount_value', 'is_active', 'start_date', 'end_date']
    list_filter = ['is_active', 'discount_type', 'start_date', 'end_date']
    search_fields = ['name', 'description']
    list_editable = ['is_active']
    filter_horizontal = ['products']
    ordering = ['-created_at']
    date_hierarchy = 'start_date'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description')
        }),
        ('Discount Settings', {
            'fields': ('discount_type', 'discount_value')
        }),
        ('Badge Display', {
            'fields': ('badge_text', 'badge_color'),
            'description': 'Configure how the promotion appears on product cards'
        }),
        ('Products', {
            'fields': ('products',)
        }),
        ('Status & Schedule', {
            'fields': ('is_active', 'start_date', 'end_date')
        }),
    )
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.prefetch_related('products')
