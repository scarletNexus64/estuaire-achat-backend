from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import JSONParser, FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from ..models import Wishlist
from ..serializers import WishlistSerializer


@extend_schema_view(
    list=extend_schema(
        tags=['Wishlists'],
        summary="Liste toutes les wishlists",
        description="Récupère la liste complète des wishlists avec possibilité de filtrage"
    ),
    create=extend_schema(
        tags=['Wishlists'],
        summary="Ajouter un produit à la wishlist",
        description="Ajoute un produit à la liste de souhaits de l'utilisateur"
    ),
    retrieve=extend_schema(
        tags=['Wishlists'],
        summary="Détails d'un élément de wishlist",
        description="Récupère les détails d'un élément spécifique de la wishlist"
    ),
    update=extend_schema(
        tags=['Wishlists'],
        summary="Modifier un élément de wishlist",
        description="Met à jour un élément de la wishlist"
    ),
    partial_update=extend_schema(
        tags=['Wishlists'],
        summary="Modifier partiellement un élément de wishlist",
        description="Met à jour partiellement un élément de la wishlist"
    ),
    destroy=extend_schema(
        tags=['Wishlists'],
        summary="Supprimer de la wishlist",
        description="Supprime un produit de la liste de souhaits"
    ),
)
class WishlistViewSet(viewsets.ModelViewSet):
    queryset = Wishlist.objects.all()
    serializer_class = WishlistSerializer
    parser_classes = [JSONParser, FormParser, MultiPartParser]
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['product', 'user']
    search_fields = ['product__name', 'user__nom', 'user__prenom']
    ordering_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']

    def get_queryset(self):
        return Wishlist.objects.select_related(
            'user', 'product__user', 'product__location', 'product__category', 'product__subcategory'
        ).prefetch_related('product__images')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @extend_schema(
        tags=['Wishlists'],
        summary="Obtenir un élément de wishlist par ID",
        description="Récupère un élément spécifique de la wishlist par son ID",
        parameters=[
            OpenApiParameter(
                name='wishlist_id',
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.PATH,
                description='ID de l\'élément de wishlist'
            )
        ]
    )
    @action(detail=False, methods=['get'], url_path='by-id/(?P<wishlist_id>[^/.]+)')
    def get_by_id(self, request, wishlist_id=None):
        try:
            wishlist_item = Wishlist.objects.select_related(
                'user', 'product__user', 'product__location', 'product__category', 'product__subcategory'
            ).prefetch_related('product__images').get(id=wishlist_id)
            
            # Vérifier que l'utilisateur peut accéder à cet élément
            if wishlist_item.user != request.user:
                return Response(
                    {'error': 'Vous n\'avez pas l\'autorisation d\'accéder à cet élément'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            serializer = self.get_serializer(wishlist_item)
            return Response(serializer.data)
        except Wishlist.DoesNotExist:
            return Response(
                {'error': 'Élément de wishlist non trouvé'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': f'Erreur lors de la récupération: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )

    @extend_schema(
        tags=['Wishlists'],
        summary="Wishlist par utilisateur",
        description="Récupère tous les éléments de la wishlist d'un utilisateur spécifique",
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
            # Seul l'utilisateur peut voir sa propre wishlist
            if str(request.user.id) != user_id:
                return Response(
                    {'error': 'Vous ne pouvez voir que votre propre wishlist'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            wishlist_items = Wishlist.objects.filter(user_id=user_id).select_related(
                'user', 'product__user', 'product__location', 'product__category', 'product__subcategory'
            ).prefetch_related('product__images')
            
            serializer = self.get_serializer(wishlist_items, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {'error': f'Erreur lors de la récupération de la wishlist: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )

    @extend_schema(
        tags=['Wishlists'],
        summary="Ma wishlist",
        description="Récupère tous les éléments de la wishlist de l'utilisateur connecté"
    )
    @action(detail=False, methods=['get'], url_path='my-wishlist')
    def my_wishlist(self, request):
        try:
            wishlist_items = Wishlist.objects.filter(user=request.user).select_related(
                'user', 'product__user', 'product__location', 'product__category', 'product__subcategory'
            ).prefetch_related('product__images')
            
            serializer = self.get_serializer(wishlist_items, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {'error': f'Erreur lors de la récupération de votre wishlist: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )

    @extend_schema(
        tags=['Wishlists'],
        summary="Vérifier si un produit est en wishlist",
        description="Vérifie si un produit spécifique est dans la wishlist de l'utilisateur",
        parameters=[
            OpenApiParameter(
                name='product_id',
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.PATH,
                description='ID du produit'
            )
        ]
    )
    @action(detail=False, methods=['get'], url_path='check-product/(?P<product_id>[^/.]+)')
    def check_product_in_wishlist(self, request, product_id=None):
        try:
            exists = Wishlist.objects.filter(user=request.user, product_id=product_id).exists()
            return Response({
                'in_wishlist': exists,
                'product_id': product_id,
                'user_id': str(request.user.id)
            })
        except Exception as e:
            return Response(
                {'error': f'Erreur lors de la vérification: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )

    @extend_schema(
        tags=['Wishlists'],
        summary="Supprimer par produit",
        description="Supprime un produit spécifique de la wishlist de l'utilisateur",
        parameters=[
            OpenApiParameter(
                name='product_id',
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.PATH,
                description='ID du produit à supprimer'
            )
        ]
    )
    @action(detail=False, methods=['delete'], url_path='remove-product/(?P<product_id>[^/.]+)')
    def remove_by_product(self, request, product_id=None):
        try:
            wishlist_item = Wishlist.objects.filter(user=request.user, product_id=product_id)
            if not wishlist_item.exists():
                return Response(
                    {'error': 'Ce produit n\'est pas dans votre wishlist'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            wishlist_item.delete()
            return Response(
                {'message': 'Produit supprimé de votre wishlist avec succès'},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {'error': f'Erreur lors de la suppression: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )

    @extend_schema(
        tags=['Wishlists'],
        summary="Vider ma wishlist",
        description="Supprime tous les éléments de la wishlist de l'utilisateur connecté"
    )
    @action(detail=False, methods=['delete'], url_path='clear-my-wishlist')
    def clear_my_wishlist(self, request):
        try:
            count = Wishlist.objects.filter(user=request.user).count()
            Wishlist.objects.filter(user=request.user).delete()
            return Response(
                {'message': f'{count} élément(s) supprimé(s) de votre wishlist'},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {'error': f'Erreur lors de la suppression: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )

    @extend_schema(
        tags=['Wishlists'],
        summary="Nombre d'éléments dans ma wishlist",
        description="Retourne le nombre d'éléments dans la wishlist de l'utilisateur"
    )
    @action(detail=False, methods=['get'], url_path='count')
    def wishlist_count(self, request):
        try:
            count = Wishlist.objects.filter(user=request.user).count()
            return Response({
                'count': count,
                'user_id': str(request.user.id)
            })
        except Exception as e:
            return Response(
                {'error': f'Erreur lors du comptage: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )