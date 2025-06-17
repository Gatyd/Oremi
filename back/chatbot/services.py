import time
import logging
import uuid
from typing import Tuple, Optional, Dict, Any
from django.conf import settings
from django.db.models import Q
from textblob import TextBlob
from langdetect import detect, DetectorFactory
from sentence_transformers import SentenceTransformer
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

from .models import KnowledgeBase, Conversation, Message, ChatbotSettings

# Configuration pour des résultats reproductibles
DetectorFactory.seed = 0

logger = logging.getLogger(__name__)


class EmotionDetector:
    """
    Détecteur d'émotions basé sur TextBlob et règles personnalisées
    """
    
    EMOTION_KEYWORDS = {
        'joy': ['heureux', 'content', 'joyeux', 'super', 'génial', 'parfait', 'excellent', 'merci'],
        'sad': ['triste', 'déprimé', 'malheureux', 'déçu', 'peine', 'chagrin'],
        'angry': ['énervé', 'furieux', 'colère', 'agacé', 'irrité', 'rage', 'damn', 'merde'],
        'fear': ['peur', 'inquiet', 'anxieux', 'stress', 'angoisse', 'crainte'],
        'surprise': ['surpris', 'étonnant', 'incroyable', 'wow', 'oh', 'vraiment'],
    }
    
    @staticmethod
    def detect_emotion(text: str) -> Tuple[str, float]:
        """
        Détecte l'émotion dans un texte
        
        Returns:
            Tuple[str, float]: (émotion, confiance)
        """
        text_lower = text.lower()
        
        # Analyse de polarité avec TextBlob
        blob = TextBlob(text)
        polarity = blob.sentiment.polarity
        
        # Détection par mots-clés
        emotion_scores = {}
        for emotion, keywords in EmotionDetector.EMOTION_KEYWORDS.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            if score > 0:
                emotion_scores[emotion] = score
        
        # Si des émotions spécifiques sont détectées
        if emotion_scores:
            best_emotion = max(emotion_scores, key=emotion_scores.get)
            confidence = min(emotion_scores[best_emotion] * 0.3, 1.0)
            return best_emotion, confidence
        
        # Sinon, utilise la polarité
        if polarity > 0.3:
            return 'positive', abs(polarity)
        elif polarity < -0.3:
            return 'negative', abs(polarity)
        else:
            return 'neutral', 0.5


