from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User, Address


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

    def validate(self, data):
        user = authenticate(
            email=data['email'],
            password=data['password']
        )

        if not user:
            raise serializers.ValidationError("Invalid email or password")

        if not user.is_active:
            raise serializers.ValidationError("User account is disabled")

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
        fields = ('id', 'email', 'phone', 'role')


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Extended user serializer with addresses for profile management
    """
    addresses = AddressSerializer(many=True, read_only=True)
    
    class Meta:
        model = User
        fields = ('id', 'email', 'phone', 'role', 'date_joined', 'addresses')
        read_only_fields = ('id', 'email', 'role', 'date_joined')
