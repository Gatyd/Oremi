from django.core.management.base import BaseCommand
from chatbot.models import KnowledgeBase, ChatbotSettings
import random


class Command(BaseCommand):
    help = 'Peuple la base de connaissances avec des données naturelles et chaleureuses pour OREMI by AFG'

    def handle(self, *args, **options):
        self.stdout.write('🚀 Initialisation de la base de connaissances OREMI by AFG...')
        
        # Créer la configuration par défaut avec une personnalité chaleureuse
        settings, created = ChatbotSettings.objects.get_or_create(
            defaults={
                'name': 'Oremi',
                'personality': 'Je suis Oremi, votre assistant virtuel personnel d\'AFG Assurances ! 😊 Je suis là pour vous aider avec vos assurances de manière simple, chaleureuse et naturelle. Mon but est de rendre votre expérience avec OREMI by AFG la plus agréable possible !',
                'default_response': 'Hmm, je ne suis pas sûr de bien saisir ce que vous voulez dire... 🤔 Pourriez-vous me l\'expliquer différemment ? Je suis là pour vous aider, alors n\'hésitez pas !',
                'max_conversation_length': 100,
                'enable_emotion_detection': True,
                'enable_ai_generation': True,
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS('✅ Configuration chaleureuse du chatbot créée'))
        
        # Base de connaissances riche et naturelle pour OREMI by AFG
        knowledge_data = [
            {
                'category': 'Salutations',
                'question': 'Bonjour, comment allez-vous ?',
                'answer': 'Bonjour ! Je vais très bien, merci. Je suis l\'assistant virtuel Oremi et je suis là pour vous aider. Comment puis-je vous assister aujourd\'hui ?',
                'keywords': 'bonjour, salut, hello, comment allez-vous, ça va',
                'confidence_threshold': 0.7
            },
            {
                'category': 'Présentation',
                'question': 'Qui êtes-vous ? Que faites-vous ?',
                'answer': 'Je suis l\'assistant virtuel d\'Oremi, votre compagnon intelligent pour naviguer dans nos services. Je peux vous aider avec des questions générales, vous orienter vers les bonnes ressources et discuter de manière naturelle avec vous.',
                'keywords': 'qui êtes-vous, que faites-vous, présentation, qui es-tu, c\'est quoi',
                'confidence_threshold': 0.6
            },
            {
                'category': 'Aide',
                'question': 'Pouvez-vous m\'aider ?',
                'answer': 'Bien sûr ! Je suis là pour vous aider. Vous pouvez me poser des questions sur les services Oremi, demander des informations générales, ou simplement discuter. N\'hésitez pas à me dire ce dont vous avez besoin !',
                'keywords': 'aide, aider, assistance, support, help',
                'confidence_threshold': 0.8
            },
            {
                'category': 'Services',
                'question': 'Quels services proposez-vous ?',
                'answer': 'Oremi propose plusieurs services incluant la gestion de devis automatisée, l\'extraction d\'informations depuis les cartes grises, et maintenant ce service de chatbot intelligent pour vous accompagner. Notre plateforme facilite vos démarches administratives.',
                'keywords': 'services, que proposez-vous, fonctionnalités, quoi faire',
                'confidence_threshold': 0.7
            },
            {
                'category': 'Devis',
                'question': 'Comment fonctionne le système de devis ?',
                'answer': 'Notre système de devis utilise l\'intelligence artificielle pour analyser automatiquement vos documents (comme les cartes grises) et générer des devis précis rapidement. Vous pouvez télécharger vos documents et recevoir une estimation en quelques minutes.',
                'keywords': 'devis, estimation, prix, tarif, carte grise',
                'confidence_threshold': 0.7
            },
            {
                'category': 'Remerciements',
                'question': 'Merci pour votre aide',
                'answer': 'Je vous en prie ! C\'était un plaisir de vous aider. N\'hésitez pas à revenir si vous avez d\'autres questions. Bonne journée !',
                'keywords': 'merci, thank you, remercie, merci beaucoup',
                'confidence_threshold': 0.8
            },
            {
                'category': 'Au revoir',
                'question': 'Au revoir, à bientôt',
                'answer': 'Au revoir ! J\'espère avoir pu vous aider. À très bientôt sur Oremi ! Passez une excellente journée.',
                'keywords': 'au revoir, bye, à bientôt, tchao, goodbye',
                'confidence_threshold': 0.8
            },
            {
                'category': 'Problème technique',
                'question': 'J\'ai un problème technique',
                'answer': 'Je comprends que vous rencontriez des difficultés techniques. Pouvez-vous me décrire plus précisément le problème que vous rencontrez ? Cela m\'aidera à mieux vous orienter vers la solution appropriée.',
                'keywords': 'problème, bug, erreur, technique, ne marche pas, dysfonctionnement',
                'confidence_threshold': 0.6
            },
            {
                'category': 'Émotions négatives',
                'question': 'Je suis frustré, rien ne marche',
                'answer': 'Je comprends votre frustration et j\'en suis désolé. Les problèmes techniques peuvent être vraiment agaçants. Prenons le temps ensemble de résoudre cela. Pouvez-vous me dire exactement ce qui ne fonctionne pas ?',
                'keywords': 'frustré, énervé, agacé, rien ne marche, problème',
                'confidence_threshold': 0.5
            },
            {
                'category': 'Compliments',
                'question': 'Vous êtes très utile !',
                'answer': 'C\'est très gentil, merci beaucoup ! Cela me fait plaisir de pouvoir vous être utile. C\'est exactement pour cela que je suis là. Y a-t-il autre chose avec quoi je peux vous aider ?',
                'keywords': 'utile, bien, super, génial, parfait, excellent',
                'confidence_threshold': 0.7
            }
        ]
        
        created_count = 0
        for data in knowledge_data:
            kb, created = KnowledgeBase.objects.get_or_create(
                question=data['question'],
                defaults=data
            )
            if created:
                created_count += 1
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Base de connaissances initialisée avec {created_count} nouvelles entrées'
            )
        )
        
        total_entries = KnowledgeBase.objects.count()
        self.stdout.write(
            self.style.SUCCESS(
                f'Total d\'entrées dans la base de connaissances: {total_entries}'
            )
        )
