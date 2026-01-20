# -----------------------------------------------------------------------------
# EGRAM SCREEN
# Refactored UI for real-time electrograms
# -----------------------------------------------------------------------------

import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from egram.egram_plot import EgramPlot
from egram.egram_storage import (
    get_or_start_session,
    add_samples,
    add_marker,
    set_telemetry
)
from egram.egram_utils import read_egram_packets
from helper.serial_comm import PacemakerSerial
import threading
import time

# ==============================================
#  PARSE TELEMETRY PACKET (20 bytes from MCU)
# ==============================================
def parse_egram_packet(packet_bytes):
    if len(packet_bytes) != 20:
        print("[DEBUG] Packet ignored: wrong length", len(packet_bytes))
        return None

    if packet_bytes[0] != 0xAA or packet_bytes[1] != 0x22:
        print("[DEBUG] Packet ignored: wrong header", packet_bytes[:2])
        return None

    vent_raw = int.from_bytes(packet_bytes[18:19], byteorder="big", signed=True)
    atr_raw  = int.from_bytes(packet_bytes[19:20], byteorder="big", signed=True)

    vent_mV = vent_raw / 10.0
    atr_mV  = atr_raw / 10.0

    print(f"[DEBUG] Parsed Packet → atrial: {atr_mV} mV, ventricular: {vent_mV} mV")

    return {
        "atrial": [{"t": 0, "value": atr_mV}],
        "ventricular": [{"t": 0, "value": vent_mV}],
        "markers": []
    }
    
