from django.db import models
from authentication.models import User
import json


class KnowledgeBase(models.Model):
    """
    Base de connaissances pour le chatbot - questions/réponses prédéfinies
    """
    category = models.CharField(max_length=100, help_text="Catégorie de la question")
    question = models.TextField(help_text="Question ou phrase clé")
    answer = models.TextField(help_text="Réponse correspondante")
    keywords = models.TextField(
        blank=True, 
        help_text="Mots-clés associés (séparés par des virgules)"
    )
    confidence_threshold = models.FloatField(
        default=0.7, 
        help_text="Seuil de confiance pour déclencher cette réponse"
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.category}: {self.question[:50]}..."

    class Meta:
        verbose_name = "Base de connaissances"
        verbose_name_plural = "Bases de connaissances"


class Conversation(models.Model):
    """
    Historique des conversations avec le chatbot
    """
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        help_text="Utilisateur (optionnel pour les conversations anonymes)"
    )
    session_id = models.CharField(
        max_length=100, 
        help_text="ID de session pour les utilisateurs anonymes"
    )
    started_at = models.DateTimeField(auto_now_add=True)
    last_message_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        user_info = self.user.username if self.user else f"Anonyme ({self.session_id[:8]})"
        return f"Conversation {user_info} - {self.started_at.strftime('%d/%m/%Y %H:%M')}"

    class Meta:
        verbose_name = "Conversation"
        verbose_name_plural = "Conversations"


class Message(models.Model):
    """
    Messages individuels dans une conversation
    """
    SENDER_CHOICES = [
        ('user', 'Utilisateur'),
        ('bot', 'Chatbot'),
    ]

    EMOTION_CHOICES = [
        ('neutral', 'Neutre'),
        ('positive', 'Positif'),
        ('negative', 'Négatif'),
        ('angry', 'Colère'),
        ('sad', 'Tristesse'),
        ('joy', 'Joie'),
        ('fear', 'Peur'),
        ('surprise', 'Surprise'),
    ]

    conversation = models.ForeignKey(
        Conversation, 
        on_delete=models.CASCADE, 
        related_name='messages'
    )
    sender = models.CharField(max_length=10, choices=SENDER_CHOICES)
    content = models.TextField(help_text="Contenu du message")
    
    # Analyse automatique du message
    detected_emotion = models.CharField(
        max_length=20, 
        choices=EMOTION_CHOICES, 
        null=True, 
        blank=True,
        help_text="Émotion détectée automatiquement"
    )
    emotion_confidence = models.FloatField(
        null=True, 
        blank=True,
        help_text="Confiance dans la détection d'émotion (0-1)"
    )
    detected_language = models.CharField(
        max_length=10, 
        null=True, 
        blank=True,
        help_text="Langue détectée"
    )
    
    # Métadonnées pour les réponses du bot
    knowledge_base_used = models.ForeignKey(
        KnowledgeBase,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Base de connaissances utilisée pour cette réponse"
    )
    response_method = models.CharField(
        max_length=20,
        choices=[
            ('knowledge_base', 'Base de connaissances'),
            ('ai_generation', 'Génération IA'),
            ('fallback', 'Réponse par défaut'),
        ],
        null=True,
        blank=True,
        help_text="Méthode utilisée pour générer la réponse"
    )
    processing_time = models.FloatField(
        null=True, 
        blank=True,
        help_text="Temps de traitement en secondes"
    )
    
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender}: {self.content[:50]}..."

    class Meta:
        verbose_name = "Message"
        verbose_name_plural = "Messages"
        ordering = ['timestamp']


class ChatbotSettings(models.Model):
    """
    Configuration globale du chatbot
    """
    name = models.CharField(max_length=100, default="Assistant Oremi")
    personality = models.TextField(
        default="Je suis un assistant virtuel bienveillant et professionnel.",
        help_text="Description de la personnalité du chatbot"
    )
    default_response = models.TextField(
        default="Je ne suis pas sûr de comprendre votre question. Pouvez-vous la reformuler ?",
        help_text="Réponse par défaut quand le chatbot ne comprend pas"
    )
    max_conversation_length = models.IntegerField(
        default=100,
        help_text="Nombre maximum de messages par conversation"
    )
    enable_emotion_detection = models.BooleanField(default=True)
    enable_ai_generation = models.BooleanField(default=True)
    ai_model_name = models.CharField(
        max_length=100,
        default="microsoft/DialoGPT-medium",
        help_text="Nom du modèle IA à utiliser"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Configuration {self.name}"

    class Meta:
        verbose_name = "Configuration du chatbot"
        verbose_name_plural = "Configurations du chatbot"
