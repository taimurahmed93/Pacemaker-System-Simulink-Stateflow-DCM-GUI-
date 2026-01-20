# STORAGE HELPERS
# place to read/write user data and parameter data

import json
import os


PATIENTS_FILE = os.path.join("data", "patients.json")

# helper function to load the user data from user.json 
def load_json(filepath, default_data):
    if not os.path.exists(filepath):
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, "w") as f:
            json.dump(default_data, f, indent=4)
    with open(filepath, "r") as f:
        return json.load(f)


# helper function that saves new user data to file
def save_json(filepath, data):

    with open(filepath, "w") as f:
        json.dump(data, f, indent=4)
        
        
# -----------------------------
# Load all patients from file
# -----------------------------
def load_all_patients():
    if not os.path.exists(PATIENTS_FILE):
        return []
    try:
        with open(PATIENTS_FILE, "r") as f:
            data = json.load(f)
            return data.get("patients", [])
    except:
        return []

# -----------------------------
# Load a patient by name
# -----------------------------
def load_patient_by_name(name):
    patients = load_all_patients()
    for p in patients:
        if p["name"] == name:
            return p
    return None

# -----------------------------
# Save or update a patient
# -----------------------------
def save_patient_to_file(patient):
    patients = load_all_patients()
    updated = False
    
    for i in range(len(patients)):
        if patients[i]["id"] == patient["id"]:
            patients[i] = patient
            updated = True
            break
        
    if not updated:
        patients.append(patient)

    with open(PATIENTS_FILE, "w") as f:
        json.dump({"patients": patients}, f, indent=4)

# -----------------------------
# Delete a patient by ID
# -----------------------------
def delete_patient(patient_id):
    # Load all patients
    patients = load_all_patients()
    updated_patients = []
    
    for patient in patients:
        # Keep only patients whose id does NOT match the one we want to delete
        if patient.get("id") != patient_id:
            updated_patients.append(patient)
    
    # Save the updated list back to the JSON file
    with open(PATIENTS_FILE, "w") as f:
        json.dump({"patients": updated_patients}, f, indent=4)

    print(f"Patient with ID {patient_id} has been deleted.")
