from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum, Count, Avg, Q, Min, Max
from django.utils import timezone
from datetime import timedelta
from ..models import Product, Order, OrderItem, Review, Wishlist, Cart, CustomUser


class CustomerDashboardViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        user = request.user
        
        if user.user_type != 'customer':
            return Response({'error': 'Only customers can access this dashboard'}, status=status.HTTP_403_FORBIDDEN)

        return Response({
            'message': 'Customer dashboard endpoints available',
            'endpoints': {
                'overview': '/customer-dashboard/overview/',
                'order_history': '/customer-dashboard/order_history/',
                'wishlist_stats': '/customer-dashboard/wishlist_stats/',
                'spending_analytics': '/customer-dashboard/spending_analytics/',
                'favorite_vendors': '/customer-dashboard/favorite_vendors/',
                'recommendations': '/customer-dashboard/recommendations/',
                'review_history': '/customer-dashboard/review_history/',
            }
        })

    @action(detail=False, methods=['get'])
    def overview(self, request):
        user = request.user
        
        if user.user_type != 'customer':
            return Response({'error': 'Only customers can access this dashboard'}, status=status.HTTP_403_FORBIDDEN)

        # Statistiques générales
        total_orders = Order.objects.filter(user=user).count()
        completed_orders = Order.objects.filter(user=user, status='delivered').count()
        pending_orders = Order.objects.filter(
            user=user, 
            status__in=['pending', 'confirmed', 'processing', 'shipped']
        ).count()

        # Montant total dépensé
        total_spent = Order.objects.filter(user=user).aggregate(
            total=Sum('total_amount')
        )['total'] or 0

        # Panier actuel
        try:
            cart = Cart.objects.get(user=user)
            cart_items = cart.total_items
            cart_amount = cart.total_amount
        except Cart.DoesNotExist:
            cart_items = 0
            cart_amount = 0

        # Wishlist
        wishlist_count = Wishlist.objects.filter(user=user).count()

        # Avis donnés
        reviews_given = Review.objects.filter(user=user).count()

        # Commandes récentes
        recent_orders = Order.objects.filter(user=user).order_by('-created_at')[:5]
        recent_orders_data = []
        for order in recent_orders:
            items_count = order.items.count()
            recent_orders_data.append({
                'id': str(order.id),
                'order_number': order.order_number,
                'status': order.status,
                'total_amount': str(order.total_amount),
                'items_count': items_count,
                'created_at': order.created_at
            })

        # Produits favoris (les plus achetés)
        favorite_products = OrderItem.objects.filter(
            order__user=user
        ).values(
            'product__id', 'product__name'
        ).annotate(
            times_bought=Count('id'),
            total_spent=Sum('total_price')
        ).order_by('-times_bought')[:5]

        return Response({
            'customer_info': {
                'id': str(user.id),
                'name': f"{user.prenom} {user.nom}",
                'identifier': user.identifier,
                'joined_date': user.date_joined
            },
            'general_stats': {
                'total_orders': total_orders,
                'completed_orders': completed_orders,
                'pending_orders': pending_orders,
                'total_spent': str(total_spent),
                'cart_items': cart_items,
                'cart_amount': str(cart_amount),
                'wishlist_count': wishlist_count,
                'reviews_given': reviews_given
            },
            'recent_orders': recent_orders_data,
            'favorite_products': list(favorite_products)
        })

    @action(detail=False, methods=['get'])
    def order_history(self, request):
        user = request.user
        
        if user.user_type != 'customer':
            return Response({'error': 'Only customers can access this dashboard'}, status=status.HTTP_403_FORBIDDEN)

        # Filtres
        order_status = request.query_params.get('status')
        limit = int(request.query_params.get('limit', 20))
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')

        orders_query = Order.objects.filter(user=user)

        if order_status:
            orders_query = orders_query.filter(status=order_status)

        if start_date:
            try:
                start_date = timezone.datetime.fromisoformat(start_date)
                orders_query = orders_query.filter(created_at__gte=start_date)
            except ValueError:
                return Response({'error': 'Invalid start_date format'}, status=status.HTTP_400_BAD_REQUEST)

        if end_date:
            try:
                end_date = timezone.datetime.fromisoformat(end_date)
                orders_query = orders_query.filter(created_at__lte=end_date)
            except ValueError:
                return Response({'error': 'Invalid end_date format'}, status=status.HTTP_400_BAD_REQUEST)

        orders = orders_query.prefetch_related('items__product', 'items__vendor').order_by('-created_at')[:limit]

        orders_data = []
        for order in orders:
            items_data = []
            for item in order.items.all():
                items_data.append({
                    'product': {
                        'id': str(item.product.id),
                        'name': item.product.name,
                        'images': [{'image': img.image.url} for img in item.product.images.all()[:1]]
                    },
                    'vendor': {
                        'id': str(item.vendor.id),
                        'name': f"{item.vendor.prenom} {item.vendor.nom}"
                    },
                    'quantity': item.quantity,
                    'unit_price': str(item.unit_price),
                    'total_price': str(item.total_price)
                })

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
                'notes': order.notes,
                'items': items_data,
                'created_at': order.created_at,
                'updated_at': order.updated_at
            })

        return Response({
            'orders': orders_data,
            'total_count': len(orders_data),
            'filters': {
                'status': order_status,
                'limit': limit,
                'start_date': start_date,
                'end_date': end_date
            }
        })

    @action(detail=False, methods=['get'])
    def wishlist_stats(self, request):
        user = request.user
        
        if user.user_type != 'customer':
            return Response({'error': 'Only customers can access this dashboard'}, status=status.HTTP_403_FORBIDDEN)

        wishlists = Wishlist.objects.filter(user=user).select_related(
            'product__user', 'product__category'
        ).prefetch_related('product__images')

        total_wishlist_items = wishlists.count()
        total_wishlist_value = sum(w.product.price for w in wishlists if w.product.status == 'active')

        # Répartition par catégorie
        category_breakdown = wishlists.values(
            'product__category__name'
        ).annotate(
            count=Count('id')
        ).order_by('-count')

        # Produits en wishlist disponibles/indisponibles
        available_count = wishlists.filter(product__status='active', product__is_stock=True, product__quantity__gt=0).count()
        unavailable_count = total_wishlist_items - available_count

        # Items de wishlist récents
        recent_wishlist = wishlists.order_by('-created_at')[:10]
        recent_data = []
        for item in recent_wishlist:
            recent_data.append({
                'id': str(item.id),
                'product': {
                    'id': str(item.product.id),
                    'name': item.product.name,
                    'price': str(item.product.price),
                    'status': item.product.status,
                    'is_available': item.product.status == 'active' and item.product.is_stock and item.product.quantity > 0,
                    'images': [{'image': img.image.url} for img in item.product.images.all()[:1]]
                },
                'vendor': {
                    'id': str(item.product.user.id),
                    'name': f"{item.product.user.prenom} {item.product.user.nom}"
                },
                'added_at': item.created_at
            })

        return Response({
            'wishlist_summary': {
                'total_items': total_wishlist_items,
                'total_value': str(total_wishlist_value),
                'available_items': available_count,
                'unavailable_items': unavailable_count
            },
            'category_breakdown': list(category_breakdown),
            'recent_wishlist': recent_data,
            'recommendations': {
                'move_to_cart': available_count,
                'price_alerts': unavailable_count  # Pourrait être implémenté plus tard
            }
        })

    @action(detail=False, methods=['get'])
    def spending_analytics(self, request):
        user = request.user
        
        if user.user_type != 'customer':
            return Response({'error': 'Only customers can access this dashboard'}, status=status.HTTP_403_FORBIDDEN)

        # Période d'analyse (12 derniers mois par défaut)
        months = int(request.query_params.get('months', 12))

        # Dépenses mensuelles
        monthly_spending = []
        for i in range(months):
            month_start = timezone.now().replace(day=1) - timedelta(days=30*i)
            month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
            
            month_orders = Order.objects.filter(
                user=user,
                created_at__gte=month_start,
                created_at__lte=month_end
            ).aggregate(
                total_spent=Sum('total_amount'),
                orders_count=Count('id')
            )

            monthly_spending.append({
                'month': month_start.strftime('%Y-%m'),
                'month_name': month_start.strftime('%B %Y'),
                'total_spent': str(month_orders['total_spent'] or 0),
                'orders_count': month_orders['orders_count'] or 0
            })

        monthly_spending.reverse()  # Ordre chronologique

        # Dépenses par catégorie
        category_spending = OrderItem.objects.filter(
            order__user=user
        ).values(
            'product__category__name'
        ).annotate(
            total_spent=Sum('total_price'),
            items_count=Count('id')
        ).order_by('-total_spent')[:10]

        # Statistiques générales
        total_lifetime_spending = Order.objects.filter(user=user).aggregate(
            total=Sum('total_amount')
        )['total'] or 0

        average_order_value = Order.objects.filter(user=user).aggregate(
            avg=Avg('total_amount')
        )['avg'] or 0

        # Vendeurs favoris (par montant dépensé)
        favorite_vendors = OrderItem.objects.filter(
            order__user=user
        ).values(
            'vendor__id', 'vendor__prenom', 'vendor__nom'
        ).annotate(
            total_spent=Sum('total_price'),
            orders_count=Count('order', distinct=True)
        ).order_by('-total_spent')[:5]

        favorite_vendors_data = []
        for vendor in favorite_vendors:
            favorite_vendors_data.append({
                'vendor_id': str(vendor['vendor__id']),
                'vendor_name': f"{vendor['vendor__prenom']} {vendor['vendor__nom']}",
                'total_spent': str(vendor['total_spent']),
                'orders_count': vendor['orders_count']
            })

        return Response({
            'spending_overview': {
                'total_lifetime_spending': str(total_lifetime_spending),
                'average_order_value': str(round(average_order_value, 2)),
                'total_orders': Order.objects.filter(user=user).count()
            },
            'monthly_spending': monthly_spending,
            'category_spending': list(category_spending),
            'favorite_vendors': favorite_vendors_data,
            'insights': {
                'highest_spending_month': max(monthly_spending, key=lambda x: float(x['total_spent'])) if monthly_spending else None,
                'most_frequent_category': category_spending[0]['product__category__name'] if category_spending else None
            }
        })

    @action(detail=False, methods=['get'])
    def favorite_vendors(self, request):
        user = request.user
        
        if user.user_type != 'customer':
            return Response({'error': 'Only customers can access this dashboard'}, status=status.HTTP_403_FORBIDDEN)

        # Vendeurs par montant d'achat
        vendors_by_spending = OrderItem.objects.filter(
            order__user=user
        ).values(
            'vendor__id', 'vendor__prenom', 'vendor__nom', 'vendor__identifier'
        ).annotate(
            total_spent=Sum('total_price'),
            orders_count=Count('order', distinct=True),
            items_bought=Sum('quantity'),
            last_order=Max('order__created_at')
        ).order_by('-total_spent')

        vendors_data = []
        for vendor_stat in vendors_by_spending:
            vendor_id = vendor_stat['vendor__id']
            
            # Récupérer les informations de rating du vendeur
            try:
                from ..models import VendorRating
                vendor_rating = VendorRating.objects.get(vendor_id=vendor_id)
                avg_rating = float(vendor_rating.average_rating)
                total_reviews = vendor_rating.total_reviews
            except:
                avg_rating = 0
                total_reviews = 0

            vendors_data.append({
                'vendor': {
                    'id': str(vendor_id),
                    'name': f"{vendor_stat['vendor__prenom']} {vendor_stat['vendor__nom']}",
                    'identifier': vendor_stat['vendor__identifier']
                },
                'relationship': {
                    'total_spent': str(vendor_stat['total_spent']),
                    'orders_count': vendor_stat['orders_count'],
                    'items_bought': vendor_stat['items_bought'],
                    'last_order': vendor_stat['last_order']
                },
                'vendor_rating': {
                    'average_rating': avg_rating,
                    'total_reviews': total_reviews
                }
            })

        return Response({
            'favorite_vendors': vendors_data,
            'summary': {
                'total_vendors': len(vendors_data),
                'top_vendor': vendors_data[0] if vendors_data else None
            }
        })

    @action(detail=False, methods=['get'])
    def recommendations(self, request):
        user = request.user
        
        if user.user_type != 'customer':
            return Response({'error': 'Only customers can access this dashboard'}, status=status.HTTP_403_FORBIDDEN)

        # Produits basés sur l'historique d'achat
        purchased_categories = OrderItem.objects.filter(
            order__user=user
        ).values_list('product__category_id', flat=True).distinct()

        category_recommendations = Product.objects.filter(
            category_id__in=purchased_categories,
            status='active',
            is_stock=True,
            quantity__gt=0
        ).exclude(
            id__in=OrderItem.objects.filter(
                order__user=user
            ).values_list('product_id', flat=True)
        ).select_related('user', 'location', 'category').prefetch_related('images', 'reviews')[:10]

        # Produits similaires à la wishlist
        wishlist_categories = Wishlist.objects.filter(
            user=user
        ).values_list('product__category_id', flat=True).distinct()

        wishlist_recommendations = Product.objects.filter(
            category_id__in=wishlist_categories,
            status='active',
            is_stock=True,
            quantity__gt=0
        ).exclude(
            id__in=Wishlist.objects.filter(
                user=user
            ).values_list('product_id', flat=True)
        ).select_related('user', 'location', 'category').prefetch_related('images', 'reviews')[:10]

        def format_product_data(products):
            data = []
            for product in products:
                avg_rating = product.reviews.aggregate(avg=Avg('rating'))['avg'] or 0
                reviews_count = product.reviews.count()
                
                data.append({
                    'id': str(product.id),
                    'name': product.name,
                    'price': str(product.price),
                    'images': [{'image': img.image.url} for img in product.images.all()[:1]],
                    'vendor': {
                        'name': f"{product.user.prenom} {product.user.nom}"
                    },
                    'location': {
                        'name': product.location.name
                    },
                    'category': {
                        'name': product.category.name if product.category else None
                    },
                    'reviews': {
                        'average_rating': round(avg_rating, 2),
                        'total_reviews': reviews_count
                    }
                })
            return data

        return Response({
            'based_on_purchases': format_product_data(category_recommendations),
            'based_on_wishlist': format_product_data(wishlist_recommendations),
            'trending_products': format_product_data(
                Product.objects.filter(
                    status='active',
                    is_stock=True,
                    quantity__gt=0
                ).annotate(
                    order_count=Count('order_items')
                ).order_by('-order_count')[:5]
            )
        })

    @action(detail=False, methods=['get'])
    def review_history(self, request):
        user = request.user
        
        if user.user_type != 'customer':
            return Response({'error': 'Only customers can access this dashboard'}, status=status.HTTP_403_FORBIDDEN)

        reviews = Review.objects.filter(user=user).select_related(
            'product', 'vendor'
        ).order_by('-created_at')

        reviews_data = []
        for review in reviews:
            reviews_data.append({
                'id': str(review.id),
                'product': {
                    'id': str(review.product.id),
                    'name': review.product.name
                },
                'vendor': {
                    'id': str(review.vendor.id),
                    'name': f"{review.vendor.prenom} {review.vendor.nom}"
                },
                'rating': review.rating,
                'comment': review.comment,
                'is_verified': review.is_verified,
                'created_at': review.created_at
            })

        # Avis en attente (produits livrés non notés)
        pending_reviews = OrderItem.objects.filter(
            order__user=user,
            order__status='delivered',
            review__isnull=True
        ).select_related('product', 'vendor')

        pending_data = []
        for item in pending_reviews:
            pending_data.append({
                'order_item_id': str(item.id),
                'product': {
                    'id': str(item.product.id),
                    'name': item.product.name
                },
                'vendor': {
                    'id': str(item.vendor.id),
                    'name': f"{item.vendor.prenom} {item.vendor.nom}"
                },
                'delivered_date': item.order.updated_at
            })

        return Response({
            'reviews_given': reviews_data,
            'pending_reviews': pending_data,
            'summary': {
                'total_reviews': len(reviews_data),
                'pending_count': len(pending_data),
                'average_rating_given': round(sum(r.rating for r in reviews) / max(len(reviews), 1), 2) if reviews else 0
            }
        })