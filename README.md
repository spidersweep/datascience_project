# Real-Time Cardiac Monitoring Pipeline (Kafka & ELK)

Ce projet implémente un pipeline de données Big Data conçu pour la surveillance en temps réel de la pression artérielle. Il permet de filtrer les flux de données cliniques pour identifier et visualiser instantanément les cas d'urgence médicale.

## Architecture du Système
Le pipeline repose sur une architecture "Event-Driven" optimisée pour la haute disponibilité et la scalabilité :

1. **Patient Data Producer (Python)** : Simule des capteurs médicaux connectés générant des flux de données au format FHIR (ID patient, timestamp, pressions systolique et diastolique).
2. **Message Broker (Apache Kafka)** : Assure le transport fiable et ordonné des flux de données.
3. **Smart Consumer (Python)** : Analyse le flux en temps réel et applique un filtrage sélectif : seules les anomalies (Systolique > 140 mmHg ou Diastolique > 90 mmHg) sont extraites pour indexation.
4. **Storage & Indexing (Elasticsearch)** : Utilisation d'un index dédié `bp_anomalies` pour stocker les dossiers critiques de manière optimisée.
5. **Clinical Dashboard (Kibana)** : Interface de visualisation pour les professionnels de santé.

## 📂 Structure du Répertoire

L'organisation du projet suit une architecture modulaire pour séparer la génération, le traitement et la visualisation des données :

```text
📦 cardiac-monitoring-kafka
 ┣ 📂 producer
 ┃ ┗ 📜 patient_producer.py      # Script de simulation des capteurs FHIR (Kafka Producer)
 ┣ 📂 consumer
 ┃ ┗ 📜 anomaly_detector.py      # Script de filtrage et d'indexation vers Elasticsearch
 ┣ 📂 kibana
 ┃ ┗ 📜 dashboard_export.ndjson  # Export des visualisations et du dashboard clinique
 ┣ 📂 docs
 ┃ ┗ 📜 architecture_diagram.png # Schéma technique du pipeline de données
 ┣ 📜 docker-compose.yml         # Orchestration des services Kafka, Zookeeper et ELK
 ┣ 📜 requirements.txt           # Liste des dépendances Python (kafka-python, elasticsearch)
 ┣ 📜 .gitignore                 # Exclusion des fichiers temporaires et des caches Python
 ┗ 📜 README.md                  # Documentation principale du projet
```

## Dashboard de Supervision Médicale
L'interface Kibana offre une vue décisionnelle complète :
* **Indices de Gravité (Gauges)** : Suivi en temps réel du pic de tension (Max) et de la moyenne du service pour une évaluation rapide du danger.
* **Analyse de Tendance (Line Chart)** : Monitoring des cycles de pression artérielle et détection des pics temporels.
* **Typologie des Risques (Pie Chart)** : Répartition qualitative des types d'hypertension détectés.
* **Registre de Triage (Table)** : Liste priorisée des 5 patients les plus critiques pour une intervention immédiate.

## Installation & Utilisation

### Pré-requis
* Docker & Docker-Compose
* Python 3.x
* Bibliothèques : `kafka-python`, `elasticsearch`

### Lancement de l'infrastructure
```bash
docker-compose up -d
# Lancer le consommateur (détection d'anomalies)
python consumer/anomaly_detector.py

# Lancer le producteur (simulation des données patients)
python producer/patient_producer.py
```

Projet académique 2026

Projet académique - 2026
