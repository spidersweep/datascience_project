from faker import Faker
import random
import uuid
import json
import time
from kafka import KafkaProducer
from kafka.errors import KafkaError

fake = Faker()

TOPIC = "pression_arterielle"
SLEEP_TIME = 5  # secondes entre chaque message

# Crée le producteur Kafka 
producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)
# Générer 5 patients fixes au début
patients = [str(uuid.uuid4()) for _ in range(5)]

def generate_observation(patient_id):
    """Génère une observation FHIR pour un patient donné."""
    timestamp = fake.date_time_between(start_date='-1d', end_date='now').isoformat()

    # 30% chance of anomaly
    if random.random() > 0.7:
        systolic = random.randint(141, 190)
        diastolic = random.randint(91, 130)
    else:
        systolic = random.randint(110, 130)
        diastolic = random.randint(70, 85)

    return {
        "resourceType": "Observation",
        "id": str(uuid.uuid4()),  # ID unique pour chaque observation
        "status": "final",
        "code": {
            "coding": [{"system": "http://loinc.org", "code": "85354-9", "display": "Blood pressure panel"}]
        },
        "subject": {"reference": f"Patient/{patient_id}"},
        "effectiveDateTime": timestamp,
        "component": [
            {
                "code": {"coding": [{"code": "8480-6", "display": "Systolic"}]},
                "valueQuantity": {"value": systolic, "unit": "mmHg"}
            },
            {
                "code": {"coding": [{"code": "8462-4", "display": "Diastolic"}]},
                "valueQuantity": {"value": diastolic, "unit": "mmHg"}
            }
        ]
    }

def send_message(data):
        """Envoie un message dans Kafka."""
    try:
        future = producer.send(TOPIC, data)
        record_metadata = future.get(timeout=10)  # Attendre l'accusé
        print(f"Message sent to {record_metadata.topic} partition {record_metadata.partition} offset {record_metadata.offset}")
    except KafkaError as e:
        print(f"Failed to send message: {e}")

def main():
    print("Starting blood pressure simulator.")
    try:
        while True:
        # Pour chaque patient, générer et envoyer une observation
             for patient_id in patients:
                observation = generate_observation(patient_id)
                send_message(observation)
            time.sleep(SLEEP_TIME)
    except KeyboardInterrupt:
        print("\nStopping simulator...")
    finally:
        producer.flush()
        producer.close()
        print("Kafka producer closed gracefully.")

if __name__ == "__main__":
    main()
