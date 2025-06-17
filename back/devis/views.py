from django.shortcuts import render
from rest_framework import status, generics
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from .models import (
    Client, Devis, AssuranceAuto, AssuranceMoto, 
    AssuranceHabitation, AssuranceSante, AssuranceVoyage
)
from .serializers import (
    DevisCreateSerializer, DevisDetailSerializer, DevisListSerializer,
    AssuranceAutoSerializer, AssuranceMotoSerializer, AssuranceHabitationSerializer,
    AssuranceSanteSerializer, AssuranceVoyageSerializer
)


class DevisListCreateView(generics.ListCreateAPIView):
    """Vue pour lister et créer des devis"""
    queryset = Devis.objects.all().order_by('-date_creation')
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return DevisCreateSerializer
        return DevisListSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        with transaction.atomic():
            devis = self.perform_create(serializer.validated_data)
            
        # Retourner le devis créé avec toutes ses informations
        response_serializer = DevisDetailSerializer(devis)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
    
    def perform_create(self, validated_data):
        """Crée un devis avec gestion du client et du bien associé"""
        client_data = validated_data.pop('client')
        type_assurance = validated_data['type_assurance']
        
        # 1. Gérer le client (créer ou récupérer)
        client = self.get_or_create_client(client_data)
        
        # 2. Créer le bien associé selon le type d'assurance
        bien_associe = self.create_bien_associe(validated_data, type_assurance)
        
        # 3. Créer le devis
        content_type = ContentType.objects.get_for_model(bien_associe)
        devis = Devis.objects.create(
            client=client,
            type_assurance=type_assurance,
            montant_total=validated_data['montant_total'],
            duree_couverture=validated_data['duree_couverture'],
            content_type=content_type,
            object_id=bien_associe.id
        )
        
        return devis
    
    def get_or_create_client(self, client_data):
        """Récupère un client existant ou en crée un nouveau"""
        npi = client_data['NPI']
        email = client_data['email']
        
        # Chercher d'abord par NPI
        try:
            client = Client.objects.get(NPI=npi)
            # Mettre à jour les informations si nécessaire
            for field, value in client_data.items():
                setattr(client, field, value)
            client.save()
            return client
        except Client.DoesNotExist:
            pass
        
        # Chercher par email
        try:
            client = Client.objects.get(email=email)
            # Mettre à jour les informations si nécessaire
            for field, value in client_data.items():
                setattr(client, field, value)
            client.save()
            return client
        except Client.DoesNotExist:
            pass
        
        # Créer un nouveau client
        return Client.objects.create(**client_data)
    
    def create_bien_associe(self, validated_data, type_assurance):
        """Crée le bien associé selon le type d'assurance"""
        type_mapping = {
            'auto': ('assurance_auto', AssuranceAuto),
            'moto': ('assurance_moto', AssuranceMoto),
            'habitation': ('assurance_habitation', AssuranceHabitation),
            'sante': ('assurance_sante', AssuranceSante),
            'voyage': ('assurance_voyage', AssuranceVoyage),
        }
        
        field_name, model_class = type_mapping[type_assurance]
        bien_data = validated_data.pop(field_name)
        
        return model_class.objects.create(**bien_data)


class DevisDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Vue pour récupérer, modifier ou supprimer un devis"""
    queryset = Devis.objects.all()
    serializer_class = DevisDetailSerializer


class DevisByClientView(generics.ListAPIView):
    """Vue pour récupérer les devis d'un client par NPI"""
    serializer_class = DevisListSerializer
    
    def get_queryset(self):
        npi = self.kwargs['npi']
        return Devis.objects.filter(client__NPI=npi).order_by('-date_creation')


@api_view(['GET'])
def devis_stats(request):
    """Statistiques sur les devis"""
    from django.db.models import Count, Avg, Sum
    
    stats = {
        'total_devis': Devis.objects.count(),
        'devis_par_type': dict(
            Devis.objects.values('type_assurance').annotate(
                count=Count('id')
            ).values_list('type_assurance', 'count')
        ),
        'montant_moyen': Devis.objects.aggregate(
            Avg('montant_total')
        )['montant_total__avg'] or 0,
        'montant_total': Devis.objects.aggregate(
            Sum('montant_total')
        )['montant_total__sum'] or 0,
        'clients_uniques': Client.objects.count()
    }
    
    return Response(stats)
