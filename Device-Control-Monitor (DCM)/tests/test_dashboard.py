import pytest
import tkinter as tk
from unittest import mock
from gui.dashboard import Dashboard

# -----------------------------
# Fixtures
# -----------------------------
@pytest.fixture
def mock_controller():
    ctrl = mock.MagicMock()
    ctrl.data = {"patients": []}
    ctrl.data_path = "mock_path.json"
    return ctrl

@pytest.fixture
def dashboard(mock_controller):
    # Create a real hidden Tk root
    root = tk.Tk()
    root.withdraw()  # hide the GUI
    dash = Dashboard(root, mock_controller)
    yield dash
    root.destroy()  # clean up after tests


# -----------------------------
# Patient loading test
# -----------------------------
def test_load_selected_patient(dashboard):
    patient_data = {"name": "John", "device": {"model": "X", "serial": "123"}}

    with mock.patch("helper.storage.load_patient_by_name", return_value=patient_data):
        with mock.patch("helper.patient_helpers.populate_patient_fields") as pop_mock:
            dashboard.load_selected_patient("John")
            pop_mock.assert_called_once_with(dashboard.patient_entries, patient_data)
            assert dashboard.patient == patient_data
            assert dashboard.patient_var.get() == "John"

# -----------------------------
# Mode parameter update test
# -----------------------------
def test_update_mode_parameters(dashboard):
    # Mock patient with device parameters
    dashboard.patient = {
        "device": {
            "model": "X100",
            "serial": "1234",
            "modes": {
                "AOO": {"parameters": {"lower_rate": 60, "upper_rate": 120}}
            }
        }
    }

    dashboard.current_mode.set("AOO")
    dashboard.update_mode_parameters()

    # Check that device fields are populated
    assert dashboard.param_entries["Model"].get() == "X100"
    assert dashboard.param_entries["Serial"].get() == "1234"

    # Check parameter fields are filled correctly
    for key, field_name in [("lower_rate", "Lower Rate"), ("upper_rate", "Upper Rate")]:
        if field_name in dashboard.param_entries:
            assert dashboard.param_entries[field_name].get() == str(dashboard.patient["device"]["modes"]["AOO"]["parameters"][key])

# -----------------------------
# Clear, Save, Remove patient tests
# -----------------------------
def test_clear_fields(dashboard):
    with mock.patch("helper.patient_helpers.clear_fields") as clear_mock:
        dashboard.clear_fields()
        clear_mock.assert_called_once_with(dashboard)

def test_save_patient(dashboard):
    with mock.patch("helper.patient_helpers.save_patient_from_dashboard") as save_mock:
        dashboard.save_patient()
        save_mock.assert_called_once_with(dashboard)

def test_remove_patient(dashboard):
    with mock.patch("helper.patient_helpers.remove_patient") as remove_mock:
        dashboard.remove_patient()
        remove_mock.assert_called_once_with(dashboard)

def test_build_serial_packet_AOO(dashboard):
    """
    Test that build_serial_packet() produces the correct 18-byte packet
    for a known set of input parameters in AOO mode.
    """
 
    # Force mode
    dashboard.current_mode.set("AOO")
    dashboard.update_mode_parameters()
 
    # Fill only allowed params for AOO
    dashboard.param_entries["Lower Rate Limit"].delete(0, "end")
    dashboard.param_entries["Lower Rate Limit"].insert(0, "60")
 
    dashboard.param_entries["Upper Rate Limit"].delete(0, "end")
    dashboard.param_entries["Upper Rate Limit"].insert(0, "120")
 
    dashboard.param_entries["Atrial Amplitude"].delete(0, "end")
    dashboard.param_entries["Atrial Amplitude"].insert(0, "3.5")  # scaled ×10
 
    dashboard.param_entries["Atrial Pulse Width"].delete(0, "end")
    dashboard.param_entries["Atrial Pulse Width"].insert(0, "100")  # raw
 
    # Activity threshold not used in AOO → set to Med (ignored)
    dashboard.activity_threshold_var.set("Med")
 
    # Build packet
    packet = dashboard.build_serial_packet()
    packet_list = list(packet)
 
    # -------------------------
    # Expected byte list (18 bytes)
    # -------------------------
    expected = [
        0x16,         # NEW: Byte 0
        0x55,         # NEW: Byte 1
        0,            # Byte 2 reserved
        1,            # Byte 3 → mode=AOO → 1
        60,           # Byte 4 → Lower Rate
        120,          # Byte 5 → Upper Rate
        0,            # Byte 6 → Max Sensor Rate (not allowed)
        35,           # Byte 7 → Atrial Amp (3.5×10)
        0,            # Byte 8 → Ventricular Amp
        100,          # Byte 9 → Atrial Pulse Width
        0,            # Byte 10 → Ventricular Pulse Width
        0,            # Byte 11 → Atrial Sensitivity
        0,            # Byte 12 → Ventricular Sensitivity
        0,            # Byte 13 → VRP
        0,            # Byte 14 → ARP
        0,            # Byte 15
        0,            # Byte 16
        0,            # Byte 17
    ]
 
    # -------------------------
    # Assertions
    # -------------------------
    assert len(packet_list) == 18, f"Packet should be 18 bytes, got {len(packet_list)}"
 
    assert packet_list == expected, (
        f"\nPacket mismatch:\nExpected: {expected}\nActual:   {packet_list}"
    )