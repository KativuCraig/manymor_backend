from django.urls import path
from .views import (
    RegisterView, LoginView, MeView, 
    ProfileView, AddressListCreateView, AddressDetailView,
    UserListView, UserDetailView
)

urlpatterns = [
    # Authentication
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('me/', MeView.as_view(), name='me'),
    
    # Customer Profile Management
    path('profile/', ProfileView.as_view(), name='profile'),
    path('addresses/', AddressListCreateView.as_view(), name='address-list-create'),
    path('addresses/<int:address_id>/', AddressDetailView.as_view(), name='address-detail'),
    
    # Admin - User Management
    path('users/', UserListView.as_view(), name='user-list'),
    path('users/<int:user_id>/', UserDetailView.as_view(), name='user-detail'),
]