class KnowledgeBaseMatcher:
    """
    Système de correspondance avec la base de connaissances
    """
    
    def __init__(self):
        # Désactiver temporairement le modèle de similarité sémantique
        # à cause des problèmes SSL
        self.model = None
        logger.info("Modèle de similarité sémantique désactivé temporairement")
    
    def find_best_match(self, user_message: str) -> Tuple[Optional[KnowledgeBase], float]:
        """
        Trouve la meilleure correspondance dans la base de connaissances
        ALGORITHME AMÉLIORÉ ET PLUS PERMISSIF
        
        Args:
            user_message: Message de l'utilisateur
            
        Returns:
            Tuple[KnowledgeBase, float]: (meilleure correspondance, score de confiance)
        """
        knowledge_entries = KnowledgeBase.objects.filter(is_active=True)
        
        if not knowledge_entries.exists():
            return None, 0.0
        
        best_match = None
        best_score = 0.0
        
        user_message_lower = user_message.lower().strip()
        user_words = set(user_message_lower.split())
        
        logger.info(f"🔍 Recherche pour: '{user_message}' -> mots: {user_words}")
        
        for entry in knowledge_entries:
            score = 0.0
            details = []
            
            # 1. CORRESPONDANCE EXACTE - Score très élevé
            if user_message_lower == entry.question.lower():
                score = 1.0
                details.append("MATCH EXACT")
            
            # 2. CORRESPONDANCE DANS LA QUESTION - Plus permissif
            question_words = set(entry.question.lower().split())
            question_matches = user_words.intersection(question_words)
            if question_matches and len(question_words) > 0:
                question_score = len(question_matches) / max(len(user_words), len(question_words))
                score += question_score * 0.6  # Poids plus élevé
                details.append(f"Question: {len(question_matches)}/{len(question_words)} = {question_score:.2f}")
            
            # 3. CORRESPONDANCE MOTS-CLÉS - Plus intelligente
            if entry.keywords:
                keywords = [k.strip().lower() for k in entry.keywords.split(',') if k.strip()]
                keyword_matches = 0
                total_keywords = len(keywords)
                
                for keyword in keywords:
                    # Correspondance exacte du mot-clé
                    if keyword in user_message_lower:
                        keyword_matches += 1
                    # Correspondance partielle pour les mots composés
                    elif any(word in keyword or keyword in word for word in user_words if len(word) > 2):
                        keyword_matches += 0.5
                
                if total_keywords > 0:
                    keyword_score = keyword_matches / total_keywords
                    score += keyword_score * 0.5  # Poids élevé pour les mots-clés
                    details.append(f"Mots-clés: {keyword_matches}/{total_keywords} = {keyword_score:.2f}")
            
            # 4. CORRESPONDANCE PARTIELLE DANS LA QUESTION - Nouveau
            if user_message_lower in entry.question.lower() or entry.question.lower() in user_message_lower:
                score += 0.3
                details.append("Correspondance partielle")
            
            # 5. BONUS POUR LES SALUTATIONS
            salutations = ['bonjour', 'salut', 'hello', 'hey', 'coucou', 'bonsoir']
            if any(sal in user_message_lower for sal in salutations) and any(sal in entry.keywords.lower() for sal in salutations if entry.keywords):
                score += 0.4
                details.append("Bonus salutation")
            
            # 6. BONUS POUR LES QUESTIONS COURTES
            if len(user_words) <= 3 and score > 0:
                score += 0.2
                details.append("Bonus question courte")
            
            # Nouveau seuil beaucoup plus bas et dynamique
            dynamic_threshold = max(0.2, entry.confidence_threshold * 0.3)  # Réduction drastique
            
            logger.info(f"{'✅' if score >= dynamic_threshold else '❌'} [{score:.3f} >= {dynamic_threshold:.3f}] {entry.question[:50]}... | {', '.join(details)}")
            
            if score >= dynamic_threshold and score > best_score:
                best_match = entry
                best_score = score
        
        if best_match:
            logger.info(f"🎯 MEILLEURE CORRESPONDANCE: '{best_match.question}' avec score {best_score:.3f}")
        else:
            logger.info("❌ Aucune correspondance trouvée")
        
        return best_match, best_score


