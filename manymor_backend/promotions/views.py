from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from .models import CarouselPromotion, ProductPromotion
from .serializers import CarouselPromotionSerializer, ProductPromotionSerializer
from products.permissions import IsAdminUserRole


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow admins with ADMIN role to edit, but anyone to read.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        # Check if user is authenticated and has ADMIN role
        return (
            request.user and 
            request.user.is_authenticated and 
            hasattr(request.user, 'role') and
            request.user.role == 'ADMIN'
        )


class CarouselPromotionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing carousel promotions.
    List and retrieve are public, create/update/delete require admin.
    """
    queryset = CarouselPromotion.objects.all()
    serializer_class = CarouselPromotionSerializer
    permission_classes = [IsAdminOrReadOnly]

    def get_queryset(self):
        """
        Optionally filter to only active promotions for non-admin users
        """
        queryset = CarouselPromotion.objects.all()
        
        # If 'active_only' parameter is passed, filter to currently active promotions
        if self.request.query_params.get('active_only', 'false').lower() == 'true':
            now = timezone.now()
            queryset = queryset.filter(
                is_active=True,
                start_date__lte=now,
                end_date__gte=now
            )
        
        return queryset.order_by('display_order', '-created_at')

    @action(detail=False, methods=['get'])
    def active(self, request):
        """
        Get only currently active carousel promotions for frontend display
        """
        now = timezone.now()
        active_promotions = self.queryset.filter(
            is_active=True,
            start_date__lte=now,
            end_date__gte=now
        ).order_by('display_order')
        
        serializer = self.get_serializer(active_promotions, many=True)
        return Response(serializer.data)


class ProductPromotionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing product promotions.
    List and retrieve are public, create/update/delete require admin.
    """
    queryset = ProductPromotion.objects.all()
    serializer_class = ProductPromotionSerializer
    permission_classes = [IsAdminOrReadOnly]

    def get_queryset(self):
        """
        Optionally filter to only active promotions
        """
        queryset = ProductPromotion.objects.all()
        
        if self.request.query_params.get('active_only', 'false').lower() == 'true':
            now = timezone.now()
            queryset = queryset.filter(
                is_active=True,
                start_date__lte=now,
                end_date__gte=now
            )
        
        return queryset.prefetch_related('products')

    @action(detail=False, methods=['get'])
    def active(self, request):
        """
        Get only currently active product promotions
        """
        now = timezone.now()
        active_promotions = self.queryset.filter(
            is_active=True,
            start_date__lte=now,
            end_date__gte=now
        )
        
        serializer = self.get_serializer(active_promotions, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def add_products(self, request, pk=None):
        """
        Add products to a promotion
        Expects: {"product_ids": [1, 2, 3]}
        """
        # Check if user has ADMIN role
        if not (request.user.is_authenticated and 
                hasattr(request.user, 'role') and 
                request.user.role == 'ADMIN'):
            return Response(
                {"error": "Only admin users can modify promotions"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        promotion = self.get_object()
        product_ids = request.data.get('product_ids', [])
        
        if not product_ids:
            return Response(
                {"error": "product_ids list is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        promotion.products.add(*product_ids)
        
        serializer = self.get_serializer(promotion)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def remove_products(self, request, pk=None):
        """
        Remove products from a promotion
        Expects: {"product_ids": [1, 2, 3]}
        """
        # Check if user has ADMIN role
        if not (request.user.is_authenticated and 
                hasattr(request.user, 'role') and 
                request.user.role == 'ADMIN'):
            return Response(
                {"error": "Only admin users can modify promotions"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        promotion = self.get_object()
        product_ids = request.data.get('product_ids', [])
        
        if not product_ids:
            return Response(
                {"error": "product_ids list is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        promotion.products.remove(*product_ids)
        
        serializer = self.get_serializer(promotion)
        return Response(serializer.data)
