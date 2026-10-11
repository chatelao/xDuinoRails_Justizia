# Arduino DCC Decoder Tester - Technical Concept & Implementation

## 1. Executive Summary

This document presents the detailed technical concept and reference implementation for an **Arduino-based DCC (Digital Command Control) Decoder Tester**.

The DCC Decoder Tester acts as a miniature Command Station (Digitalzentrale) and automated test rig. It generates NMRA-compliant DCC signals via gated dual H-bridge output pairs and measures the resulting outputs of the Device Under Test (DUT) — specifically motor outputs (MOTOR0, MOTOR1), function auxiliary outputs (FUNC0, FUNC1), and hardware fault conditions (`def_fault_a`).

---

## 2. Pin Assignment & Hardware Interface Mapping

The Arduino pin assignment for the tester rig is defined as follows:

| Arduino Pin Number | Pin Name / Header | Net Name / Signal | Signal Direction | Description / Function |
| :--- | :--- | :--- | :--- | :--- |
| **9** | **A0** | `FUNC0_DIV` | Input (Analog) | Scaled analog voltage feedback from Decoder Function Output 0 (FL / Auxiliary 0). |
| **10** | **A1** | `MOTOR0_DIV` | Input (Analog) | Scaled analog voltage feedback from Decoder Motor Output 0 (Track / Motor A). |
| **11** | **A2** | `MOTOR1_DIV` | Input (Analog) | Scaled analog voltage feedback from Decoder Motor Output 1 (Track / Motor B). |
| **12** | **A3** | `FUNC1_DIV` | Input (Analog) | Scaled analog voltage feedback from Decoder Function Output 1 (FR / Auxiliary 1). |
| **13** | **SDA / A4** | `def_fault_a` | Input (Digital / Int) | Active-Low / Active-High hardware fault flag input (e.g., overcurrent / thermal trip). |
| **17** | **D2** | `DCC0.HIGH` | Output (Digital) | High-side gate control signal for DCC Output Rail 0 H-Bridge driver. |
| **19** | **D4** | `DCC0.LOW` | Output (Digital) | Low-side gate control signal for DCC Output Rail 0 H-Bridge driver. |
| **21** | **D6** | `DCC1.HIGH` | Output (Digital) | High-side gate control signal for DCC Output Rail 1 H-Bridge driver. |
| **23** | **D8** | `DCC1.LOW` | Output (Digital) | Low-side gate control signal for DCC Output Rail 1 H-Bridge driver. |

---

## 3. Circuit & Hardware Architecture

### 3.1 DCC Signal Generation H-Bridge Driver
To convert 5V ATmega/Arduino logic signals into high-power differential rail signals (typically 12V–18V track voltage):
* **Dual Half-Bridge / Full H-Bridge Output Stage**:
  - `DCC0.HIGH` (Pin D2) & `DCC0.LOW` (Pin D4) drive Rail 0.
  - `DCC1.HIGH` (Pin D6) & `DCC1.LOW` (Pin D8) drive Rail 1.
* **Non-Overlap / Dead-Time Guarding**:
  To prevent shoot-through current (simultaneous conduction of High and Low switches), a software dead-time (~2–5 µs) or hardware dead-time logic gate is implemented during signal polarity switching.
* **Rail Polarity Logic**:
  - **Phase A (Rail 0 = V_TRACK, Rail 1 = GND)**:
    - `DCC0.HIGH = HIGH`, `DCC0.LOW = LOW`
    - `DCC1.HIGH = LOW`, `DCC1.LOW = HIGH`
  - **Phase B (Rail 0 = GND, Rail 1 = V_TRACK)**:
    - `DCC0.HIGH = LOW`, `DCC0.LOW = HIGH`
    - `DCC1.HIGH = HIGH`, `DCC1.LOW = LOW`
  - **Idle / Dead Phase**:
    - All pins LOW (`HIGH = LOW`, `LOW = LOW`).

### 3.2 Signal Measurement & Voltage Divider Inputs
Decoder outputs (Motor 0/1 and Function 0/1) switch high DC voltages (up to 20V) or PWM signals. To measure these safely with the 0–5V ADC of the Arduino:
* **Resistor Voltage Dividers**:
  $$V_{\text{ADC}} = V_{\text{DECODER\_OUT}} \times \frac{R_2}{R_1 + R_2}$$
  - Recommended divider ratio: $R_1 = 33\,\text{k}\Omega$, $R_2 = 10\,\text{k}\Omega$ (Divider factor ~0.2326), mapping 0–20V input to 0–4.65V ADC range.
* **Filtering & RC Smoothing**:
  Optional low-pass filter capacitor ($C = 100\,\text{nF}$) across $R_2$ provides average DC output voltage sensing for PWM motor and function outputs.

### 3.3 Hardware Fault Monitoring (`def_fault_a`)
* Connected to pin **A4 / SDA (Pin 13)**.
* Configured with internal or external pull-up resistor.
* In the event of track short-circuit, overcurrent detection from sense resistor/comparator, or decoder fault flag, the `def_fault_a` line triggers an immediate emergency shutdown of all DCC outputs (`DCC*.HIGH = LOW`, `DCC*.LOW = LOW`).

---

## 4. NMRA DCC Signal Protocol & Timing

The standard NMRA S-9.1 and S-9.2 specifications require exact bit timing:

* **Logic '1' Bit**:
  - Half-period duration: **58 µs** nominal (valid range 55 µs to 61 µs).
  - Total bit duration: **116 µs**.
* **Logic '0' Bit**:
  - Half-period duration: **100 µs** nominal (valid range 95 µs to 9900 µs).
  - Total bit duration: **200 µs**.
* **DCC Packet Structure**:
  1. **Preamble**: Minimum 12 consecutive logic '1' bits (typically 14–16 bits).
  2. **Start Bit**: 1x logic '0' bit.
  3. **Address Byte**: Decoder address (e.g., Short address `0x03` or extended 14-bit address).
  4. **Data Byte(s)**: Speed/direction commands, function control bits (F0–F28), or CV configuration commands.
  5. **Error Detection Byte (XOR Checksum)**: Bitwise XOR of all address and data bytes.
  6. **Stop Bit**: 1x logic '1' bit.

---

## 5. Software Architecture

The software architecture consists of three main layers:

1. **DCC Engine (Timer Interrupt Driven)**:
   - Uses Timer1 (16-bit timer) configured in CTC (Clear Timer on Compare) mode.
   - Precision interrupts every 58 µs ('1' half-bit) or 100 µs ('0' half-bit) toggle the H-bridge state and shift out bits from a ring buffer.
2. **Analog & Fault Sensation Task**:
   - Periodic ADC sampling of `FUNC0_DIV`, `MOTOR0_DIV`, `MOTOR1_DIV`, and `FUNC1_DIV`.
   - Continuous polling / interrupt handling on `def_fault_a` pin.
3. **Control & Test Automation Engine**:
   - Interactive CLI over Serial UART (115200 baud).
   - Automated sequence testing: Speed sweep, Direction reversal, Function output toggle, Fault detection test.

---

## 6. Directory Structure

```
.
├── README.md                  # Detailed Technical Concept & Circuit Documentation
├── src/
│   └── dcc_decoder_tester.ino # Complete Reference Arduino Code
└── tests/
    └── validate_sketch.py     # Automated Firmware & Pin Mapping Test Script
```
