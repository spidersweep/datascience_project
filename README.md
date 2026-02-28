# "Real-Time Blood Pressure Monitoring with FHIR, Kafka, Elasticsearch & Kibana"

Ce projet implémente un pipeline de données Big Data conçu pour la surveillance en temps réel de la pression artérielle, tout en constituant une simulation académique d’un système de monitoring. Les données de pression artérielle sont entièrement générées de manière synthétique à l’aide de scripts Python et ne proviennent d’aucun dispositif médical réel. L’objectif est de démontrer la capacité du pipeline, basé sur le standard FHIR, à traiter, filtrer et visualiser en continu des flux de données cliniques simulées, afin d’identifier et d’analyser automatiquement les anomalies détectées.


## Architecture du système
Le pipeline repose sur une architecture "Event-Driven" optimisée pour la haute disponibilité et la scalabilité :

1. **Patient Data Producer (Python)** : Simule des capteurs médicaux connectés générant des flux de données au format FHIR (ID patient, timestamp, pressions systolique et diastolique).
2. **Message Broker (Apache Kafka)** : Assure le transport fiable et ordonné des flux de données.
3. **Smart Consumer (Python)** : Analyse le flux en temps réel et applique un filtrage sélectif : seules les anomalies (Systolique > 140 mmHg ou Diastolique > 90 mmHg) sont extraites pour indexation.
4. **Storage & Indexing (Elasticsearch)** : Utilisation d'un index dédié `bp_anomalies` pour stocker les dossiers critiques de manière optimisée.
5. **Clinical Dashboard (Kibana)** : Interface de visualisation pour l’analyse et la supervision des flux de données simulées.

## Structure du répertoire

L'organisation du projet suit une architecture modulaire pour séparer la génération, le traitement et la visualisation des données :

```text
 cardiac-monitoring-kafka
 ┣ 📂 producer
 ┃ ┗ producer.py      # Script de simulation des capteurs FHIR (Kafka Producer)
 ┣ 📂 consumer
 ┃ ┗ consumer.py      # Script de filtrage et d'indexation vers Elasticsearch
 ┣ 📂 kibana
 ┃ ┗ dashboard_export.ndjson  # Export des visualisations et du dashboard clinique
 ┣ 📂 docs
 ┃ ┗ kibana-dashboard.pdf # Dashboard Kibana : Triage et Détection d'Anomalies en Temps Réel
 ┃ Message_FHIR_Project.py
 ┣ docker-compose.yml         # Orchestration des services Kafka, Zookeeper et ELK
 ┣ requirements.txt           # Liste des dépendances Python (kafka-python, elasticsearch)
 ┣ .gitignore                 # Exclusion des fichiers temporaires et des caches Python
 ┗ README.md                  # Documentation principale du projet
```

## Dashboard de supervision médicale
L'interface Kibana offre une vue décisionnelle complète :
* **Indices de gravité (Gauges)** : Suivi en temps réel du pic de tension (Max) et de la moyenne du service pour une évaluation rapide du danger.
* **Analyse de tendance (Line Chart)** : Monitoring des cycles de pression artérielle et détection des pics temporels.
* **Typologie des risques (Pie Chart)** : Répartition qualitative des types d'hypertension détectés.
* **Tableau de priorisation des anomalies détectées(Table)** : Liste priorisée des 5 patients les plus critiques pour une intervention immédiate.

## Installation & utilisation

### Pré-requis
* Docker & Docker-Compose
* Python 3.x
* Bibliothèques : `kafka-python`, `elasticsearch`

### Lancement de l'infrastructure
```bash
docker-compose up -d
# Lancer le consommateur (détection d'anomalies)
python consumer/consumer.py

# Lancer le producteur (simulation des données patients)
python producer/producer.py
```

### Importer le Dashboard
Pour visualiser le dashboard clinique :
1. Allez dans **Stack Management** > **Saved Objects** sur votre instance Kibana.
2. Cliquez sur **Import** et sélectionnez le fichier `kibana/dashboard_monitoring.ndjson`.
3. Le dashboard complet, incluant les jauges de gravité et le registre de triage, sera automatiquement recréé.

Projet académique - 2026