class AIResponseGenerator:
    """
    Générateur de réponses IA en fallback
    """
    
    def __init__(self):
        self.fallback_responses = [
            "Hmm, c'est une question intéressante ! 🤔 Je n'ai pas toutes les informations sous la main pour vous répondre précisément. Pouvez-vous me donner un peu plus de contexte ?",
            "Ah, je vois ce que vous voulez dire ! Malheureusement, je n'ai pas encore assez d'infos sur ce point spécifique. Essayons d'aborder cela autrement - que cherchez-vous exactement à faire ?",
            "Oh là là, je dois avouer que je ne suis pas sûr d'avoir bien saisi ! 😅 Pouvez-vous reformuler votre question ? J'aimerais vraiment pouvoir vous aider !",
            "Excellente question ! Je sens que c'est important pour vous. Même si je n'ai pas la réponse exacte, peut-être que je peux vous orienter autrement. Dites-moi en plus sur votre situation ?",
            "Je dois être honnête avec vous - cette question me dépasse un peu ! 😊 Mais ne vous découragez pas, on va trouver une solution ensemble. Pouvez-vous me dire ce qui vous amène à poser cette question ?",
        ]
        
        self.conversation_starters = [
            "Au fait, pendant que j'y pense",
            "D'ailleurs",
            "À propos",
            "Cela me fait penser à",
            "Tiens, ça me rappelle que",
        ]
        
        self.empathy_expressions = {
            'frustration': [
                "Je comprends que ce soit frustrant",
                "C'est vrai que ça peut être agaçant",
                "Je vois que vous êtes un peu embêté",
            ],
            'confusion': [
                "Pas de souci, c'est normal d'être un peu perdu",
                "Ne vous inquiétez pas, on va démêler ça ensemble",
                "C'est tout à fait compréhensible d'avoir des questions",
            ],            'urgency': [
                "Je vois que c'est urgent pour vous",
                "Je comprends que vous ayez besoin d'une réponse rapide",
                "C'est important, je vais faire de mon mieux",
            ]
        }
    
    def generate_response(self, user_message: str, conversation_history: list = None, detected_emotion: str = None) -> str:
        """
        Génère une réponse IA naturelle et empathique
        
        Args:
            user_message: Message de l'utilisateur
            conversation_history: Historique de la conversation
            detected_emotion: Émotion détectée
            
        Returns:
            str: Réponse générée
        """
        user_message_lower = user_message.lower()
        
        # Réponses contextuelles et naturelles
        if any(greeting in user_message_lower for greeting in ['bonjour', 'salut', 'hello', 'hey', 'coucou']):
            greetings = [
                "Salut ! 😊 Super de vous voir ! Comment ça va aujourd'hui ?",
                "Hello ! Ravi de vous retrouver ! Qu'est-ce qui vous amène ?",
                "Bonjour ! J'espère que vous passez une belle journée ! Comment puis-je vous aider ?",
                "Hey ! Content de vous voir par ici ! Dites-moi tout, qu'est-ce que je peux faire pour vous ?",
                "Coucou ! 👋 Ça fait plaisir ! Alors, qu'est-ce qui vous préoccupe aujourd'hui ?"
            ]
            return self._random_choice(greetings)
        
        if any(thanks in user_message_lower for thanks in ['merci', 'thank', 'remercie', 'super', 'génial']):
            thanks_responses = [
                "Mais de rien, ça me fait plaisir ! 😊 C'est pour ça que je suis là !",
                "Avec grand plaisir ! N'hésitez surtout pas si vous avez d'autres questions !",
                "Oh, c'est gentil ! J'adore pouvoir vous aider ! Autre chose ?",
                "Tout le plaisir est pour moi ! 🤗 Y a-t-il autre chose que je puisse faire ?",
                "Ça me fait chaud au cœur ! N'hésitez pas à revenir quand vous voulez !"
            ]
            return self._random_choice(thanks_responses)
        
        if any(goodbye in user_message_lower for goodbye in ['au revoir', 'bye', 'à bientôt', 'salut', 'tchao']):
            goodbye_responses = [
                "Au revoir ! 👋 C'était un vrai plaisir de discuter avec vous ! À très bientôt !",
                "Bye bye ! J'espère qu'on se reparlera bientôt ! Passez une excellente journée ! ☀️",
                "À bientôt ! N'hésitez surtout pas à revenir me voir ! 😊",
                "Salut ! Prenez soin de vous et à la prochaine ! 🤗",
                "Tchao ! C'était super sympa ! Revenez me voir quand vous voulez !"
            ]
            return self._random_choice(goodbye_responses)
        
        # Réponses selon l'émotion détectée
        if detected_emotion:
            emotion_response = self._get_empathetic_response(detected_emotion, user_message_lower)
            if emotion_response:
                return emotion_response
        
        # Réponses contextuelles spécifiques
        if any(word in user_message_lower for word in ['aide', 'aider', 'help', 'assistance']):
            help_responses = [
                "Bien sûr que je peux vous aider ! 😊 C'est exactement pour ça que je suis là ! Dites-moi ce qui vous préoccupe !",
                "Avec plaisir ! J'adore pouvoir rendre service ! Alors, qu'est-ce qui vous tracasse ?",
                "Absolument ! Je suis tout ouïe ! 👂 Expliquez-moi votre situation, on va trouver une solution ensemble !",
                "Évidemment ! C'est ma mission préférée ! Racontez-moi tout, qu'est-ce que je peux faire pour vous ?",
            ]
            return self._random_choice(help_responses)
        
        if any(word in user_message_lower for word in ['problème', 'souci', 'bug', 'erreur', 'marche pas']):
            problem_responses = [
                "Oh là là, un petit souci ? 😔 Pas de panique, on va régler ça ensemble ! Dites-moi exactement ce qui se passe !",
                "Aïe, un problème ! Ne vous inquiétez pas, je vais faire de mon mieux pour vous aider ! Pouvez-vous me décrire la situation ?",
                "Zut alors ! Un bug qui vous embête ? 🤔 Racontez-moi tout en détail, qu'on puisse voir ce qui cloche !",
                "Oh non, quelque chose ne marche pas comme il faut ? Décrivez-moi le problème, on va trouver la solution !",
            ]
            return self._random_choice(problem_responses)
        
        # Réponse par défaut aléatoire et naturelle
        return self._get_natural_fallback_response(user_message_lower)
    
    def _get_empathetic_response(self, emotion: str, message: str) -> str:
        """Génère une réponse empathique selon l'émotion"""
        if emotion == 'angry' or emotion == 'negative':
            return "Je sens que vous êtes un peu frustré... 😔 C'est tout à fait compréhensible ! Prenons le temps de voir comment je peux vous aider. Qu'est-ce qui vous préoccupe le plus ?"
        
        elif emotion == 'sad':
            return "Je vois que quelque chose vous tracasse... 💙 Je suis là pour vous écouter et vous aider du mieux que je peux. Voulez-vous me parler de ce qui vous préoccupe ?"
        
        elif emotion == 'fear':
            return "Je sens un peu d'inquiétude dans votre message... Ne vous en faites pas, on va prendre les choses une par une ! 🤗 Dites-moi ce qui vous fait peur, on va voir ça ensemble !"
        
        elif emotion == 'joy' or emotion == 'positive':
            return "J'adore votre enthousiasme ! 😄 Ça fait plaisir ! Alors, comment puis-je contribuer à cette bonne humeur ? Qu'est-ce que je peux faire pour vous ?"
        
        return None
    
    def _get_natural_fallback_response(self, message: str) -> str:
        """Génère une réponse de fallback naturelle"""
        import random
        
        # Analyser le message pour une réponse plus contextuelle
        if '?' in message:
            question_responses = [
                "Excellente question ! 🤔 Même si je n'ai pas la réponse exacte sous la main, dites-moi en plus sur ce que vous cherchez ? Peut-être que je peux vous orienter !",
                "Ah, une question intéressante ! Je dois avouer que je ne suis pas sûr d'avoir toutes les infos nécessaires... Pouvez-vous me donner un peu plus de contexte ?",
                "Oh, bonne question ! 😊 Je sens que c'est important pour vous. Même si je n'ai pas la réponse précise, on peut sûrement trouver une solution ensemble. Expliquez-moi votre situation !",
            ]
            return random.choice(question_responses)
        
        # Réponses générales naturelles
        return random.choice(self.fallback_responses)
    
    def _random_choice(self, options):
        """Sélection aléatoire avec un peu de variabilité"""
        import random
        return random.choice(options)


