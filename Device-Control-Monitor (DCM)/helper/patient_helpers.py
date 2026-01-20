# Patient Helper
import tkinter as tk
from tkinter import messagebox
from helper import storage, param_helpers
from helper.serial_comm import PacemakerSerial

# function used to generate a unique patient ID
def generate_unique_patient_id(dashboard):
    patients = dashboard.patients
    
    # If no patients exist, start with P001
    if not patients:
        return "P001"
    
    existing_ids = []
    for patient in patients:
        patient_id = patient.get("id", "")
        # Check if the ID starts with "P" and the rest is a number
        if patient_id.startswith("P") and patient_id[1:].isdigit():
            existing_ids.append(int(patient_id[1:]))
    
    # Determine the next number
    next_num = max(existing_ids, default=0) + 1
    
    # Return the formatted new ID
    return f"P{next_num:03d}"


# Populate patient fields in the dashboard
def populate_patient_fields(entries, patient):
    entries["ID"].config(state="normal")
    entries["ID"].delete(0, tk.END)
    entries["ID"].insert(0, patient.get("id", ""))
    entries["ID"].config(state="disabled")
    entries["Name"].delete(0, tk.END)
    entries["Name"].insert(0, patient.get("name", ""))


# Clear all fields for a new patient
def clear_fields(dashboard):
    for key in dashboard.patient_entries:
        if key == "ID":
            continue
        dashboard.patient_entries[key].delete(0, "end")
        
    for key in dashboard.param_entries:
        dashboard.param_entries[key].delete(0, "end")
    dashboard.patient = None
    
    # Generate new ID
    new_id = generate_unique_patient_id(dashboard)
    
    # Set new ID in the ID entry
    dashboard.patient_entries["ID"].config(state="normal")
    dashboard.patient_entries["ID"].delete(0, "end")
    dashboard.patient_entries["ID"].insert(0, new_id)
    dashboard.patient_entries["ID"].config(state="disabled")
    dashboard.patient_var.set("New Patient")
    
    dashboard.update_mode_parameters()


# -----------------------------
# Validation helper for parameter ranges
# -----------------------------
def validate_parameters(params):
    errors = []

    # Helper: check if value in numeric range
    def in_range(val, low, high):
        try:
            num = float(val)
            return low <= num <= high
        except ValueError:
            return False

    # Helper: check that val is valid increment
    def valid_increment(val, step):
        try:
            num = float(val)
            return abs((num / step) - round(num / step)) < 1e-6
        except:
            return False

    # Special LRL increment helper
    def valid_lrl_increment(val):
        try:
            num = float(val)
        except:
            return False

        if 30 <= num <= 50:
            return valid_increment(num, 5)
        elif 50 < num <= 90:
            return valid_increment(num, 1)
        elif 90 < num <= 175:
            return valid_increment(num, 5)

        return False

    # --------------------------------------------
    # Lower/Upper Rate Limit
    # --------------------------------------------
    lrl = params.get("lower_rate_limit", 0)
    url = params.get("upper_rate_limit", 0)

    # LRL range
    if not in_range(lrl, 30, 175):
        errors.append("Lower Rate Limit must be between 30 and 175 ppm.")
    else:
        # LRL increment
        if not valid_lrl_increment(lrl):
            errors.append(
                "Lower Rate Limit increment invalid. Must follow:\n"
                "• 30–50: increments of 5\n"
                "• 50–90: increments of 1\n"
                "• 90–175: increments of 5"
            )

    # URL range
    if not in_range(url, 50, 175):
        errors.append("Upper Rate Limit must be between 50 and 175 ppm.")
    else:
        # URL > LRL
        try:
            if float(url) <= float(lrl):
                errors.append("Upper Rate Limit must be higher than Lower Rate Limit.")
        except:
            pass

        # URL increment
        if not valid_increment(url, 5):
            errors.append("Upper Rate Limit must increase in steps of 5 ppm.")

    # --------------------------------------------
    # Common parameters with increment validation
    # --------------------------------------------
    for key, label, low, high, unit, step in [
        ("maximum_sensor_rate", "Maximum Sensor Rate", 50, 175, "ppm", 5),

        ("atrial_amplitude", "Atrial Amplitude", 0, 5.0, "V", 0.1),
        ("ventricular_amplitude", "Ventricular Amplitude", 0, 5.0, "V", 0.1),

        ("atrial_pulse_width", "Atrial Pulse Width", 1, 30, "ms", 1),
        ("ventricular_pulse_width", "Ventricular Pulse Width", 1, 30, "ms", 1),

        ("atrial_sensitivity", "Atrial Sensitivity", 0, 5.0, "mV", 0.1),
        ("ventricular_sensitivity", "Ventricular Sensitivity", 0, 5.0, "mV", 0.1),

        ("arp", "ARP", 150, 500, "ms", 10),
        ("vrp", "VRP", 150, 500, "ms", 10),
        ("pvarp", "PVARP", 150, 500, "ms", 10),

        ("reaction_time", "Reaction Time", 10, 50, "s", 10),
        ("response_factor", "Response Factor", 1, 16, "", 1),
        ("recovery_time", "Recovery Time", 2, 16, "min", 1),
    ]:
        val = params.get(key)
        if not val:
            continue

        # Range check
        if not in_range(val, low, high):
            errors.append(f"{label} must be between {low} and {high} {unit}.")
            continue

        # Increment check
        if not valid_increment(val, step):
            errors.append(f"{label} must increase in steps of {step} {unit}.")

    # --------------------------------------------
    # Rate Smoothing
    # --------------------------------------------
    smoothing_allowed = {"0", "3", "6", "9", "12", "15", "18", "21", "25"}
    if params.get("rate_smoothing") and params.get("rate_smoothing") not in smoothing_allowed:
        errors.append("Rate Smoothing must be one of: 0, 3, 6, 9, 12, 15, 18, 21, 25.")

    # --------------------------------------------
    # Activity Threshold
    # --------------------------------------------
    activity_allowed = {
        "V-Low", "Low", "Med-Low", "Med", "Med-High", "High", "V-High"
    }
    if params.get("activity_threshold") and params.get("activity_threshold") not in activity_allowed:
        errors.append("Activity Threshold must be one of: V-Low, Low, Med-Low, Med, Med-High, High, V-High.")

    # --------------------------------------------
    # Hysteresis
    # --------------------------------------------
    hysteresis_val = params.get("hysteresis", "")
    if hysteresis_val and hysteresis_val.lower() != "off":
        try:
            lrl_num = float(lrl)
            hyst_num = float(hysteresis_val)
            if abs(hyst_num - lrl_num) > 0.1:
                errors.append("Hysteresis must be 'Off' or equal to the Lower Rate Limit.")
        except ValueError:
            errors.append("Hysteresis must be 'Off' or a numeric value equal to LRL.")

    # --------------------------------------------
    # FINAL ERROR POPUP
    # --------------------------------------------
    if errors:
        messagebox.showerror("Invalid Parameters", "\n".join(errors))
        return False

    return True



