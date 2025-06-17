from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'conversations', views.ConversationViewSet)
router.register(r'knowledge-base', views.KnowledgeBaseViewSet)

urlpatterns = [
    # API principale du chatbot
    path('chat/', views.ChatbotAPIView.as_view(), name='chatbot-chat'),
    
    # Endpoints utilitaires
    path('settings/', views.get_chatbot_settings, name='chatbot-settings'),
    path('history/', views.get_conversation_history, name='conversation-history'),
    path('health/', views.chatbot_health_check, name='chatbot-health'),
    
    # ViewSets via router
    path('', include(router.urls)),
]
