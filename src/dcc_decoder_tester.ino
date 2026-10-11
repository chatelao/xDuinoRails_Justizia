/*
 * Arduino DCC Decoder Tester
 * ============================================================================
 * Hardware Pin Mapping:
 *   Pin 9  / A0    : FUNC0_DIV    (Analog input: Scaled Function 0 voltage)
 *   Pin 10 / A1    : MOTOR0_DIV   (Analog input: Scaled Motor 0 voltage)
 *   Pin 11 / A2    : MOTOR1_DIV   (Analog input: Scaled Motor 1 voltage)
 *   Pin 12 / A3    : FUNC1_DIV    (Analog input: Scaled Function 1 voltage)
 *   Pin 13 / SDA/A4: def_fault_a  (Digital input: Active-LOW Hardware Fault)
 *   Pin 17 / D2    : DCC0.HIGH    (Digital output: H-Bridge Rail 0 High-side)
 *   Pin 19 / D4    : DCC0.LOW     (Digital output: H-Bridge Rail 0 Low-side)
 *   Pin 21 / D6    : DCC1.HIGH    (Digital output: H-Bridge Rail 1 High-side)
 *   Pin 23 / D8    : DCC1.LOW     (Digital output: H-Bridge Rail 1 Low-side)
 * ============================================================================
 */

#include <Arduino.h>

// ----------------------------------------------------------------------------
// Pin Definitions (Mapped to Arduino Pin Labels and Physical Header Numbers)
// ----------------------------------------------------------------------------
const uint8_t PIN_FUNC0_DIV   = A0; // Pin 9  - Function 0 divider input
const uint8_t PIN_MOTOR0_DIV  = A1; // Pin 10 - Motor 0 divider input
const uint8_t PIN_MOTOR1_DIV  = A2; // Pin 11 - Motor 1 divider input
const uint8_t PIN_FUNC1_DIV   = A3; // Pin 12 - Function 1 divider input
const uint8_t PIN_DEF_FAULT_A = A4; // Pin 13 - Fault sense (SDA / A4)

const uint8_t PIN_DCC0_HIGH   = 2;  // Pin 17 - DCC Rail 0 High Side (D2)
const uint8_t PIN_DCC0_LOW    = 4;  // Pin 19 - DCC Rail 0 Low Side  (D4)
const uint8_t PIN_DCC1_HIGH   = 6;  // Pin 21 - DCC Rail 1 High Side (D6)
const uint8_t PIN_DCC1_LOW    = 8;  // Pin 23 - DCC Rail 1 Low Side  (D8)

// ----------------------------------------------------------------------------
// NMRA DCC Constants & Timing Specifications
// ----------------------------------------------------------------------------
// Microsecond half-period times for NMRA DCC encoding
#define DCC_BIT_1_HALF_PERIOD_US  58
#define DCC_BIT_0_HALF_PERIOD_US 100

// Voltage divider ratio factor: (R1 + R2) / R2 = (33k + 10k) / 10k = 4.3
const float VOLTAGE_DIVIDER_FACTOR = 4.30f;
const float ADC_REF_VOLTAGE        = 5.00f;

// ----------------------------------------------------------------------------
// DCC Packet & Queue Buffers
// ----------------------------------------------------------------------------
#define DCC_MAX_PACKET_BYTES 6

struct DCCPacket {
  uint8_t data[DCC_MAX_PACKET_BYTES];
  uint8_t len;
};

// Current active packet sent in loop
volatile DCCPacket currentPacket;
volatile uint8_t currentByteIdx = 0;
volatile uint8_t currentBitIdx = 7;
volatile bool currentHalfBitPhase = false; // false = Phase A, true = Phase B
volatile bool dccOutputEnabled = true;
volatile bool systemFaultDetected = false;

// Packet buffer queue
DCCPacket idlePacket = {{0xFF, 0x00, 0xFF}, 3};
DCCPacket activePacket = {{0xFF, 0x00, 0xFF}, 3};

