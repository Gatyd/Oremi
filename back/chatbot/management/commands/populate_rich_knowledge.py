from django.core.management.base import BaseCommand
from chatbot.models import KnowledgeBase, ChatbotSettings


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
            # === SALUTATIONS ET PRÉSENTATION ===
            {
                'category': 'Salutations',
                'question': 'Bonjour ! Comment allez-vous ?',
                'answer': 'Salut ! 😊 Ça va super bien, merci de demander ! Moi c\'est Oremi, ravi de vous rencontrer ! Comment ça va de votre côté ? Qu\'est-ce qui vous amène aujourd\'hui ?',
                'keywords': 'bonjour, salut, hello, comment allez-vous, ça va, hey, coucou, bonsoir',
                'confidence_threshold': 0.7
            },
            {
                'category': 'Présentation Oremi',
                'question': 'Qui êtes-vous ? Présentez-vous',
                'answer': 'Alors, moi c\'est Oremi ! 👋 Je suis votre assistant virtuel personnel pour OREMI by AFG ! En gros, je représente l\'application mobile et web super pratique d\'AFG Assurances IARDT Bénin. Mon truc, c\'est de vous permettre de souscrire à vos assurances et de gérer vos contrats sans bouger de chez vous ! Plus besoin de se déplacer, tout se fait en quelques clics ! Sympa, non ? 😄',
                'keywords': 'qui êtes-vous, présentez-vous, qui es-tu, présentation, c\'est quoi ton nom',
                'confidence_threshold': 0.8
            },
            {
                'category': 'Qu\'est-ce qu\'OREMI',
                'question': 'C\'est quoi OREMI by AFG ?',
                'answer': 'OREMI by AFG, c\'est L\'application révolutionnaire (Mobile & Web) de souscription et de gestion de contrats d\'assurance d\'AFG Assurances IARDT Bénin ! 🚀 En gros, ça vous permet de souscrire à vos contrats d\'assurance sans vous déplacer et d\'effectuer vos déclarations de sinistres en toute simplicité. C\'est comme avoir votre agent d\'assurance dans votre poche ! 📱✨',
                'keywords': 'oremi, qu\'est-ce que, c\'est quoi, AFG, application, définition, explication',
                'confidence_threshold': 0.8
            },
            
            # === TYPES D'ASSURANCE ===
            {
                'category': 'Types d\'assurance',
                'question': 'Quelles assurances puis-je souscrire ?',
                'answer': 'Oh là là, on a plein de super produits pour vous ! 🚗✈️🏠🏍️ Vous pouvez souscrire à :\n\n🚗 Votre assurance automobile personnelle pour rouler tranquille\n✈️ Votre assurance voyage pour ne jamais être seul à l\'étranger (ça c\'est rassurant !)\n🏍️ Votre assurance moto pour vos déplacements quotidiens\n🏠 Votre assurance habitation que vous soyez locataire ou propriétaire !\n\nEt ce n\'est qu\'un début, plein d\'autres produits arrivent très prochainement ! 🎉',
                'keywords': 'assurance, souscrire, automobile, voyage, moto, habitation, produits, types, quelles assurances',
                'confidence_threshold': 0.7
            },
            {
                'category': 'Assurance automobile',
                'question': 'Parlez-moi de l\'assurance auto',
                'answer': 'L\'assurance automobile, c\'est notre spécialité ! 🚗💨 C\'est parfait pour couvrir votre voiture personnelle et rouler l\'esprit tranquille. Que ce soit pour les petits accrochages ou les gros pépins, on est là pour vous ! En plus, vous pouvez souscrire directement depuis l\'app en quelques minutes. Pratique, non ? 😎',
                'keywords': 'assurance automobile, auto, voiture, véhicule, rouler',
                'confidence_threshold': 0.7
            },
            {
                'category': 'Assurance voyage',
                'question': 'L\'assurance voyage, ça couvre quoi ?',
                'answer': 'L\'assurance voyage, c\'est votre meilleur compagnon à l\'étranger ! ✈️🌍 Ça vous évite d\'être seul face aux galères quand vous voyagez. Problème de santé, bagages perdus, annulation de vol... On est là pour vous accompagner ! Parce que voyager, ça doit rester un plaisir, pas un stress ! 😌✨',
                'keywords': 'assurance voyage, voyager, étranger, bagages, santé voyage',
                'confidence_threshold': 0.7
            },
            {
                'category': 'Assurance moto',
                'question': 'Et pour ma moto ?',
                'answer': 'Ah, la moto ! 🏍️💨 Notre assurance moto, c\'est exactement ce qu\'il vous faut pour couvrir tous vos déplacements quotidiens ! Que vous alliez au boulot, faire vos courses ou juste vous balader, on assure vos arrières ! Et comme pour l\'auto, tout se fait facilement via l\'app ! 😎',
                'keywords': 'assurance moto, moto, deux roues, scooter, déplacements',
                'confidence_threshold': 0.7
            },
            {
                'category': 'Assurance habitation',
                'question': 'Je veux assurer mon logement',
                'answer': 'Excellente idée ! 🏠💕 Notre assurance habitation s\'adapte parfaitement à votre situation : que vous soyez locataire ou propriétaire, on a ce qu\'il faut ! Vol, dégât des eaux, incendie... Votre petit cocon sera protégé ! Parce qu\'on sait à quel point c\'est important, chez soi ! 🛡️✨',
                'keywords': 'assurance habitation, logement, maison, appartement, locataire, propriétaire',
                'confidence_threshold': 0.7
            },
            
            # === PAIEMENT ===
            {
                'category': 'Moyens de paiement',
                'question': 'Comment payer ? Quels moyens de paiement ?',
                'answer': 'Pour le paiement, c\'est super facile ! 💳📱 Vous pouvez payer par Mobile Money (MTN et Moov) en juste deux clics - c\'est vraiment pratique ! Vous avez aussi la possibilité d\'utiliser votre carte de crédit si vous en avez une. Et devinez quoi ? On travaille déjà à mettre en place encore plus de moyens de paiement flexibles ! On veut que ce soit le plus simple possible pour vous ! 😊',
                'keywords': 'paiement, payer, mobile money, MTN, Moov, carte crédit, moyens, comment payer',
                'confidence_threshold': 0.8
            },
            {
                'category': 'Mobile Money',
                'question': 'Le Mobile Money, ça marche comment ?',
                'answer': 'Le Mobile Money, c\'est magique ! 📱✨ En deux clics, c\'est réglé ! Que vous soyez chez MTN ou Moov, pas de souci ! C\'est rapide, sécurisé, et vous n\'avez même pas besoin de sortir votre portefeuille ! La technologie au service de la simplicité, comme on aime ! 😄',
                'keywords': 'mobile money, MTN, Moov, deux clics, rapide',
                'confidence_threshold': 0.7
            },
            
            # === PROCESSUS DE SOUSCRIPTION ===
            {
                'category': 'Comment souscrire',
                'question': 'Comment souscrire à une assurance ?',
                'answer': 'Ah, c\'est vraiment simple ! 📱✨ Voilà comment ça marche :\n\n1️⃣ Vous allez sur l\'accueil de votre app\n2️⃣ Vous choisissez l\'assurance qui vous intéresse\n3️⃣ Vous lisez le descriptif avec tous les avantages (pas de blabla compliqué !)\n4️⃣ Vous faites votre devis en répondant à quelques questions - ça prend quelques minutes max !\n5️⃣ Clic sur SOUSCRIRE une fois votre devis prêt\n6️⃣ On vous demande quelques infos supplémentaires\n7️⃣ Vous payez via Mobile Money ou carte\n8️⃣ Et hop ! Vos documents s\'affichent, vous les téléchargez ! 🎉\n\nSimple comme bonjour !',
                'keywords': 'souscrire, comment, étapes, processus, devis, formulaire, comment faire',
                'confidence_threshold': 0.7
            },
            {
                'category': 'Devis',
                'question': 'Comment ça marche le devis ?',
                'answer': 'Le devis, c\'est votre estimation personnalisée ! 📊✨ Vous répondez à quelques questions simples sur ce que vous voulez assurer, et hop ! On vous calcule un prix sur mesure ! Pas de surprise, pas de frais cachés, juste un tarif honnête adapté à VOS besoins ! Et ça prend vraiment que quelques minutes ! ⏱️😊',
                'keywords': 'devis, estimation, prix, tarif, personnalisé, calcul',
                'confidence_threshold': 0.7
            },
            
            # === GESTION DES CONTRATS ===
            {
                'category': 'Modification contrat',
                'question': 'Puis-je modifier mon contrat ?',
                'answer': 'Bonne question ! 📝 Pour l\'instant, vous pouvez faire des prorogations de votre police d\'assurance automobile si vous aviez souscrit sur une durée inférieure à 12 mois. C\'est déjà pas mal ! Et bonne nouvelle : encore plus d\'options de modifications arrivent avec les prochaines mises à jour ! On améliore constamment l\'app pour vous ! 🚀',
                'keywords': 'modifier, modification, contrat, prorogation, changer, durée',
                'confidence_threshold': 0.7
            },
            {
                'category': 'Prorogation',
                'question': 'C\'est quoi une prorogation ?',
                'answer': 'Une prorogation ? C\'est tout simple ! 📅 Si vous avez pris votre assurance auto pour moins de 12 mois, vous pouvez l\'étendre ! Genre, vous aviez pris 6 mois et vous voulez continuer ? Pas de souci, on prolonge ! C\'est pratique quand on veut pas se tracasser à refaire toute la démarche ! 😌',
                'keywords': 'prorogation, prolonger, étendre, durée, continuer',
                'confidence_threshold': 0.7
            },
            
            # === ATTESTATIONS ===
            {
                'category': 'Validité attestations',
                'question': 'Mes e-attestations sont-elles valides ?',
                'answer': 'Absolument ! 📋✅ Vos e-attestations automobile et moto sont totalement valides et acceptées par la police en République du Bénin et dans toute la zone UMOA ! Les forces de l\'ordre sont bien au courant ! Vous pouvez même vérifier la validité en envoyant le code de vérification par SMS au numéro court indiqué sur l\'attestation. Donc roulez tranquille, vous êtes parfaitement en règle ! 🚗😎',
                'keywords': 'attestation, valide, validité, police, circulation, e-attestation, forces ordre',
                'confidence_threshold': 0.8
            },
            {
                'category': 'Contrôle police',
                'question': 'La police accepte vraiment les attestations électroniques ?',
                'answer': 'Oh que oui ! 👮‍♂️✅ Les forces de l\'ordre sont parfaitement informées et acceptent nos e-attestations ! C\'est officiel dans toute la République du Bénin et la zone UMOA ! Plus besoin de s\'inquiéter avec des papiers qui traînent dans la boîte à gants ! Votre téléphone suffit ! Moderne, non ? 📱😎',
                'keywords': 'police, contrôle, accepte, forces ordre, officiel, Bénin, UMOA',
                'confidence_threshold': 0.7
            },
            
            # === SINISTRES ===
            {
                'category': 'Déclaration sinistre',
                'question': 'Comment déclarer un sinistre ?',
                'answer': 'Oh, c\'est vraiment simple ! 📋💨 Allez dans votre compte, cliquez sur le bouton (+), choisissez la police d\'assurance concernée, remplissez le petit formulaire et soumettez ! Simple comme bonjour, non ? 😊 On reçoit automatiquement votre requête et on la traite rapidement ! Vous recevrez des notifications au fur et à mesure pour suivre l\'avancement de votre dossier. Pas de stress !',
                'keywords': 'sinistre, déclarer, déclaration, formulaire, dossier, accident',
                'confidence_threshold': 0.8
            },
            {
                'category': 'Suivi sinistre',
                'question': 'Comment suivre mon dossier de sinistre ?',
                'answer': 'Super question ! 📱🔍 Une fois votre sinistre déclaré, vous recevrez des notifications push directement sur votre téléphone ! Comme ça, vous savez toujours où en est votre dossier ! Plus besoin d\'appeler pour demander des nouvelles, tout est transparent ! On vous tient au courant de chaque étape ! C\'est ça, le service moderne ! ✨',
                'keywords': 'suivi, suivre, dossier, sinistre, notifications, avancement, étapes',
                'confidence_threshold': 0.7
            },
            
            # === REMBOURSEMENT ===
            {
                'category': 'Remboursement',
                'question': 'Comment ça marche le remboursement ?',
                'answer': 'Alors, voici comment ça se passe ! 💰 Une fois votre dossier traité, on vous fait une proposition financière claire ! Si elle vous convient (et on espère que oui ! 😊), vous nous indiquez comment vous voulez être remboursé : en espèce, via Mobile Money ou par virement. Selon votre choix, on vous demande juste les infos nécessaires. Simple et efficace ! 👍',
                'keywords': 'remboursement, remboursé, proposition, espèce, mobile money, virement, comment',
                'confidence_threshold': 0.7
            },
            {
                'category': 'Délai remboursement',
                'question': 'Ça prend combien de temps pour être remboursé ?',
                'answer': 'On fait tout pour que ce soit rapide ! ⚡ Une fois qu\'on a toutes les pièces du dossier et que vous avez accepté notre proposition, ça va vite ! Selon le mode de remboursement choisi (Mobile Money, virement, espèces), ça peut aller de quelques heures à quelques jours. On sait que vous êtes pressés de récupérer vos sous ! 😄💸',
                'keywords': 'délai, temps, combien, rapide, remboursement, durée',
                'confidence_threshold': 0.6
            },
            
            # === SOUSCRIPTION EN AGENCE ===
            {
                'category': 'Sinistre souscription agence',
                'question': 'J\'ai souscrit en agence, puis-je déclarer un sinistre sur l\'app ?',
                'answer': 'Ah, excellente question ! 🤔 Pour le moment, les déclarations de sinistres sur l\'app ne sont disponibles que pour les polices souscrites via l\'application elle-même. Mais ne vous inquiétez pas ! Nos équipes travaillent dur pour rendre les déclarations disponibles pour TOUS les clients de la compagnie, peu importe où vous avez souscrit ! Ça arrive bientôt ! 🚀',
                'keywords': 'agence, souscrit en agence, sinistre, déclaration, police, tous clients',
                'confidence_threshold': 0.7
            },
            
            # === CONTACT ET ASSISTANCE ===
            {
                'category': 'Contact assistance',
                'question': 'Comment contacter l\'assistance ?',
                'answer': 'On est là pour vous ! 🤝 Plusieurs moyens de nous joindre :\n\n📧 Par email : afg.iard@afgassurance.bj\n📞 Appelez-nous au +229 01 63 63 28 28\n📞 Ou au +229 01 21 31 51 48\n\nEt bien sûr, je suis là aussi pour vous aider directement ! N\'hésitez pas à me poser toutes vos questions ! 😊',
                'keywords': 'contact, assistance, aide, téléphone, email, joindre, appeler',
                'confidence_threshold': 0.8
            },
            {
                'category': 'Aide générale',
                'question': 'J\'ai besoin d\'aide',
                'answer': 'Bien sûr, je suis là pour ça ! 🤗 Dites-moi ce qui vous tracasse, on va régler ça ensemble ! Que ce soit pour comprendre comment marche l\'app, souscrire à une assurance, ou n\'importe quoi d\'autre, je suis votre homme... enfin, votre assistant ! 😄 Alors, qu\'est-ce qui vous préoccupe ?',
                'keywords': 'aide, besoin aide, help, assistance, problème, question',
                'confidence_threshold': 0.6
            },
            
            # === ÉMOTIONS ET SITUATIONS ===
            {
                'category': 'Frustration',
                'question': 'Je suis frustré, rien ne marche !',
                'answer': 'Ohlala, je comprends votre frustration ! 😔 C\'est vraiment embêtant quand les choses ne marchent pas comme on veut... Bon, on va respirer un coup et on va régler ça ensemble, d\'accord ? 💪 Dites-moi exactement ce qui coince, et on va trouver une solution ! Je suis là pour vous accompagner ! 🤝',
                'keywords': 'frustré, énervé, agacé, rien ne marche, problème, bug',
                'confidence_threshold': 0.5
            },
            {
                'category': 'Compliments',
                'question': 'Vous êtes super !',
                'answer': 'Awww, merci beaucoup ! 🥰 Ça me fait vraiment plaisir ! C\'est exactement pour ça que je suis là - pour vous rendre service avec le sourire ! Votre satisfaction, c\'est ma récompense ! Y a-t-il autre chose que je puisse faire pour vous ? 😊✨',
                'keywords': 'super, génial, excellent, bravo, fantastique, impressionnant, merci',
                'confidence_threshold': 0.8
            },
            {
                'category': 'Confusion',
                'question': 'Je ne comprends pas, c\'est compliqué',
                'answer': 'Ah non non, on va pas laisser les choses compliquées ! 😅 Vous savez quoi ? On va reprendre depuis le début, tranquillement ! Pas de stress ! Dites-moi exactement ce qui vous pose problème, et je vais vous expliquer ça de manière super simple ! C\'est mon boulot de rendre tout facile ! 🤗',
                'keywords': 'comprends pas, compliqué, difficile, confus, perdu, pas clair',
                'confidence_threshold': 0.5
            },
            
            # === REMERCIEMENTS ET AU REVOIR ===
            {
                'category': 'Remerciements',
                'question': 'Merci beaucoup pour votre aide !',
                'answer': 'Mais de rien, ça me fait plaisir ! 😊 C\'était un vrai plaisir de vous aider ! N\'hésitez surtout pas à revenir si vous avez d\'autres questions - je suis toujours là ! Passez une excellente journée ! 🌟',
                'keywords': 'merci, thank you, remercie, merci beaucoup, reconnaissance',
                'confidence_threshold': 0.8
            },
            {
                'category': 'Au revoir',
                'question': 'Au revoir, à bientôt !',
                'answer': 'Au revoir ! 👋 J\'espère vraiment avoir pu vous aider ! À très bientôt sur OREMI by AFG ! Prenez soin de vous et passez une merveilleuse journée ! 😊✨',
                'keywords': 'au revoir, bye, à bientôt, tchao, goodbye, ciao',
                'confidence_threshold': 0.8
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
                f'🎉 Base de connaissances initialisée avec {created_count} nouvelles entrées'
            )
        )
        
        total_entries = KnowledgeBase.objects.count()
        self.stdout.write(
            self.style.SUCCESS(
                f'✅ Total d\'entrées dans la base de connaissances: {total_entries}'
            )
        )
