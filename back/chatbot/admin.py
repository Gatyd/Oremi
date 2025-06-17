from django.contrib import admin
from .models import KnowledgeBase, Conversation, Message, ChatbotSettings


@admin.register(KnowledgeBase)
class KnowledgeBaseAdmin(admin.ModelAdmin):
    list_display = ['category', 'question_preview', 'is_active', 'confidence_threshold', 'created_at']
    list_filter = ['category', 'is_active', 'created_at']
    search_fields = ['question', 'answer', 'keywords', 'category']
    list_editable = ['is_active', 'confidence_threshold']
    
    fieldsets = (
        ('Information principale', {
            'fields': ('category', 'question', 'answer')
        }),
        ('Configuration', {
            'fields': ('keywords', 'confidence_threshold', 'is_active')
        }),
        ('Métadonnées', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']
    
    def question_preview(self, obj):
        return obj.question[:50] + "..." if len(obj.question) > 50 else obj.question
    question_preview.short_description = "Question"


class MessageInline(admin.TabularInline):
    model = Message
    extra = 0
    readonly_fields = ['timestamp', 'detected_emotion', 'emotion_confidence', 'processing_time']
    fields = ['sender', 'content', 'detected_emotion', 'response_method', 'timestamp']


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ['id', 'user_info', 'session_preview', 'message_count', 'started_at', 'is_active']
    list_filter = ['is_active', 'started_at']
    search_fields = ['session_id', 'user__username']
    readonly_fields = ['started_at', 'last_message_at']
    
    inlines = [MessageInline]
    
    def user_info(self, obj):
        return obj.user.username if obj.user else "Anonyme"
    user_info.short_description = "Utilisateur"
    
    def session_preview(self, obj):
        return obj.session_id[:8] + "..."
    session_preview.short_description = "Session"
    
    def message_count(self, obj):
        return obj.messages.count()
    message_count.short_description = "Messages"


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['id', 'conversation_id', 'sender', 'content_preview', 'detected_emotion', 'timestamp']
    list_filter = ['sender', 'detected_emotion', 'response_method', 'timestamp']
    search_fields = ['content']
    readonly_fields = ['timestamp', 'detected_emotion', 'emotion_confidence', 'processing_time']
    
    fieldsets = (
        ('Message', {
            'fields': ('conversation', 'sender', 'content')
        }),
        ('Analyse automatique', {
            'fields': ('detected_emotion', 'emotion_confidence', 'detected_language'),
            'classes': ('collapse',)
        }),
        ('Métadonnées de réponse', {
            'fields': ('knowledge_base_used', 'response_method', 'processing_time'),
            'classes': ('collapse',)
        }),
        ('Horodatage', {
            'fields': ('timestamp',),
            'classes': ('collapse',)
        }),
    )
    
    def content_preview(self, obj):
        return obj.content[:100] + "..." if len(obj.content) > 100 else obj.content
    content_preview.short_description = "Contenu"


@admin.register(ChatbotSettings)
class ChatbotSettingsAdmin(admin.ModelAdmin):
    list_display = ['name', 'enable_emotion_detection', 'enable_ai_generation', 'updated_at']
    
    fieldsets = (
        ('Configuration générale', {
            'fields': ('name', 'personality', 'default_response')
        }),
        ('Fonctionnalités', {
            'fields': ('enable_emotion_detection', 'enable_ai_generation', 'ai_model_name')
        }),
        ('Limites', {
            'fields': ('max_conversation_length',)
        }),
        ('Métadonnées', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']
    
    def has_add_permission(self, request):
        # Permettre seulement une instance de configuration
        return not ChatbotSettings.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        # Empêcher la suppression de la configuration
        return False
