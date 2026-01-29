from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework_simplejwt.tokens import RefreshToken
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache

from .serializers import (
    RegisterSerializer, LoginSerializer, UserSerializer,
    UserProfileSerializer, AddressSerializer
)
from .models import User, Address
from .ratelimit import rate_limit
from products.permissions import IsAdminUserRole


@method_decorator(never_cache, name='dispatch')
@method_decorator(rate_limit(max_requests=5, window_seconds=300, key_prefix='register'), name='post')
class RegisterView(APIView):
    # don't run authentication (avoid invalid token errors when callers send
    # an expired/invalid Authorization header). Allow anyone to register.
    authentication_classes = []
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        refresh = RefreshToken.for_user(user)

        return Response({
            'user': UserSerializer(user).data,
            'access': str(refresh.access_token),
            'refresh': str(refresh)
        }, status=status.HTTP_201_CREATED)


@method_decorator(never_cache, name='dispatch')
@method_decorator(rate_limit(max_requests=5, window_seconds=300, key_prefix='login'), name='post')
class LoginView(APIView):
    # Login should also be callable without attempting JWT authentication
    # (prevents "Given token not valid for any token type" when a bad
    # Authorization header is present).
    authentication_classes = []
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data

        refresh = RefreshToken.for_user(user)

        return Response({
            'user': UserSerializer(user).data,
            'access': str(refresh.access_token),
            'refresh': str(refresh)
        })


class MeView(APIView):
    def get(self, request):
        return Response(UserSerializer(request.user).data)


class ProfileView(APIView):
    """
    Customer profile management - view and update profile with addresses
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """Get current user's profile with all addresses"""
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data)
    
    def put(self, request):
        """Update user profile (phone number only, email/role are read-only)"""
        serializer = UserProfileSerializer(
            request.user, 
            data=request.data, 
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class AddressListCreateView(APIView):
    """
    List all addresses for current user or create a new address
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """Get all addresses for the current user"""
        addresses = Address.objects.filter(user=request.user).order_by('-is_default', 'label')
        serializer = AddressSerializer(addresses, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        """Create a new address for the current user"""
        serializer = AddressSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class AddressDetailView(APIView):
    """
    Retrieve, update or delete a specific address
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self, request, address_id):
        """Get address and ensure it belongs to the current user"""
        return get_object_or_404(Address, id=address_id, user=request.user)
    
    def get(self, request, address_id):
        """Get a specific address"""
        address = self.get_object(request, address_id)
        serializer = AddressSerializer(address)
        return Response(serializer.data)
    
    def put(self, request, address_id):
        """Update a specific address"""
        address = self.get_object(request, address_id)
        serializer = AddressSerializer(
            address, 
            data=request.data, 
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
    
    def patch(self, request, address_id):
        """Partially update a specific address"""
        address = self.get_object(request, address_id)
        serializer = AddressSerializer(
            address, 
            data=request.data, 
            partial=True,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
    
    def delete(self, request, address_id):
        """Delete a specific address"""
        address = self.get_object(request, address_id)
        address.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class UserListView(APIView):
    """
    Admin endpoint to list all users
    """
    permission_classes = [IsAdminUserRole]

    def get(self, request):
        users = User.objects.all().order_by('-date_joined')
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)


class UserDetailView(APIView):
    """
    Admin endpoint to get a specific user's details
    """
    permission_classes = [IsAdminUserRole]

    def get(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)
            serializer = UserSerializer(user)
            return Response(serializer.data)
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found'},
                status=status.HTTP_404_NOT_FOUND
            )


# Two-Factor Authentication Views
from .two_factor import (
    generate_2fa_secret, get_totp_uri, generate_qr_code,
    verify_totp_code, get_backup_codes
)


class TwoFactorSetupView(APIView):
    """
    Initialize 2FA setup - generate secret and QR code
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        user = request.user
        
        # Check if 2FA is already enabled
        if user.two_factor_enabled:
            return Response(
                {'error': 'Two-factor authentication is already enabled'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Generate new secret
        secret = generate_2fa_secret()
        
        # Generate TOTP URI
        totp_uri = get_totp_uri(user, secret)
        
        # Generate QR code
        qr_code = generate_qr_code(totp_uri)
        
        # Store secret temporarily (not enabled yet)
        user.two_factor_secret = secret
        user.save(update_fields=['two_factor_secret'])
        
        return Response({
            'secret': secret,
            'qr_code': qr_code,
            'manual_entry_key': secret,
            'message': 'Scan the QR code with your authenticator app, then verify with a code'
        })


class TwoFactorVerifyView(APIView):
    """
    Verify and enable 2FA with a code from authenticator app
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        user = request.user
        code = request.data.get('code', '').strip()
        
        if not code:
            return Response(
                {'error': 'Verification code is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if secret exists
        if not user.two_factor_secret:
            return Response(
                {'error': 'Please setup 2FA first'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Verify the code
        if not verify_totp_code(user.two_factor_secret, code):
            return Response(
                {'error': 'Invalid verification code'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Enable 2FA
        user.two_factor_enabled = True
        user.save(update_fields=['two_factor_enabled'])
        
        # Generate backup codes
        backup_codes = get_backup_codes()
        
        return Response({
            'message': 'Two-factor authentication enabled successfully',
            'backup_codes': backup_codes,
            'warning': 'Save these backup codes in a safe place. You can use them to access your account if you lose your device.'
        })


class TwoFactorDisableView(APIView):
    """
    Disable 2FA (requires password confirmation)
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        user = request.user
        password = request.data.get('password', '')
        
        if not user.check_password(password):
            return Response(
                {'error': 'Invalid password'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not user.two_factor_enabled:
            return Response(
                {'error': 'Two-factor authentication is not enabled'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Disable 2FA
        user.two_factor_enabled = False
        user.two_factor_secret = ''
        user.save(update_fields=['two_factor_enabled', 'two_factor_secret'])
        
        return Response({
            'message': 'Two-factor authentication disabled successfully'
        })


class TwoFactorStatusView(APIView):
    """
    Get current 2FA status
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        user = request.user
        return Response({
            'two_factor_enabled': user.two_factor_enabled,
            'email': user.email
        })
