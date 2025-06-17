from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

class Client(models.Model):
    NPI = models.CharField(max_length=20, unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)

class DevisChoice(models.TextChoices):
    AUTO = "auto", "Auto"
    MOTO = "moto", "Moto"
    HABITATION = "habitation", "Habitation"
    SANTE = "sante", "Santé"
    VOYAGE = "voyage", "Voyage"

class Devis(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    date_creation = models.DateTimeField(auto_now_add=True)
    type_assurance = models.CharField(max_length=50, choices=DevisChoice.choices)
    montant_total = models.DecimalField(max_digits=10, decimal_places=2)
    duree_couverture = models.IntegerField(help_text="Durée de la couverture en mois")
    # Lien générique vers le bien assuré
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    bien_associe = GenericForeignKey("content_type", "object_id")

class AssuranceAuto(models.Model):
    # Propriétaire du véhicule
    zone_residence = models.CharField(max_length=100)
    adresse = models.CharField(max_length=255)
    date_obtention_permis = models.DateField()
    categorie_socio_professionnelle = models.CharField(max_length=100)
    # Informations sur le véhicule
    immatriculation = models.CharField(max_length=20)
    marque = models.CharField(max_length=50)
    modele = models.CharField(max_length=50)
    puissance_fiscale = models.DecimalField(max_digits=5, decimal_places=2)
    numero_chassis = models.CharField(max_length=50, unique=True)
    date_mise_circulation = models.DateField()
    places_assises = models.IntegerField(help_text="Nombre de places assises")
    carburation = models.CharField(max_length=20, choices=[
        ("essence", "Essence"),
        ("diesel", "Diesel"),
        ("electrique", "Électrique"),
        ("hybride", "Hybride")
    ])
    valeur_achat = models.DecimalField(max_digits=10, decimal_places=2, help_text="Valeur d'achat du véhicule")
    valeur_venale = models.DecimalField(max_digits=10, decimal_places=2, help_text="Valeur vénale du véhicule")


class AssuranceMoto(models.Model):
    # Propriétaire de la moto
    zone_residence = models.CharField(max_length=100)
    adresse = models.CharField(max_length=255)
    date_obtention_permis = models.DateField()
    type_permis = models.CharField(max_length=10, choices=[
        ("A1", "A1"),
        ("A2", "A2"), 
        ("A", "A")
    ])
    # Informations sur la moto
    immatriculation = models.CharField(max_length=20)
    marque = models.CharField(max_length=50)
    modele = models.CharField(max_length=50)
    cylindree = models.IntegerField(help_text="Cylindrée en cm³")
    puissance = models.DecimalField(max_digits=5, decimal_places=2, help_text="Puissance en kW")
    numero_chassis = models.CharField(max_length=50, unique=True)
    date_mise_circulation = models.DateField()
    valeur_achat = models.DecimalField(max_digits=10, decimal_places=2)
    valeur_venale = models.DecimalField(max_digits=10, decimal_places=2)
    usage = models.CharField(max_length=50, choices=[
        ("promenade", "Promenade"),
        ("travail", "Travail"),
        ("sport", "Sport")
    ])


class AssuranceHabitation(models.Model):
    # Informations sur le logement
    adresse = models.CharField(max_length=255)
    type_logement = models.CharField(max_length=50, choices=[
        ("appartement", "Appartement"),
        ("maison", "Maison"),
        ("studio", "Studio"),
        ("villa", "Villa")
    ])
    surface_habitable = models.DecimalField(max_digits=6, decimal_places=2, help_text="Surface en m²")
    nombre_pieces = models.IntegerField()
    nombre_chambres = models.IntegerField()
    etage = models.IntegerField(null=True, blank=True)
    annee_construction = models.IntegerField()
    
    # Statut occupant
    statut_occupant = models.CharField(max_length=50, choices=[
        ("proprietaire", "Propriétaire"),
        ("locataire", "Locataire"),
        ("usufruitier", "Usufruitier")
    ])
    
    # Équipements et sécurité
    systeme_securite = models.BooleanField(default=False)
    alarme = models.BooleanField(default=False)
    gardiennage = models.BooleanField(default=False)
    
    # Valeurs
    valeur_mobilier = models.DecimalField(max_digits=10, decimal_places=2)
    valeur_immobilier = models.DecimalField(max_digits=12, decimal_places=2)


class AssuranceSante(models.Model):
    # Informations sur l'assuré
    age = models.IntegerField()
    profession = models.CharField(max_length=100)
    situation_familiale = models.CharField(max_length=50, choices=[
        ("celibataire", "Célibataire"),
        ("marie", "Marié(e)"),
        ("pacs", "Pacsé(e)"),
        ("divorce", "Divorcé(e)"),
        ("veuf", "Veuf/Veuve")
    ])
    nombre_enfants = models.IntegerField(default=0)
    
    # Antécédents médicaux
    antecedents_medicaux = models.TextField(blank=True, null=True)
    traitements_en_cours = models.TextField(blank=True, null=True)
    hospitalisation_recente = models.BooleanField(default=False)
    
    # Formule choisie
    formule = models.CharField(max_length=50, choices=[
        ("essentielle", "Essentielle"),
        ("confort", "Confort"),
        ("premium", "Premium")
    ])
    
    # Options
    dentaire = models.BooleanField(default=False)
    optique = models.BooleanField(default=False)
    medecine_douce = models.BooleanField(default=False)
    chambre_particuliere = models.BooleanField(default=False)


class AssuranceVoyage(models.Model):
    # Détails du voyage
    destination = models.CharField(max_length=100)
    zone_geographique = models.CharField(max_length=50, choices=[
        ("europe", "Europe"),
        ("monde_sans_usa", "Monde sans USA/Canada"),
        ("monde_entier", "Monde entier")
    ])
    date_depart = models.DateField()
    date_retour = models.DateField()
    duree_sejour = models.IntegerField(help_text="Durée en jours")
    
    # Type de voyage
    motif_voyage = models.CharField(max_length=50, choices=[
        ("tourisme", "Tourisme"),
        ("affaires", "Affaires"),
        ("etudes", "Études"),
        ("sport", "Sport"),
        ("visite_famille", "Visite famille")
    ])
    
    # Voyageurs
    nombre_voyageurs = models.IntegerField()
    age_voyageur_principal = models.IntegerField()
    voyageurs_seniors = models.BooleanField(default=False, help_text="Voyageurs de plus de 65 ans")
    
    # Activités et risques
    activites_sportives = models.BooleanField(default=False)
    sports_extremes = models.BooleanField(default=False)
    
    # Couvertures
    frais_medicaux_max = models.DecimalField(max_digits=10, decimal_places=2, default=100000)
    rapatriement = models.BooleanField(default=True)
    annulation = models.BooleanField(default=False)
    bagages = models.BooleanField(default=False)
    responsabilite_civile = models.BooleanField(default=True)