class EgramScreen(tk.Frame):
    DARK_BG = "#1e1e1e"
    FG_COLOR = "#ffffff"
    BTN_BG = "white"
    BTN_FG = "black"
    BTN_ACTIVE_BG = "#dddddd"
    BTN_ACTIVE_FG = "black"

    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.session = None
        self.plot = None
        self.canvas = None
        self.collecting = False
        self.active_patient = None


        # UI layout
        self.configure(bg=self.DARK_BG)
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # ttk style for dark-themed Combobox
        style = ttk.Style()
        style.theme_use('clam')
        style.configure(
            "TCombobox",
            fieldbackground="white",  # white input area
            background="white",       # dropdown background
            foreground="black",       # text color
            arrowcolor="black"        # dropdown arrow color
        )

        # Build UI
        self.build_header()
        self.build_controls()
        self.build_plot_container()

        # Initialize the empty plot
        self.plot = EgramPlot(window_seconds=5)
        self.setup_plot_canvas()

        # Update axes visibility based on selected channels
        self.update_plot_mode()

    # -------------------------------------------------------------------------
    # Header with Back button
    # -------------------------------------------------------------------------
    def build_header(self):
        header = tk.Frame(self, bg=self.DARK_BG)
        header.grid(row=0, column=0, sticky="ew", pady=10)
        header.grid_columnconfigure(0, weight=1)  # title stretch

        # Title Label
        tk.Label(
            header,
            text="Real-Time Electrograms",
            font=("Arial", 18, "bold"),
            bg=self.DARK_BG,
            fg=self.FG_COLOR
        ).grid(row=0, column=0, sticky="w", padx=10)

        # Back button under title
        # Back + Patient Name Frame
        left_info = tk.Frame(header, bg=self.DARK_BG)
        left_info.grid(row=1, column=0, sticky="w", padx=10, pady=(5, 0))

        back_btn = tk.Button(
            left_info,
            text="Back",
            width=10,
            bg=self.BTN_BG,
            fg=self.BTN_FG,
            activebackground=self.BTN_ACTIVE_BG,
            activeforeground=self.BTN_ACTIVE_FG,
            command=self.go_back
        )
        back_btn.pack(side="left")

        # Patient label (auto-updated when you load a patient)
        self.patient_label = tk.Label(
            left_info,
            text="Patient: None",
            bg=self.DARK_BG,
            fg=self.FG_COLOR,
            font=("Arial", 12, "bold")
        )
        self.patient_label.pack(side="left", padx=15)


        # Telemetry + Start/Stop buttons frame (right-aligned)
        right_frame = tk.Frame(header, bg=self.DARK_BG)
        right_frame.grid(row=0, column=1, rowspan=2, sticky="e", padx=10)

        # Telemetry label
        self.telemetry_label = tk.Label(
            right_frame,
            text="Telemetry: idle",
            bg=self.DARK_BG,
            fg="red",
            font=("Arial", 12, "bold")
        )
        self.telemetry_label.pack(side="top", anchor="e", pady=(0, 5))

        # Start / Stop buttons
        start_btn = tk.Button(
            right_frame,
            text="Start",
            width=10,
            bg=self.BTN_BG,
            fg=self.BTN_FG,
            activebackground=self.BTN_ACTIVE_BG,
            activeforeground=self.BTN_ACTIVE_FG,
            command=self.start_collection
        )
        start_btn.pack(side="top", anchor="e", pady=2)

        stop_btn = tk.Button(
            right_frame,
            text="Stop",
            width=10,
            bg=self.BTN_BG,
            fg=self.BTN_FG,
            activebackground=self.BTN_ACTIVE_BG,
            activeforeground=self.BTN_ACTIVE_FG,
            command=self.stop_collection
        )
        stop_btn.pack(side="top", anchor="e", pady=2)


    # -------------------------------------------------------------------------
    # Control widgets
    # -------------------------------------------------------------------------
    # -------------------------------------------------------------------------
    # Control widgets (single row layout)
    # -------------------------------------------------------------------------
    def build_controls(self):
        controls = tk.Frame(self, bg=self.DARK_BG)
        controls.grid(row=1, column=0, sticky="ew", pady=(5, 10))

        padx_label = 5   # space between label and dropdown
        padx_control = 10  # space between controls

        # Channels
        tk.Label(controls, text="Channels:", bg=self.DARK_BG, fg=self.FG_COLOR).grid(row=0, column=0, padx=(0, padx_label))
        self.channel_var = tk.StringVar(value="both")
        channel_menu = ttk.Combobox(
            controls,
            textvariable=self.channel_var,
            values=["atrial", "ventricular", "both", "surface"],
            width=12
        )
        channel_menu.grid(row=0, column=1, padx=(0, padx_control))
        channel_menu.bind("<<ComboboxSelected>>", lambda e: self.update_plot_mode())

        # EGM Gain
        tk.Label(controls, text="EGM Gain:", bg=self.DARK_BG, fg=self.FG_COLOR).grid(row=0, column=2, padx=(0, padx_label))
        self.egm_gain_var = tk.StringVar(value="1X")
        egm_gain_menu = ttk.Combobox(
            controls,
            textvariable=self.egm_gain_var,
            values=["0.5X", "1X", "2X"],
            width=8
        )
        egm_gain_menu.grid(row=0, column=3, padx=(0, padx_control))

        # ECG Gain
        tk.Label(controls, text="ECG Gain:", bg=self.DARK_BG, fg=self.FG_COLOR).grid(row=0, column=4, padx=(0, padx_label))
        self.ecg_gain_var = tk.StringVar(value="1X")
        ecg_gain_menu = ttk.Combobox(
            controls,
            textvariable=self.ecg_gain_var,
            values=["0.5X", "1X", "2X"],
            width=8
        )
        ecg_gain_menu.grid(row=0, column=5, padx=(0, padx_control))

        # High-pass Filter
        self.hpf_var = tk.BooleanVar(value=False)
        tk.Checkbutton(
            controls,
            text="High-pass Filter",
            variable=self.hpf_var,
            bg=self.DARK_BG,
            fg=self.FG_COLOR,
            selectcolor=self.DARK_BG
        ).grid(row=0, column=6, padx=(0, padx_control))

        # Event Markers
        self.marker_var = tk.BooleanVar(value=True)
        tk.Checkbutton(
            controls,
            text="Event Markers",
            variable=self.marker_var,
            bg=self.DARK_BG,
            fg=self.FG_COLOR,
            selectcolor=self.DARK_BG
        ).grid(row=0, column=7, padx=(0, 0))  # last item, no extra padding

    def set_active_patient(self, patient):
        # Receive patient object from Dashboard and display name.
        self.active_patient = patient
        name = patient.get("name", "Unknown")
        self.patient_label.config(text=f"Patient: {name}")

        

    # -------------------------------------------------------------------------
    # Plot container
    # -------------------------------------------------------------------------
    def build_plot_container(self):
        container = tk.Frame(self, bg=self.DARK_BG)
        container.grid(row=2, column=0, sticky="nsew", pady=10)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        self.plot_area = container

    # -------------------------------------------------------------------------
    # Embed the matplotlib figure once
    # -------------------------------------------------------------------------
    def setup_plot_canvas(self):
        fig = self.plot.fig
        fig.patch.set_facecolor(self.DARK_BG)
        for ax in fig.axes:
            ax.set_facecolor(self.DARK_BG)
            ax.tick_params(colors=self.FG_COLOR)
            ax.xaxis.label.set_color(self.FG_COLOR)
            ax.yaxis.label.set_color(self.FG_COLOR)
            ax.title.set_color(self.FG_COLOR)

        self.canvas = FigureCanvasTkAgg(fig, master=self.plot_area)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

    # -------------------------------------------------------------------------
    # Update axes visibility based on selected channels
    # -------------------------------------------------------------------------
    def update_plot_mode(self):
        selected = self.channel_var.get()

        # Reset all axes buffers
        self.plot.reset()

        # Redraw the figure for the selected mode
        self.plot.redraw(selected)

        # Remove the old canvas and embed a fresh one
        if self.canvas:
            self.canvas.get_tk_widget().destroy()

        self.setup_plot_canvas()  # creates a fresh FigureCanvasTkAgg
        self.canvas.draw()

    # -------------------------------------------------------------------------
    # Navigation
    # -------------------------------------------------------------------------
    def go_back(self):
        self.stop_collection()
        self.controller.show_frame("Dashboard")

    # -------------------------------------------------------------------------
    # Start / Stop collection
    # -------------------------------------------------------------------------
    def start_collection(self):
        # Ensure serial is connected only when telemetry starts
        ser = getattr(self.controller, "serial", None)
        if ser is None:
            self.controller.serial = PacemakerSerial(port="COM7", baud=115200)
            ser = self.controller.serial

        if not ser.connect():
            print("Warning: Could not connect to pacemaker. Telemetry will not start.")
            self.collecting = False
            return

        # Initialize session if needed
        if self.session is None:
            if not self.active_patient:
                patient_id = "UNKNOWN"
            else:
                patient_id = self.active_patient.get("id", "UNKNOWN")

            self.session = get_or_start_session(patient_id, {
                "patient_name": self.active_patient.get("name", ""),
                "egm_gain": self.egm_gain_var.get(),
                "ecg_gain": self.ecg_gain_var.get(),
                "high_pass_filter": self.hpf_var.get(),
                "channels_selected": self.channel_var.get()
            })

        self.collecting = True
        self.telemetry_label.config(text="Telemetry: Connected", fg="green")

        # -----------------------------
        # Unified read loop
        # -----------------------------
        def read_loop():
            buffer = bytearray()
            while self.collecting:
                try:
                    if not ser or not ser.ser or not ser.ser.is_open:
                        time.sleep(0.01)
                        continue

                    # Read all available bytes
                    in_waiting = ser.ser.in_waiting
                    if in_waiting:
                        buffer += ser.ser.read(in_waiting)

                        # Extract full 20-byte packets
                        while len(buffer) >= 20:
                            # Check header
                            if not (buffer[0] == 0xAA and buffer[1] == 0x22):
                                buffer.pop(0)
                                continue

                            packet = buffer[:20]
                            buffer = buffer[20:]

                            # --- Parse packet and update plots ---
                            payload = parse_egram_packet(packet)
                            if payload:
                                self.handle_incoming_data(payload)

                            # --- Telemetry 19th/20th byte ---
                            byte19, byte20 = packet[18], packet[19]
                            telemetry_value = (byte19 << 8) | byte20

                            mode = self.channel_var.get().lower()
                            if mode in ["atrial", "both"]:
                                self.update_egm_plot('atrial', telemetry_value)
                            if mode in ["ventricular", "both"]:
                                self.update_egm_plot('ventricular', telemetry_value)

                    else:
                        time.sleep(0.01)

                except Exception as e:
                    print("[EGRAM ERROR] read_loop:", e)
                    time.sleep(0.05)

        threading.Thread(target=read_loop, daemon=True).start()
        

    def stop_collection(self):
        self.collecting = False
        if self.session:
            set_telemetry(self.session["session_id"], "disconnected")
        self.telemetry_label.config(text="Telemetry: Disconnected", fg="red")

    # -------------------------------------------------------------------------
    # Update loop (periodic)
    # -------------------------------------------------------------------------
    def update_plot_loop(self):
        if not self.collecting:
            return

        # Demo/fake data
        samples = [{"t": i*2, "value": i % 10 / 10.0} for i in range(20)]
        selected = self.channel_var.get()

        if selected in ["atrial", "both"]:
            self.plot.update_samples("atrial", samples, self.egm_gain_var.get())
            add_samples(self.session["session_id"], "atrial", samples)
        if selected in ["ventricular", "both"]:
            self.plot.update_samples("ventricular", samples, self.egm_gain_var.get())
            add_samples(self.session["session_id"], "ventricular", samples)
        if selected == "surface":
            self.plot.update_samples("surface", samples, self.ecg_gain_var.get())
            add_samples(self.session["session_id"], "surface", samples)

        self.plot.redraw(selected)
        self.canvas.draw()
        self.after(100, self.update_plot_loop)

    # -------------------------------------------------------------------------
    # Handle incoming data from device
    # -------------------------------------------------------------------------
    def handle_incoming_data(self, payload):
        if not self.collecting:
            return

        print("[DEBUG] handle_incoming_data called with payload:", payload)

        for channel in ["atrial", "ventricular", "surface"]:
            if channel in payload:
                gain = self.egm_gain_var.get() if channel != "surface" else self.ecg_gain_var.get()
                self.plot.update_samples(channel, payload[channel], gain)
                add_samples(self.session["session_id"], channel, payload[channel])
                print(f"[DEBUG] {channel} channel updated with {payload[channel]}")

        if "markers" in payload:
            for m in payload["markers"]:
                self.plot.add_marker(m)
                add_marker(self.session["session_id"], m)
                print("[DEBUG] Marker added:", m)

        self.canvas.draw()

    