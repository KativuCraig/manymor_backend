from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.utils import timezone

from .models import Delivery, DeliveryStatusLog
from .serializers import DeliverySerializer
from orders.models import Order


class IsAdminUser(permissions.BasePermission):
    """Permission check for admin users only"""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'ADMIN'


class DeliveryViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.role == 'ADMIN':
            return Delivery.objects.all()
        # Customers can only see their own deliveries
        return Delivery.objects.filter(order__user=user)
    
    # GET /api/delivery/{order_id}/ - Get delivery tracking for an order
    def retrieve(self, request, pk=None):
        """Get delivery status for a specific order"""
        try:
            order_id = int(pk)
        except ValueError:
            return Response(
                {'error': 'Invalid order ID'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        order = get_object_or_404(Order, id=order_id)
        
        # Authorization check
        if request.user.role == 'CUSTOMER' and order.user != request.user:
            return Response(
                {'error': 'You can only view your own orders'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Get or create delivery record
        delivery, created = Delivery.objects.get_or_create(order=order)
        
        # If created, add initial status log
        if created:
            DeliveryStatusLog.objects.create(
                delivery=delivery,
                status=Delivery.Status.PLACED,
                notes='Order placed',
                created_by=request.user if request.user.role == 'ADMIN' else None
            )
        
        serializer = DeliverySerializer(delivery)
        return Response(serializer.data)
    
    # PUT /api/delivery/{order_id}/update_status/ - Admin updates delivery status
    @action(detail=True, methods=['put'], permission_classes=[IsAdminUser])
    def update_status(self, request, pk=None):
        """Admin endpoint to update delivery status"""
        try:
            order_id = int(pk)
        except ValueError:
            return Response(
                {'error': 'Invalid order ID'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        order = get_object_or_404(Order, id=order_id)
        delivery, _ = Delivery.objects.get_or_create(order=order)
        
        # Validate status
        new_status = request.data.get('status')
        if not new_status or new_status not in Delivery.Status.values:
            return Response(
                {'error': f'Invalid status. Must be one of: {list(Delivery.Status.values)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Update delivery status
        old_status = delivery.status
        delivery.status = new_status
        delivery.save()
        
        # Log the status change
        notes = request.data.get('notes', f'Status changed from {old_status} to {new_status}')
        DeliveryStatusLog.objects.create(
            delivery=delivery,
            status=new_status,
            notes=notes,
            created_by=request.user
        )
        
        # Sync order status (optional but good practice)
        order.status = new_status
        order.save()
        
        return Response({
            'message': 'Delivery status updated successfully',
            'delivery': DeliverySerializer(delivery).data
        })
    
    # GET /api/delivery/ - List all deliveries (Admin) or customer's deliveries
    def list(self, request):
        """List deliveries based on user role"""
        deliveries = self.get_queryset()
        serializer = DeliverySerializer(deliveries, many=True)
        return Response(serializer.data)