# Save patient data from dashboard
def save_patient_from_dashboard(dashboard):
    patient_id = dashboard.patient_entries["ID"].get().strip()
    patient_name = dashboard.patient_entries["Name"].get().strip().capitalize()
    model = dashboard.param_entries["Model"].get().strip().capitalize()
    serial = dashboard.param_entries["Serial"].get().strip().capitalize()
    mode = dashboard.current_mode.get()

    if not patient_name or not model or not serial:
        messagebox.showwarning("Missing Fields", "Patient Name, Model, and Serial are required.")
        return

    existing_patients = storage.load_all_patients()
    existing_dcm_serials = []

    for p in existing_patients:
        if "device" in p and "dcm_serial" in p["device"]:
            existing_dcm_serials.append(p["device"]["dcm_serial"])

    if dashboard.patient and "device" in dashboard.patient and "dcm_serial" in dashboard.patient["device"]:
        dcm_serial = dashboard.patient["device"]["dcm_serial"]
    else:
        next_num = len(existing_dcm_serials) + 1
        dcm_serial = "DCM-" + str(next_num).zfill(3)

    # Gather parameters from entries
    parameters = {}
    for key, field_name in param_helpers.PARAMETER_MAPPING:
        if field_name == "Activity Threshold":
            value = dashboard.activity_threshold_var.get().strip()
        else:
            value = dashboard.param_entries[field_name].get().strip()
        if value:
            parameters[key] = value

    if not validate_parameters(parameters):
        return

    modes = {}
    if dashboard.patient and "device" in dashboard.patient:
        modes = dashboard.patient["device"].get("modes", {})

    modes[mode] = {"parameters": parameters}

    new_patient = {
        "id": patient_id,
        "name": patient_name,
        "device": {
            "model": model,
            "serial": serial,
            "dcm_serial": dcm_serial,
            "modes": modes
        }
    }

    # Save patient data
    storage.save_patient_to_file(new_patient)
    dashboard.patients = storage.load_all_patients()
    dashboard.patient = new_patient
    dashboard.refresh_patient_dropdown()
    dashboard.patient_var.set(patient_name)
    messagebox.showinfo("Saved", f"Patient {patient_id} saved successfully!")

    
    # -----------------------------
    # SEND 18-BYTE PACKET AUTOMATICALLY (WITH DEBUGGING)
    # -----------------------------

    print("\n--- SAVE PATIENT DEBUG ---")

    # 1. Check serial_link exists
    if not hasattr(dashboard, "serial_link"):
        print("[DEBUG] dashboard.serial_link does NOT exist.")
        print("Packet NOT sent.")
        return

    # 2. Check serial object exists
    if dashboard.serial_link.ser is None:
        print("[DEBUG] serial_link.ser is None — connect_pacemaker was never called.")
        return
    else:
        print("[DEBUG] serial_link.ser exists.")

    # 3. Check port open
    if not dashboard.serial_link.ser.is_open:
        print("[DEBUG] serial port exists but is NOT OPEN.")
        return
    else:
        print(f"[DEBUG] Serial port {dashboard.serial_link.port} is OPEN.")

    # 4. Build packet
    packet = dashboard.build_serial_packet()
    packet_list = list(packet)
    print(f"[DEBUG] Built packet ({len(packet_list)} bytes): {packet_list}")
    


    # 5. Try sending packet
    try:
        bytes_written = dashboard.serial_link.ser.write(packet)
        dashboard.serial_link.ser.flush()
        print(f"[DEBUG] Bytes actually written: {bytes_written}")
    except Exception as e:
        print("[ERROR] Failed to write packet over serial:", e)
        return

    print("[DEBUG] Packet successfully sent to pacemaker.")
    print("--- END DEBUG ---\n")




def remove_patient(dashboard):
    # Remove the currently loaded patient
    if not dashboard.patient:
        messagebox.showwarning("No Selection", "No patient selected to remove.")
        return

    # Get patient ID and confirm deletion
    patient_id = dashboard.patient.get("id")
    confirm = messagebox.askyesno("Confirm Delete", f"Are you sure you want to remove patient {patient_id}?")
    if confirm:
        storage.delete_patient(patient_id)
        dashboard.patients = storage.load_all_patients()
        dashboard.patient = None
        dashboard.clear_fields()
        dashboard.refresh_patient_dropdown()
