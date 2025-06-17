from rest_framework import serializers
from .models import Message, Conversation, KnowledgeBase, ChatbotSettings


class MessageSerializer(serializers.ModelSerializer):
    """
    Serializer pour les messages
    """
    class Meta:
        model = Message
        fields = [
            'id', 'sender', 'content', 'detected_emotion', 
            'emotion_confidence', 'detected_language', 'timestamp',
            'response_method', 'processing_time'
        ]
        read_only_fields = [
            'id', 'detected_emotion', 'emotion_confidence', 
            'detected_language', 'timestamp', 'response_method', 
            'processing_time'
        ]


class ConversationSerializer(serializers.ModelSerializer):
    """
    Serializer pour les conversations avec les messages
    """
    messages = MessageSerializer(many=True, read_only=True)
    
    class Meta:
        model = Conversation
        fields = [
            'id', 'session_id', 'started_at', 
            'last_message_at', 'is_active', 'messages'
        ]
        read_only_fields = ['id', 'started_at', 'last_message_at']


class ChatRequestSerializer(serializers.Serializer):
    """
    Serializer pour les requêtes de chat
    """
    message = serializers.CharField(max_length=1000)
    session_id = serializers.CharField(max_length=100, required=False)
    user_id = serializers.IntegerField(required=False)


class ChatResponseSerializer(serializers.Serializer):
    """
    Serializer pour les réponses du chatbot
    """
    message = serializers.CharField()
    session_id = serializers.CharField()
    conversation_id = serializers.IntegerField()
    detected_emotion = serializers.CharField(required=False)
    emotion_confidence = serializers.FloatField(required=False)
    response_method = serializers.CharField()
    processing_time = serializers.FloatField()


class KnowledgeBaseSerializer(serializers.ModelSerializer):
    """
    Serializer pour la base de connaissances
    """
    class Meta:
        model = KnowledgeBase
        fields = '__all__'


class ChatbotSettingsSerializer(serializers.ModelSerializer):
    """
    Serializer pour les paramètres du chatbot
    """
    class Meta:
        model = ChatbotSettings
        fields = '__all__'
