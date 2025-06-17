from django.core.management.base import BaseCommand
from chatbot.models import KnowledgeBase, ChatbotSettings
import json
import random


class Command(BaseCommand):
    help = 'Génère automatiquement des variations de questions pour enrichir la base de connaissances'

    def add_arguments(self, parser):
        parser.add_argument(
            '--multiply',
            type=int,
            default=3,
            help='Nombre de variations à créer par question de base'
        )

    def handle(self, *args, **options):
        self.stdout.write('🤖 Génération automatique de variations de questions...')
        
        multiply_factor = options['multiply']
        
        # Patterns de reformulation pour générer des variations naturelles
        question_patterns = {
            'what_is': [
                "C'est quoi {}?",
                "Qu'est-ce que c'est {}?", 
                "Expliquez-moi {}",
                "Dites-moi ce que c'est {}",
                "Parlez-moi de {}",
                "Je veux savoir sur {}",
                "Pouvez-vous m'expliquer {}?"
            ],
            'how_to': [
                "Comment faire pour {}?",
                "Comment je peux {}?",
                "Comment ça marche {}?",
                "Quelle est la procédure pour {}?",
                "Comment on fait {}?",
                "Je veux savoir comment {}",
                "Aidez-moi à {}"
            ],
            'can_i': [
                "Est-ce que je peux {}?",
                "C'est possible de {}?",
                "Je peux {}?",
                "Y a-t-il moyen de {}?",
                "Est-il possible de {}?",
                "Ai-je la possibilité de {}?"
            ],
            'greetings': [
                "Salut !",
                "Hey !",
                "Coucou !",
                "Bonjour !",
                "Hello !",
                "Bonsoir !",
                "Yo !",
                "Wesh !"
            ],
            'emotions_positive': [
                "C'est génial !",
                "Super !",
                "Excellent !",
                "Parfait !",
                "Vous êtes au top !",
                "Fantastique !",
                "Bravo !",
                "Incroyable !"
            ],
            'emotions_negative': [
                "C'est nul !",
                "Ça marche pas !",
                "Je suis énervé !",
                "C'est frustrant !",
                "J'en ai marre !",
                "Ça bug !",
                "C'est la galère !",
                "J'y arrive pas !"
            ],
            'help': [
                "Aidez-moi !",
                "J'ai besoin d'aide !",
                "Je suis perdu !",
                "Pouvez-vous m'aider ?",
                "Je ne comprends pas !",
                "Help !",
                "Au secours !",
                "SOS !"
            ]
        }
        
        # Variations spécifiques pour OREMI by AFG
        oremi_variations = [
            # Variations sur OREMI
            {
                'base_keywords': ['oremi', 'AFG'],
                'variations': [
                    "OREMI by AFG, c'est quoi exactement ?",
                    "Parlez-moi de l'app OREMI",
                    "Comment ça marche OREMI ?",
                    "OREMI AFG, qu'est-ce que ça fait ?",
                    "L'application d'AFG, elle sert à quoi ?",
                    "Expliquez-moi OREMI by AFG"
                ]
            },
            # Variations sur les assurances
            {
                'base_keywords': ['assurance', 'souscrire'],
                'variations': [
                    "Quoi comme assurance vous avez ?",
                    "Je peux assurer quoi avec vous ?",
                    "Vous faites quoi comme assurance ?",
                    "C'est quoi vos produits d'assurance ?",
                    "Qu'est-ce que je peux assurer ?",
                    "Vos assurances, c'est quoi ?",
                    "Montrez-moi vos assurances"
                ]
            },
            # Variations sur le paiement
            {
                'base_keywords': ['paiement', 'payer'],
                'variations': [
                    "Je paie comment ?",
                    "C'est quoi les moyens de paiement ?",
                    "Comment je règle ?",
                    "Avec quoi je peux payer ?",
                    "Les modes de paiement ?",
                    "Comment régler ma prime ?",
                    "Je peux payer avec quoi ?"
                ]
            },
            # Variations sur Mobile Money
            {
                'base_keywords': ['mobile money', 'MTN', 'Moov'],
                'variations': [
                    "Mobile Money, ça marche ?",
                    "Je peux utiliser MTN Money ?",
                    "Moov Money c'est bon ?",
                    "Le paiement mobile ?",
                    "Payer avec mon téléphone ?",
                    "Mobile banking ça marche ?",
                    "Paiement via mobile ?"
                ]
            },
            # Variations sur la souscription
            {
                'base_keywords': ['souscrire', 'comment'],
                'variations': [
                    "Comment je m'inscris ?",
                    "Comment prendre une assurance ?",
                    "Je fais comment pour souscrire ?",
                    "Quelle est la démarche ?",
                    "Comment ça se passe pour s'assurer ?",
                    "Je veux m'assurer, comment faire ?",
                    "La procédure pour s'assurer ?"
                ]
            },
            # Variations sur les sinistres
            {
                'base_keywords': ['sinistre', 'déclarer'],
                'variations': [
                    "J'ai eu un accident, je fais quoi ?",
                    "Comment signaler un sinistre ?",
                    "J'ai un problème, comment déclarer ?",
                    "Accident, que faire ?",
                    "Sinistre, comment procéder ?",
                    "J'ai un pépin, comment faire ?",
                    "Dégâts, comment déclarer ?"
                ]
            },
            # Variations sur les attestations
            {
                'base_keywords': ['attestation', 'valide'],
                'variations': [
                    "Mon attestation électronique est valable ?",
                    "La police accepte l'e-attestation ?",
                    "Attestation numérique, c'est bon ?",
                    "Mon attestation sur le téléphone, ça marche ?",
                    "E-attestation, c'est légal ?",
                    "Attestation dématérialisée valide ?",
                    "Papiers électroniques acceptés ?"
                ]
            },
            # Variations sur le contact
            {
                'base_keywords': ['contact', 'assistance'],
                'variations': [
                    "Comment vous joindre ?",
                    "Numéro de téléphone ?",
                    "Je vous appelle où ?",
                    "Votre email ?",
                    "Comment vous contacter ?",
                    "Service client ?",
                    "Numéro d'assistance ?"
                ]
            }
        ]
        
        created_count = 0
        
        # Générer des variations basées sur les patterns
        for variation_group in oremi_variations:
            base_keywords = variation_group['base_keywords']
            variations = variation_group['variations']
            
            # Trouver une réponse de base qui correspond
            base_entry = None
            for keyword in base_keywords:
                base_entry = KnowledgeBase.objects.filter(
                    keywords__icontains=keyword,
                    is_active=True
                ).first()
                if base_entry:
                    break
            
            if base_entry:
                for i, variation_question in enumerate(variations):
                    # Créer une variation de la réponse avec un style légèrement différent
                    base_answer = base_entry.answer
                    
                    # Ajouter des variations dans le ton
                    variation_prefixes = [
                        "Ah ! ",
                        "Alors, ",
                        "Eh bien, ",
                        "Bon, ",
                        "OK, ",
                        "Parfait ! ",
                        "Super question ! "
                    ]
                    
                    variation_answer = random.choice(variation_prefixes) + base_answer
                    
                    # Créer l'entrée de variation
                    variation_entry = {
                        'category': f"{base_entry.category} - Variation {i+1}",
                        'question': variation_question,
                        'answer': variation_answer,
                        'keywords': base_entry.keywords + f", variation, {variation_question.lower()}",
                        'confidence_threshold': max(0.4, base_entry.confidence_threshold - 0.2)
                    }
                    
                    kb, created = KnowledgeBase.objects.get_or_create(
                        question=variation_entry['question'],
                        defaults=variation_entry
                    )
                    if created:
                        created_count += 1
        
        # Ajouter des questions d'émotions spécifiques
        emotion_entries = [
            {
                'category': 'Émotion - Joie',
                'question': 'Je suis trop content !',
                'answer': 'Génial ! 🎉 Ça me fait super plaisir de voir que vous êtes content ! C\'est exactement ce qu\'on veut chez OREMI by AFG - des clients heureux ! Qu\'est-ce qui vous rend si joyeux ? 😊',
                'keywords': 'content, joyeux, heureux, génial, parfait',
                'confidence_threshold': 0.6
            },
            {
                'category': 'Émotion - Surprise',
                'question': 'Waouh, c\'est incroyable !',
                'answer': 'Oh ! Ça c\'est une belle réaction ! 😍 Qu\'est-ce qui vous surprend tant ? J\'adore quand OREMI by AFG fait cet effet-là ! Racontez-moi tout ! ✨',
                'keywords': 'waouh, incroyable, surprenant, étonnant, impressionnant',
                'confidence_threshold': 0.6
            },
            {
                'category': 'Familier',
                'question': 'Wesh, ça va ?',
                'answer': 'Wesh ! 😄 Ça va nickel, et toi ? Cool de te voir ici ! Qu\'est-ce qui t\'amène sur OREMI today ? Je suis là pour t\'aider ! 🤙',
                'keywords': 'wesh, ça va, familier, cool, nickel',
                'confidence_threshold': 0.7
            },
            {
                'category': 'Blague',
                'question': 'Raconte-moi une blague !',
                'answer': 'Haha ! 😄 Alors... Pourquoi les assurances aiment OREMI by AFG ? Parce que c\'est le seul endroit où on peut dire "tout va bien se passer" et le penser vraiment ! 😂 Bon, je sais, je ne suis pas humoriste, mais j\'espère que ça vous a fait sourire ! 😊',
                'keywords': 'blague, humour, rigolo, drôle, rire',
                'confidence_threshold': 0.8
            }
        ]
        
        for entry in emotion_entries:
            kb, created = KnowledgeBase.objects.get_or_create(
                question=entry['question'],
                defaults=entry
            )
            if created:
                created_count += 1
        
        self.stdout.write(
            self.style.SUCCESS(
                f'🎯 {created_count} nouvelles variations générées automatiquement !'
            )
        )
        
        total_entries = KnowledgeBase.objects.count()
        self.stdout.write(
            self.style.SUCCESS(
                f'📊 Total dans la base de connaissances: {total_entries} entrées'
            )
        )
