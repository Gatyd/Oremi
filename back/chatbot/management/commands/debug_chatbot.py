from django.core.management.base import BaseCommand
from chatbot.models import KnowledgeBase
from chatbot.services import KnowledgeBaseMatcher, ChatbotService
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Teste et débogue le système de correspondance du chatbot'

    def add_arguments(self, parser):
        parser.add_argument(
            '--message',
            type=str,
            default='Bonjour',
            help='Message à tester'
        )

    def handle(self, *args, **options):
        test_message = options['message']
        
        self.stdout.write(f"🔍 Test du message: '{test_message}'")
        self.stdout.write("=" * 60)
        
        # 1. Vérifier la base de connaissances
        total_entries = KnowledgeBase.objects.count()
        active_entries = KnowledgeBase.objects.filter(is_active=True).count()
        
        self.stdout.write(f"📊 Entrées totales: {total_entries}")
        self.stdout.write(f"📊 Entrées actives: {active_entries}")
        
        if active_entries == 0:
            self.stdout.write(self.style.ERROR("❌ Aucune entrée active dans la base de connaissances!"))
            return
        
        # 2. Tester le matcher
        matcher = KnowledgeBaseMatcher()
        
        # 3. Analyser chaque entrée
        self.stdout.write(f"\n🔎 Analyse détaillée pour: '{test_message}'")
        self.stdout.write("-" * 50)
        
        user_message_lower = test_message.lower()
        knowledge_entries = KnowledgeBase.objects.filter(is_active=True)[:10]  # Limiter pour le debug
        
        for entry in knowledge_entries:
            score = 0.0
            details = []
            
            # Test mots-clés
            if entry.keywords:
                keywords = [k.strip().lower() for k in entry.keywords.split(',')]
                keyword_matches = sum(1 for keyword in keywords if keyword in user_message_lower)
                keyword_score = (keyword_matches / len(keywords)) * 0.4 if keywords else 0
                score += keyword_score
                details.append(f"Mots-clés: {keyword_matches}/{len(keywords)} = {keyword_score:.2f}")
            
            # Test correspondance question
            question_words = entry.question.lower().split()
            message_words = user_message_lower.split()
            common_words = set(question_words) & set(message_words)
            question_score = (len(common_words) / len(question_words)) * 0.3 if question_words else 0
            score += question_score
            details.append(f"Question: {len(common_words)}/{len(question_words)} = {question_score:.2f}")
            
            # Affichage
            status = "✅ MATCH" if score >= entry.confidence_threshold else "❌ NO MATCH"
            self.stdout.write(f"\n{status} [{score:.3f} >= {entry.confidence_threshold}]")
            self.stdout.write(f"Q: {entry.question[:50]}...")
            self.stdout.write(f"Mots-clés: {entry.keywords[:50]}...")
            for detail in details:
                self.stdout.write(f"  - {detail}")
        
        # 4. Test du service complet
        self.stdout.write(f"\n🤖 Test du service chatbot complet")
        self.stdout.write("-" * 50)
        
        try:
            best_match, confidence = matcher.find_best_match(test_message)
            if best_match:
                self.stdout.write(f"✅ Meilleure correspondance trouvée!")
                self.stdout.write(f"Question: {best_match.question}")
                self.stdout.write(f"Réponse: {best_match.answer[:100]}...")
                self.stdout.write(f"Confiance: {confidence:.3f}")
            else:
                self.stdout.write(f"❌ Aucune correspondance trouvée")
            
            # Test du service complet
            chatbot_service = ChatbotService()
            response = chatbot_service.process_message(test_message, "debug-session")
            self.stdout.write(f"\n📝 Réponse finale: {response['message'][:100]}...")
            self.stdout.write(f"📝 Méthode: {response['response_method']}")
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Erreur: {str(e)}"))
            import traceback
            traceback.print_exc()
        
        # 5. Suggestions d'amélioration
        self.stdout.write(f"\n💡 Suggestions:")
        self.stdout.write("- Réduire les seuils de confiance (essayer 0.3-0.5)")
        self.stdout.write("- Ajouter plus de mots-clés aux entrées")
        self.stdout.write("- Vérifier que les keywords contiennent les termes du message test")