// ----------------------------------------------------------------------------
// Signal Generation Output Drivers
// ----------------------------------------------------------------------------
void setHBridgeOutputs(bool phase) {
  if (!dccOutputEnabled || systemFaultDetected) {
    // Disable all H-bridge transistors in fault or disabled state
    digitalWrite(PIN_DCC0_HIGH, LOW);
    digitalWrite(PIN_DCC0_LOW,  LOW);
    digitalWrite(PIN_DCC1_HIGH, LOW);
    digitalWrite(PIN_DCC1_LOW,  LOW);
    return;
  }

  // Dead-time protection: turn off high-sides first before switching
  digitalWrite(PIN_DCC0_HIGH, LOW);
  digitalWrite(PIN_DCC1_HIGH, LOW);

  if (!phase) {
    // Phase A: Rail 0 = HIGH, Rail 1 = LOW
    digitalWrite(PIN_DCC0_LOW,  LOW);
    digitalWrite(PIN_DCC1_LOW,  HIGH);
    digitalWrite(PIN_DCC0_HIGH, HIGH);
  } else {
    // Phase B: Rail 0 = LOW, Rail 1 = HIGH
    digitalWrite(PIN_DCC0_LOW,  HIGH);
    digitalWrite(PIN_DCC1_LOW,  LOW);
    digitalWrite(PIN_DCC1_HIGH, HIGH);
  }
}

// ----------------------------------------------------------------------------
// Timer Interrupt (DCC Signal Generator)
// ----------------------------------------------------------------------------
void setupDccTimer() {
  cli(); // Disable interrupts
  // Clear Timer1 control registers
  TCCR1A = 0;
  TCCR1B = 0;
  TCNT1  = 0;

  // Set CTC mode (Clear Timer on Compare Match)
  TCCR1B |= (1 << WGM12);
  // Set Prescaler to 8 -> 16MHz / 8 = 2MHz (0.5us per tick)
  TCCR1B |= (1 << CS11);

  // Default to 58us half period (116 ticks at 0.5us per tick)
  OCR1A = (DCC_BIT_1_HALF_PERIOD_US * 2) - 1;

  // Enable Timer1 compare interrupt A
  TIMSK1 |= (1 << OCIE1A);
  sei(); // Enable interrupts
}

ISR(TIMER1_COMPA_vect) {
  // Toggle polarity phase
  currentHalfBitPhase = !currentHalfBitPhase;
  setHBridgeOutputs(currentHalfBitPhase);

  // Advance bit state machine when completing a full cycle (end of Phase B)
  if (!currentHalfBitPhase) {
    // Fetch next bit to transmit
    uint8_t currentByte = currentPacket.data[currentByteIdx];
    bool bitVal = (currentByte >> currentBitIdx) & 0x01;

    // Set next timer period based on current bit value
    uint16_t halfPeriodUs = bitVal ? DCC_BIT_1_HALF_PERIOD_US : DCC_BIT_0_HALF_PERIOD_US;
    OCR1A = (halfPeriodUs * 2) - 1;

    // Advance bit index
    if (currentBitIdx == 0) {
      currentBitIdx = 7;
      currentByteIdx++;
      if (currentByteIdx >= currentPacket.len) {
        currentByteIdx = 0;
        // Reload active packet
        currentPacket = activePacket;
      }
    } else {
      currentBitIdx--;
    }
  }
}

// ----------------------------------------------------------------------------
// NMRA DCC Packet Construction Helper Functions
// ----------------------------------------------------------------------------
DCCPacket buildSpeedPacket(uint8_t address, uint8_t speedStep, bool forward) {
  DCCPacket pkt;
  // Standard Preamble: 14 '1' bits sent as preamble byte 0xFF and top 6 bits of byte 0xFF
  // For simplicity, buffer contains byte payload with start/stop bits or framed raw bytes
  pkt.data[0] = address & 0x7F; // 7-bit decoder address

  // Speed instruction byte: 01DC SSSS (D=Direction, C=Speed LSB / C-bit)
  uint8_t speedByte = 0x40; // Base speed command prefix
  if (forward) speedByte |= 0x20; // Set Direction bit
  speedByte |= (speedStep & 0x1F);

  pkt.data[1] = speedByte;
  pkt.data[2] = pkt.data[0] ^ pkt.data[1]; // XOR Checksum byte
  pkt.len = 3;
  return pkt;
}

