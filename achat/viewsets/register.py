from django.contrib.auth import get_user_model
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import JSONParser, FormParser, MultiPartParser
from drf_spectacular.utils import extend_schema
from ..serializers import RegisterSerializer, UserResponseSerializer

User = get_user_model()


class RegisterView(APIView):
    parser_classes = [JSONParser, FormParser, MultiPartParser]
    
    @extend_schema(
        tags=['Authentication'],
        summary="Inscription d'un nouclaudevel utilisateur",
        description="Cree un nouveau compte utilisateur avec ses informations et sa localisation",
        request=RegisterSerializer,
        responses={
            201: UserResponseSerializer,
            400: {"type": "object", "properties": {"error": {"type": "string"}}}
        }
    )
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            user_data = UserResponseSerializer(user).data
            return Response(user_data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)