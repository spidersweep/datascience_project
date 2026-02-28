import uuid
from faker import Faker
import random
from datetime import datetime

fake = Faker()

def generate_fhir_observation(patient_id: str = None):
    """
    Génère une observation FHIR de tension artérielle (systolique/diastolique)
    conforme aux codes LOINC.
    """
    if patient_id is None:
        patient_id = str(uuid.uuid4())

    timestamp = datetime.now().isoformat()

    # 30% chance d'anomalie
    if random.random() > 0.7:
        systolic = random.randint(141, 190)
        diastolic = random.randint(91, 130)
    else:
        systolic = random.randint(110, 130)
        diastolic = random.randint(70, 85)

    fhir_obs = {
        "resourceType": "Observation",
        "id": str(uuid.uuid4()),
        "status": "final",
        "code": {
            "coding": [
                {
                    "system": "http://loinc.org",
                    "code": "85354-9",
                    "display": "Blood pressure panel"
                }
            ]
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

    return fhir_obs


# --- Exemple d'utilisation ---
if __name__ == "__main__":
    # Génère 5 patients fictifs
    for _ in range(5):
        obs = generate_fhir_observation()
        print(obs)