from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum, Count, Avg, Q, Min, Max
from django.utils import timezone
from datetime import timedelta
from ..models import Product, Order, OrderItem, Review, VendorRating, CustomUser


class VendorDashboardViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        user = request.user
        
        if user.user_type != 'vendor':
            return Response({'error': 'Only vendors can access this dashboard'}, status=status.HTTP_403_FORBIDDEN)

        return Response({
            'message': 'Vendor dashboard endpoints available',
            'endpoints': {
                'overview': '/vendor-dashboard/overview/',
                'sales_analytics': '/vendor-dashboard/sales_analytics/',
                'product_performance': '/vendor-dashboard/product_performance/',
                'recent_orders': '/vendor-dashboard/recent_orders/',
                'reviews_summary': '/vendor-dashboard/reviews_summary/',
                'monthly_stats': '/vendor-dashboard/monthly_stats/',
            }
        })

    @action(detail=False, methods=['get'])
    def overview(self, request):
        user = request.user
        
        if user.user_type != 'vendor':
            return Response({'error': 'Only vendors can access this dashboard'}, status=status.HTTP_403_FORBIDDEN)

        # Statistiques générales
        total_products = Product.objects.filter(user=user).count()
        active_products = Product.objects.filter(user=user, status='active').count()
        total_sales = OrderItem.objects.filter(vendor=user).count()
        
        # Revenue total
        total_revenue = OrderItem.objects.filter(vendor=user).aggregate(
            total=Sum('total_price')
        )['total'] or 0

        # Commandes en cours
        pending_orders = OrderItem.objects.filter(
            vendor=user,
            order__status__in=['pending', 'confirmed', 'processing']
        ).count()

        # Statistiques des avis
        try:
            vendor_rating = VendorRating.objects.get(vendor=user)
            avg_rating = float(vendor_rating.average_rating)
            total_reviews = vendor_rating.total_reviews
        except VendorRating.DoesNotExist:
            avg_rating = 0
            total_reviews = 0

        # Produits les plus vendus (top 5)
        top_products = OrderItem.objects.filter(vendor=user).values(
            'product__name', 'product__id'
        ).annotate(
            total_sold=Sum('quantity'),
            total_revenue=Sum('total_price')
        ).order_by('-total_sold')[:5]

        # Commandes récentes
        recent_orders = OrderItem.objects.filter(vendor=user).select_related(
            'order', 'product'
        ).order_by('-created_at')[:5]

        recent_orders_data = []
        for item in recent_orders:
            recent_orders_data.append({
                'order_number': item.order.order_number,
                'product_name': item.product.name,
                'quantity': item.quantity,
                'total_price': str(item.total_price),
                'status': item.order.status,
                'customer_name': f"{item.order.user.prenom} {item.order.user.nom}",
                'created_at': item.created_at
            })

        return Response({
            'vendor_info': {
                'id': str(user.id),
                'name': f"{user.prenom} {user.nom}",
                'identifier': user.identifier,
                'joined_date': user.date_joined
            },
            'general_stats': {
                'total_products': total_products,
                'active_products': active_products,
                'inactive_products': total_products - active_products,
                'total_sales': total_sales,
                'total_revenue': str(total_revenue),
                'pending_orders': pending_orders,
                'average_rating': avg_rating,
                'total_reviews': total_reviews
            },
            'top_products': list(top_products),
            'recent_orders': recent_orders_data
        })

    @action(detail=False, methods=['get'])
    def sales_analytics(self, request):
        user = request.user
        
        if user.user_type != 'vendor':
            return Response({'error': 'Only vendors can access this dashboard'}, status=status.HTTP_403_FORBIDDEN)

        # Période d'analyse (30 derniers jours par défaut)
        days = int(request.query_params.get('days', 30))
        end_date = timezone.now()
        start_date = end_date - timedelta(days=days)

        # Ventes par jour
        daily_sales = OrderItem.objects.filter(
            vendor=user,
            created_at__gte=start_date,
            created_at__lte=end_date
        ).extra({
            'day': 'date(created_at)'
        }).values('day').annotate(
            total_sales=Sum('total_price'),
            orders_count=Count('order', distinct=True),
            items_sold=Sum('quantity')
        ).order_by('day')

        # Répartition par statut de commande
        order_status_stats = OrderItem.objects.filter(vendor=user).values(
            'order__status'
        ).annotate(
            count=Count('id'),
            total_revenue=Sum('total_price')
        )

        # Produits les plus rentables
        profitable_products = OrderItem.objects.filter(vendor=user).values(
            'product__name', 'product__id'
        ).annotate(
            total_revenue=Sum('total_price'),
            units_sold=Sum('quantity'),
            orders_count=Count('order', distinct=True)
        ).order_by('-total_revenue')[:10]

        # Analyse des prix
        price_analysis = Product.objects.filter(user=user, status='active').aggregate(
            min_price=Min('price'),
            max_price=Max('price'),
            avg_price=Avg('price')
        )

        return Response({
            'period': {
                'start_date': start_date,
                'end_date': end_date,
                'days': days
            },
            'daily_sales': list(daily_sales),
            'order_status_breakdown': list(order_status_stats),
            'top_profitable_products': list(profitable_products),
            'price_analysis': {
                'min_price': price_analysis['min_price'],
                'max_price': price_analysis['max_price'],
                'average_price': round(price_analysis['avg_price'] or 0, 2)
            }
        })

    @action(detail=False, methods=['get'])
    def product_performance(self, request):
        user = request.user
        
        if user.user_type != 'vendor':
            return Response({'error': 'Only vendors can access this dashboard'}, status=status.HTTP_403_FORBIDDEN)

        products = Product.objects.filter(user=user).prefetch_related('reviews', 'order_items')
        
        performance_data = []
        for product in products:
            # Statistiques de vente
            sales_stats = OrderItem.objects.filter(product=product).aggregate(
                total_sold=Sum('quantity'),
                total_revenue=Sum('total_price'),
                orders_count=Count('order', distinct=True)
            )

            # Statistiques des avis
            reviews_stats = product.reviews.aggregate(
                avg_rating=Avg('rating'),
                total_reviews=Count('id')
            )

            # Performance relative
            view_count = 0  # Pourrait être ajouté plus tard avec un modèle de tracking
            
            performance_data.append({
                'product': {
                    'id': str(product.id),
                    'name': product.name,
                    'price': str(product.price),
                    'status': product.status,
                    'quantity': product.quantity,
                    'is_stock': product.is_stock
                },
                'sales': {
                    'total_sold': sales_stats['total_sold'] or 0,
                    'total_revenue': str(sales_stats['total_revenue'] or 0),
                    'orders_count': sales_stats['orders_count'] or 0
                },
                'reviews': {
                    'average_rating': round(reviews_stats['avg_rating'] or 0, 2),
                    'total_reviews': reviews_stats['total_reviews'] or 0
                },
                'performance_score': self.calculate_performance_score(
                    sales_stats['total_sold'] or 0,
                    reviews_stats['avg_rating'] or 0,
                    reviews_stats['total_reviews'] or 0
                )
            })

        # Trier par score de performance
        performance_data.sort(key=lambda x: x['performance_score'], reverse=True)

        return Response({
            'products_performance': performance_data,
            'summary': {
                'total_products': len(performance_data),
                'top_performer': performance_data[0] if performance_data else None,
                'needs_attention': [p for p in performance_data if p['performance_score'] < 30]
            }
        })

    def calculate_performance_score(self, total_sold, avg_rating, total_reviews):
        """Calcule un score de performance basé sur les ventes et avis"""
        sales_score = min(total_sold * 2, 50)  # Max 50 points pour les ventes
        rating_score = (avg_rating / 5) * 30 if total_reviews > 0 else 0  # Max 30 points pour la note
        review_score = min(total_reviews * 2, 20)  # Max 20 points pour le nombre d'avis
        
        return round(sales_score + rating_score + review_score, 1)

    @action(detail=False, methods=['get'])
    def recent_orders(self, request):
        user = request.user
        
        if user.user_type != 'vendor':
            return Response({'error': 'Only vendors can access this dashboard'}, status=status.HTTP_403_FORBIDDEN)

        limit = int(request.query_params.get('limit', 20))
        order_status = request.query_params.get('status')

        orders_query = OrderItem.objects.filter(vendor=user).select_related(
            'order', 'product'
        )

        if order_status:
            orders_query = orders_query.filter(order__status=order_status)

        recent_orders = orders_query.order_by('-created_at')[:limit]

        orders_data = []
        for item in recent_orders:
            orders_data.append({
                'order_item_id': str(item.id),
                'order': {
                    'id': str(item.order.id),
                    'number': item.order.order_number,
                    'status': item.order.status,
                    'total_amount': str(item.order.total_amount),
                    'created_at': item.order.created_at
                },
                'customer': {
                    'id': str(item.order.user.id),
                    'name': f"{item.order.user.prenom} {item.order.user.nom}",
                    'identifier': item.order.user.identifier
                },
                'product': {
                    'id': str(item.product.id),
                    'name': item.product.name,
                    'price': str(item.unit_price)
                },
                'quantity': item.quantity,
                'total_price': str(item.total_price),
                'delivery_location': {
                    'name': item.order.delivery_location.name,
                    'latitude': str(item.order.delivery_location.latitude),
                    'longitude': str(item.order.delivery_location.longitude)
                }
            })

        return Response({
            'recent_orders': orders_data,
            'total_count': len(orders_data),
            'filters': {
                'status': order_status,
                'limit': limit
            }
        })

    @action(detail=False, methods=['get'])
    def reviews_summary(self, request):
        user = request.user
        
        if user.user_type != 'vendor':
            return Response({'error': 'Only vendors can access this dashboard'}, status=status.HTTP_403_FORBIDDEN)

        # Récupérer le rating du vendeur
        try:
            vendor_rating = VendorRating.objects.get(vendor=user)
            rating_breakdown = {
                '5': vendor_rating.rating_5_count,
                '4': vendor_rating.rating_4_count,
                '3': vendor_rating.rating_3_count,
                '2': vendor_rating.rating_2_count,
                '1': vendor_rating.rating_1_count,
            }
            avg_rating = float(vendor_rating.average_rating)
            total_reviews = vendor_rating.total_reviews
        except VendorRating.DoesNotExist:
            rating_breakdown = {'5': 0, '4': 0, '3': 0, '2': 0, '1': 0}
            avg_rating = 0
            total_reviews = 0

        # Avis récents
        recent_reviews = Review.objects.filter(vendor=user).select_related(
            'user', 'product'
        ).order_by('-created_at')[:10]

        recent_reviews_data = []
        for review in recent_reviews:
            recent_reviews_data.append({
                'id': str(review.id),
                'customer': {
                    'name': f"{review.user.prenom} {review.user.nom}",
                    'avatar': review.user.photo_profile.url if review.user.photo_profile else None
                },
                'product': {
                    'id': str(review.product.id),
                    'name': review.product.name
                },
                'rating': review.rating,
                'comment': review.comment,
                'is_verified': review.is_verified,
                'created_at': review.created_at
            })

        return Response({
            'rating_summary': {
                'average_rating': avg_rating,
                'total_reviews': total_reviews,
                'rating_breakdown': rating_breakdown,
                'satisfaction_rate': round((vendor_rating.rating_4_count + vendor_rating.rating_5_count) / max(total_reviews, 1) * 100, 1) if total_reviews > 0 else 0
            },
            'recent_reviews': recent_reviews_data,
            'review_trends': {
                'this_month': Review.objects.filter(
                    vendor=user,
                    created_at__gte=timezone.now() - timedelta(days=30)
                ).count(),
                'last_month': Review.objects.filter(
                    vendor=user,
                    created_at__gte=timezone.now() - timedelta(days=60),
                    created_at__lt=timezone.now() - timedelta(days=30)
                ).count()
            }
        })

    @action(detail=False, methods=['get'])
    def monthly_stats(self, request):
        user = request.user
        
        if user.user_type != 'vendor':
            return Response({'error': 'Only vendors can access this dashboard'}, status=status.HTTP_403_FORBIDDEN)

        # Statistiques des 12 derniers mois
        monthly_data = []
        for i in range(12):
            month_start = timezone.now().replace(day=1) - timedelta(days=30*i)
            month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
            
            month_stats = OrderItem.objects.filter(
                vendor=user,
                created_at__gte=month_start,
                created_at__lte=month_end
            ).aggregate(
                revenue=Sum('total_price'),
                orders=Count('order', distinct=True),
                items_sold=Sum('quantity')
            )

            monthly_data.append({
                'month': month_start.strftime('%Y-%m'),
                'month_name': month_start.strftime('%B %Y'),
                'revenue': str(month_stats['revenue'] or 0),
                'orders': month_stats['orders'] or 0,
                'items_sold': month_stats['items_sold'] or 0
            })

        monthly_data.reverse()  # Ordre chronologique

        return Response({
            'monthly_stats': monthly_data,
            'summary': {
                'best_month': max(monthly_data, key=lambda x: float(x['revenue'])) if monthly_data else None,
                'total_revenue_year': str(sum(float(m['revenue']) for m in monthly_data)),
                'average_monthly_revenue': str(sum(float(m['revenue']) for m in monthly_data) / 12)
            }
        })