from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.db.models import Q
from ..models import Order, OrderItem, Cart, Product, Location, CustomUser
from rest_framework.permissions import IsAuthenticated


class OrderViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        user = request.user
        user_type = request.query_params.get('type', 'customer')
        
        if user_type == 'vendor':
            orders = Order.objects.filter(items__vendor=user).distinct().order_by('-created_at')
        else:
            orders = Order.objects.filter(user=user).order_by('-created_at')

        orders_data = []
        for order in orders:
            items_data = []
            for item in order.items.all():
                if user_type == 'vendor' and item.vendor != user:
                    continue
                    
                items_data.append({
                    'id': str(item.id),
                    'product': {
                        'id': str(item.product.id),
                        'name': item.product.name,
                        'images': [{'image': img.image.url} for img in item.product.images.all()],
                    },
                    'vendor': {
                        'id': str(item.vendor.id),
                        'name': f"{item.vendor.prenom} {item.vendor.nom}"
                    },
                    'quantity': item.quantity,
                    'unit_price': str(item.unit_price),
                    'total_price': str(item.total_price)
                })

            if items_data or user_type == 'customer':
                orders_data.append({
                    'id': str(order.id),
                    'order_number': order.order_number,
                    'status': order.status,
                    'total_amount': str(order.total_amount),
                    'delivery_location': {
                        'name': order.delivery_location.name,
                        'latitude': str(order.delivery_location.latitude),
                        'longitude': str(order.delivery_location.longitude)
                    },
                    'customer': {
                        'id': str(order.user.id),
                        'name': f"{order.user.prenom} {order.user.nom}"
                    } if user_type == 'vendor' else None,
                    'notes': order.notes,
                    'items': items_data,
                    'created_at': order.created_at,
                    'updated_at': order.updated_at
                })

        return Response({'orders': orders_data})

    def retrieve(self, request, pk=None):
        user = request.user
        
        try:
            if user.user_type == 'vendor':
                order = Order.objects.filter(
                    Q(id=pk) & Q(items__vendor=user)
                ).distinct().first()
            else:
                order = Order.objects.get(id=pk, user=user)
                
            if not order:
                return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)
        except Order.DoesNotExist:
            return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)

        items_data = []
        for item in order.items.all():
            if user.user_type == 'vendor' and item.vendor != user:
                continue
                
            items_data.append({
                'id': str(item.id),
                'product': {
                    'id': str(item.product.id),
                    'name': item.product.name,
                    'description': item.product.description,
                    'images': [{'image': img.image.url} for img in item.product.images.all()],
                },
                'vendor': {
                    'id': str(item.vendor.id),
                    'name': f"{item.vendor.prenom} {item.vendor.nom}"
                },
                'quantity': item.quantity,
                'unit_price': str(item.unit_price),
                'total_price': str(item.total_price),
                'created_at': item.created_at
            })

        order_data = {
            'id': str(order.id),
            'order_number': order.order_number,
            'status': order.status,
            'total_amount': str(order.total_amount),
            'delivery_location': {
                'name': order.delivery_location.name,
                'latitude': str(order.delivery_location.latitude),
                'longitude': str(order.delivery_location.longitude)
            },
            'customer': {
                'id': str(order.user.id),
                'name': f"{order.user.prenom} {order.user.nom}",
                'identifier': order.user.identifier
            } if user.user_type == 'vendor' else None,
            'notes': order.notes,
            'items': items_data,
            'created_at': order.created_at,
            'updated_at': order.updated_at
        }

        return Response(order_data)

    @action(detail=False, methods=['post'])
    def create_from_cart(self, request):
        user = request.user
        delivery_location_id = request.data.get('delivery_location_id')
        notes = request.data.get('notes', '')

        if not delivery_location_id:
            return Response({'error': 'delivery_location_id is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            delivery_location = Location.objects.get(id=delivery_location_id, user=user)
        except Location.DoesNotExist:
            return Response({'error': 'Delivery location not found'}, status=status.HTTP_404_NOT_FOUND)

        try:
            cart = Cart.objects.get(user=user)
        except Cart.DoesNotExist:
            return Response({'error': 'Cart is empty'}, status=status.HTTP_400_BAD_REQUEST)

        if not cart.items.exists():
            return Response({'error': 'Cart is empty'}, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            total_amount = cart.total_amount

            order = Order.objects.create(
                user=user,
                total_amount=total_amount,
                delivery_location=delivery_location,
                notes=notes
            )

            for cart_item in cart.items.all():
                if cart_item.product.is_stock and cart_item.quantity > cart_item.product.quantity:
                    raise ValueError(f'Insufficient stock for {cart_item.product.name}')

                OrderItem.objects.create(
                    order=order,
                    product=cart_item.product,
                    vendor=cart_item.product.user,
                    quantity=cart_item.quantity,
                    unit_price=cart_item.product.price
                )

                if cart_item.product.is_stock:
                    cart_item.product.quantity -= cart_item.quantity
                    if cart_item.product.quantity == 0:
                        cart_item.product.status = 'sold'
                    cart_item.product.save()

            cart.items.all().delete()

        return Response({
            'message': 'Order created successfully',
            'order': {
                'id': str(order.id),
                'order_number': order.order_number,
                'total_amount': str(order.total_amount),
                'status': order.status
            }
        }, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['patch'])
    def update_status(self, request, pk=None):
        user = request.user
        new_status = request.data.get('status')

        if not new_status:
            return Response({'error': 'status is required'}, status=status.HTTP_400_BAD_REQUEST)

        valid_statuses = [choice[0] for choice in Order.STATUS_CHOICES]
        if new_status not in valid_statuses:
            return Response({'error': f'Invalid status. Valid options: {valid_statuses}'}, 
                          status=status.HTTP_400_BAD_REQUEST)

        try:
            if user.user_type == 'vendor':
                order = Order.objects.filter(
                    Q(id=pk) & Q(items__vendor=user)
                ).distinct().first()
            else:
                order = Order.objects.get(id=pk, user=user)
                
            if not order:
                return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)
        except Order.DoesNotExist:
            return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)

        if user.user_type == 'customer' and new_status not in ['cancelled']:
            return Response({'error': 'Customers can only cancel orders'}, status=status.HTTP_403_FORBIDDEN)

        order.status = new_status
        order.save()

        return Response({
            'message': 'Order status updated successfully',
            'order': {
                'id': str(order.id),
                'order_number': order.order_number,
                'status': order.status
            }
        })

    @action(detail=False, methods=['get'])
    def my_sales(self, request):
        user = request.user
        
        if user.user_type != 'vendor':
            return Response({'error': 'Only vendors can access sales data'}, status=status.HTTP_403_FORBIDDEN)

        order_items = OrderItem.objects.filter(vendor=user).order_by('-created_at')
        
        sales_data = []
        for item in order_items:
            sales_data.append({
                'id': str(item.id),
                'order_number': item.order.order_number,
                'product': {
                    'id': str(item.product.id),
                    'name': item.product.name,
                },
                'customer': {
                    'id': str(item.order.user.id),
                    'name': f"{item.order.user.prenom} {item.order.user.nom}"
                },
                'quantity': item.quantity,
                'unit_price': str(item.unit_price),
                'total_price': str(item.total_price),
                'order_status': item.order.status,
                'created_at': item.created_at
            })

        return Response({'sales': sales_data})