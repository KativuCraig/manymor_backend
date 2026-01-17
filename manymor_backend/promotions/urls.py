from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CarouselPromotionViewSet, ProductPromotionViewSet

router = DefaultRouter()
router.register(r'carousel-promotions', CarouselPromotionViewSet, basename='carousel-promotion')
router.register(r'product-promotions', ProductPromotionViewSet, basename='product-promotion')

urlpatterns = [
    path('', include(router.urls)),
]
