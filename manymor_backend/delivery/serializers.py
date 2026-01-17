from rest_framework import serializers
from .models import Delivery, DeliveryStatusLog

class DeliveryStatusLogSerializer(serializers.ModelSerializer):
    created_by = serializers.StringRelatedField()
    
    class Meta:
        model = DeliveryStatusLog
        fields = ['status', 'notes', 'created_at', 'created_by']
        read_only_fields = ['created_at', 'created_by']


class DeliverySerializer(serializers.ModelSerializer):
    status_logs = DeliveryStatusLogSerializer(many=True, read_only=True)
    order_id = serializers.IntegerField(source='order.id', read_only=True)
    customer_name = serializers.CharField(source='order.user.get_full_name', read_only=True)
    
    class Meta:
        model = Delivery
        fields = [
            'id',
            'order_id',
            'customer_name',
            'status',
            'estimated_delivery',
            'status_logs',
            'updated_at'
        ]
        read_only_fields = ['status_logs', 'updated_at']