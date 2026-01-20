# Pacemaker System (Simulink/Stateflow + DCM GUI)

A safety-critical real-time **cardiac pacemaker system** implemented using **MATLAB Simulink + Stateflow** and a supporting **Device Controller–Monitor (DCM)** clinician interface.

This project simulates and controls cardiac pacing behaviour across multiple pacing modes, supports **programmable parameters**, and includes **serial communication** between the pacemaker and DCM. The pacemaker design integrates sensing/pacing timing logic, refractory periods, and **rate-adaptive pacing** using an on-board accelerometer.


---

## System Overview
This system consists of two major components:

### 1) Pacemaker Controller (Simulink/Stateflow)
Implements pacing logic as mode-dependent state machines, including:
- Demand pacing (inhibit pacing when intrinsic heartbeats are detected)
- Continuous pacing (fixed periodic pacing)
- Rate-adaptive pacing using accelerometer-based activity tracking

### 2) DCM (Device Controller–Monitor)
A clinician-facing GUI used to:
- Login/register users
- Select pacing mode
- Configure programmable parameters
- Transmit/receive parameter data to/from the pacemaker via serial protocol
- (Deliverable 2) display electrogram (egram) information

---

## Supported Modes
The pacemaker controller supports the following pacing modes:

### Fixed-rate modes (no sensing)
- **AOO** – Asynchronous atrial pacing
- **VOO** – Asynchronous ventricular pacing

### Demand modes (sensing + inhibit behaviour)
- **AAI** – Atrial demand pacing
- **VVI** – Ventricular demand pacing

### Rate-adaptive modes (accelerometer-driven)
- **AOOR** – Rate adaptive atrial asynchronous pacing
- **VOOR** – Rate adaptive ventricular asynchronous pacing
- **AAIR** – Rate adaptive atrial demand pacing
- **VVIR** – Rate adaptive ventricular demand pacing

(Mode integration and parameter usage follow Deliverable requirements.)  

---

## Key Features
- **Integrated multi-mode pacemaker** in one Simulink model
- Stateflow-based timing logic using temporal transitions (`after(x, msec)`)
- **Hardware hiding** (pin mapping abstracted from core logic)
- **Rate adaptivity** driven by onboard accelerometer activity level
- Serial packet protocol for sending/receiving programmable parameters
- DCM GUI includes patient/device data + mode parameter editing
- Formal documentation including:
  - requirements, design decisions
  - module descriptions
  - verification & testing results

---

## Programmable Parameters (examples)
The system supports clinically relevant programmable parameters including:
- Lower Rate Limit (LRL)
- Upper Rate Limit (URL)
- Maximum Sensor Rate (MSR)
- Pulse amplitude & width (atrial + ventricular)
- Atrial/Ventricular sensitivity
- VRP / ARP (refractory periods)
- Activity threshold, response factor
- Reaction time and recovery time (rate smoothing dynamics)

Deliverable 2 also required DCM storage + device verification of stored parameters.  

---

## Rate Adaptive Logic
In rate-adaptive modes, pacemaker rate changes based on measured activity level:
- accelerometer → activity level computation
- desired rate computed with thresholding and response factor
- rate is adjusted gradually using **reaction time** and **recovery time**

This ensures pacing rate increases smoothly when activity is detected and returns safely during recovery.

---

## Serial Communication Protocol (Pacemaker ↔ DCM)
The pacemaker and DCM communicate through UART using a structured packet format.

Example packet ordering used for parameter transfer:
- fixed headers
- mode identifier
- parameter bytes (LRL, URL, pulse widths, amplitudes, sensitivities, VRP/ARP, etc.)

This supports both:
- receiving updated parameters from DCM
- transmitting stored parameters back to DCM for verification

---

## Technologies / Tools Used
### Embedded / Control
- MATLAB Simulink
- Stateflow
- Real-time hardware deployment (course hardware platform)

### DCM Application
- Python (Tkinter GUI)
- JSON-based patient/device storage
- Unit testing for internal helpers


### Microcontroller (Main Controller)
- **NXP FRDM-K64F** development board  
  Runs the real-time execution of the pacemaker control logic, generates PWM outputs used for pacing amplitude regulation / sensing thresholds, and reads digital sensing inputs.

### Pacemaker Shield (Analog Front-End)
- Pacemaker shield provides:
  - comparator-based sensing (atrial + ventricular detect)
  - signal conditioning / rectification outputs
  - charge-balanced pacing circuitry (capacitor charge/discharge path)
  - impedance measurement circuitry (Z_SIGNAL)

### Testing Environment
- HeartView-based testing setup (course-provided) used to verify pacing output behaviour and sensing functionality.


---

## Documentation
This repository includes the official deliverables:
- `reports/deliverable1_group30.pdf`
- `reports/deliverable2_group30.pdf`

---

## Notes 
This project demonstrates:
- modeling real-time embedded systems with Stateflow
- modular software design (information hiding, separation of concerns)
- validation/verification mindset (safety-critical software)
- practical protocol design + system integration