class ChatbotService:
    """
    Service principal du chatbot
    """
    
    def __init__(self):
        self.emotion_detector = EmotionDetector()
        self.knowledge_matcher = KnowledgeBaseMatcher()
        self.ai_generator = AIResponseGenerator()
    
    def process_message(self, user_message: str, session_id: str = None, user_id: int = None) -> Dict[str, Any]:
        """
        Traite un message utilisateur et génère une réponse
        
        Args:
            user_message: Message de l'utilisateur
            session_id: ID de session (optionnel)
            user_id: ID utilisateur (optionnel)
            
        Returns:
            Dict: Réponse complète avec métadonnées
        """
        start_time = time.time()
        
        # Génération d'un session_id si non fourni
        if not session_id:
            session_id = str(uuid.uuid4())
        
        # Récupération ou création de la conversation
        conversation = self._get_or_create_conversation(session_id, user_id)
        
        # Détection de la langue
        try:
            detected_language = detect(user_message)
        except:
            detected_language = 'fr'  # Français par défaut
        
        # Détection d'émotion
        emotion, emotion_confidence = self.emotion_detector.detect_emotion(user_message)
        
        # Sauvegarde du message utilisateur
        user_message_obj = Message.objects.create(
            conversation=conversation,
            sender='user',
            content=user_message,
            detected_emotion=emotion,
            emotion_confidence=emotion_confidence,
            detected_language=detected_language
        )
        
        # Génération de la réponse
        response_text, response_method, knowledge_used = self._generate_response(
            user_message, conversation
        )
        
        # Calcul du temps de traitement
        processing_time = time.time() - start_time
        
        # Sauvegarde de la réponse du bot
        bot_message = Message.objects.create(
            conversation=conversation,
            sender='bot',
            content=response_text,
            knowledge_base_used=knowledge_used,
            response_method=response_method,
            processing_time=processing_time
        )
        
        return {
            'message': response_text,
            'session_id': session_id,
            'conversation_id': conversation.id,
            'detected_emotion': emotion,
            'emotion_confidence': emotion_confidence,
            'response_method': response_method,
            'processing_time': processing_time
        }
    
    def _get_or_create_conversation(self, session_id: str, user_id: int = None) -> Conversation:
        """
        Récupère ou crée une conversation
        """
        conversation_filter = Q(session_id=session_id, is_active=True)
        if user_id:
            conversation_filter &= Q(user_id=user_id)
        
        conversation = Conversation.objects.filter(conversation_filter).first()
        
        if not conversation:
            conversation = Conversation.objects.create(
                session_id=session_id,
                user_id=user_id if user_id else None
            )
        
        return conversation
    
    def _generate_response(self, user_message: str, conversation: Conversation) -> Tuple[str, str, Optional[KnowledgeBase]]:
        """
        Génère une réponse en utilisant la stratégie en couches
        
        Returns:
            Tuple[str, str, KnowledgeBase]: (réponse, méthode, base_connaissance_utilisée)
        """
        # 1. Recherche dans la base de connaissances
        knowledge_match, confidence = self.knowledge_matcher.find_best_match(user_message)
        
        if knowledge_match and confidence > knowledge_match.confidence_threshold:
            return knowledge_match.answer, 'knowledge_base', knowledge_match
          # 2. Génération IA
        settings_obj = ChatbotSettings.objects.first()
        if not settings_obj or settings_obj.enable_ai_generation:
            # Récupérer l'historique récent
            recent_messages = conversation.messages.order_by('-timestamp')[:10]
            conversation_history = [msg.content for msg in recent_messages]
            
            # Passer l'émotion détectée si disponible
            user_emotion = None
            last_user_message = conversation.messages.filter(sender='user').order_by('-timestamp').first()
            if last_user_message:
                user_emotion = last_user_message.detected_emotion
            
            ai_response = self.ai_generator.generate_response(user_message, conversation_history, user_emotion)
            return ai_response, 'ai_generation', None
        
        # 3. Réponse par défaut
        default_response = "Je ne suis pas sûr de comprendre votre question. Pouvez-vous la reformuler ?"
        if settings_obj:
            default_response = settings_obj.default_response
        
        return default_response, 'fallback', None
