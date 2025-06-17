from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.openapi import OpenApiTypes

from .models import Conversation, Message, KnowledgeBase, ChatbotSettings
from .serializers import (
    ChatRequestSerializer, ChatResponseSerializer, ConversationSerializer,
    MessageSerializer, KnowledgeBaseSerializer, ChatbotSettingsSerializer
)
from .services import ChatbotService


class ChatbotAPIView(APIView):
    """
    API principale pour discuter avec le chatbot
    """
    permission_classes = [AllowAny]  # Permettre l'accès anonyme
    
    @extend_schema(
        request=ChatRequestSerializer,
        responses={200: ChatResponseSerializer},
        description="Envoie un message au chatbot et reçoit une réponse intelligente",
        tags=['Chatbot']
    )
    def post(self, request):
        """
        Traite un message utilisateur et retourne la réponse du chatbot
        """
        serializer = ChatRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        # Extraction des données
        message = serializer.validated_data['message']
        session_id = serializer.validated_data.get('session_id')
        user_id = serializer.validated_data.get('user_id')
        
        # Si l'utilisateur est authentifié, utiliser son ID
        if request.user.is_authenticated:
            user_id = request.user.id
        
        try:
            # Traitement via le service chatbot
            chatbot_service = ChatbotService()
            response_data = chatbot_service.process_message(
                user_message=message,
                session_id=session_id,
                user_id=user_id
            )
            
            response_serializer = ChatResponseSerializer(data=response_data)
            if response_serializer.is_valid():
                return Response(response_serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(
                    {"error": "Erreur dans la génération de la réponse"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
                
        except Exception as e:
            return Response(
                {"error": f"Erreur interne: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ConversationViewSet(ModelViewSet):
    """
    ViewSet pour gérer les conversations
    """
    queryset = Conversation.objects.all()
    serializer_class = ConversationSerializer
    
    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='session_id',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='ID de session pour filtrer les conversations'
            ),
        ],
        tags=['Conversations']
    )
    def list(self, request, *args, **kwargs):
        """
        Liste les conversations, avec filtrage optionnel par session_id
        """
        session_id = request.query_params.get('session_id')
        
        queryset = self.get_queryset()
        
        if session_id:
            queryset = queryset.filter(session_id=session_id)
        
        if request.user.is_authenticated:
            queryset = queryset.filter(user=request.user)
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class KnowledgeBaseViewSet(ModelViewSet):
    """
    ViewSet pour gérer la base de connaissances (admin uniquement)
    """
    queryset = KnowledgeBase.objects.all()
    serializer_class = KnowledgeBaseSerializer
    
    @extend_schema(tags=['Base de connaissances'])
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @extend_schema(tags=['Base de connaissances'])
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
    
    @extend_schema(tags=['Base de connaissances'])
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
    
    @extend_schema(tags=['Base de connaissances'])
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)
    
    @extend_schema(tags=['Base de connaissances'])
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)


@extend_schema(
    responses={200: ChatbotSettingsSerializer},
    description="Récupère la configuration actuelle du chatbot",
    tags=['Configuration']
)
@api_view(['GET'])
@permission_classes([AllowAny])
def get_chatbot_settings(request):
    """
    Récupère les paramètres publics du chatbot
    """
    settings_obj = ChatbotSettings.objects.first()
    if not settings_obj:
        # Créer des paramètres par défaut
        settings_obj = ChatbotSettings.objects.create()
    
    # Ne retourner que les paramètres publics
    public_data = {
        'name': settings_obj.name,
        'personality': settings_obj.personality,
        'enable_emotion_detection': settings_obj.enable_emotion_detection,
    }
    
    return Response(public_data)


@extend_schema(
    parameters=[
        OpenApiParameter(
            name='session_id',
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description='ID de session',
            required=True
        ),
    ],
    responses={200: MessageSerializer(many=True)},
    description="Récupère l'historique des messages d'une conversation",
    tags=['Messages']
)
@api_view(['GET'])
@permission_classes([AllowAny])
def get_conversation_history(request):
    """
    Récupère l'historique des messages d'une conversation
    """
    session_id = request.query_params.get('session_id')
    if not session_id:
        return Response(
            {"error": "session_id est requis"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    conversation = get_object_or_404(
        Conversation,
        session_id=session_id,
        is_active=True
    )
    
    # Vérifier les permissions si l'utilisateur est authentifié
    if request.user.is_authenticated and conversation.user != request.user:
        return Response(
            {"error": "Accès non autorisé à cette conversation"},
            status=status.HTTP_403_FORBIDDEN
        )
    
    messages = conversation.messages.all().order_by('timestamp')
    serializer = MessageSerializer(messages, many=True)
    
    return Response(serializer.data)


@extend_schema(
    request=None,
    responses={200: {"type": "object", "properties": {"message": {"type": "string"}}}},
    description="Teste la disponibilité de l'API chatbot",
    tags=['Utilitaires']
)
@api_view(['GET'])
@permission_classes([AllowAny])
def chatbot_health_check(request):
    """
    Endpoint de vérification de santé du chatbot
    """
    try:
        # Vérifier que les modèles sont accessibles
        KnowledgeBase.objects.count()
        Conversation.objects.count()
        
        return Response({
            "message": "Chatbot API est opérationnel",
            "status": "healthy"
        })
    except Exception as e:
        return Response({
            "message": "Erreur dans le chatbot API",
            "status": "unhealthy",
            "error": str(e)
        }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
