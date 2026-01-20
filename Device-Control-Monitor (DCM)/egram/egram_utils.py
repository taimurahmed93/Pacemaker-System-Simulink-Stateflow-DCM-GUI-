# -----------------------------------------------------------------------------
# EGRAM UTILITY FUNCTIONS
# helper functions for gains, trimming, markers, and sample formatting
# -----------------------------------------------------------------------------
import time

# -----------------------------------------------------------------------------
# gain helpers
# -----------------------------------------------------------------------------
def gain_value(gain_str):
    # convert gain string into numeric multiplier
    if gain_str == "0.5X":
        return 0.5
    elif gain_str == "1X":
        return 1.0
    elif gain_str == "2X":
        return 2.0
    else:
        return 1.0   # fallback gain


def apply_gain(samples, gain_str):
    # multiply each sample's value by the gain
    gain = gain_value(gain_str)
    out = []

    for sample in samples:
        new_sample = {}

        # copy timestamp
        if "t" in sample:
            new_sample["t"] = sample["t"]

        # apply gain only if value exists
        if "value" in sample:
            new_sample["value"] = sample["value"] * gain
        else:
            new_sample["value"] = None

        out.append(new_sample)

    return out


# -----------------------------------------------------------------------------
# sample trimming helpers
# keeps buffers within window size for rolling displays
# -----------------------------------------------------------------------------
def trim_window(samples, max_ms):
    # if buffer has no samples, return empty list
    if samples is None or len(samples) == 0:
        return []

    # assume samples are ordered oldest → newest
    latest_sample = samples[-1]
    latest_timestamp = latest_sample.get("t", 0)
    threshold = latest_timestamp - max_ms

    trimmed = []
    for sample in samples:
        timestamp = sample.get("t", 0)
        if timestamp >= threshold:
            trimmed.append(sample)

    return trimmed


# -----------------------------------------------------------------------------
# marker formatting helpers
# -----------------------------------------------------------------------------
def format_marker_label(marker):
    # convert marker dict into label text for plotting
    abbr = marker.get("abbr", "")
    modifier = marker.get("modifier")

    if modifier is not None:
        label = f"{abbr}{modifier}"
    else:
        label = abbr

    return label


# -----------------------------------------------------------------------------
# placeholder for raw ADC → mv conversion
# will update later once microcontroller protocol is confirmed
# -----------------------------------------------------------------------------
def convert_raw_samples(raw_list, scale=1.0):
    # raw_list may be ints; convert to {"t": <ms>, "value": <float>}
    out = []
    timestamp = 0

    for value in raw_list:
        sample = {}
        sample["t"] = timestamp
        sample["value"] = value * scale

        out.append(sample)

        # assume 2 ms between samples (placeholder)
        timestamp = timestamp + 2

    return out


# -----------------------------------------------------------------------------
# helper to merge sample lists for plotting
# -----------------------------------------------------------------------------
def append_and_trim(existing, new_samples, window_ms):
    # start with empty list if no existing samples
    if existing is None or len(existing) == 0:
        combined = []

        # copy new samples
        for sample in new_samples:
            combined.append(sample)
    else:
        combined = []

        # copy existing samples
        for sample in existing:
            combined.append(sample)

        # append new samples
        for sample in new_samples:
            combined.append(sample)

    # trim after combining
    combined = trim_window(combined, window_ms)
    return combined

def read_egram_packets(serial_port, running_flag, packet_size, on_packet):
    buffer = bytearray()

    while running_flag():
        if serial_port.in_waiting:
            buffer += serial_port.read(serial_port.in_waiting)

            while len(buffer) >= packet_size:
                if not (buffer[0] == 0xAA and buffer[1] == 0x22):
                    buffer.pop(0)
                    continue

                packet = buffer[:packet_size]
                buffer = buffer[packet_size:]

                print(f"[DEBUG] Packet received ({len(packet)} bytes): {list(packet)}")

                on_packet(packet)

        time.sleep(0.001)