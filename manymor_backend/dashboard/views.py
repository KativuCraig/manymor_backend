from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Sum, Count, Q
from django.shortcuts import get_object_or_404
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal

from products.permissions import IsAdminUserRole
from orders.models import Order
from orders.serializers import OrderSerializer
from products.models import Product
from accounts.models import User
from promotions.models import CarouselPromotion, ProductPromotion
from promotions.serializers import CarouselPromotionSerializer, ProductPromotionSerializer


class AdminSummaryView(APIView):
    """
    Get admin dashboard summary statistics
    """
    permission_classes = [IsAdminUserRole]

    def get(self, request):
        # Total orders
        total_orders = Order.objects.count()
        
        # Total revenue (sum of all completed orders)
        total_revenue = Order.objects.exclude(
            status=Order.Status.CANCELLED
        ).aggregate(
            total=Sum('total_amount')
        )['total'] or Decimal('0.00')
        
        # Total customers
        total_customers = User.objects.filter(
            role=User.Role.CUSTOMER
        ).count()
        
        # Total products
        total_products = Product.objects.count()
        
        # Active products
        active_products = Product.objects.filter(is_active=True).count()
        
        # Low stock products count (stock < 10)
        low_stock_count = Product.objects.filter(
            is_active=True,
            stock_quantity__lt=10
        ).count()
        
        # Recent orders (last 7 days)
        seven_days_ago = timezone.now() - timedelta(days=7)
        recent_orders = Order.objects.filter(
            created_at__gte=seven_days_ago
        ).count()
        
        # Pending orders
        pending_orders = Order.objects.filter(
            status__in=[Order.Status.PLACED, Order.Status.PACKED]
        ).count()
        
        summary = {
            'total_orders': total_orders,
            'total_revenue': str(total_revenue),
            'total_customers': total_customers,
            'total_products': total_products,
            'active_products': active_products,
            'low_stock_count': low_stock_count,
            'recent_orders': recent_orders,
            'pending_orders': pending_orders
        }
        
        return Response(summary, status=status.HTTP_200_OK)


class AdminSalesView(APIView):
    """
    Get sales data for admin dashboard charts
    """
    permission_classes = [IsAdminUserRole]

    def get(self, request):
        # Get query parameters for date range
        days = int(request.query_params.get('days', 30))
        
        # Calculate date range
        end_date = timezone.now()
        start_date = end_date - timedelta(days=days)
        
        # Get daily sales data
        daily_sales = []
        current_date = start_date.date()
        
        while current_date <= end_date.date():
            next_date = current_date + timedelta(days=1)
            
            # Get orders for this day
            day_orders = Order.objects.filter(
                created_at__date=current_date
            ).exclude(status=Order.Status.CANCELLED)
            
            daily_revenue = day_orders.aggregate(
                total=Sum('total_amount')
            )['total'] or Decimal('0.00')
            
            daily_sales.append({
                'date': current_date.isoformat(),
                'revenue': str(daily_revenue),
                'orders_count': day_orders.count()
            })
            
            current_date = next_date
        
        # Get sales by status
        sales_by_status = []
        for status_choice in Order.Status.choices:
            status_code = status_choice[0]
            status_label = status_choice[1]
            
            status_count = Order.objects.filter(
                status=status_code,
                created_at__gte=start_date
            ).count()
            
            status_revenue = Order.objects.filter(
                status=status_code,
                created_at__gte=start_date
            ).aggregate(
                total=Sum('total_amount')
            )['total'] or Decimal('0.00')
            
            sales_by_status.append({
                'status': status_label,
                'count': status_count,
                'revenue': str(status_revenue)
            })
        
        # Top selling products
        top_products = Product.objects.filter(
            orderitem__order__created_at__gte=start_date
        ).annotate(
            total_sold=Sum('orderitem__quantity'),
            revenue=Sum('orderitem__quantity') * Sum('orderitem__unit_price')
        ).prefetch_related('images').order_by('-total_sold')[:10]
        
        top_products_data = [{
            'id': product.id,
            'name': product.name,
            'total_sold': product.total_sold or 0,
            'current_stock': product.stock_quantity,
            'images': [request.build_absolute_uri(img.image.url) for img in product.images.all()]
        } for product in top_products]
        
        sales_data = {
            'daily_sales': daily_sales,
            'sales_by_status': sales_by_status,
            'top_products': top_products_data,
            'period_days': days
        }
        
        return Response(sales_data, status=status.HTTP_200_OK)