DCCPacket buildFunctionPacket(uint8_t address, bool f0, bool f1) {
  DCCPacket pkt;
  pkt.data[0] = address & 0x7F;
  // Function Group 1: 100D F4 F3 F2 F1 (where D is F0 / FL)
  uint8_t funcByte = 0x80;
  if (f0) funcByte |= 0x10; // FL / F0
  if (f1) funcByte |= 0x01; // F1

  pkt.data[1] = funcByte;
  pkt.data[2] = pkt.data[0] ^ pkt.data[1];
  pkt.len = 3;
  return pkt;
}

// ----------------------------------------------------------------------------
// Analog Voltage Reading & Measurement Functions
// ----------------------------------------------------------------------------
float readScaledVoltage(uint8_t pin) {
  uint32_t sum = 0;
  const uint8_t samples = 16;
  for (uint8_t i = 0; i < samples; i++) {
    sum += analogRead(pin);
    delayMicroseconds(50);
  }
  float avgAdc = (float)sum / samples;
  float rawVoltage = (avgAdc / 1023.0f) * ADC_REF_VOLTAGE;
  return rawVoltage * VOLTAGE_DIVIDER_FACTOR;
}

void printDecoderTelemetry() {
  float vFunc0  = readScaledVoltage(PIN_FUNC0_DIV);
  float vMotor0 = readScaledVoltage(PIN_MOTOR0_DIV);
  float vMotor1 = readScaledVoltage(PIN_MOTOR1_DIV);
  float vFunc1  = readScaledVoltage(PIN_FUNC1_DIV);
  float vMotorDiff = abs(vMotor0 - vMotor1);

  Serial.println(F("--- DECODER TELEMETRY READOUT ---"));
  Serial.print(F("FUNC0 Voltage (Pin 9 / A0):   ")); Serial.print(vFunc0, 2); Serial.println(F(" V"));
  Serial.print(F("MOTOR0 Voltage (Pin 10 / A1): ")); Serial.print(vMotor0, 2); Serial.println(F(" V"));
  Serial.print(F("MOTOR1 Voltage (Pin 11 / A2): ")); Serial.print(vMotor1, 2); Serial.println(F(" V"));
  Serial.print(F("FUNC1 Voltage (Pin 12 / A3):  ")); Serial.print(vFunc1, 2); Serial.println(F(" V"));
  Serial.print(F("Motor Differential Voltage:   ")); Serial.print(vMotorDiff, 2); Serial.println(F(" V"));
  Serial.print(F("Hardware Fault Line (A4):    "));
  Serial.println(digitalRead(PIN_DEF_FAULT_A) == LOW ? F("FAULT TRIGGERED") : F("OK"));
  Serial.println(F("---------------------------------"));
}

// ----------------------------------------------------------------------------
// Hardware Fault & Safety Routines
// ----------------------------------------------------------------------------
void checkFaultStatus() {
  // active-LOW fault pin check
  if (digitalRead(PIN_DEF_FAULT_A) == LOW) {
    if (!systemFaultDetected) {
      systemFaultDetected = true;
      dccOutputEnabled = false;
      setHBridgeOutputs(false);
      Serial.println(F("\n[EMERGENCY TRIP] Hardware Fault Detected on pin def_fault_a (A4/13)! Rail outputs disabled."));
    }
  }
}

void resetFault() {
  if (digitalRead(PIN_DEF_FAULT_A) == HIGH) {
    systemFaultDetected = false;
    dccOutputEnabled = true;
    Serial.println(F("[SYSTEM OK] Fault cleared. Normal DCC operation restored."));
  } else {
    Serial.println(F("[ERROR] Cannot reset fault: def_fault_a pin is still LOW."));
  }
}

