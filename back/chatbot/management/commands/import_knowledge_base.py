import json
import os
from django.core.management.base import BaseCommand
from django.conf import settings
from chatbot.models import KnowledgeBase


class Command(BaseCommand):
    help = 'Importe la base de connaissances depuis un fichier JSON'

    def add_arguments(self, parser):
        parser.add_argument(
            '--file',
            type=str,
            default='chatbot/knowledge_base.json',
            help='Chemin vers le fichier JSON à importer'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Vide la base de connaissances avant l\'importation'
        )

    def handle(self, *args, **options):
        file_path = options['file']
        
        # Construire le chemin complet
        if not os.path.isabs(file_path):
            file_path = os.path.join(settings.BASE_DIR, file_path)
        
        if not os.path.exists(file_path):
            self.stdout.write(
                self.style.ERROR(f'Le fichier {file_path} n\'existe pas')
            )
            return
        
        # Vider la base si demandé
        if options['clear']:
            count = KnowledgeBase.objects.count()
            KnowledgeBase.objects.all().delete()
            self.stdout.write(
                self.style.WARNING(f'{count} entrées supprimées de la base de connaissances')
            )
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            knowledge_entries = data.get('knowledge_base', [])
            created_count = 0
            updated_count = 0
            
            for entry_data in knowledge_entries:
                # Vérifier si l'entrée existe déjà
                existing = KnowledgeBase.objects.filter(
                    question=entry_data['question']
                ).first()
                
                if existing:
                    # Mettre à jour l'entrée existante
                    for field, value in entry_data.items():
                        setattr(existing, field, value)
                    existing.save()
                    updated_count += 1
                else:
                    # Créer une nouvelle entrée
                    KnowledgeBase.objects.create(**entry_data)
                    created_count += 1
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Importation terminée: {created_count} entrées créées, {updated_count} mises à jour'
                )
            )
            
            # Afficher les métadonnées si disponibles
            metadata = data.get('metadata', {})
            if metadata:
                self.stdout.write('Métadonnées du fichier:')
                for key, value in metadata.items():
                    self.stdout.write(f'  {key}: {value}')
                    
        except json.JSONDecodeError as e:
            self.stdout.write(
                self.style.ERROR(f'Erreur de format JSON: {e}')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Erreur lors de l\'importation: {e}')
            )
