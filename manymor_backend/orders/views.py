from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from django.shortcuts import get_object_or_404

from .models import Order, OrderItem
from .serializers import OrderSerializer
from cart.models import Cart
from products.models import Product

class CheckoutView(APIView):
    permission_classes = [IsAuthenticated]
    
    @transaction.atomic
    def post(self, request):
        cart = get_object_or_404(Cart, user=request.user)

        if not cart.items.exists():
            return Response(
                {"detail": "Cart is empty"},
                status=status.HTTP_400_BAD_REQUEST
            )

        total = 0
        
        # Create order WITH shipping_address
        order = Order.objects.create(
            user=request.user,
            total_amount=0,  
            status='PLACED',
            payment_status='PAID',
            shipping_address=request.data.get('shipping_address', '')  
        )

        # Process order items
        for item in cart.items.select_related('product'):
            product = item.product

            if product.stock_quantity < item.quantity:
                raise ValueError(f"Not enough stock for {product.name}")

            # Reduce stock
            product.stock_quantity -= item.quantity
            product.save()

            # Create order item
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=item.quantity,
                unit_price=product.price
            )

            total += product.price * item.quantity

        # Update order total
        order.total_amount = total
        order.save()

        # Clear cart
        cart.items.all().delete()
        
        

        return Response(
            OrderSerializer(order).data,
            status=status.HTTP_201_CREATED
        )

class OrderListView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        orders = Order.objects.filter(user=request.user).order_by('-created_at')
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)


class OrderDetailView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, order_id):
        order = get_object_or_404(Order, id=order_id, user=request.user)
        serializer = OrderSerializer(order)
        return Response(serializer.data)