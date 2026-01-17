from django.urls import path
from .views import AdminSummaryView, AdminSalesView, StockAlertsView, AdminOrdersView, AdminPromotionStatsView

urlpatterns = [
    path('summary/', AdminSummaryView.as_view(), name='admin-summary'),
    path('sales/', AdminSalesView.as_view(), name='admin-sales'),
    path('stock-alerts/', StockAlertsView.as_view(), name='stock-alerts'),
    path('orders/', AdminOrdersView.as_view(), name='admin-orders'),
    path('orders/<int:order_id>/', AdminOrdersView.as_view(), name='admin-order-update'),
    path('promotions/stats/', AdminPromotionStatsView.as_view(), name='admin-promotion-stats'),
]
