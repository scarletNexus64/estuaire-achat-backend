from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import JSONParser, FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from django.db.models import Q, Count, Avg, Min, Max
from math import radians, cos, sin, asin, sqrt
from ..models import Product, ProductImage, Location
from ..serializers import ProductSerializer, ProductImageSerializer


@extend_schema_view(
    list=extend_schema(
        tags=['Products'],
        summary="Liste tous les produits",
        description="Récupère la liste complète des produits avec possibilité de filtrage"
    ),
    create=extend_schema(
        tags=['Products'],
        summary="Créer un nouveau produit",
        description="Crée un nouveau produit avec ses images"
    ),
    retrieve=extend_schema(
        tags=['Products'],
        summary="Détails d'un produit",
        description="Récupère les détails d'un produit spécifique par son ID"
    ),
    update=extend_schema(
        tags=['Products'],
        summary="Modifier un produit",
        description="Met à jour toutes les informations d'un produit"
    ),
    partial_update=extend_schema(
        tags=['Products'],
        summary="Modifier partiellement un produit",
        description="Met à jour partiellement les informations d'un produit"
    ),
    destroy=extend_schema(
        tags=['Products'],
        summary="Supprimer un produit",
        description="Supprime définitivement un produit"
    ),
)
class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    parser_classes = [JSONParser, FormParser, MultiPartParser]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status', 'is_stock', 'category', 'subcategory', 'user']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'price', 'created_at', 'updated_at']
    ordering = ['-created_at']

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action in ['list', 'retrieve', 'active_products', 'in_stock_products', 'get_by_category', 'get_by_subcategory']:
            # Read-only actions can be accessed without authentication for API documentation
            permission_classes = [AllowAny]
        else:
            # Write actions require authentication
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_queryset(self):
        return Product.objects.select_related(
            'user', 'location', 'category', 'subcategory'
        ).prefetch_related('images')

    @extend_schema(
        tags=['Products'],
        summary="Obtenir un produit par ID",
        description="Récupère un produit spécifique par son ID",
        parameters=[
            OpenApiParameter(
                name='product_id',
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.PATH,
                description='ID du produit'
            )
        ]
    )
    @action(detail=False, methods=['get'], url_path='by-id/(?P<product_id>[^/.]+)')
    def get_by_id(self, request, product_id=None):
        try:
            product = Product.objects.select_related(
                'user', 'location', 'category', 'subcategory'
            ).prefetch_related('images').get(id=product_id)
            serializer = self.get_serializer(product)
            return Response(serializer.data)
        except Product.DoesNotExist:
            return Response(
                {'error': 'Produit non trouvé'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': f'Erreur lors de la récupération du produit: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )

    @extend_schema(
        tags=['Products'],
        summary="Produits par catégorie",
        description="Récupère tous les produits d'une catégorie spécifique",
        parameters=[
            OpenApiParameter(
                name='category_id',
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.PATH,
                description='ID de la catégorie'
            )
        ]
    )
    @action(detail=False, methods=['get'], url_path='by-category/(?P<category_id>[^/.]+)')
    def get_by_category(self, request, category_id=None):
        try:
            products = Product.objects.filter(category_id=category_id).select_related(
                'user', 'location', 'category', 'subcategory'
            ).prefetch_related('images')
            serializer = self.get_serializer(products, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {'error': f'Erreur lors de la récupération des produits: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )

    @extend_schema(
        tags=['Products'],
        summary="Produits par sous-catégorie",
        description="Récupère tous les produits d'une sous-catégorie spécifique",
        parameters=[
            OpenApiParameter(
                name='subcategory_id',
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.PATH,
                description='ID de la sous-catégorie'
            )
        ]
    )
    @action(detail=False, methods=['get'], url_path='by-subcategory/(?P<subcategory_id>[^/.]+)')
    def get_by_subcategory(self, request, subcategory_id=None):
        try:
            products = Product.objects.filter(subcategory_id=subcategory_id).select_related(
                'user', 'location', 'category', 'subcategory'
            ).prefetch_related('images')
            serializer = self.get_serializer(products, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {'error': f'Erreur lors de la récupération des produits: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )

    @extend_schema(
        tags=['Products'],
        summary="Produits par utilisateur",
        description="Récupère tous les produits d'un utilisateur spécifique",
        parameters=[
            OpenApiParameter(
                name='user_id',
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.PATH,
                description='ID de l\'utilisateur'
            )
        ]
    )
    @action(detail=False, methods=['get'], url_path='by-user/(?P<user_id>[^/.]+)')
    def get_by_user_id(self, request, user_id=None):
        try:
            products = Product.objects.filter(user_id=user_id).select_related(
                'user', 'location', 'category', 'subcategory'
            ).prefetch_related('images')
            serializer = self.get_serializer(products, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {'error': f'Erreur lors de la récupération des produits: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )

    @extend_schema(
        tags=['Products'],
        summary="Mes produits",
        description="Récupère tous les produits de l'utilisateur connecté"
    )
    @action(detail=False, methods=['get'], url_path='my-products')
    def my_products(self, request):
        try:
            products = Product.objects.filter(user=request.user).select_related(
                'user', 'location', 'category', 'subcategory'
            ).prefetch_related('images')
            serializer = self.get_serializer(products, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {'error': f'Erreur lors de la récupération de vos produits: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )

    @extend_schema(
        tags=['Products'],
        summary="Supprimer produits par catégorie",
        description="Supprime tous les produits d'une catégorie spécifique",
        parameters=[
            OpenApiParameter(
                name='category_id',
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.PATH,
                description='ID de la catégorie'
            )
        ]
    )
    @action(detail=False, methods=['delete'], url_path='delete-by-category/(?P<category_id>[^/.]+)')
    def delete_by_category(self, request, category_id=None):
        try:
            products = Product.objects.filter(category_id=category_id, user=request.user)
            count = products.count()
            products.delete()
            return Response(
                {'message': f'{count} produit(s) supprimé(s) avec succès'},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {'error': f'Erreur lors de la suppression: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )

    @extend_schema(
        tags=['Products'],
        summary="Supprimer produits par sous-catégorie",
        description="Supprime tous les produits d'une sous-catégorie spécifique",
        parameters=[
            OpenApiParameter(
                name='subcategory_id',
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.PATH,
                description='ID de la sous-catégorie'
            )
        ]
    )
    @action(detail=False, methods=['delete'], url_path='delete-by-subcategory/(?P<subcategory_id>[^/.]+)')
    def delete_by_subcategory(self, request, subcategory_id=None):
        try:
            products = Product.objects.filter(subcategory_id=subcategory_id, user=request.user)
            count = products.count()
            products.delete()
            return Response(
                {'message': f'{count} produit(s) supprimé(s) avec succès'},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {'error': f'Erreur lors de la suppression: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )

    @extend_schema(
        tags=['Products'],
        summary="Produits actifs seulement",
        description="Récupère uniquement les produits actifs"
    )
    @action(detail=False, methods=['get'], url_path='active')
    def active_products(self, request):
        try:
            products = Product.objects.filter(status='active').select_related(
                'user', 'location', 'category', 'subcategory'
            ).prefetch_related('images')
            serializer = self.get_serializer(products, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {'error': f'Erreur lors de la récupération des produits actifs: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )

    @extend_schema(
        tags=['Products'],
        summary="Produits en stock seulement",
        description="Récupère uniquement les produits en stock"
    )
    @action(detail=False, methods=['get'], url_path='in-stock')
    def in_stock_products(self, request):
        try:
            products = Product.objects.filter(is_stock=True).select_related(
                'user', 'location', 'category', 'subcategory'
            ).prefetch_related('images')
            serializer = self.get_serializer(products, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {'error': f'Erreur lors de la récupération des produits en stock: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )

    @extend_schema(
        tags=['Products'],
        summary="Recherche avancée avec filtres",
        description="Recherche de produits avec filtres avancés (prix, localisation, etc.)",
        parameters=[
            OpenApiParameter(name='search', type=OpenApiTypes.STR, description='Terme de recherche'),
            OpenApiParameter(name='min_price', type=OpenApiTypes.NUMBER, description='Prix minimum'),
            OpenApiParameter(name='max_price', type=OpenApiTypes.NUMBER, description='Prix maximum'),
            OpenApiParameter(name='category_id', type=OpenApiTypes.UUID, description='ID de la catégorie'),
            OpenApiParameter(name='subcategory_id', type=OpenApiTypes.UUID, description='ID de la sous-catégorie'),
            OpenApiParameter(name='latitude', type=OpenApiTypes.NUMBER, description='Latitude pour recherche géolocalisée'),
            OpenApiParameter(name='longitude', type=OpenApiTypes.NUMBER, description='Longitude pour recherche géolocalisée'),
            OpenApiParameter(name='radius_km', type=OpenApiTypes.NUMBER, description='Rayon de recherche en km (défaut: 50)'),
            OpenApiParameter(name='in_stock_only', type=OpenApiTypes.BOOL, description='Produits en stock uniquement'),
            OpenApiParameter(name='sort_by', type=OpenApiTypes.STR, description='Tri: price_asc, price_desc, date_asc, date_desc, distance'),
        ]
    )
    @action(detail=False, methods=['get'])
    def advanced_search(self, request):
        queryset = Product.objects.filter(status='active').select_related(
            'user', 'location', 'category', 'subcategory'
        ).prefetch_related('images', 'reviews')

        search = request.query_params.get('search')
        min_price = request.query_params.get('min_price')
        max_price = request.query_params.get('max_price')
        category_id = request.query_params.get('category_id')
        subcategory_id = request.query_params.get('subcategory_id')
        latitude = request.query_params.get('latitude')
        longitude = request.query_params.get('longitude')
        radius_km = request.query_params.get('radius_km', 50)
        in_stock_only = request.query_params.get('in_stock_only', 'false').lower() == 'true'
        sort_by = request.query_params.get('sort_by', 'date_desc')

        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | 
                Q(description__icontains=search) |
                Q(category__name__icontains=search) |
                Q(subcategory__name__icontains=search)
            )

        if min_price:
            try:
                queryset = queryset.filter(price__gte=float(min_price))
            except ValueError:
                return Response({'error': 'Invalid min_price format'}, status=status.HTTP_400_BAD_REQUEST)

        if max_price:
            try:
                queryset = queryset.filter(price__lte=float(max_price))
            except ValueError:
                return Response({'error': 'Invalid max_price format'}, status=status.HTTP_400_BAD_REQUEST)

        if category_id:
            queryset = queryset.filter(category_id=category_id)

        if subcategory_id:
            queryset = queryset.filter(subcategory_id=subcategory_id)

        if in_stock_only:
            queryset = queryset.filter(is_stock=True, quantity__gt=0)

        products_data = []
        user_lat = None
        user_lng = None

        if latitude and longitude:
            try:
                user_lat = float(latitude)
                user_lng = float(longitude)
                radius_km = float(radius_km)
            except ValueError:
                return Response({'error': 'Invalid coordinates format'}, status=status.HTTP_400_BAD_REQUEST)

        for product in queryset:
            distance = None
            if user_lat and user_lng and product.location:
                distance = self.calculate_distance(
                    user_lat, user_lng,
                    float(product.location.latitude), 
                    float(product.location.longitude)
                )
                
                if distance > radius_km:
                    continue

            avg_rating = product.reviews.aggregate(avg=Avg('rating'))['avg'] or 0
            reviews_count = product.reviews.count()

            product_data = {
                'id': str(product.id),
                'name': product.name,
                'description': product.description,
                'price': str(product.price),
                'quantity': product.quantity,
                'is_stock': product.is_stock,
                'status': product.status,
                'conditions_paiement': product.conditions_paiement,
                'images': [{'id': str(img.id), 'image': img.image.url} for img in product.images.all()],
                'location': {
                    'id': str(product.location.id),
                    'name': product.location.name,
                    'latitude': str(product.location.latitude),
                    'longitude': str(product.location.longitude),
                    'distance_km': round(distance, 2) if distance else None
                },
                'user': {
                    'id': str(product.user.id),
                    'name': f"{product.user.prenom} {product.user.nom}",
                    'user_type': product.user.user_type
                },
                'category': {
                    'id': str(product.category.id) if product.category else None,
                    'name': product.category.name if product.category else None,
                },
                'subcategory': {
                    'id': str(product.subcategory.id) if product.subcategory else None,
                    'name': product.subcategory.name if product.subcategory else None,
                },
                'reviews': {
                    'average_rating': round(avg_rating, 2),
                    'total_reviews': reviews_count
                },
                'created_at': product.created_at,
                'updated_at': product.updated_at,
            }
            products_data.append(product_data)

        if sort_by == 'price_asc':
            products_data.sort(key=lambda x: float(x['price']))
        elif sort_by == 'price_desc':
            products_data.sort(key=lambda x: float(x['price']), reverse=True)
        elif sort_by == 'date_asc':
            products_data.sort(key=lambda x: x['created_at'])
        elif sort_by == 'date_desc':
            products_data.sort(key=lambda x: x['created_at'], reverse=True)
        elif sort_by == 'distance' and user_lat and user_lng:
            products_data.sort(key=lambda x: x['location']['distance_km'] or float('inf'))

        return Response({
            'products': products_data,
            'total_count': len(products_data),
            'filters_applied': {
                'search': search,
                'price_range': f"{min_price or 'N/A'} - {max_price or 'N/A'}",
                'location_filter': f"{radius_km}km radius" if user_lat and user_lng else None,
                'in_stock_only': in_stock_only,
                'sort_by': sort_by
            }
        })

    def calculate_distance(self, lat1, lon1, lat2, lon2):
        """Calculate distance between two points using Haversine formula"""
        R = 6371  # Earth's radius in kilometers
        
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        return 2 * R * asin(sqrt(a))

    @extend_schema(
        tags=['Products'],
        summary="Suggestions de recherche",
        description="Obtenir des suggestions de produits similaires",
        parameters=[
            OpenApiParameter(name='product_id', type=OpenApiTypes.UUID, description='ID du produit de référence'),
            OpenApiParameter(name='limit', type=OpenApiTypes.INT, description='Nombre de suggestions (défaut: 5)'),
        ]
    )
    @action(detail=False, methods=['get'])
    def suggestions(self, request):
        product_id = request.query_params.get('product_id')
        limit = int(request.query_params.get('limit', 5))

        if not product_id:
            return Response({'error': 'product_id is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            reference_product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)

        suggestions = Product.objects.filter(
            status='active'
        ).exclude(id=product_id).select_related(
            'user', 'location', 'category', 'subcategory'
        ).prefetch_related('images', 'reviews')

        if reference_product.category:
            suggestions = suggestions.filter(category=reference_product.category)

        if reference_product.subcategory:
            suggestions = suggestions.filter(subcategory=reference_product.subcategory)

        min_price = reference_product.price * 0.7
        max_price = reference_product.price * 1.3
        suggestions = suggestions.filter(price__gte=min_price, price__lte=max_price)

        suggestions = suggestions.order_by('?')[:limit]

        suggestions_data = []
        for product in suggestions:
            avg_rating = product.reviews.aggregate(avg=Avg('rating'))['avg'] or 0
            reviews_count = product.reviews.count()

            suggestions_data.append({
                'id': str(product.id),
                'name': product.name,
                'price': str(product.price),
                'images': [{'image': img.image.url} for img in product.images.all()[:1]],
                'location': {
                    'name': product.location.name,
                },
                'user': {
                    'name': f"{product.user.prenom} {product.user.nom}",
                },
                'reviews': {
                    'average_rating': round(avg_rating, 2),
                    'total_reviews': reviews_count
                },
            })

        return Response({
            'suggestions': suggestions_data,
            'reference_product': {
                'id': str(reference_product.id),
                'name': reference_product.name,
                'category': reference_product.category.name if reference_product.category else None
            }
        })

    @extend_schema(
        tags=['Products'],
        summary="Statistiques des produits",
        description="Obtenir des statistiques générales sur les produits"
    )
    @action(detail=False, methods=['get'])
    def stats(self, request):
        total_products = Product.objects.count()
        active_products = Product.objects.filter(status='active').count()
        in_stock_products = Product.objects.filter(is_stock=True, quantity__gt=0).count()
        
        price_stats = Product.objects.filter(status='active').aggregate(
            min_price=Min('price'),
            max_price=Max('price'),
            avg_price=Avg('price')
        )

        category_stats = Product.objects.filter(status='active').values(
            'category__name'
        ).annotate(
            count=Count('id')
        ).order_by('-count')[:10]

        return Response({
            'general_stats': {
                'total_products': total_products,
                'active_products': active_products,
                'in_stock_products': in_stock_products,
                'out_of_stock_products': total_products - in_stock_products,
            },
            'price_stats': {
                'min_price': price_stats['min_price'],
                'max_price': price_stats['max_price'],
                'average_price': round(price_stats['avg_price'] or 0, 2),
            },
            'top_categories': category_stats
        })