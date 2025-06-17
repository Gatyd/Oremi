from rest_framework import serializers
from django.contrib.contenttypes.models import ContentType
from .models import (
    Client, Devis, AssuranceAuto, AssuranceMoto, 
    AssuranceHabitation, AssuranceSante, AssuranceVoyage
)

class CarteGriseResponseSerializer(serializers.Serializer):
    """Serializer pour documenter la réponse de l'API"""
    A = serializers.CharField(allow_null=True, help_text="Numéro d'immatriculation")
    B = serializers.CharField(allow_null=True, help_text="Date de première immatriculation")
    C_1 = serializers.CharField(allow_null=True, help_text="Titulaire du certificat")
    D_1 = serializers.CharField(allow_null=True, help_text="Marque")
    D_2 = serializers.CharField(allow_null=True, help_text="Type, variante, version")
    E = serializers.CharField(allow_null=True, help_text="Numéro d'identification du véhicule (VIN)")
    F_1 = serializers.CharField(allow_null=True, help_text="Masse en charge maximale techniquement admissible")
    G = serializers.CharField(allow_null=True, help_text="Masse en service")
    P_1 = serializers.CharField(allow_null=True, help_text="Cylindrée")
    P_2 = serializers.CharField(allow_null=True, help_text="Puissance nette maximale")
    Q = serializers.CharField(allow_null=True, help_text="Rapport puissance/masse")
    extraction_confidence = serializers.CharField(help_text="Niveau de confiance: low, medium, high")


# Serializers pour les différents types d'assurance
class AssuranceAutoSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssuranceAuto
        fields = '__all__'


class AssuranceMotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssuranceMoto
        fields = '__all__'


class AssuranceHabitationSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssuranceHabitation
        fields = '__all__'


class AssuranceSanteSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssuranceSante
        fields = '__all__'


class AssuranceVoyageSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssuranceVoyage
        fields = '__all__'


# Serializer pour les informations client dans la requête
class ClientDataSerializer(serializers.Serializer):
    NPI = serializers.CharField(max_length=20)
    first_name = serializers.CharField(max_length=100)
    last_name = serializers.CharField(max_length=100)
    email = serializers.EmailField()
    phone_number = serializers.CharField(max_length=20, required=False, allow_blank=True)


# Serializer pour afficher les informations client dans la réponse
class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = ['NPI', 'first_name', 'last_name', 'email', 'phone_number']


# Serializer pour créer un devis
class DevisCreateSerializer(serializers.Serializer):
    # Informations client
    client = ClientDataSerializer()
    
    # Informations du devis
    type_assurance = serializers.ChoiceField(choices=[
        ('auto', 'Auto'),
        ('moto', 'Moto'),
        ('habitation', 'Habitation'),
        ('sante', 'Santé'),
        ('voyage', 'Voyage')
    ])
    montant_total = serializers.DecimalField(max_digits=10, decimal_places=2)
    duree_couverture = serializers.IntegerField()
    
    # Données spécifiques à chaque type d'assurance
    assurance_auto = AssuranceAutoSerializer(required=False)
    assurance_moto = AssuranceMotoSerializer(required=False)
    assurance_habitation = AssuranceHabitationSerializer(required=False)
    assurance_sante = AssuranceSanteSerializer(required=False)
    assurance_voyage = AssuranceVoyageSerializer(required=False)
    
    def validate(self, data):
        type_assurance = data.get('type_assurance')
        
        # Vérifier que les données correspondantes au type d'assurance sont fournies
        assurance_fields = {
            'auto': 'assurance_auto',
            'moto': 'assurance_moto',
            'habitation': 'assurance_habitation',
            'sante': 'assurance_sante',
            'voyage': 'assurance_voyage'
        }
        
        required_field = assurance_fields.get(type_assurance)
        if not data.get(required_field):
            raise serializers.ValidationError(
                f"Les données {required_field} sont requises pour le type d'assurance {type_assurance}"
            )
        
        # Vérifier qu'aucun autre champ d'assurance n'est fourni
        for field_name, field_key in assurance_fields.items():
            if field_name != type_assurance and data.get(field_key):
                raise serializers.ValidationError(
                    f"Les données {field_key} ne doivent pas être fournies pour le type d'assurance {type_assurance}"
                )
        
        return data


# Serializer pour afficher un devis avec toutes ses informations
class DevisDetailSerializer(serializers.ModelSerializer):
    client = ClientSerializer(read_only=True)
    bien_associe_data = serializers.SerializerMethodField()
    
    class Meta:
        model = Devis
        fields = [
            'id', 'client', 'date_creation', 'type_assurance', 
            'montant_total', 'duree_couverture', 'bien_associe_data'
        ]
    
    def get_bien_associe_data(self, obj):
        """Retourne les données du bien associé selon son type"""
        if not obj.bien_associe:
            return None
        
        serializers_map = {
            'assuranceauto': AssuranceAutoSerializer,
            'assurancemoto': AssuranceMotoSerializer,
            'assurancehabitation': AssuranceHabitationSerializer,
            'assurancesante': AssuranceSanteSerializer,
            'assurancevoyage': AssuranceVoyageSerializer,
        }
        
        model_name = obj.content_type.model
        serializer_class = serializers_map.get(model_name)
        
        if serializer_class:
            return serializer_class(obj.bien_associe).data
        return None


# Serializer pour lister les devis
class DevisListSerializer(serializers.ModelSerializer):
    client = ClientSerializer(read_only=True)
    
    class Meta:
        model = Devis
        fields = [
            'id', 'client', 'date_creation', 'type_assurance', 
            'montant_total', 'duree_couverture'
        ]