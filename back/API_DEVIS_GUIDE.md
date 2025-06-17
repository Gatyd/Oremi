# API Devis - Guide d'utilisation

## Endpoints disponibles

### 1. Créer un devis
**POST** `/api/devis/`

#### Exemple pour une assurance auto :
```json
{
  "client": {
    "NPI": "123456789",
    "first_name": "Jean",
    "last_name": "Dupont",
    "email": "jean.dupont@email.com",
    "phone_number": "0123456789"
  },
  "type_assurance": "auto",
  "montant_total": 850.00,
  "duree_couverture": 12,
  "assurance_auto": {
    "zone_residence": "Paris",
    "adresse": "123 Rue de la Paix, 75001 Paris",
    "date_obtention_permis": "2010-05-15",
    "categorie_socio_professionnelle": "Cadre",
    "immatriculation": "AB-123-CD",
    "marque": "Renault",
    "modele": "Clio",
    "puissance_fiscale": 5.0,
    "numero_chassis": "VF1XXXXXXXXXX1234",
    "date_mise_circulation": "2020-03-10",
    "places_assises": 5,
    "carburation": "essence",
    "valeur_achat": 18000.00,
    "valeur_venale": 15000.00
  }
}
```

#### Exemple pour une assurance moto :
```json
{
  "client": {
    "NPI": "987654321",
    "first_name": "Marie",
    "last_name": "Martin",
    "email": "marie.martin@email.com",
    "phone_number": "0987654321"
  },
  "type_assurance": "moto",
  "montant_total": 650.00,
  "duree_couverture": 12,
  "assurance_moto": {
    "zone_residence": "Lyon",
    "adresse": "456 Avenue de la République, 69003 Lyon",
    "date_obtention_permis": "2015-08-20",
    "type_permis": "A2",
    "immatriculation": "EF-456-GH",
    "marque": "Yamaha",
    "modele": "MT-07",
    "cylindree": 689,
    "puissance": 55.0,
    "numero_chassis": "JYARN23EXXXXXX567",
    "date_mise_circulation": "2022-01-15",
    "valeur_achat": 8500.00,
    "valeur_venale": 7500.00,
    "usage": "promenade"
  }
}
```

#### Exemple pour une assurance habitation :
```json
{
  "client": {
    "NPI": "456789123",
    "first_name": "Pierre",
    "last_name": "Durand",
    "email": "pierre.durand@email.com",
    "phone_number": "0456789123"
  },
  "type_assurance": "habitation",
  "montant_total": 450.00,
  "duree_couverture": 12,
  "assurance_habitation": {
    "adresse": "789 Boulevard des Jardins, 13001 Marseille",
    "type_logement": "appartement",
    "surface_habitable": 75.5,
    "nombre_pieces": 4,
    "nombre_chambres": 2,
    "etage": 3,
    "annee_construction": 1995,
    "statut_occupant": "proprietaire",
    "systeme_securite": true,
    "alarme": true,
    "gardiennage": false,
    "valeur_mobilier": 25000.00,
    "valeur_immobilier": 280000.00
  }
}
```

#### Exemple pour une assurance santé :
```json
{
  "client": {
    "NPI": "789123456",
    "first_name": "Sophie",
    "last_name": "Moreau",
    "email": "sophie.moreau@email.com",
    "phone_number": "0789123456"
  },
  "type_assurance": "sante",
  "montant_total": 1200.00,
  "duree_couverture": 12,
  "assurance_sante": {
    "age": 35,
    "profession": "Professeur",
    "situation_familiale": "marie",
    "nombre_enfants": 2,
    "antecedents_medicaux": "Aucun antécédent particulier",
    "traitements_en_cours": "",
    "hospitalisation_recente": false,
    "formule": "confort",
    "dentaire": true,
    "optique": true,
    "medecine_douce": false,
    "chambre_particuliere": true
  }
}
```

#### Exemple pour une assurance voyage :
```json
{
  "client": {
    "NPI": "321654987",
    "first_name": "Lucas",
    "last_name": "Bernard",
    "email": "lucas.bernard@email.com",
    "phone_number": "0321654987"
  },
  "type_assurance": "voyage",
  "montant_total": 180.00,
  "duree_couverture": 1,
  "assurance_voyage": {
    "destination": "Japon",
    "zone_geographique": "monde_entier",
    "date_depart": "2025-08-15",
    "date_retour": "2025-08-30",
    "duree_sejour": 15,
    "motif_voyage": "tourisme",
    "nombre_voyageurs": 2,
    "age_voyageur_principal": 28,
    "voyageurs_seniors": false,
    "activites_sportives": true,
    "sports_extremes": false,
    "frais_medicaux_max": 150000.00,
    "rapatriement": true,
    "annulation": true,
    "bagages": true,
    "responsabilite_civile": true
  }
}
```

### 2. Lister tous les devis
**GET** `/api/devis/`

### 3. Récupérer un devis spécifique
**GET** `/api/devis/{id}/`

### 4. Récupérer les devis d'un client
**GET** `/api/devis/client/{NPI}/`

### 5. Statistiques des devis
**GET** `/api/devis/stats/`

## Gestion automatique des clients

Le système gère automatiquement les clients :
- Si un client existe avec le même NPI ou email, ses informations sont mises à jour
- Sinon, un nouveau client est créé
- Aucun doublon n'est créé

## Validation

- Seules les données correspondant au type d'assurance sont acceptées
- Les champs requis sont validés automatiquement
- Les formats de données (dates, emails, etc.) sont vérifiés
