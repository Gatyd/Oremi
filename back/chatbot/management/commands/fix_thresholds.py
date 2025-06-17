from django.core.management.base import BaseCommand
from chatbot.models import KnowledgeBase


class Command(BaseCommand):
    help = 'Corrige les seuils de confiance pour améliorer les correspondances'

    def handle(self, *args, **options):
        self.stdout.write('🔧 Correction des seuils de confiance...')
        
        # Réduire drastiquement tous les seuils de confiance
        updated_count = 0
        
        for entry in KnowledgeBase.objects.all():
            # Nouveau seuil beaucoup plus bas
            new_threshold = 0.2  # Au lieu de 0.7-0.8
            
            # Seuils spéciaux pour certaines catégories
            if 'salut' in entry.keywords.lower() or 'bonjour' in entry.keywords.lower():
                new_threshold = 0.1  # Très bas pour les salutations
            elif 'aide' in entry.keywords.lower() or 'help' in entry.keywords.lower():
                new_threshold = 0.15  # Bas pour l'aide
            elif 'merci' in entry.keywords.lower():
                new_threshold = 0.1  # Très bas pour les remerciements
            
            if entry.confidence_threshold != new_threshold:
                entry.confidence_threshold = new_threshold
                entry.save()
                updated_count += 1
                self.stdout.write(f'✅ {entry.question[:30]}... : {entry.confidence_threshold:.1f} -> {new_threshold:.1f}')
        
        self.stdout.write(
            self.style.SUCCESS(f'🎉 {updated_count} seuils mis à jour !')
        )
        
        # Afficher quelques statistiques
        total = KnowledgeBase.objects.count()
        low_threshold = KnowledgeBase.objects.filter(confidence_threshold__lte=0.2).count()
        
        self.stdout.write(f'📊 Total: {total} entrées')
        self.stdout.write(f'📊 Seuils bas (≤0.2): {low_threshold} entrées')
        
        # Test rapide
        self.stdout.write('\n🧪 Test rapide...')
        test_messages = ['bonjour', 'salut', 'aide', 'merci']
        
        from chatbot.services import KnowledgeBaseMatcher
        matcher = KnowledgeBaseMatcher()
        
        for msg in test_messages:
            match, score = matcher.find_best_match(msg)
            if match:
                self.stdout.write(f'✅ "{msg}" -> {match.question[:30]}... (score: {score:.3f})')
            else:
                self.stdout.write(f'❌ "{msg}" -> Aucune correspondance')
        
        self.stdout.write('\n🎯 Correction terminée !')
