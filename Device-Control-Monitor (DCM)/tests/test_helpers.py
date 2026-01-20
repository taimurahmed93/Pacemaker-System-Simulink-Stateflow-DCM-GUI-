import pytest
import os
import json
import tkinter as tk
from unittest.mock import Mock, patch

from helper import storage, patient_helpers


# -------------------------------
# FIXTURES
# -------------------------------
@pytest.fixture
def temp_patient_file(tmp_path):
    """Create a temporary patients.json file for testing."""
    file = tmp_path / "patients.json"
    with open(file, "w") as f:
        json.dump({"patients": []}, f)
    return file


@pytest.fixture
def dashboard_mock():
    """Mock a dashboard object with minimal attributes for helper testing."""
    root = tk.Tk()
    mock = Mock()
    mock.patient_entries = {
        "ID": tk.Entry(root),
        "Name": tk.Entry(root),
        "Model": tk.Entry(root),
        "Serial": tk.Entry(root)
    }
    mock.param_entries = {
        "PVARP": tk.Entry(root),
        "VRP": tk.Entry(root)
    }
    mock.patient_var = tk.StringVar()
    mock.patients = []
    mock.current_mode = tk.StringVar(value="AOO")
    mock.update_mode_parameters = Mock()
    return mock


# -------------------------------
# TESTS FOR PATIENT HELPERS
# -------------------------------
def test_generate_unique_patient_id_empty(dashboard_mock):
    dashboard_mock.patients = []
    result = patient_helpers.generate_unique_patient_id(dashboard_mock)
    assert result == "P001"


def test_generate_unique_patient_id_increments(dashboard_mock):
    dashboard_mock.patients = [{"id": "P001"}, {"id": "P002"}]
    result = patient_helpers.generate_unique_patient_id(dashboard_mock)
    assert result == "P003"


def test_clear_fields_resets_entries(dashboard_mock):
    # Fill entries
    for e in dashboard_mock.patient_entries.values():
        e.insert(0, "test")

    patient_helpers.clear_fields(dashboard_mock)

    # Check cleared name/model fields
    assert dashboard_mock.patient_entries["Name"].get() == ""
    assert dashboard_mock.patient_entries["Model"].get() == ""
    assert dashboard_mock.patient_var.get() == "New Patient"
    dashboard_mock.update_mode_parameters.assert_called_once()


def test_populate_patient_fields_sets_entries():
    root = tk.Tk()
    entries = {
        "ID": tk.Entry(root),
        "Name": tk.Entry(root)
    }
    patient = {"id": "P010", "name": "John"}
    patient_helpers.populate_patient_fields(entries, patient)

    assert entries["ID"].get() == "P010"
    assert entries["Name"].get() == "John"
    assert entries["ID"].cget("state") == "disabled"


# -------------------------------
# TESTS FOR STORAGE HELPERS
# -------------------------------
def test_load_json_creates_file(tmp_path):
    file = tmp_path / "missing.json"
    default_data = {"patients": []}
    result = storage.load_json(file, default_data)
    assert os.path.exists(file)
    assert result == default_data


def test_save_json_and_load_json(tmp_path):
    file = tmp_path / "data.json"
    data = {"patients": [{"id": "P001"}]}
    storage.save_json(file, data)
    result = storage.load_json(file, {"patients": []})
    assert result == data


def test_save_and_load_all_patients(temp_patient_file, monkeypatch):
    monkeypatch.setattr(storage, "PATIENTS_FILE", temp_patient_file)
    patient = {"id": "P001", "name": "Alice"}
    storage.save_patient_to_file(patient)
    patients = storage.load_all_patients()
    assert any(p["id"] == "P001" for p in patients)


def test_delete_patient(temp_patient_file, monkeypatch):
    monkeypatch.setattr(storage, "PATIENTS_FILE", temp_patient_file)
    # Add 2 patients
    storage.save_patient_to_file({"id": "P001", "name": "A"})
    storage.save_patient_to_file({"id": "P002", "name": "B"})
    storage.delete_patient("P001")
    patients = storage.load_all_patients()
    assert len(patients) == 1
    assert patients[0]["id"] == "P002"
