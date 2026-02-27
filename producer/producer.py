from faker import Faker
import random
import uuid
import json
import time
from kafka import KafkaProducer
from kafka.errors import KafkaError

fake = Faker()

TOPIC = "pression_arterielle"
SLEEP_TIME = 5  # seconds between messages

# Create Kafka producer
producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

def generate_patient():
    patient_id = str(uuid.uuid4())
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
        "id": patient_id,
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
    try:
        future = producer.send(TOPIC, data)
        record_metadata = future.get(timeout=10)  # Wait for ack
        print(f"Message sent to {record_metadata.topic} partition {record_metadata.partition} offset {record_metadata.offset}")
    except KafkaError as e:
        print(f"Failed to send message: {e}")

def main():
    print("Starting blood pressure simulator. Press Ctrl+C to stop.")
    try:
        while True:
            data = generate_patient()
            send_message(data)
            time.sleep(SLEEP_TIME)
    except KeyboardInterrupt:
        print("\nStopping simulator...")
    finally:
        producer.flush()
        producer.close()
        print("Kafka producer closed gracefully.")

if __name__ == "__main__":
    main()