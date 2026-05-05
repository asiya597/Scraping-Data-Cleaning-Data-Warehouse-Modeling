# AVITO Pipeline

Pipeline de données pour le traitement, le nettoyage et le chargement d’annonces immobilières dans un Data Warehouse orienté BI et Machine Learning.

## Objectif du projet

Ce projet a pour objectif de construire un pipeline de données simple et structuré permettant de :

- nettoyer les données immobilières collectées
- enrichir les données avec des variables dérivées utiles
- charger les données dans un Data Warehouse
- préparer les données pour l’analyse BI et le Machine Learning
- automatiser l’exécution du traitement

## Architecture générale

Le pipeline suit la logique suivante :

`clean -> warehouse -> validation`

Le Data Warehouse est organisé en deux schémas :

- `bi_schema` : destiné à l’analyse décisionnelle et à Power BI
- `ml_schema` : destiné à la préparation des données pour le Machine Learning

## Structure du projet

```text
AVITO_PIPELINE/
│
├── clean/
│   └── clean_data.py
├── docker/
│   └── docker-compose.yml
├── extract/
├── warehouse/
│   ├── create_warehouse.sql
│   └── load_warehouse.py
├── avito_data_clean.csv
├── clean_data.csv
├── pipeline.py
├── pipeline.log
├── README.md
└── .gitignore
1. Clean Layer
Le script clean/clean_data.py applique un nettoyage structuré des données :

suppression des doublons
gestion des valeurs manquantes
correction des types de données
standardisation des villes et quartiers
traitement simple des valeurs aberrantes
Cette étape génère un dataset propre et cohérent exporté dans le fichier :

clean_data.csv
2. Feature Engineering
Le projet crée des variables dérivées simples pour enrichir le dataset :

price_per_m2
estimated_age
city
district
Les transformations avancées de Machine Learning, telles que le scaling, l’encoding, la normalisation ou le SMOTE, ne sont pas réalisées dans cette étape. Elles sont prévues après extraction depuis la base de données.

3. Data Warehouse
À partir des données nettoyées, le projet construit deux structures de données.

BI Schema (bi_schema)
Le schéma BI suit un modèle dimensionnel en étoile et contient :

fact_listing
dim_time
dim_location
dim_characteristics
Ce schéma est conçu pour faciliter l’analyse et l’intégration avec Power BI.

ML Schema (ml_schema)
Le schéma ML contient une table unique :

listings_features
Cette table correspond à une One Big Table (OBT) contenant l’ensemble des variables utiles à une future phase de Machine Learning.

4. Validation des données
Le processus de chargement inclut plusieurs contrôles :

cohérence du nombre de lignes entre clean.cleaned_listings, bi_schema.fact_listing et ml_schema.listings_features
vérification des valeurs importantes manquantes
contrôle de l’intégrité des relations entre la table de faits et les dimensions
validation de la complétude des datasets BI et ML
Résultats obtenus
clean.cleaned_listings : 264 lignes
bi_schema.fact_listing : 264 lignes
ml_schema.listings_features : 264 lignes
valeurs importantes manquantes : 0
relations BI cassées : 0
5. Automatisation du pipeline
Le fichier pipeline.py permet d’automatiser l’exécution du pipeline.

Dans la version actuelle, il exécute les étapes suivantes :

nettoyage des données
chargement dans le warehouse
validation finale
Le pipeline inclut :

exécution séquentielle
génération de logs
mécanisme de retry simple
réexécution automatique facilitée
6. Docker et base de données
La base PostgreSQL est exécutée avec Docker Compose.

Le fichier docker/docker-compose.yml permet de lancer le service avec :

POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=avito_dw
Installation et exécution
1. Activer l’environnement virtuel
.\venv\Scripts\Activate.ps1
2. Générer les données nettoyées
python clean\clean_data.py
3. Lancer PostgreSQL avec Docker Compose
docker compose -f docker/docker-compose.yml up -d
4. Créer les schémas et les tables
Get-Content warehouse\create_warehouse.sql | docker exec -i fin_db psql -U postgres -d avito_dw
5. Charger les données dans le Data Warehouse
python warehouse\load_warehouse.py
6. Lancer le pipeline complet
python pipeline.py
Technologies utilisées
Python
Pandas
SQLAlchemy
PostgreSQL
Docker Compose
Remarques
Le schéma public correspond au schéma par défaut de PostgreSQL.
Les schémas utilisés dans le projet sont clean, bi_schema et ml_schema.
Le fichier pipeline.log est généré automatiquement pour enregistrer l’exécution du pipeline.
La zone staging n’est pas utilisée dans cette version finale, mais sa gestion est prévue dans le processus de chargement.
