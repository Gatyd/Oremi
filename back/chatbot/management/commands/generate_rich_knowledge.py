import json
from django.core.management.base import BaseCommand
from chatbot.models import KnowledgeBase, ChatbotSettings


class Command(BaseCommand):
    help = 'Génère une base de connaissances riche et conversationnelle pour OREMI by AFG'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Vide la base de connaissances avant l\'importation'
        )

    def handle(self, *args, **options):
        if options['clear']:
            count = KnowledgeBase.objects.count()
            KnowledgeBase.objects.all().delete()
            self.stdout.write(
                self.style.WARNING(f'{count} entrées supprimées de la base de connaissances')
            )
        
        # Configuration du chatbot
        settings, created = ChatbotSettings.objects.get_or_create(
            defaults={
                'name': 'Oremi by AFG',
                'personality': 'Je suis Oremi, votre assistant virtuel sympa et bienveillant d\'AFG Assurances ! Je suis là pour vous aider avec vos assurances de manière décontractée et chaleureuse. J\'aime utiliser des emojis et avoir des conversations naturelles ! 😊',
                'default_response': 'Hmm, c\'est une question intéressante ! 🤔 Je n\'ai pas toutes les informations sous la main pour vous répondre précisément. Pouvez-vous me donner un peu plus de contexte ? Ou peut-être reformuler votre question ?',
                'max_conversation_length': 100,
                'enable_emotion_detection': True,
                'enable_ai_generation': True,
            }
        )
        
        # Base de connaissances étendue avec variations
        knowledge_data = []
        
        # SALUTATIONS - Variations multiples
        salutation_variations = [
            {
                'questions': ['Bonjour', 'Salut', 'Hello', 'Hey', 'Coucou', 'Bonsoir', 'Bonne journée'],
                'answer': 'Salut ! 😊 Super de vous voir ! Je suis Oremi, votre assistant virtuel d\'AFG Assurances ! Comment ça va aujourd\'hui ? Qu\'est-ce qui vous amène ?',
                'keywords': 'bonjour, salut, hello, hey, coucou, bonsoir',
                'confidence_threshold': 0.8
            },
            {
                'questions': ['Comment allez-vous ?', 'Comment ça va ?', 'Ça va ?', 'Vous allez bien ?'],
                'answer': 'Ça va super bien, merci de demander ! 😄 Moi c\'est Oremi et je suis en pleine forme pour vous aider ! Et vous, comment ça se passe de votre côté ?',
                'keywords': 'comment ça va, comment allez-vous, ça va, allez bien',
                'confidence_threshold': 0.8
            }
        ]
        
        # PRÉSENTATION D'OREMI - Variations
        presentation_variations = [
            {
                'questions': [
                    'Qu\'est-ce qu\'Oremi ?', 'C\'est quoi Oremi ?', 'Qui êtes-vous ?', 
                    'Présentez-vous', 'Que faites-vous ?', 'Oremi c\'est quoi ?'
                ],
                'answer': 'Alors, moi c\'est Oremi ! 👋 Je suis votre assistant virtuel pour OREMI by AFG ! En fait, je représente l\'application mobile et web super pratique d\'AFG Assurances IARDT Bénin. Mon truc, c\'est de vous permettre de souscrire à vos assurances et de gérer vos contrats sans bouger de chez vous ! Plus besoin de se déplacer, tout se fait en quelques clics ! Sympa, non ? 😄',
                'keywords': 'oremi, qu\'est-ce que, c\'est quoi, qui êtes-vous, présentation, AFG, assurance',
                'confidence_threshold': 0.8
            },
            {
                'questions': [
                    'AFG c\'est quoi ?', 'Qu\'est-ce qu\'AFG ?', 'AFG Assurances', 
                    'Parlez-moi d\'AFG', 'C\'est quoi AFG Assurances ?'
                ],
                'answer': 'AFG Assurances IARDT Bénin, c\'est notre compagnie d\'assurance ! 🏢 Nous, on est spécialisés dans les assurances IARDT (Incendie, Accidents et Risques Divers). Et OREMI by AFG, c\'est notre application révolutionnaire qui vous permet de tout gérer depuis votre téléphone ! Simple, rapide et efficace ! 📱✨',
                'keywords': 'AFG, assurances, IARDT, compagnie, Bénin',
                'confidence_threshold': 0.8
            }
        ]
        
        # TYPES D'ASSURANCE - Détaillé
        assurance_variations = [
            {
                'questions': [
                    'Quelles assurances proposez-vous ?', 'À quelles assurances puis-je souscrire ?',
                    'Quels types d\'assurance ?', 'Vos produits d\'assurance', 'Que puis-je assurer ?'
                ],
                'answer': 'Oh là là, on a plein de super produits pour vous ! 🚗✈️🏠🏍️ Vous avez l\'assurance automobile pour votre voiture personnelle, l\'assurance voyage pour ne jamais être seul à l\'étranger (ça c\'est rassurant !), l\'assurance moto pour vos déplacements quotidiens, et l\'assurance habitation que vous soyez locataire ou propriétaire ! Et ce n\'est qu\'un début, plein d\'autres produits arrivent très bientôt ! 🎉',
                'keywords': 'assurance, souscrire, automobile, voyage, moto, habitation, produits, types',
                'confidence_threshold': 0.7
            },
            {
                'questions': [
                    'Assurance automobile', 'Assurance voiture', 'Assurer ma voiture',
                    'Auto assurance', 'Assurance auto'
                ],
                'answer': 'Parfait ! L\'assurance automobile, c\'est notre spécialité ! 🚗 Avec nous, vous pouvez assurer votre voiture personnelle facilement ! Fini les longues attentes en agence, tout se fait sur l\'app ! Vous remplissez le formulaire, vous avez votre devis personnalisé, et hop, vous êtes couvert ! Et vos e-attestations sont valides partout au Bénin et dans la zone UMOA ! 📋✅',
                'keywords': 'automobile, voiture, auto, assurer voiture',
                'confidence_threshold': 0.8
            },
            {
                'questions': [
                    'Assurance voyage', 'Assurer voyage', 'Voyage à l\'étranger',
                    'Assurance à l\'étranger', 'Partir en voyage'
                ],
                'answer': 'L\'assurance voyage, c\'est le truc génial pour partir l\'esprit tranquille ! ✈️🌍 Avec ça, vous n\'êtes jamais seul à l\'étranger ! On vous couvre pour tous les petits (et gros) pépins qui peuvent arriver en voyage. Plus besoin de stresser, on s\'occupe de vous ! Vous pouvez souscrire direct sur l\'app en quelques minutes ! 😊',
                'keywords': 'voyage, étranger, partir, vacances, international',
                'confidence_threshold': 0.8
            }
        ]
        
        # PROCESSUS - Étapes détaillées
        process_variations = [
            {
                'questions': [
                    'Comment souscrire ?', 'Étapes de souscription', 'Comment faire ?',
                    'Processus de souscription', 'Comment ça marche ?'
                ],
                'answer': 'C\'est vraiment simple ! 📱✨ Allez sur l\'accueil de l\'app, choisissez votre assurance, lisez le descriptif (tout est expliqué simplement !), faites votre devis en répondant aux questions - ça prend que quelques minutes ! Cliquez sur SOUSCRIRE, donnez quelques infos supplémentaires, payez via Mobile Money ou carte, et voilà ! Vos documents s\'affichent, vous les téléchargez ! Magique ! 🎉',
                'keywords': 'souscrire, comment, étapes, processus, devis, marche',
                'confidence_threshold': 0.7
            },
            {
                'questions': [
                    'Faire un devis', 'Devis assurance', 'Estimation prix',
                    'Combien ça coûte ?', 'Prix assurance'
                ],
                'answer': 'Ah, pour le devis c\'est super facile ! 💰 Vous choisissez votre assurance, vous répondez à quelques questions personnalisées (âge, type de véhicule, etc.), et hop ! Votre devis personnalisé apparaît instantanément ! Pas de surprise, tout est transparent ! Et si ça vous plaît, vous pouvez souscrire direct ! 😊',
                'keywords': 'devis, prix, coût, tarif, estimation, combien',
                'confidence_threshold': 0.8
            }
        ]
        
        # PAIEMENT
        payment_variations = [
            {
                'questions': [
                    'Comment payer ?', 'Moyens de paiement', 'Paiement',
                    'Mobile Money', 'Carte de crédit', 'MTN', 'Moov'
                ],
                'answer': 'Pour le paiement, c\'est super flexible ! 💳📱 Vous pouvez payer par Mobile Money (MTN et Moov) en juste deux clics - c\'est vraiment pratique ! Ou utiliser votre carte de crédit si vous préférez. Et on travaille sur encore plus de moyens de paiement pour que ce soit encore plus facile ! On veut que tout soit simple pour vous ! 😊',
                'keywords': 'paiement, payer, mobile money, MTN, Moov, carte crédit',
                'confidence_threshold': 0.8
            }
        ]
        
        # SINISTRES
        sinistre_variations = [
            {
                'questions': [
                    'Déclarer un sinistre', 'Comment déclarer ?', 'Sinistre',
                    'Accident', 'Déclaration sinistre', 'J\'ai eu un accident'
                ],
                'answer': 'Oh, désolé pour ce qui vous arrive ! 😔 Mais pas de panique ! Déclarer un sinistre c\'est simple : allez dans votre compte, cliquez sur (+), choisissez votre police, remplissez le formulaire et envoyez ! On reçoit tout automatiquement et on traite votre dossier rapidement ! Vous aurez des notifications pour suivre l\'avancement ! 📋💨',
                'keywords': 'sinistre, déclarer, accident, déclaration, dossier',
                'confidence_threshold': 0.8
            },
            {
                'questions': [
                    'Remboursement', 'Comment être remboursé ?', 'Indemnisation',
                    'Quand serai-je remboursé ?', 'Paiement sinistre'
                ],
                'answer': 'Alors pour le remboursement ! 💰 Une fois qu\'on a traité votre dossier, on vous fait une proposition financière. Si elle vous convient, vous nous dites comment vous voulez être remboursé : espèces, Mobile Money ou virement ! On vous demande les infos nécessaires et c\'est parti ! Simple et efficace ! 👍',
                'keywords': 'remboursement, remboursé, indemnisation, proposition',
                'confidence_threshold': 0.7
            }
        ]
        
        # CONTACT ET SUPPORT
        contact_variations = [
            {
                'questions': [
                    'Contacter support', 'Assistance', 'Aide', 'Contact',
                    'Numéro de téléphone', 'Email', 'Comment vous joindre ?'
                ],
                'answer': 'On est toujours là pour vous ! 📞💬 Vous pouvez nous écrire à afg.iard@afgassurance.bj, nous appeler au +229 01 63 63 28 28 ou au +229 01 21 31 51 48. Et bien sûr, vous pouvez toujours me parler ici ! J\'adore discuter et aider ! 😊',
                'keywords': 'contact, assistance, aide, téléphone, email, support',
                'confidence_threshold': 0.8
            }
        ]
        
        # PROBLÈMES TECHNIQUES
        tech_variations = [
            {
                'questions': [
                    'Bug application', 'App ne marche pas', 'Problème technique',
                    'Erreur', 'Application plante', 'Ça ne fonctionne pas'
                ],
                'answer': 'Oh là là, un petit souci technique ? 😔 Pas de panique ! Ça arrive parfois ! Pouvez-vous me dire exactement ce qui se passe ? L\'app ne se lance pas ? Vous n\'arrivez pas à vous connecter ? Plus vous me donnez de détails, mieux je peux vous aider ! On va régler ça ensemble ! 💪',
                'keywords': 'bug, problème, technique, erreur, ne marche pas, application',
                'confidence_threshold': 0.6
            }
        ]
        
        # Compilation de toutes les variations
        all_variations = [
            *salutation_variations, *presentation_variations, *assurance_variations,
            *process_variations, *payment_variations, *sinistre_variations,
            *contact_variations, *tech_variations
        ]
        
        # Génération des entrées
        for category_idx, variation_group in enumerate(all_variations):
            category = self._get_category_name(category_idx)
            
            for question in variation_group['questions']:
                knowledge_data.append({
                    'category': category,
                    'question': question,
                    'answer': variation_group['answer'],
                    'keywords': variation_group['keywords'],
                    'confidence_threshold': variation_group['confidence_threshold']
                })
        
        # Ajout d'entrées supplémentaires pour les réponses émotionnelles
        emotional_responses = [
            {
                'category': 'Support émotionnel',
                'question': 'Je suis frustré',
                'answer': 'Je comprends votre frustration... 😔 C\'est vraiment pas cool quand les choses ne se passent pas comme prévu ! Prenons le temps ensemble de voir ce qui vous embête. Racontez-moi tout, on va trouver une solution ! 🤗',
                'keywords': 'frustré, énervé, agacé, colère',
                'confidence_threshold': 0.5
            },
            {
                'category': 'Support émotionnel',
                'question': 'Je ne comprends rien',
                'answer': 'Hey, pas de stress ! 😊 C\'est normal de se sentir un peu perdu au début ! Je suis là exactement pour ça ! On va prendre les choses une par une, tranquillement. Qu\'est-ce qui vous pose problème en premier ? 🤝',
                'keywords': 'comprends rien, perdu, confus, difficile',
                'confidence_threshold': 0.5
            },
            {
                'category': 'Compliments',
                'question': 'Vous êtes génial !',
                'answer': 'Aww, merci beaucoup ! 🥰 Ça me fait super plaisir ! J\'adore pouvoir vous aider ! C\'est exactement pour ça que j\'existe ! Y a-t-il autre chose que je puisse faire pour vous ? 😊',
                'keywords': 'génial, super, excellent, formidable, top',
                'confidence_threshold': 0.8
            }
        ]
        
        knowledge_data.extend(emotional_responses)
        
        # Sauvegarde dans la base de données
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
                f'Base de connaissances générée avec {created_count} nouvelles entrées!'
            )
        )
        
        total_entries = KnowledgeBase.objects.count()
        self.stdout.write(
            self.style.SUCCESS(
                f'Total d\'entrées dans la base: {total_entries}'
            )
        )
    
    def _get_category_name(self, idx):
        categories = [
            'Salutations', 'Salutations', 'Présentation', 'Présentation',
            'Types d\'assurance', 'Types d\'assurance', 'Types d\'assurance',
            'Processus', 'Processus', 'Paiement', 'Sinistres', 'Sinistres',
            'Contact', 'Support technique'
        ]
        return categories[idx] if idx < len(categories) else 'Général'
