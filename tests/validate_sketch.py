#!/usr/bin/env python3
import sys
import re

def validate_sketch(filepath):
    print(f"Validating sketch file: {filepath}")
    with open(filepath, "r") as f:
        code = f.read()

    errors = []

    # Check pin definitions
    expected_pins = {
        "PIN_FUNC0_DIV": "A0",
        "PIN_MOTOR0_DIV": "A1",
        "PIN_MOTOR1_DIV": "A2",
        "PIN_FUNC1_DIV": "A3",
        "PIN_DEF_FAULT_A": "A4",
        "PIN_DCC0_HIGH": "2",
        "PIN_DCC0_LOW": "4",
        "PIN_DCC1_HIGH": "6",
        "PIN_DCC1_LOW": "8",
    }

    for pin_name, pin_val in expected_pins.items():
        pattern = r"const\s+uint8_t\s+" + pin_name + r"\s*=\s*" + pin_val + r"\s*;"
        if not re.search(pattern, code):
            errors.append(f"Missing or incorrect definition for {pin_name} = {pin_val}")

    # Check NMRA DCC timing constants
    if "DCC_BIT_1_HALF_PERIOD_US  58" not in code and "DCC_BIT_1_HALF_PERIOD_US 58" not in code:
        errors.append("Missing DCC_BIT_1_HALF_PERIOD_US definition (58 us)")

    if "DCC_BIT_0_HALF_PERIOD_US 100" not in code:
        errors.append("Missing DCC_BIT_0_HALF_PERIOD_US definition (100 us)")

    # Check required functions
    required_funcs = [
        "setHBridgeOutputs",
        "setupDccTimer",
        "buildSpeedPacket",
        "buildFunctionPacket",
        "readScaledVoltage",
        "printDecoderTelemetry",
        "checkFaultStatus",
        "handleSerialCommand",
        "setup",
        "loop"
    ]

    for func in required_funcs:
        if func not in code:
            errors.append(f"Missing required function or ISR component: {func}")

    # Check ISR definition
    if "ISR(TIMER1_COMPA_vect)" not in code:
        errors.append("Missing Timer1 compare match ISR for DCC signal generation")

    if errors:
        print("\n❌ Validation Failed with the following errors:")
        for err in errors:
            print(f"  - {err}")
        return False
    else:
        print("\n✅ All sketch checks passed successfully!")
        return True

if __name__ == "__main__":
    sketch_file = "src/dcc_decoder_tester.ino"
    if len(sys.argv) > 1:
        sketch_file = sys.argv[1]

    success = validate_sketch(sketch_file)
    if not success:
        sys.exit(1)
    sys.exit(0)