class StockAlertsView(APIView):
    """
    Get products with low stock or out of stock
    """
    permission_classes = [IsAdminUserRole]

    def get(self, request):
        # Get threshold from query params (default: 10)
        threshold = int(request.query_params.get('threshold', 10))
        
        # Get products with low stock
        low_stock_products = Product.objects.filter(
            is_active=True,
            stock_quantity__lte=threshold,
            stock_quantity__gt=0
        ).select_related('category').prefetch_related('images').order_by('stock_quantity')
        
        # Get out of stock products
        out_of_stock_products = Product.objects.filter(
            is_active=True,
            stock_quantity=0
        ).select_related('category').prefetch_related('images').order_by('name')
        
        low_stock_data = [{
            'id': product.id,
            'name': product.name,
            'category': product.category.name,
            'stock_quantity': product.stock_quantity,
            'price': str(product.price),
            'status': 'low_stock',
            'images': [request.build_absolute_uri(img.image.url) for img in product.images.all()]
        } for product in low_stock_products]
        
        out_of_stock_data = [{
            'id': product.id,
            'name': product.name,
            'category': product.category.name,
            'stock_quantity': 0,
            'price': str(product.price),
            'status': 'out_of_stock',
            'images': [request.build_absolute_uri(img.image.url) for img in product.images.all()]
        } for product in out_of_stock_products]
        
        alerts = {
            'low_stock': low_stock_data,
            'out_of_stock': out_of_stock_data,
            'low_stock_count': len(low_stock_data),
            'out_of_stock_count': len(out_of_stock_data),
            'threshold': threshold
        }
        
        return Response(alerts, status=status.HTTP_200_OK)


class AdminOrdersView(APIView):
    """
    Get all orders for admin dashboard with filtering and pagination support
    """
    permission_classes = [IsAdminUserRole]

    def get(self, request):
        # Get all orders (not filtered by user)
        orders = Order.objects.select_related('user').prefetch_related('items__product')
        
        # Filter by status if provided
        status_filter = request.query_params.get('status')
        if status_filter:
            orders = orders.filter(status=status_filter)
        
        # Filter by payment status if provided
        payment_status = request.query_params.get('payment_status')
        if payment_status:
            orders = orders.filter(payment_status=payment_status)
        
        # Search by order ID or user email
        search = request.query_params.get('search')
        if search:
            orders = orders.filter(
                Q(id__icontains=search) | 
                Q(user__email__icontains=search) |
                Q(user__first_name__icontains=search) |
                Q(user__last_name__icontains=search)
            )
        
        # Order by most recent first
        orders = orders.order_by('-created_at')
        
        # Serialize the orders
        serializer = OrderSerializer(orders, many=True)
        
        return Response({
            'count': orders.count(),
            'orders': serializer.data
        }, status=status.HTTP_200_OK)
    
    def patch(self, request, order_id):
        """
        Update order status (admin only)
        """
        order = get_object_or_404(Order, id=order_id)
        
        # Update status if provided
        new_status = request.data.get('status')
        if new_status and new_status in dict(Order.Status.choices):
            order.status = new_status
            order.save()
            
        # Update payment status if provided
        new_payment_status = request.data.get('payment_status')
        if new_payment_status and new_payment_status in dict(Order.PaymentStatus.choices):
            order.payment_status = new_payment_status
            order.save()
        
        serializer = OrderSerializer(order)
        return Response(serializer.data, status=status.HTTP_200_OK)


class AdminPromotionStatsView(APIView):
    """
    Get promotion statistics for admin dashboard
    """
    permission_classes = [IsAdminUserRole]

    def get(self, request):
        now = timezone.now()
        
        # Active carousel promotions
        active_carousel = CarouselPromotion.objects.filter(
            is_active=True,
            start_date__lte=now,
            end_date__gte=now
        ).count()
        
        # Active product promotions
        active_product_promos = ProductPromotion.objects.filter(
            is_active=True,
            start_date__lte=now,
            end_date__gte=now
        ).count()
        
        # Upcoming promotions (starting in next 7 days)
        upcoming = ProductPromotion.objects.filter(
            is_active=True,
            start_date__gt=now,
            start_date__lte=now + timedelta(days=7)
        ).count()
        
        # Expired promotions (ended in last 30 days)
        recently_expired = ProductPromotion.objects.filter(
            end_date__lt=now,
            end_date__gte=now - timedelta(days=30)
        ).count()
        
        # Products with active promotions
        promoted_products = Product.objects.filter(
            promotions__is_active=True,
            promotions__start_date__lte=now,
            promotions__end_date__gte=now
        ).distinct().count()
        
        return Response({
            'active_carousel_promotions': active_carousel,
            'active_product_promotions': active_product_promos,
            'upcoming_promotions': upcoming,
            'recently_expired_promotions': recently_expired,
            'products_with_promotions': promoted_products,
        }, status=status.HTTP_200_OK)
