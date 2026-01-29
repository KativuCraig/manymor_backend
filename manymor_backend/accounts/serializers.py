from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User, Address
from .two_factor import verify_totp_code


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = ('email', 'password', 'phone')

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            phone=validated_data.get('phone', '')
        )
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    two_factor_code = serializers.CharField(required=False, allow_blank=True, write_only=True)

    def validate(self, data):
        user = authenticate(
            email=data['email'],
            password=data['password']
        )

        if not user:
            raise serializers.ValidationError("Invalid email or password")

        if not user.is_active:
            raise serializers.ValidationError("User account is disabled")

        # Check if 2FA is enabled for this user
        if user.two_factor_enabled:
            two_factor_code = data.get('two_factor_code', '').strip()
            
            if not two_factor_code:
                # Return a special flag indicating 2FA is required
                raise serializers.ValidationError({
                    'two_factor_required': True,
                    'message': 'Two-factor authentication code required'
                })
            
            # Verify the 2FA code
            if not verify_totp_code(user.two_factor_secret, two_factor_code):
                raise serializers.ValidationError("Invalid two-factor authentication code")

        return user


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ('id', 'label', 'city', 'address_line', 'is_default')
        
    def validate(self, data):
        # If this address is being set as default, ensure only one default exists
        if data.get('is_default', False):
            user = self.context['request'].user
            # Unset other default addresses
            Address.objects.filter(user=user, is_default=True).update(is_default=False)
        return data


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'phone', 'role', 'two_factor_enabled')


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Extended user serializer with addresses for profile management
    """
    addresses = AddressSerializer(many=True, read_only=True)
    
    class Meta:
        model = User
        fields = ('id', 'email', 'phone', 'role', 'date_joined', 'addresses', 'two_factor_enabled')
        read_only_fields = ('id', 'email', 'role', 'date_joined', 'two_factor_enabled')
