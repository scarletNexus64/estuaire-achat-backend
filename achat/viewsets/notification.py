from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import JSONParser, FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from ..models import Notification
from ..serializers import NotificationSerializer


@extend_schema_view(
    list=extend_schema(
        tags=['Notifications'],
        summary="Liste toutes les notifications",
        description="Récupère la liste complète des notifications avec possibilité de filtrage"
    ),
    create=extend_schema(
        tags=['Notifications'],
        summary="Créer une nouvelle notification",
        description="Crée une nouvelle notification pour un utilisateur"
    ),
    retrieve=extend_schema(
        tags=['Notifications'],
        summary="Détails d'une notification",
        description="Récupère les détails d'une notification spécifique par son ID"
    ),
    update=extend_schema(
        tags=['Notifications'],
        summary="Modifier une notification",
        description="Met à jour toutes les informations d'une notification"
    ),
    partial_update=extend_schema(
        tags=['Notifications'],
        summary="Modifier partiellement une notification",
        description="Met à jour partiellement les informations d'une notification"
    ),
    destroy=extend_schema(
        tags=['Notifications'],
        summary="Supprimer une notification",
        description="Supprime définitivement une notification"
    ),
)
class NotificationViewSet(viewsets.ModelViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    parser_classes = [JSONParser, FormParser, MultiPartParser]
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['is_read', 'user']
    search_fields = ['titre', 'content']
    ordering_fields = ['created_at', 'updated_at', 'is_read']
    ordering = ['-created_at']

    def get_queryset(self):
        # Les utilisateurs ne voient que leurs propres notifications
        return Notification.objects.filter(user=self.request.user).select_related('user')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @extend_schema(
        tags=['Notifications'],
        summary="Obtenir une notification par ID",
        description="Récupère une notification spécifique par son ID",
        parameters=[
            OpenApiParameter(
                name='notification_id',
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.PATH,
                description='ID de la notification'
            )
        ]
    )
    @action(detail=False, methods=['get'], url_path='by-id/(?P<notification_id>[^/.]+)')
    def get_by_id(self, request, notification_id=None):
        try:
            notification = Notification.objects.select_related('user').get(
                id=notification_id, 
                user=request.user  # S'assurer que l'utilisateur ne peut voir que ses notifications
            )
            serializer = self.get_serializer(notification)
            return Response(serializer.data)
        except Notification.DoesNotExist:
            return Response(
                {'error': 'Notification non trouvée'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': f'Erreur lors de la récupération de la notification: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )

    @extend_schema(
        tags=['Notifications'],
        summary="Notifications par utilisateur",
        description="Récupère toutes les notifications d'un utilisateur spécifique",
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
            # Seul l'utilisateur peut voir ses propres notifications
            if str(request.user.id) != user_id:
                return Response(
                    {'error': 'Vous ne pouvez voir que vos propres notifications'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            notifications = Notification.objects.filter(user_id=user_id).select_related('user')
            serializer = self.get_serializer(notifications, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {'error': f'Erreur lors de la récupération des notifications: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )

    @extend_schema(
        tags=['Notifications'],
        summary="Mes notifications",
        description="Récupère toutes les notifications de l'utilisateur connecté"
    )
    @action(detail=False, methods=['get'], url_path='my-notifications')
    def my_notifications(self, request):
        try:
            notifications = Notification.objects.filter(user=request.user).select_related('user')
            serializer = self.get_serializer(notifications, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {'error': f'Erreur lors de la récupération de vos notifications: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )

    @extend_schema(
        tags=['Notifications'],
        summary="Notifications non lues",
        description="Récupère toutes les notifications non lues de l'utilisateur connecté"
    )
    @action(detail=False, methods=['get'], url_path='unread')
    def unread_notifications(self, request):
        try:
            notifications = Notification.objects.filter(
                user=request.user, 
                is_read=False
            ).select_related('user')
            serializer = self.get_serializer(notifications, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {'error': f'Erreur lors de la récupération des notifications non lues: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )

    @extend_schema(
        tags=['Notifications'],
        summary="Notifications lues",
        description="Récupère toutes les notifications lues de l'utilisateur connecté"
    )
    @action(detail=False, methods=['get'], url_path='read')
    def read_notifications(self, request):
        try:
            notifications = Notification.objects.filter(
                user=request.user, 
                is_read=True
            ).select_related('user')
            serializer = self.get_serializer(notifications, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {'error': f'Erreur lors de la récupération des notifications lues: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )

    @extend_schema(
        tags=['Notifications'],
        summary="Marquer comme lue",
        description="Marque une notification spécifique comme lue",
        parameters=[
            OpenApiParameter(
                name='notification_id',
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.PATH,
                description='ID de la notification à marquer comme lue'
            )
        ]
    )
    @action(detail=False, methods=['patch'], url_path='mark-as-read/(?P<notification_id>[^/.]+)')
    def mark_as_read(self, request, notification_id=None):
        try:
            notification = Notification.objects.get(
                id=notification_id,
                user=request.user
            )
            notification.is_read = True
            notification.save()
            
            serializer = self.get_serializer(notification)
            return Response({
                'message': 'Notification marquée comme lue',
                'notification': serializer.data
            })
        except Notification.DoesNotExist:
            return Response(
                {'error': 'Notification non trouvée'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': f'Erreur lors de la mise à jour: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )

    @extend_schema(
        tags=['Notifications'],
        summary="Marquer comme non lue",
        description="Marque une notification spécifique comme non lue",
        parameters=[
            OpenApiParameter(
                name='notification_id',
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.PATH,
                description='ID de la notification à marquer comme non lue'
            )
        ]
    )
    @action(detail=False, methods=['patch'], url_path='mark-as-unread/(?P<notification_id>[^/.]+)')
    def mark_as_unread(self, request, notification_id=None):
        try:
            notification = Notification.objects.get(
                id=notification_id,
                user=request.user
            )
            notification.is_read = False
            notification.save()
            
            serializer = self.get_serializer(notification)
            return Response({
                'message': 'Notification marquée comme non lue',
                'notification': serializer.data
            })
        except Notification.DoesNotExist:
            return Response(
                {'error': 'Notification non trouvée'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': f'Erreur lors de la mise à jour: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )

    @extend_schema(
        tags=['Notifications'],
        summary="Marquer toutes comme lues",
        description="Marque toutes les notifications de l'utilisateur comme lues"
    )
    @action(detail=False, methods=['patch'], url_path='mark-all-as-read')
    def mark_all_as_read(self, request):
        try:
            count = Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
            return Response({
                'message': f'{count} notification(s) marquée(s) comme lue(s)',
                'count': count
            })
        except Exception as e:
            return Response(
                {'error': f'Erreur lors de la mise à jour: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )

    @extend_schema(
        tags=['Notifications'],
        summary="Supprimer toutes les notifications lues",
        description="Supprime toutes les notifications lues de l'utilisateur"
    )
    @action(detail=False, methods=['delete'], url_path='delete-all-read')
    def delete_all_read(self, request):
        try:
            count = Notification.objects.filter(user=request.user, is_read=True).count()
            Notification.objects.filter(user=request.user, is_read=True).delete()
            return Response({
                'message': f'{count} notification(s) lue(s) supprimée(s)',
                'count': count
            })
        except Exception as e:
            return Response(
                {'error': f'Erreur lors de la suppression: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )

    @extend_schema(
        tags=['Notifications'],
        summary="Nombre de notifications",
        description="Retourne le nombre total et non lu de notifications de l'utilisateur"
    )
    @action(detail=False, methods=['get'], url_path='count')
    def notifications_count(self, request):
        try:
            total_count = Notification.objects.filter(user=request.user).count()
            unread_count = Notification.objects.filter(user=request.user, is_read=False).count()
            read_count = total_count - unread_count
            
            return Response({
                'total_count': total_count,
                'unread_count': unread_count,
                'read_count': read_count,
                'user_id': str(request.user.id)
            })
        except Exception as e:
            return Response(
                {'error': f'Erreur lors du comptage: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )