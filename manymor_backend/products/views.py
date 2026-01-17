from rest_framework import viewsets, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend

from .models import Category, Product
from .serializers import CategorySerializer, ProductSerializer
from .permissions import IsAdminUserRole


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.prefetch_related('children').all()
    serializer_class = CategorySerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminUserRole()]
        return [permissions.AllowAny()]


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.select_related('category').prefetch_related('images', 'promotions').filter(is_active=True)
    serializer_class = ProductSerializer

    filter_backends = [
        filters.SearchFilter,
        DjangoFilterBackend
    ]
    search_fields = ['name', 'description']
    filterset_fields = ['category']

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminUserRole()]
        return [permissions.AllowAny()]
