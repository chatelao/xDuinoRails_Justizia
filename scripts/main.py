"""
MicroPython DCC Decoder Tester
============================================================================
Hardware Pin Mapping:
  Pin 9  / A0    : PIN_FUNC0_DIV   (Analog input: Scaled Function 0 voltage)
  Pin 10 / A1    : PIN_MOTOR0_DIV  (Analog input: Scaled Motor 0 voltage)
  Pin 11 / A2    : PIN_MOTOR1_DIV  (Analog input: Scaled Motor 1 voltage)
  Pin 12 / A3    : PIN_FUNC1_DIV   (Analog input: Scaled Function 1 voltage)
  Pin 13 / SDA/A4: PIN_DEF_FAULT_A (Digital input: Active-LOW Hardware Fault)
  Pin 17 / D2    : PIN_DCC0_HIGH   (Digital output: H-Bridge Rail 0 High-side)
  Pin 19 / D4    : PIN_DCC0_LOW    (Digital output: H-Bridge Rail 0 Low-side)
  Pin 21 / D6    : PIN_DCC1_HIGH   (Digital output: H-Bridge Rail 1 High-side)
  Pin 23 / D8    : PIN_DCC1_LOW    (Digital output: H-Bridge Rail 1 Low-side)
  Pin 25 / D10   : PIN_VIN         (VIN signal - 7.2V)
  Pin 26 / D11   : PIN_VM          (VM signal - 15V)
  Pin 27 / D12   : PIN_U_PLUS      (Decoder common positive U+)
  Pin 28 / D13   : PIN_3V3         (Logic power line +3V3)
============================================================================
"""

import sys
import time
import select

try:
    import micropython
    micropython.alloc_emergency_exception_buf(100)
except Exception:
    pass

try:
    from machine import Pin, ADC, Timer
    MICROPYTHON = True
except ImportError:
    MICROPYTHON = False
    class Pin:
        IN = 0
        OUT = 1
        PULL_UP = 2

        def __init__(self, id, mode=-1, pull=-1, value=1):
            self.id = id
            self.mode = mode
            self.pull = pull
            self._value = value

        def value(self, val=None):
            if val is not None:
                self._value = val
            return self._value

    class ADC:
        def __init__(self, pin):
            self.pin = pin

        def read_u16(self):
            return 32768

        def read(self):
            return 512

    class Timer:
        PERIODIC = 0
        ONE_SHOT = 1

        def __init__(self, id=-1):
            pass

        def init(self, period=1, freq=1000, mode=PERIODIC, callback=None):
            pass

        def deinit(self):
            pass


# ----------------------------------------------------------------------------
# Hardware Pin Mapping
# ----------------------------------------------------------------------------
PIN_FUNC0_DIV_NUM   = "A0"  # Pin 9  / A0
PIN_MOTOR0_DIV_NUM  = "A1"  # Pin 10 / A1
PIN_MOTOR1_DIV_NUM  = "A2"  # Pin 11 / A2
PIN_FUNC1_DIV_NUM   = "A3"  # Pin 12 / A3
PIN_DEF_FAULT_A_NUM = "A4"  # Pin 13 / A4 (SDA)

PIN_DCC0_HIGH_NUM   = 2     # Pin 17 / D2
PIN_DCC0_LOW_NUM    = 4     # Pin 19 / D4
PIN_DCC1_HIGH_NUM   = 6     # Pin 21 / D6
PIN_DCC1_LOW_NUM    = 8     # Pin 23 / D8

PIN_VIN_NUM         = 10    # Pin 25 / D10
PIN_VM_NUM          = 11    # Pin 26 / D11
PIN_U_PLUS_NUM      = 12    # Pin 27 / D12
PIN_3V3_NUM         = 13    # Pin 28 / D13

# ----------------------------------------------------------------------------
# NMRA DCC Constants & Timing Specifications
# ----------------------------------------------------------------------------
DCC_BIT_1_HALF_PERIOD_US = 58
DCC_BIT_0_HALF_PERIOD_US = 100

VOLTAGE_DIVIDER_FACTOR = 4.30
ADC_REF_VOLTAGE        = 5.00

