from rest_framework import serializers

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