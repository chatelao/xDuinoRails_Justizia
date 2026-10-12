# Testprotokoll Thor

## Inhaltsverzeichnis
- Testaufbau (S. 2)
  - Aussenschnittstelle des Decoders (S. 2)
  - Innenmesspunkte des Decoders (S. 3)
- Testprotokoll (S. 4)
  - Stromversorgung (S. 4)
    - BR - Brückengleichrichter (Bridge Rectifier) (S. 4)
    - PWR - Stromversorgung (Voltage supply) (S. 4)
  - Protokolle Zentrale zu Decoder (S. 5)
    - Digitale Protokolle Zentrale zu Decoder (DCC/MM/SX) (S. 5)
    - Analoge Protokolle Zentrale zu Decoder (AC/DC) (S. 5)
  - Protokolle Decoder zu Zentrale (S. 6)
    - Digitale Protokolle Decoder zu Zentrale (S. 6)
    - DCC-Acknowledge (S. 6)
    - Railcom (S. 6)
  - Ein-/Ausgänge Decoder zu Funktionen (S. 7)
    - Motor (S. 7)
    - Funktionsausgänge (S. 7)
  - Fahrtkontrolle des Decoder (S. 8)
    - Highlevel Befehle decodieren (S. 8)
    - Motorensteuerung anwenden (S. 8)

---

## 1. Testaufbau

### 1.1 Aussenschnittstelle des Decoders
Messpunkt | Expected mode | Ansteuerung | Messverfahren
-- | -- | -- | --
DCC0 | Input 0-30V | Via externe H-Brücke |
DCC1 | Input 0-30V | Via externe H-Brücke |
U+ | Output 0-30V | | ADC via Spannungsteiler 1:10
GND | 0V (relativ zu U+) | | ADC via Spannungsteiler 1:10
M0_AMP | Output 0-30V | | ADC via Spannungsteiler 1:10
M1_AMP | Output 0-30V | | ADC via Spannungsteiler 1:10
F0_AMP | Output GND oder Open-Drain | | ADC via Spannungsteiler 1:10
F1_AMP | Output 0-30V | | ADC via Spannungsteiler 1:10

### 1.2 Innenmesspunkte des Decoders
Messpunkt | Expected mode | Ansteuerung | Messverfahren
-- | -- | -- | --
GND | 0V (relativ zu U+) | | ADC via Spannungsteiler 1:10
5V | 5V (relativ zu GND) | | ADC via Spannungsteiler 1:10
3v3 | 3.3V (relativ zu GND) | | ADC via Spannungsteiler 1:10
M0 | Input 3v3 | GPIO (3v3) |
M1 | Input 3v3 | GPIO (3v3) |
F0 | Input 3v3 | GPIO (3v3) |
F1 | Input 3v3 | GPIO (3v3) |
bEMF-A | Output 0-3v3 | | ADC

---

## 2. Testprotokoll

### 2.1 Stromversorgung

#### BR - Brückengleichrichter (Bridge Rectifier)
ID | Testcase | Erwartetes Testresult | Effektives Resultat
-- | -- | -- | --
PWR-BR-1 | DCC0 = GND, DCC1 = 12V | U+ = >11V |
PWR-BR-2 | DCC0 = 12V, DCC1 = GND | U+ = >11V |

#### PWR - Stromversorgung (Voltage supply)
ID | Testcase | Erwartetes Testresult | Effektives Resultat
-- | -- | -- | --
PWR-5V | DCC0 = GND, DCC1 = 12V | +5V is close to +5V |
PWR-3v3 | DCC0 = GND, DCC1 = 12V | +3v3 from MCU is close to +3v3 |

---

### 2.2 Protokolle Zentrale zu Decoder

#### Digitale Protokolle Zentrale zu Decoder (DCC/MM/SX)
ID | Testcase | Erwartetes Testresult | Effektives Resultat
-- | -- | -- | --
MM/DCC-OFF | DCC0 = 12V, DCC1 = GND | Dxx = Off (0v) |
MM/DCC-ON | DCC0 = GND, DCC1 = 12V | Dxx = On (12v, max 1mA), Axx = Xv (12 / ??? = ) |

#### Analoge Protokolle Zentrale zu Decoder (AC/DC)
ID | Testcase | Erwartetes Testresult | Effektives Resultat
-- | -- | -- | --
2V | DCC1 = 2V | Axx = Xv (2 / ??? = ) |
6V | DCC1 = 6V | Axx = Xv (6 / ??? = ) |
10V | DCC1 = 8V | Axx = Xv (8 / ??? = ) |
24V | DCC1 = 24V | Axx = Xv (8 / ??? = ) |

---

### 2.3 Protokolle Decoder zu Zentrale

#### Digitale Protokolle Decoder zu Zentrale

##### DCC-Acknowledge
ID | Testcase | Erwartetes Testresult | Effektives Resultat
-- | -- | -- | --
DCC-ACK-ON | DCC0 = GND, DCC1 = 12V | DCC-ACK = 3v3, +60mA load at DCC1/0 |
DCC-ACK-OFF | DCC0 = GND, DCC1 = 12V | DCC-ACK = GND, (Zero) normal load at DCC1/0 |

##### Railcom
ID | Testcase | Erwartetes Testresult | Effektives Resultat
-- | -- | -- | --
RC-ON | DCC0-DCC1 shunt (short) | Railcom-TX = GND, USB-Power (5v => 3v3 for Constant Current Source), 18mA source at DCC1/0 |
RC-OFF | DCC0-DCC1 shunt (short) | Railcom-TX = 3v3, Zero source at DCC1/0 |

---

### 2.4 Ein-/Ausgänge Decoder zu Funktionen

#### Motor
ID | Testcase | Erwartetes Testresult | Effektives Resultat
-- | -- | -- | --
H-Bridge fwd | High / Low | 11V / Normale Polarität |
H-Bridge bwd | Low / High | 11V / Inverse Polarität |
H-Bridge off | Low / Low | Hoher Widerstand |
H-Bridge brake | High / High | Niederiger Widerstand |

#### Funktionsausgänge
ID | Testcase | Erwartetes Testresult | Effektives Resultat
-- | -- | -- | --
F0f on | F0 = 5v | F0 leitet gegen GND |
F0f off | F0 = GND | F0 leitet nicht gegen GND |
F0b on | F1 = 5v | F1 leitet gegen GND |
F0b off | F1 = GND | F1 leitet nicht gegen GND |

---

### 2.5 Fahrtkontrolle des Decoder

#### Highlevel Befehle decodieren
ID | Testcase | Erwartetes Testresult | Effektives Resultat
-- | -- | -- | --
MM v0.2 | MM v0.2 Protocol Command | Speed / Dir / Func decoded |
DCC v0.2 | DCC v0.2 Protocol Command | Speed / Dir / Func decoded |
SX v0.2 | SX v0.2 Protocol Command | Speed / Dir / Func decoded |

#### Motorensteuerung anwenden
ID | Testcase | Erwartetes Testresult | Effektives Resultat
-- | -- | -- | --
Medium | Medium Speed Command | 50% PWM open-loop |
Rangiergang | Shunting Speed Command | Gaaaanz langsam fahren |
Fast | Fast Speed Command | 90% PWM open-loop |