# Pre-framed bit array helper according to NMRA S-9.2 DCC Protocol:
# 14 '1' preamble bits + for each byte: '0' start bit + 8 data bits + '1' stop bit
def encode_dcc_packet_bits(data_bytes):
    bits = [1] * 14  # Minimum 14 preamble '1' bits
    for b in data_bytes:
        bits.append(0)  # Start bit
        for shift in range(7, -1, -1):
            bits.append((b >> shift) & 1)
    bits.append(1)  # Stop bit
    return bits


# Pre-allocated bit streams
idle_packet_data = [0xFF, 0x00, 0xFF]
idle_bit_stream = encode_dcc_packet_bits(idle_packet_data)

active_bit_stream = list(idle_bit_stream)
current_bit_stream = list(idle_bit_stream)

current_bit_idx = 0
current_half_bit_phase = False  # False = Phase A, True = Phase B
tick_count = 0
dcc_output_enabled = True
system_fault_detected = False

# Hardware objects
pin_dcc0_high = None
pin_dcc0_low = None
pin_dcc1_high = None
pin_dcc1_low = None

pin_func0_div = None
pin_motor0_div = None
pin_motor1_div = None
pin_func1_div = None
pin_def_fault_a = None

pin_vin = None
pin_vm = None
pin_u_plus = None
pin_3v3 = None

dcc_timer = None


# ----------------------------------------------------------------------------
# Signal Generation Output Drivers
# ----------------------------------------------------------------------------
def set_hbridge_outputs(phase):
    global dcc_output_enabled, system_fault_detected
    if not dcc_output_enabled or system_fault_detected:
        pin_dcc0_high.value(0)
        pin_dcc0_low.value(0)
        pin_dcc1_high.value(0)
        pin_dcc1_low.value(0)
        return

    # Dead-time protection: disable high sides before switching
    pin_dcc0_high.value(0)
    pin_dcc1_high.value(0)

    if not phase:
        # Phase A: Rail 0 = HIGH, Rail 1 = LOW
        pin_dcc0_low.value(0)
        pin_dcc1_low.value(1)
        pin_dcc0_high.value(1)
    else:
        # Phase B: Rail 0 = LOW, Rail 1 = HIGH
        pin_dcc0_low.value(1)
        pin_dcc1_low.value(0)
        pin_dcc1_high.value(1)


# ----------------------------------------------------------------------------
# Zero-Allocation DCC Timer Interrupt Handler
# ----------------------------------------------------------------------------
def timer_isr(t):
    global current_half_bit_phase, current_bit_idx, tick_count
    global current_bit_stream, active_bit_stream

    current_bit = current_bit_stream[current_bit_idx]
    # For '1' bit: 1 tick per half-period (58us).
    # For '0' bit: 2 ticks per half-period (100us).
    required_ticks = 1 if current_bit == 1 else 2

    tick_count += 1
    if tick_count >= required_ticks:
        tick_count = 0
        current_half_bit_phase = not current_half_bit_phase
        set_hbridge_outputs(current_half_bit_phase)

        # Advance to next bit at end of Phase B
        if not current_half_bit_phase:
            current_bit_idx += 1
            if current_bit_idx >= len(current_bit_stream):
                current_bit_idx = 0
                current_bit_stream = active_bit_stream


def setup_dcc_timer():
    global dcc_timer
    dcc_timer = Timer(-1 if MICROPYTHON else 0)
    # Timer running at ~17.2 kHz (~58us tick duration) zero allocation inside ISR
    try:
        dcc_timer.init(freq=17241, callback=timer_isr)
    except Exception:
        dcc_timer.init(period=1, mode=Timer.PERIODIC, callback=timer_isr)


# ----------------------------------------------------------------------------
# NMRA DCC Packet Construction Helpers
# ----------------------------------------------------------------------------
def build_speed_packet(address, speed_step, forward):
    data = [0] * 3
    data[0] = address & 0x7F

    speed_byte = 0x40  # Base speed command prefix
    if forward:
        speed_byte |= 0x20
    speed_byte |= (speed_step & 0x1F)

    data[1] = speed_byte
    data[2] = data[0] ^ data[1]  # XOR checksum
    return encode_dcc_packet_bits(data)