// ----------------------------------------------------------------------------
// Interactive Serial Command Processing
// ----------------------------------------------------------------------------
void printMenu() {
  Serial.println(F("\n====== ARDUINO DCC DECODER TESTER CLI ======"));
  Serial.println(F("Commands:"));
  Serial.println(F("  '1' : Send Idle Packets"));
  Serial.println(F("  '2' : Set Motor Speed Forward (Step 14)"));
  Serial.println(F("  '3' : Set Motor Speed Reverse (Step 14)"));
  Serial.println(F("  '4' : Set Motor Stop"));
  Serial.println(F("  '5' : Toggle Function F0 (FL) ON"));
  Serial.println(F("  '6' : Toggle Function F1 ON"));
  Serial.println(F("  '7' : Turn Functions OFF"));
  Serial.println(F("  'r' : Read Telemetry / Voltage Dividers"));
  Serial.println(F("  'c' : Clear Fault State"));
  Serial.println(F("  's' : Emergency Stop Outputs"));
  Serial.println(F("============================================"));
}

void handleSerialCommand(char cmd) {
  const uint8_t targetAddress = 3; // Default short address 3

  switch (cmd) {
    case '1':
      activePacket = idlePacket;
      Serial.println(F("Transmitting DCC Idle Packets..."));
      break;
    case '2':
      activePacket = buildSpeedPacket(targetAddress, 14, true);
      Serial.println(F("DCC Command: Address 3 -> Speed Forward 14"));
      break;
    case '3':
      activePacket = buildSpeedPacket(targetAddress, 14, false);
      Serial.println(F("DCC Command: Address 3 -> Speed Reverse 14"));
      break;
    case '4':
      activePacket = buildSpeedPacket(targetAddress, 0, true);
      Serial.println(F("DCC Command: Address 3 -> Motor Stop"));
      break;
    case '5':
      activePacket = buildFunctionPacket(targetAddress, true, false);
      Serial.println(F("DCC Command: Address 3 -> Function F0 ON, F1 OFF"));
      break;
    case '6':
      activePacket = buildFunctionPacket(targetAddress, false, true);
      Serial.println(F("DCC Command: Address 3 -> Function F0 OFF, F1 ON"));
      break;
    case '7':
      activePacket = buildFunctionPacket(targetAddress, false, false);
      Serial.println(F("DCC Command: Address 3 -> Functions F0/F1 OFF"));
      break;
    case 'r':
      printDecoderTelemetry();
      break;
    case 'c':
      resetFault();
      break;
    case 's':
      dccOutputEnabled = false;
      setHBridgeOutputs(false);
      Serial.println(F("EMERGENCY STOP: Rail power disabled."));
      break;
    case '?':
    case 'h':
      printMenu();
      break;
    default:
      break;
  }
}

// ----------------------------------------------------------------------------
// Setup & Main Loop
// ----------------------------------------------------------------------------
void setup() {
  // Initialize Serial interface
  Serial.begin(115200);
  while (!Serial && millis() < 2000);

  Serial.println(F("Initializing Arduino DCC Decoder Tester..."));

  // Configure Output Pins for Dual H-Bridge Rails
  pinMode(PIN_DCC0_HIGH, OUTPUT);
  pinMode(PIN_DCC0_LOW,  OUTPUT);
  pinMode(PIN_DCC1_HIGH, OUTPUT);
  pinMode(PIN_DCC1_LOW,  OUTPUT);

  // Initialize outputs to safe inactive state
  digitalWrite(PIN_DCC0_HIGH, LOW);
  digitalWrite(PIN_DCC0_LOW,  LOW);
  digitalWrite(PIN_DCC1_HIGH, LOW);
  digitalWrite(PIN_DCC1_LOW,  LOW);

  // Configure Analog & Fault Input Pins
  pinMode(PIN_FUNC0_DIV,   INPUT);
  pinMode(PIN_MOTOR0_DIV,  INPUT);
  pinMode(PIN_MOTOR1_DIV,  INPUT);
  pinMode(PIN_FUNC1_DIV,   INPUT);
  pinMode(PIN_DEF_FAULT_A, INPUT_PULLUP); // Active LOW hardware fault input

  // Set default DCC packet
  currentPacket = idlePacket;

  // Initialize Timer Interrupt for DCC Generation
  setupDccTimer();

  Serial.println(F("DCC Generator and Tester initialized successfully."));
  printMenu();
}

void loop() {
  // Monitor hardware fault input line continuously
  checkFaultStatus();

  // Process incoming Serial commands
  if (Serial.available() > 0) {
    char cmd = Serial.read();
    handleSerialCommand(cmd);
  }

  delay(10);
}
