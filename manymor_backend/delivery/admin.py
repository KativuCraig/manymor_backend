from django.contrib import admin
from .models import Delivery, DeliveryStatusLog

class DeliveryStatusLogInline(admin.TabularInline):
    model = DeliveryStatusLog
    extra = 0
    readonly_fields = ['created_at', 'created_by']
    can_delete = False
    
    def has_add_permission(self, request, obj):
        return False

@admin.register(Delivery)
class DeliveryAdmin(admin.ModelAdmin):
    list_display = ['order_id', 'status', 'estimated_delivery', 'updated_at']
    list_filter = ['status']
    search_fields = ['order__id']
    readonly_fields = ['updated_at']
    inlines = [DeliveryStatusLogInline]
    
    def order_id(self, obj):
        return f"Order #{obj.order.id}"
    order_id.short_description = 'Order'

@admin.register(DeliveryStatusLog)
class DeliveryStatusLogAdmin(admin.ModelAdmin):
    list_display = ['delivery', 'status', 'created_at', 'created_by']
    list_filter = ['status', 'created_at']
    readonly_fields = ['created_at']
    search_fields = ['delivery__order__id']