def build_function_packet(address, f0, f1):
    data = [0] * 3
    data[0] = address & 0x7F

    func_byte = 0x80  # Function Group 1
    if f0:
        func_byte |= 0x10  # FL / F0
    if f1:
        func_byte |= 0x01  # F1

    data[1] = func_byte
    data[2] = data[0] ^ data[1]
    return encode_dcc_packet_bits(data)


# ----------------------------------------------------------------------------
# Analog Voltage Reading & Telemetry Functions
# ----------------------------------------------------------------------------
def read_scaled_voltage(adc_obj):
    samples = 16
    raw_sum = 0
    for _ in range(samples):
        if hasattr(adc_obj, "read_u16"):
            raw_sum += adc_obj.read_u16() >> 6  # Convert 16-bit to 10-bit
        elif hasattr(adc_obj, "read"):
            raw_sum += adc_obj.read()
        else:
            raw_sum += 512
        time.sleep_us(50) if hasattr(time, "sleep_us") else time.sleep(0.00005)

    avg_adc = raw_sum / samples
    raw_voltage = (avg_adc / 1023.0) * ADC_REF_VOLTAGE
    return raw_voltage * VOLTAGE_DIVIDER_FACTOR


def print_decoder_telemetry():
    v_func0 = read_scaled_voltage(pin_func0_div)
    v_motor0 = read_scaled_voltage(pin_motor0_div)
    v_motor1 = read_scaled_voltage(pin_motor1_div)
    v_func1 = read_scaled_voltage(pin_func1_div)
    v_motor_diff = abs(v_motor0 - v_motor1)

    fault_state = "FAULT TRIGGERED" if pin_def_fault_a.value() == 0 else "OK"

    print("--- DECODER TELEMETRY READOUT ---")
    print("FUNC0 Voltage (Pin 9 / A0):   {:.2f} V".format(v_func0))
    print("MOTOR0 Voltage (Pin 10 / A1): {:.2f} V".format(v_motor0))
    print("MOTOR1 Voltage (Pin 11 / A2): {:.2f} V".format(v_motor1))
    print("FUNC1 Voltage (Pin 12 / A3):  {:.2f} V".format(v_func1))
    print("Motor Differential Voltage:   {:.2f} V".format(v_motor_diff))
    print("Hardware Fault Line (A4):    {}".format(fault_state))
    print("---------------------------------")


# ----------------------------------------------------------------------------
# Hardware Fault & Safety Routines
# ----------------------------------------------------------------------------
def check_fault_status():
    global system_fault_detected, dcc_output_enabled
    if pin_def_fault_a.value() == 0:  # Active LOW fault
        if not system_fault_detected:
            system_fault_detected = True
            dcc_output_enabled = False
            set_hbridge_outputs(False)
            print("\n[EMERGENCY TRIP] Hardware Fault Detected on pin def_fault_a (A4/13)! Rail outputs disabled.")


def reset_fault():
    global system_fault_detected, dcc_output_enabled
    if pin_def_fault_a.value() == 1:
        system_fault_detected = False
        dcc_output_enabled = True
        print("[SYSTEM OK] Fault cleared. Normal DCC operation restored.")
    else:
        print("[ERROR] Cannot reset fault: def_fault_a pin is still LOW.")


# ----------------------------------------------------------------------------
# Interactive Serial Command Processing
# ----------------------------------------------------------------------------
def print_menu():
    print("\n====== ARDUINO DCC DECODER TESTER CLI (MicroPython) ======")
    print("Commands:")
    print("  '1' : Send Idle Packets")
    print("  '2' : Set Motor Speed Forward (Step 14)")
    print("  '3' : Set Motor Speed Reverse (Step 14)")
    print("  '4' : Set Motor Stop")
    print("  '5' : Toggle Function F0 (FL) ON")
    print("  '6' : Toggle Function F1 ON")
    print("  '7' : Turn Functions OFF")
    print("  'r' : Read Telemetry / Voltage Dividers")
    print("  'c' : Clear Fault State")
    print("  's' : Emergency Stop Outputs")
    print("==========================================================")


