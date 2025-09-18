from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from ..models import Cart, CartItem, Product, CustomUser
from rest_framework.permissions import IsAuthenticated


class CartViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def get_or_create_cart(self, user):
        cart, created = Cart.objects.get_or_create(user=user)
        return cart

    def list(self, request):
        user = request.user
        cart = self.get_or_create_cart(user)
        
        items_data = []
        for item in cart.items.all():
            items_data.append({
                'id': str(item.id),
                'product': {
                    'id': str(item.product.id),
                    'name': item.product.name,
                    'price': str(item.product.price),
                    'images': [{'image': img.image.url} for img in item.product.images.all()],
                    'vendor': {
                        'name': f"{item.product.user.prenom} {item.product.user.nom}",
                        'id': str(item.product.user.id)
                    }
                },
                'quantity': item.quantity,
                'total_price': str(item.total_price),
                'created_at': item.created_at
            })

        return Response({
            'cart_id': str(cart.id),
            'total_items': cart.total_items,
            'total_amount': str(cart.total_amount),
            'items': items_data
        })

    @action(detail=False, methods=['post'])
    def add_item(self, request):
        user = request.user
        product_id = request.data.get('product_id')
        quantity = int(request.data.get('quantity', 1))

        if not product_id:
            return Response({'error': 'product_id is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            product = Product.objects.get(id=product_id, status='active')
        except Product.DoesNotExist:
            return Response({'error': 'Product not found or inactive'}, status=status.HTTP_404_NOT_FOUND)

        if product.user == user:
            return Response({'error': 'Cannot add your own product to cart'}, status=status.HTTP_400_BAD_REQUEST)

        if quantity <= 0:
            return Response({'error': 'Quantity must be positive'}, status=status.HTTP_400_BAD_REQUEST)

        if product.is_stock and quantity > product.quantity:
            return Response({'error': f'Only {product.quantity} items available'}, status=status.HTTP_400_BAD_REQUEST)

        cart = self.get_or_create_cart(user)
        
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={'quantity': quantity}
        )

        if not created:
            cart_item.quantity += quantity
            if product.is_stock and cart_item.quantity > product.quantity:
                return Response({'error': f'Total quantity would exceed available stock ({product.quantity})'}, 
                              status=status.HTTP_400_BAD_REQUEST)
            cart_item.save()

        return Response({
            'message': 'Item added to cart successfully',
            'cart_item': {
                'id': str(cart_item.id),
                'product_name': product.name,
                'quantity': cart_item.quantity,
                'total_price': str(cart_item.total_price)
            }
        }, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['patch'])
    def update_item(self, request):
        user = request.user
        item_id = request.data.get('item_id')
        quantity = request.data.get('quantity')

        if not item_id or quantity is None:
            return Response({'error': 'item_id and quantity are required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            quantity = int(quantity)
        except ValueError:
            return Response({'error': 'Quantity must be a number'}, status=status.HTTP_400_BAD_REQUEST)

        if quantity <= 0:
            return Response({'error': 'Quantity must be positive'}, status=status.HTTP_400_BAD_REQUEST)

        cart = self.get_or_create_cart(user)
        
        try:
            cart_item = CartItem.objects.get(id=item_id, cart=cart)
        except CartItem.DoesNotExist:
            return Response({'error': 'Cart item not found'}, status=status.HTTP_404_NOT_FOUND)

        if cart_item.product.is_stock and quantity > cart_item.product.quantity:
            return Response({'error': f'Only {cart_item.product.quantity} items available'}, 
                          status=status.HTTP_400_BAD_REQUEST)

        cart_item.quantity = quantity
        cart_item.save()

        return Response({
            'message': 'Cart item updated successfully',
            'cart_item': {
                'id': str(cart_item.id),
                'quantity': cart_item.quantity,
                'total_price': str(cart_item.total_price)
            }
        })

    @action(detail=False, methods=['delete'])
    def remove_item(self, request):
        user = request.user
        item_id = request.data.get('item_id')

        if not item_id:
            return Response({'error': 'item_id is required'}, status=status.HTTP_400_BAD_REQUEST)

        cart = self.get_or_create_cart(user)
        
        try:
            cart_item = CartItem.objects.get(id=item_id, cart=cart)
            cart_item.delete()
            return Response({'message': 'Item removed from cart successfully'})
        except CartItem.DoesNotExist:
            return Response({'error': 'Cart item not found'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['delete'])
    def clear(self, request):
        user = request.user
        cart = self.get_or_create_cart(user)
        cart.items.all().delete()
        return Response({'message': 'Cart cleared successfully'})