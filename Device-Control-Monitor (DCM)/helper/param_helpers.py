# PARAM HELPERS

# place to define parameter fields and mappings
PARAM_FIELDS = [
    "Model", "Serial",
    "Lower Rate Limit", "Upper Rate Limit",
    "Maximum Sensor Rate",
    "Atrial Amplitude", "Ventricular Amplitude",
    "Atrial Pulse Width", "Ventricular Pulse Width",
    "ARP", "VRP",
    "Atrial Sensitivity", "Ventricular Sensitivity",
    "PVARP", "Hysteresis",
    "Rate Smoothing", "Activity Threshold",
    "Reaction Time", "Response Factor",
    "Recovery Time"
]

# Mapping between internal parameter keys and UI field names
PARAMETER_MAPPING = [
    ("lower_rate_limit", "Lower Rate Limit"),
    ("upper_rate_limit", "Upper Rate Limit"),
    ("maximum_sensor_rate", "Maximum Sensor Rate"),
    ("atrial_amplitude", "Atrial Amplitude"),
    ("ventricular_amplitude", "Ventricular Amplitude"),
    ("atrial_pulse_width", "Atrial Pulse Width"),
    ("ventricular_pulse_width", "Ventricular Pulse Width"),
    ("arp", "ARP"),
    ("vrp", "VRP"),
    ("atrial_sensitivity", "Atrial Sensitivity"),
    ("ventricular_sensitivity", "Ventricular Sensitivity"),
    ("pvarp", "PVARP"),
    ("hysteresis", "Hysteresis"),
    ("rate_smoothing", "Rate Smoothing"),
    ("activity_threshold", "Activity Threshold"),
    ("reaction_time", "Reaction Time"),
    ("response_factor", "Response Factor"),
    ("recovery_time", "Recovery Time")
]

# Define which parameters are editable for each pacing mode
MODE_PARAMETER_MAP = {
    "AOO": [
        "Lower Rate Limit",
        "Upper Rate Limit",
        "Atrial Amplitude",
        "Atrial Pulse Width"
    ],
    "VOO": [
        "Lower Rate Limit",
        "Upper Rate Limit",
        "Ventricular Amplitude",
        "Ventricular Pulse Width"
    ],
    "AAI": [
        "Lower Rate Limit",
        "Upper Rate Limit",
        "Atrial Amplitude",
        "Atrial Pulse Width",
        "Atrial Sensitivity",
        "ARP",
        "PVARP",
        "Hysteresis",
        "Rate Smoothing"
    ],
    "VVI": [
        "Lower Rate Limit",
        "Upper Rate Limit",
        "Ventricular Amplitude",
        "Ventricular Pulse Width",
        "Ventricular Sensitivity",
        "VRP",
        "Hysteresis",
        "Rate Smoothing"
    ],
    "AOOR": [
        "Lower Rate Limit",
        "Upper Rate Limit",
        "Maximum Sensor Rate",
        "Atrial Amplitude",
        "Atrial Pulse Width",
        "Activity Threshold",
        "Reaction Time",
        "Response Factor",
        "Recovery Time"
    ],
    "VOOR": [
        "Lower Rate Limit",
        "Upper Rate Limit",
        "Maximum Sensor Rate",
        "Ventricular Amplitude",
        "Ventricular Pulse Width",
        "Activity Threshold",
        "Reaction Time",
        "Response Factor",
        "Recovery Time"
    ],
    "AAIR": [
        "Lower Rate Limit",
        "Upper Rate Limit",
        "Maximum Sensor Rate",
        "Atrial Amplitude",
        "Atrial Sensitivity",
        "ARP",
        "PVARP",
        "Hysteresis",
        "Rate Smoothing",
        "Atrial Pulse Width",
        "Activity Threshold",
        "Reaction Time",
        "Response Factor",
        "Recovery Time"
    ],
    "VVIR": [
        "Lower Rate Limit",
        "Upper Rate Limit",
        "Maximum Sensor Rate",
        "Ventricular Amplitude",
        "Ventricular Pulse Width",
        "Ventricular Sensitivity",
        "VRP",
        "Hysteresis",
        "Rate Smoothing",
        "Activity Threshold",
        "Reaction Time",
        "Response Factor",
        "Recovery Time"
    ],
}



def populate_parameter_entries(entries, device):
    #Populate the device and parameter fields in the UI from the patient/device data
    parameters = device.get("parameters", {})

    # Device-level fields
    entries["Model"].delete(0, "end")
    entries["Model"].insert(0, device.get("model", ""))

    entries["Serial"].delete(0, "end")
    entries["Serial"].insert(0, device.get("serial", ""))

    # Parameter fields
    for key, field_name in PARAMETER_MAPPING:
        entries[field_name].delete(0, "end")
        entries[field_name].insert(0, parameters.get(key, ""))