def handle_serial_command(cmd):
    global active_bit_stream, dcc_output_enabled
    target_address = 3

    if cmd == '1':
        active_bit_stream = idle_bit_stream
        print("Transmitting DCC Idle Packets...")
    elif cmd == '2':
        active_bit_stream = build_speed_packet(target_address, 14, True)
        print("DCC Command: Address 3 -> Speed Forward 14")
    elif cmd == '3':
        active_bit_stream = build_speed_packet(target_address, 14, False)
        print("DCC Command: Address 3 -> Speed Reverse 14")
    elif cmd == '4':
        active_bit_stream = build_speed_packet(target_address, 0, True)
        print("DCC Command: Address 3 -> Motor Stop")
    elif cmd == '5':
        active_bit_stream = build_function_packet(target_address, True, False)
        print("DCC Command: Address 3 -> Function F0 ON, F1 OFF")
    elif cmd == '6':
        active_bit_stream = build_function_packet(target_address, False, True)
        print("DCC Command: Address 3 -> Function F0 OFF, F1 ON")
    elif cmd == '7':
        active_bit_stream = build_function_packet(target_address, False, False)
        print("DCC Command: Address 3 -> Functions F0/F1 OFF")
    elif cmd == 'r':
        print_decoder_telemetry()
    elif cmd == 'c':
        reset_fault()
    elif cmd == 's':
        dcc_output_enabled = False
        set_hbridge_outputs(False)
        print("EMERGENCY STOP: Rail power disabled.")
    elif cmd in ('?', 'h'):
        print_menu()


def poll_serial_input():
    """Non-blocking poll for user input on sys.stdin/Serial CLI."""
    if MICROPYTHON:
        poll_obj = select.poll()
        poll_obj.register(sys.stdin, select.POLLIN)
        if poll_obj.poll(0):
            ch = sys.stdin.read(1)
            if ch:
                handle_serial_command(ch.strip())
    else:
        rlist, _, _ = select.select([sys.stdin], [], [], 0)
        if rlist:
            line = sys.stdin.readline()
            if line:
                for ch in line.strip():
                    handle_serial_command(ch)


# ----------------------------------------------------------------------------
# Initialization & Main Loop
# ----------------------------------------------------------------------------
def setup():
    global pin_dcc0_high, pin_dcc0_low, pin_dcc1_high, pin_dcc1_low
    global pin_func0_div, pin_motor0_div, pin_motor1_div, pin_func1_div
    global pin_def_fault_a, pin_vin, pin_vm, pin_u_plus, pin_3v3
    global current_bit_stream

    print("Initializing MicroPython DCC Decoder Tester...")

    # Configure Dual H-Bridge Digital Output Pins
    pin_dcc0_high = Pin(PIN_DCC0_HIGH_NUM, Pin.OUT, value=0)
    pin_dcc0_low  = Pin(PIN_DCC0_LOW_NUM,  Pin.OUT, value=0)
    pin_dcc1_high = Pin(PIN_DCC1_HIGH_NUM, Pin.OUT, value=0)
    pin_dcc1_low  = Pin(PIN_DCC1_LOW_NUM,  Pin.OUT, value=0)

    # Configure Fault Input (active LOW with pull-up)
    pin_def_fault_a = Pin(PIN_DEF_FAULT_A_NUM, Pin.IN, Pin.PULL_UP)

    # Configure ADC Input Pins
    pin_func0_div  = ADC(Pin(PIN_FUNC0_DIV_NUM))
    pin_motor0_div = ADC(Pin(PIN_MOTOR0_DIV_NUM))
    pin_motor1_div = ADC(Pin(PIN_MOTOR1_DIV_NUM))
    pin_func1_div  = ADC(Pin(PIN_FUNC1_DIV_NUM))

    # Configure Power Sense Input Pins
    pin_vin    = Pin(PIN_VIN_NUM,    Pin.IN)
    pin_vm     = Pin(PIN_VM_NUM,     Pin.IN)
    pin_u_plus = Pin(PIN_U_PLUS_NUM, Pin.IN)
    pin_3v3    = Pin(PIN_3V3_NUM,    Pin.IN)

    current_bit_stream = list(idle_bit_stream)

    setup_dcc_timer()
    print("DCC Generator and Tester initialized successfully.")
    print_menu()


def loop():
    while True:
        check_fault_status()
        poll_serial_input()
        time.sleep(0.01)


if __name__ == "__main__":
    setup()
    try:
        loop()
    except KeyboardInterrupt:
        print("\nExiting MicroPython DCC Decoder Tester.")
