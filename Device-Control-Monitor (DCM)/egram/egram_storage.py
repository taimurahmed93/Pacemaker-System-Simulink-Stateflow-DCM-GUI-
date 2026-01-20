# -----------------------------------------------------------------------------
# EGRAM STORAGE HELPERS
# Stores and updates real-time electrogram sessions
# Uses helper.storage load_json / save_json
# -----------------------------------------------------------------------------

import os
import uuid
from datetime import datetime, timezone
from helper.storage import load_json, save_json


# Path to JSON file
EGRAM_FILE = os.path.join("data", "egram.json")


# -----------------------------------------------------------------------------
# internal helper for timestamps
# -----------------------------------------------------------------------------
def time_now():
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds")


# -----------------------------------------------------------------------------
# load all sessions into memory
# -----------------------------------------------------------------------------
def load_sessions():
    default_data = {"egram_sessions": []}
    data = load_json(EGRAM_FILE, default_data)
    return data


# -----------------------------------------------------------------------------
# save all sessions to disk
# -----------------------------------------------------------------------------
def save_sessions(data):
    save_json(EGRAM_FILE, data)


# -----------------------------------------------------------------------------
# find a session by ID
# -----------------------------------------------------------------------------
def get_session(session_id):
    data = load_sessions()
    sessions = data.get("egram_sessions", [])

    for s in sessions:
        if s.get("session_id") == session_id:
            return s

    return None


# -----------------------------------------------------------------------------
# create a new EGRAM session
# -----------------------------------------------------------------------------
def create_session(patient_id, settings):
    data = load_sessions()
    sessions = data.get("egram_sessions", [])

    session_id = "EGRAM_" + uuid.uuid4().hex[:8].upper()
    now = time_now()

    # Default session settings
    default_settings = {
        "egm_gain": "1X",
        "ecg_gain": "1X",
        "high_pass_filter": False,
        "window_seconds": 5,
        "sampling_rate_hz": 500,
        "channels_selected": "both",
        "markers_enabled": True
    }

    # Ensure settings is a dictionary
    if settings:
        extra_settings = settings
    else:
        extra_settings = {}

    # Merge default settings with extra settings
    session_settings = default_settings.copy()
    for key, value in extra_settings.items():
        session_settings[key] = value

    # Create the session dictionary
    session = {
        "session_id": session_id,
        "patient_id": patient_id,
        "start_time": now,
        "end_time": None,
        
        "telemetry_status_log": [
            {"time": now, "status": "created"}
        ],

        "settings": session_settings,

        "channels": {
            "atrial": {"enabled": True, "samples": []},
            "ventricular": {"enabled": True, "samples": []},
            "surface": {"enabled": False, "samples": []}
        },

        "markers": [],

        "print_metadata": {
            "printed": False,
            "printed_at": None,
            "file_path": None
        }
    }

    sessions.append(session)
    save_sessions({"egram_sessions": sessions})

    return session


# -----------------------------------------------------------------------------
# add samples to a session channel
# -----------------------------------------------------------------------------
def add_samples(session_id, channel, samples):
    data = load_sessions()
    sessions = data.get("egram_sessions", [])

    # find session
    target = None
    for s in sessions:
        if s.get("session_id") == session_id:
            target = s
            break

    if target is None:
        raise ValueError("Session not found")

    if channel not in ["atrial", "ventricular", "surface"]:
        raise ValueError("Invalid channel")

    target["channels"][channel]["enabled"] = True
    target["channels"][channel]["samples"].extend(samples)

    save_sessions({"egram_sessions": sessions})


# -----------------------------------------------------------------------------
# append a marker to a session
# -----------------------------------------------------------------------------
def add_marker(session_id, marker):
    data = load_sessions()
    sessions = data.get("egram_sessions", [])

    target = None
    for s in sessions:
        if s.get("session_id") == session_id:
            target = s
            break

    if target is None:
        raise ValueError("Session not found")

    target["markers"].append(marker)
    save_sessions({"egram_sessions": sessions})


# -----------------------------------------------------------------------------
# update telemetry status
# -----------------------------------------------------------------------------
def set_telemetry(session_id, status):
    data = load_sessions()
    sessions = data.get("egram_sessions", [])

    target = None
    for s in sessions:
        if s.get("session_id") == session_id:
            target = s
            break

    if target is None:
        raise ValueError("Session not found")

    target["telemetry_status_log"].append({
        "time": time_now(),
        "status": status
    })

    save_sessions({"egram_sessions": sessions})


# -----------------------------------------------------------------------------
# finalize a session
# -----------------------------------------------------------------------------
def finish_session(session_id):
    data = load_sessions()
    sessions = data.get("egram_sessions", [])

    target = None
    for s in sessions:
        if s.get("session_id") == session_id:
            target = s
            break

    if target is None:
        raise ValueError("Session not found")

    target["end_time"] = time_now()
    save_sessions({"egram_sessions": sessions})

    return target


# -----------------------------------------------------------------------------
# get active session or create one
# -----------------------------------------------------------------------------
def get_or_start_session(patient_id, settings=None):
    data = load_sessions()
    sessions = data.get("egram_sessions", [])

    # return last unfinished session
    for s in reversed(sessions):
        if s.get("patient_id") == patient_id and s.get("end_time") is None:
            return s

    # else, create a new one
    return create_session(patient_id, settings or {})


# -----------------------------------------------------------------------------
# list sessions for a patient
# -----------------------------------------------------------------------------
def list_sessions(patient_id):
    data = load_sessions()
    sessions = data.get("egram_sessions", [])

    out = []
    for s in sessions:
        if s.get("patient_id") == patient_id:
            out.append(s)

    return out
