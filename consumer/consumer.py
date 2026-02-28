"""
Script Consumer / module de tri pour le projet

Ce que fait ce script :
- Lit les messages FHIR (Observation) envoyés dans Kafka
- Extrait les valeurs de pression artérielle systolique et diastolique
- Applique les règles médicales :
    systolique > 140 ou < 90  => anomalie
    diastolique > 90 ou < 60 => anomalie
- Si la mesure est NORMALE  -> ajoute le JSON dans un fichier d’archive local (format JSON Lines)
- Si la mesure est ANORMALE -> envoie un document simplifié vers Elasticsearch
  (pour visualisation dans Kibana)

Exécution (après installation des dépendances) :
    pip install kafka-python requests

Puis lancement :
    python consumer.py

"""

import json
import os
import time
from datetime import datetime, timezone

import requests
from kafka import KafkaConsumer


# --- Config (keep localhost to match your teammate's instruction) ---
KAFKA_BOOTSTRAP = os.getenv("KAFKA_BOOTSTRAP", "localhost:9092")
TOPIC = os.getenv("KAFKA_TOPIC", "pression_arterielle")  # must match producer.py
GROUP_ID = os.getenv("KAFKA_GROUP_ID", "bp-consumer-group")

# Elasticsearch (your teammate will run it on their machine)
ELASTIC_URL = os.getenv("ELASTIC_URL", "http://localhost:9200")
ELASTIC_INDEX = os.getenv("ELASTIC_INDEX", "bp_anomalies")

# Local archive for normal observations (JSON Lines = 1 JSON per line)
NORMAL_ARCHIVE_PATH = os.getenv("NORMAL_ARCHIVE_PATH", "normal_observations.jsonl")


def extract_bp_values(fhir_obs: dict) -> tuple[float | None, float | None]:
    """
    Extraction des valeurs de pression artérielle systolique et diastolique à partir d’une structure FHIR de type Observation, comme celle envoyée par producer.py.
Emplacement attendu :
- fhir_obs["component"] est une liste contenant :
le code 8480-6 (pression systolique)
le code 8462-4 (pression diastolique)
chaque composant contient la valeur dans valueQuantity.value

Retourne :
(systolique, diastolique)
ou (None, None) si les valeurs sont absentes.
    """
    systolic = None
    diastolic = None

    components = fhir_obs.get("component", [])
    for c in components:
        coding = (((c.get("code") or {}).get("coding")) or [])
        code = (coding[0].get("code") if coding else None)

        vq = c.get("valueQuantity") or {}
        val = vq.get("value")

        if code == "8480-6":  # systolic
            systolic = val
        elif code == "8462-4":  # diastolic
            diastolic = val

    return systolic, diastolic


def classify_bp(systolic: float, diastolic: float) -> tuple[bool, list[str]]:
    """
    Returns (is_anomaly, anomaly_types)
    """
    anomaly_types: list[str] = []

    if systolic > 140:
        anomaly_types.append("hypertension_systolic")
    if systolic < 90:
        anomaly_types.append("hypotension_systolic")
    if diastolic > 90:
        anomaly_types.append("hypertension_diastolic")
    if diastolic < 60:
        anomaly_types.append("hypotension_diastolic")

    return (len(anomaly_types) > 0), anomaly_types


def archive_normal(fhir_obs: dict) -> None:
    """
    Append to local JSONL file. This is the 'archive locally' requirement.
    """
    with open(NORMAL_ARCHIVE_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(fhir_obs, ensure_ascii=False))
        f.write("\n")


def push_to_elasticsearch(doc: dict) -> None:
    """
    Index anomaly document to Elasticsearch.
    Uses the Index API: POST /{index}/_doc
    """
    url = f"{ELASTIC_URL.rstrip('/')}/{ELASTIC_INDEX}/_doc"
    r = requests.post(url, json=doc, timeout=10)
    # Raise if not 2xx so you see problems quickly
    r.raise_for_status()


def build_anomaly_doc(fhir_obs: dict, systolic: float, diastolic: float, anomaly_types: list[str]) -> dict:
    """
    A simplified document for Kibana. Keeps key fields + anomaly metadata.
    """
    patient_ref = ((fhir_obs.get("subject") or {}).get("reference")) or ""
    observation_id = fhir_obs.get("id")

    effective_dt = fhir_obs.get("effectiveDateTime")
    # Kibana likes an ISO date field; if missing, use now
    if not effective_dt:
        effective_dt = datetime.now(timezone.utc).isoformat()

    return {
        "timestamp": effective_dt,
        "observation_id": observation_id,
        "patient_ref": patient_ref,
        "systolic_pressure": systolic,
        "diastolic_pressure": diastolic,
        "anomaly_type": anomaly_types,
        "raw_resourceType": fhir_obs.get("resourceType"),
        "ingested_at": datetime.now(timezone.utc).isoformat(),
    }


def main() -> None:
    print("Starting BP consumer (Membre 2). Ctrl+C to stop.")
    print(f"- Kafka: {KAFKA_BOOTSTRAP} | topic: {TOPIC} | group: {GROUP_ID}")
    print(f"- Elasticsearch: {ELASTIC_URL} | index: {ELASTIC_INDEX}")
    print(f"- Normal archive file: {NORMAL_ARCHIVE_PATH}")

    consumer = KafkaConsumer(
        TOPIC,
        bootstrap_servers=KAFKA_BOOTSTRAP,
        group_id=GROUP_ID,
        auto_offset_reset="latest",  # start from newest if no committed offset
        enable_auto_commit=True,
        value_deserializer=lambda m: json.loads(m.decode("utf-8")),
    )

    try:
        for msg in consumer:
            fhir_obs = msg.value

            systolic, diastolic = extract_bp_values(fhir_obs)
            if systolic is None or diastolic is None:
                print(" Message ignored (missing systolic/diastolic):", fhir_obs.get("id"))
                continue

            is_anomaly, anomaly_types = classify_bp(float(systolic), float(diastolic))

            if not is_anomaly:
                archive_normal(fhir_obs)
                print(f" NORMAL  | sys/dia={systolic}/{diastolic} | saved to archive")
            else:
                doc = build_anomaly_doc(fhir_obs, float(systolic), float(diastolic), anomaly_types)
                try:
                    push_to_elasticsearch(doc)
                    print(f" ANOMALY | sys/dia={systolic}/{diastolic} | {anomaly_types} | sent to ES")
                except Exception as e:
                    # If ES isn't reachable locally (which is normal on your machine),
                    # you still want your code to keep running to validate logic.
                    print(f" ANOMALY | sys/dia={systolic}/{diastolic} | {anomaly_types} | ES push failed: {e}")

            # small sleep to keep logs readable (optional)
            time.sleep(0.1)

    except KeyboardInterrupt:
        print("\nStopping consumer...")
    finally:
        consumer.close()
        print("Kafka consumer closed gracefully.")


if __name__ == "__main__":
    main()
