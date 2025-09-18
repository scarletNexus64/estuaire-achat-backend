from django.contrib.auth import authenticate, get_user_model
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema
from ..serializers import LoginSerializer, UserResponseSerializer
from ..models import UserToken

User = get_user_model()


class LoginView(APIView):
    @extend_schema(
        tags=['Authentication'],
        summary="Connexion utilisateur",
        description="Connecte un utilisateur avec son identifier et mot de passe",
        request=LoginSerializer,
        responses={
            200: UserResponseSerializer,
            401: {"type": "object", "properties": {"error": {"type": "string"}}}
        }
    )
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            identifier = serializer.validated_data['identifier']
            password = serializer.validated_data['password']
            
            user = authenticate(request, identifier=identifier, password=password)
            if user:
                # Creer ou recuperer le token
                user_token, created = UserToken.objects.get_or_create(user=user)
                user_data = UserResponseSerializer(user).data
                return Response(user_data, status=status.HTTP_200_OK)
            else:
                return Response(
                    {"error": "Identifier ou mot de passe incorrect"}, 
                    status=status.HTTP_401_UNAUTHORIZED
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)