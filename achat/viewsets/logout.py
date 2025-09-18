from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema
from ..models import UserToken
from ..authentication import UUIDTokenAuthentication


class LogoutView(APIView):
    authentication_classes = [UUIDTokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        tags=['Authentication'],
        summary="Deconnexion utilisateur",
        description="Deconnecte l'utilisateur et invalide son token",
        responses={
            200: {"type": "object", "properties": {"message": {"type": "string"}}},
            401: {"type": "object", "properties": {"error": {"type": "string"}}}
        }
    )
    def post(self, request):
        try:
            # Désactiver le token de l'utilisateur au lieu de le supprimer
            UserToken.objects.filter(user=request.user).update(is_active=False)
            return Response(
                {"message": "Deconnexion reussie"}, 
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {"error": "Erreur lors de la deconnexion"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )