from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import JSONParser, FormParser, MultiPartParser
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from ..models import Category, SubCategory
from ..serializers import CategorySerializer, SubCategorySerializer


@extend_schema_view(
    list=extend_schema(
        tags=['Categories'],
        summary="Liste toutes les catégories",
        description="Récupère la liste complète des catégories avec possibilité de filtrage"
    ),
    create=extend_schema(
        tags=['Categories'],
        summary="Créer une nouvelle catégorie",
        description="Crée une nouvelle catégorie avec ses traductions"
    ),
    retrieve=extend_schema(
        tags=['Categories'],
        summary="Détails d'une catégorie",
        description="Récupère les détails d'une catégorie spécifique par son ID"
    ),
    update=extend_schema(
        tags=['Categories'],
        summary="Modifier une catégorie",
        description="Met à jour toutes les informations d'une catégorie"
    ),
    partial_update=extend_schema(
        tags=['Categories'],
        summary="Modifier partiellement une catégorie",
        description="Met à jour partiellement les informations d'une catégorie"
    ),
    destroy=extend_schema(
        tags=['Categories'],
        summary="Supprimer une catégorie",
        description="Supprime définitivement une catégorie"
    ),
)
class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    parser_classes = [JSONParser, FormParser, MultiPartParser]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['is_active']
    search_fields = ['name', 'name_trl', 'description']
    ordering_fields = ['name', 'created_at', 'updated_at']
    ordering = ['name']

    @extend_schema(
        tags=['Categories'],
        summary="Catégories par sous-catégorie",
        description="Récupère toutes les catégories qui contiennent une sous-catégorie spécifique",
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
    def by_subcategory(self, request, subcategory_id=None):
        try:
            categories = Category.objects.filter(subcategories__id=subcategory_id)
            serializer = self.get_serializer(categories, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {'error': f'Erreur lors de la récupération des catégories: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )

    @extend_schema(
        tags=['Categories'],
        summary="Catégories actives seulement",
        description="Récupère uniquement les catégories actives"
    )
    @action(detail=False, methods=['get'], url_path='active')
    def active_categories(self, request):
        categories = Category.objects.filter(is_active=True)
        serializer = self.get_serializer(categories, many=True)
        return Response(serializer.data)


@extend_schema_view(
    list=extend_schema(
        tags=['SubCategories'],
        summary="Liste toutes les sous-catégories",
        description="Récupère la liste complète des sous-catégories avec possibilité de filtrage"
    ),
    create=extend_schema(
        tags=['SubCategories'],
        summary="Créer une nouvelle sous-catégorie",
        description="Crée une nouvelle sous-catégorie avec ses traductions"
    ),
    retrieve=extend_schema(
        tags=['SubCategories'],
        summary="Détails d'une sous-catégorie",
        description="Récupère les détails d'une sous-catégorie spécifique par son ID"
    ),
    update=extend_schema(
        tags=['SubCategories'],
        summary="Modifier une sous-catégorie",
        description="Met à jour toutes les informations d'une sous-catégorie"
    ),
    partial_update=extend_schema(
        tags=['SubCategories'],
        summary="Modifier partiellement une sous-catégorie",
        description="Met à jour partiellement les informations d'une sous-catégorie"
    ),
    destroy=extend_schema(
        tags=['SubCategories'],
        summary="Supprimer une sous-catégorie",
        description="Supprime définitivement une sous-catégorie"
    ),
)
class SubCategoryViewSet(viewsets.ModelViewSet):
    queryset = SubCategory.objects.all()
    serializer_class = SubCategorySerializer
    parser_classes = [JSONParser, FormParser, MultiPartParser]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['is_active']
    search_fields = ['name', 'name_trl', 'description']
    ordering_fields = ['name', 'created_at', 'updated_at']
    ordering = ['name']

    @extend_schema(
        tags=['SubCategories'],
        summary="Sous-catégories actives seulement",
        description="Récupère uniquement les sous-catégories actives"
    )
    @action(detail=False, methods=['get'], url_path='active')
    def active_subcategories(self, request):
        subcategories = SubCategory.objects.filter(is_active=True)
        serializer = self.get_serializer(subcategories, many=True)
        return Response(serializer.data)

    @extend_schema(
        tags=['SubCategories'],
        summary="Sous-catégories par catégorie",
        description="Récupère toutes les sous-catégories d'une catégorie spécifique",
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
    def by_category(self, request, category_id=None):
        try:
            subcategories = SubCategory.objects.filter(categories__id=category_id)
            serializer = self.get_serializer(subcategories, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {'error': f'Erreur lors de la récupération des sous-catégories: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )