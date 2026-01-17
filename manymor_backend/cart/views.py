from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

from .models import Cart, CartItem
from .serializers import CartSerializer, CartItemSerializer
from products.models import Product


class CartDetailView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        cart, _ = Cart.objects.get_or_create(user=request.user)
        serializer = CartSerializer(cart)
        return Response(serializer.data)


class AddToCartView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        cart, _ = Cart.objects.get_or_create(user=request.user)

        product_id = request.data.get('product_id')
        quantity = int(request.data.get('quantity', 1))

        product = get_object_or_404(Product, id=product_id)

        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product
        )

        if not created:
            cart_item.quantity += quantity
        else:
            cart_item.quantity = quantity

        cart_item.save()

        return Response(
            CartSerializer(cart).data,
            status=status.HTTP_200_OK
        )


class UpdateCartItemView(APIView):
    permission_classes = [IsAuthenticated]
    
    def put(self, request, item_id):
        cart = get_object_or_404(Cart, user=request.user)
        item = get_object_or_404(CartItem, id=item_id, cart=cart)

        quantity = int(request.data.get('quantity', 1))

        if quantity <= 0:
            item.delete()
        else:
            item.quantity = quantity
            item.save()

        return Response(CartSerializer(cart).data)


class RemoveCartItemView(APIView):
    permission_classes = [IsAuthenticated]
    
    def delete(self, request, item_id):
        cart = get_object_or_404(Cart, user=request.user)
        item = get_object_or_404(CartItem, id=item_id, cart=cart)
        item.delete()

        return Response(CartSerializer(cart).data)
