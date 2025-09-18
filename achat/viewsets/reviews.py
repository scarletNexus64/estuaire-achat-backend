from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Avg, Count, Q
from ..models import Review, VendorRating, Product, OrderItem, CustomUser
from rest_framework.permissions import IsAuthenticated


class ReviewViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        product_id = request.query_params.get('product_id')
        vendor_id = request.query_params.get('vendor_id')
        user_id = request.query_params.get('user_id')
        
        reviews = Review.objects.all()
        
        if product_id:
            reviews = reviews.filter(product_id=product_id)
        elif vendor_id:
            reviews = reviews.filter(vendor_id=vendor_id)
        elif user_id:
            reviews = reviews.filter(user_id=user_id)

        reviews_data = []
        for review in reviews.order_by('-created_at'):
            reviews_data.append({
                'id': str(review.id),
                'user': {
                    'id': str(review.user.id),
                    'name': f"{review.user.prenom} {review.user.nom}",
                    'avatar': review.user.photo_profile.url if review.user.photo_profile else None
                },
                'product': {
                    'id': str(review.product.id),
                    'name': review.product.name,
                    'images': [{'image': img.image.url} for img in review.product.images.all()]
                },
                'vendor': {
                    'id': str(review.vendor.id),
                    'name': f"{review.vendor.prenom} {review.vendor.nom}"
                },
                'rating': review.rating,
                'comment': review.comment,
                'is_verified': review.is_verified,
                'created_at': review.created_at,
                'updated_at': review.updated_at
            })

        return Response({'reviews': reviews_data})

    def retrieve(self, request, pk=None):
        try:
            review = Review.objects.get(id=pk)
        except Review.DoesNotExist:
            return Response({'error': 'Review not found'}, status=status.HTTP_404_NOT_FOUND)

        review_data = {
            'id': str(review.id),
            'user': {
                'id': str(review.user.id),
                'name': f"{review.user.prenom} {review.user.nom}",
                'avatar': review.user.photo_profile.url if review.user.photo_profile else None
            },
            'product': {
                'id': str(review.product.id),
                'name': review.product.name,
                'description': review.product.description,
                'images': [{'image': img.image.url} for img in review.product.images.all()]
            },
            'vendor': {
                'id': str(review.vendor.id),
                'name': f"{review.vendor.prenom} {review.vendor.nom}"
            },
            'rating': review.rating,
            'comment': review.comment,
            'is_verified': review.is_verified,
            'created_at': review.created_at,
            'updated_at': review.updated_at
        }

        return Response(review_data)

    def create(self, request):
        user = request.user
        product_id = request.data.get('product_id')
        order_item_id = request.data.get('order_item_id')
        rating = request.data.get('rating')
        comment = request.data.get('comment', '')

        if not product_id or not rating:
            return Response({'error': 'product_id and rating are required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            rating = int(rating)
            if rating < 1 or rating > 5:
                raise ValueError()
        except ValueError:
            return Response({'error': 'Rating must be an integer between 1 and 5'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)

        if product.user == user:
            return Response({'error': 'Cannot review your own product'}, status=status.HTTP_400_BAD_REQUEST)

        if Review.objects.filter(user=user, product=product).exists():
            return Response({'error': 'You have already reviewed this product'}, status=status.HTTP_400_BAD_REQUEST)

        order_item = None
        if order_item_id:
            try:
                order_item = OrderItem.objects.get(id=order_item_id, order__user=user, product=product)
            except OrderItem.DoesNotExist:
                return Response({'error': 'Order item not found or not owned by you'}, status=status.HTTP_404_NOT_FOUND)

        review = Review.objects.create(
            user=user,
            product=product,
            order_item=order_item,
            rating=rating,
            comment=comment
        )

        vendor_rating, created = VendorRating.objects.get_or_create(vendor=product.user)
        vendor_rating.update_rating()

        return Response({
            'message': 'Review created successfully',
            'review': {
                'id': str(review.id),
                'rating': review.rating,
                'comment': review.comment,
                'is_verified': review.is_verified
            }
        }, status=status.HTTP_201_CREATED)

    def update(self, request, pk=None):
        user = request.user
        
        try:
            review = Review.objects.get(id=pk, user=user)
        except Review.DoesNotExist:
            return Response({'error': 'Review not found or not owned by you'}, status=status.HTTP_404_NOT_FOUND)

        rating = request.data.get('rating')
        comment = request.data.get('comment')

        if rating is not None:
            try:
                rating = int(rating)
                if rating < 1 or rating > 5:
                    raise ValueError()
                review.rating = rating
            except ValueError:
                return Response({'error': 'Rating must be an integer between 1 and 5'}, status=status.HTTP_400_BAD_REQUEST)

        if comment is not None:
            review.comment = comment

        review.save()

        vendor_rating, created = VendorRating.objects.get_or_create(vendor=review.vendor)
        vendor_rating.update_rating()

        return Response({
            'message': 'Review updated successfully',
            'review': {
                'id': str(review.id),
                'rating': review.rating,
                'comment': review.comment,
                'is_verified': review.is_verified
            }
        })

    def destroy(self, request, pk=None):
        user = request.user
        
        try:
            review = Review.objects.get(id=pk, user=user)
            vendor = review.vendor
            review.delete()
            
            vendor_rating, created = VendorRating.objects.get_or_create(vendor=vendor)
            vendor_rating.update_rating()
            
            return Response({'message': 'Review deleted successfully'})
        except Review.DoesNotExist:
            return Response({'error': 'Review not found or not owned by you'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['get'])
    def product_stats(self, request):
        product_id = request.query_params.get('product_id')
        
        if not product_id:
            return Response({'error': 'product_id is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)

        reviews = Review.objects.filter(product=product)
        
        stats = {
            'total_reviews': reviews.count(),
            'average_rating': 0,
            'rating_breakdown': {
                '1': 0, '2': 0, '3': 0, '4': 0, '5': 0
            }
        }

        if stats['total_reviews'] > 0:
            avg_rating = reviews.aggregate(avg=Avg('rating'))['avg']
            stats['average_rating'] = round(avg_rating, 2) if avg_rating else 0
            
            rating_counts = reviews.values('rating').annotate(count=Count('rating'))
            for item in rating_counts:
                stats['rating_breakdown'][str(item['rating'])] = item['count']

        return Response(stats)

    @action(detail=False, methods=['get'])
    def vendor_stats(self, request):
        vendor_id = request.query_params.get('vendor_id')
        
        if not vendor_id:
            return Response({'error': 'vendor_id is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            vendor = CustomUser.objects.get(id=vendor_id, user_type='vendor')
        except CustomUser.DoesNotExist:
            return Response({'error': 'Vendor not found'}, status=status.HTTP_404_NOT_FOUND)

        try:
            vendor_rating = VendorRating.objects.get(vendor=vendor)
            stats = {
                'vendor_id': str(vendor.id),
                'vendor_name': f"{vendor.prenom} {vendor.nom}",
                'total_reviews': vendor_rating.total_reviews,
                'average_rating': float(vendor_rating.average_rating),
                'rating_breakdown': {
                    '1': vendor_rating.rating_1_count,
                    '2': vendor_rating.rating_2_count,
                    '3': vendor_rating.rating_3_count,
                    '4': vendor_rating.rating_4_count,
                    '5': vendor_rating.rating_5_count,
                },
                'updated_at': vendor_rating.updated_at
            }
        except VendorRating.DoesNotExist:
            stats = {
                'vendor_id': str(vendor.id),
                'vendor_name': f"{vendor.prenom} {vendor.nom}",
                'total_reviews': 0,
                'average_rating': 0,
                'rating_breakdown': {
                    '1': 0, '2': 0, '3': 0, '4': 0, '5': 0
                },
                'updated_at': None
            }

        return Response(stats)

    @action(detail=False, methods=['get'])
    def my_reviews(self, request):
        user = request.user
        reviews = Review.objects.filter(user=user).order_by('-created_at')
        
        reviews_data = []
        for review in reviews:
            reviews_data.append({
                'id': str(review.id),
                'product': {
                    'id': str(review.product.id),
                    'name': review.product.name,
                    'images': [{'image': img.image.url} for img in review.product.images.all()]
                },
                'vendor': {
                    'id': str(review.vendor.id),
                    'name': f"{review.vendor.prenom} {review.vendor.nom}"
                },
                'rating': review.rating,
                'comment': review.comment,
                'is_verified': review.is_verified,
                'created_at': review.created_at,
                'updated_at': review.updated_at
            })

        return Response({'reviews': reviews_data})

    @action(detail=False, methods=['get'])
    def pending_reviews(self, request):
        user = request.user
        
        order_items = OrderItem.objects.filter(
            order__user=user,
            order__status='delivered',
            review__isnull=True
        ).select_related('product', 'vendor')
        
        pending_data = []
        for item in order_items:
            pending_data.append({
                'order_item_id': str(item.id),
                'order_number': item.order.order_number,
                'product': {
                    'id': str(item.product.id),
                    'name': item.product.name,
                    'images': [{'image': img.image.url} for img in item.product.images.all()]
                },
                'vendor': {
                    'id': str(item.vendor.id),
                    'name': f"{item.vendor.prenom} {item.vendor.nom}"
                },
                'delivered_date': item.order.updated_at
            })

        return Response({'pending_reviews': pending_data})