# Statische Testfallspezifikation - ThorTestaufbau (TESTS_THOR_TEST.md)

## 1. Übersicht und Einleitung

Dieses Dokument definiert die detaillierten **statischen Einzeltestfälle** für den Thor-Testaufbau (**ThorTestaufbau** / DCC Decoder Tester), basierend auf dem Testkonzept in `CONCEPT_THOR_TEST.md`.

Die Testfälle decken die funktionale und elektrische Überprüfung der Schnittstellen des Decoders (Aussenschnittstelle & Messpunkte), die Stromversorgung (BR/PWR), die digitalen/analogen Steuerprotokolle (DCC, MM, SX, AC, DC), die Rückmeldeverfahren (DCC-ACK, RailCom), die Motor- und Funktionsausgänge (M0_AMP, M1_AMP, F0_AMP, F1_AMP) sowie die Hardware-Schutzschaltungen (`def_fault_a`) ab.

### Schnittstellen- und Messpunktübersicht
| Messpunkt | Typ / Modus | Signalnetz | Beschreibung / Hardware-Schnittstelle |
| :--- | :--- | :--- | :--- |
| **DCC0** | Input (0–30V) | Rail 0 | Gleissignal-Eingang 0 via externe H-Brücke |
| **DCC1** | Input (0–30V) | Rail 1 | Gleissignal-Eingang 1 via externe H-Brücke |
| **U+** | Output (0–30V) | Common Positive | Gemeinsamer positiver Rückleiter des Decoders |
| **GND** | Reference (0V) | System Ground | Bezugspotenzial (0V relativ zu U+) |
| **M0_AMP** | Output (0–30V) | Motor 0 / A | Motorausgang Phase A (PWM) |
| **M1_AMP** | Output (0–30V) | Motor 1 / B | Motorausgang Phase B (PWM) |
| **F0_AMP** | Output (0–30V / GND) | Function 0 / FL | Funktionsausgang Light / Aux 0 (Open-Drain / Low-Side) |
| **F1_AMP** | Output (0–30V) | Function 1 / FR | Funktionsausgang Aux 1 (High-Side / Switched) |
| **def_fault_a** | Input (Digital Int) | Hardware Fault | Active-LOW Hardware-Fehlersignal |

---

## 2. Matrix der Statischen Testfälle (Static Test Cases Summary)

| Testfall-ID | Ref. TS | Bereich / Kategorie | Messpunkt | Kurzbeschreibung | Sollwert / Erwartung |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **ST-PWR-01** | TS-01 | Stromversorgung (BR/PWR) | U+ / GND | DC-Ausgangsspannung bei Nennspannung | $U_+ = U_{\text{DCC}} - 2 \cdot V_D \approx 13.6\,\text{V} \dots 16.6\,\text{V}$ |
| **ST-PWR-02** | TS-01 | Stromversorgung (BR/PWR) | GND | Potenzialprüfung System-GND | $0\,\text{V}$ bezogen auf Tester-GND |
| **ST-PWR-03** | TS-01 | Stromversorgung (BR/PWR) | U+ | Minimal-Eingangsspannung (Under-Voltage) | $U_+ \ge 5.5\,\text{V}$ bei $U_{\text{IN}} = 7.0\,\text{V}$ |
| **ST-PWR-04** | TS-01 | Stromversorgung (BR/PWR) | U+ | Maximal-Eingangsspannung (Over-Voltage) | $U_+ \le 28.5\,\text{V}$ bei $U_{\text{IN}} = 30.0\,\text{V}$ |
| **ST-PWR-05** | TS-01 | Spannungsteiler | A0–A3 | ADC-Skalierung (1:10 bzw. Factor 4.30) | $V_{\text{ADC}} = V_{\text{IN}} / 4.30 \pm 2\%$ |
| **ST-DCC-01** | TS-02 | Digital-Protokoll (DCC) | DCC0 / DCC1 | Statische Pegelprüfung High/Low | $U_{\text{High}} \ge 12\,\text{V}$, $U_{\text{Low}} \le 0.5\,\text{V}$ |
| **ST-DCC-02** | TS-02 | Digital-Protokoll (DCC) | DCC0 / DCC1 | NMRA Bit '1' Timing (58 µs Half-Period) | $t_{\text{half}} = 58\,\mu\text{s} \pm 3\,\mu\text{s}$ |
| **ST-DCC-03** | TS-02 | Digital-Protokoll (DCC) | DCC0 / DCC1 | NMRA Bit '0' Timing (100 µs Half-Period) | $t_{\text{half}} = 100\,\mu\text{s} \pm 5\,\mu\text{s}$ |
| **ST-DCC-04** | TS-02 | Digital-Protokoll (DCC) | DCC0 / DCC1 | NMRA Preamble Timing | $\ge 14$ aufeinanderfolgende Logisch '1' Bits |
| **ST-DCC-05** | TS-02 | Digital-Protokoll (DCC) | Decoder | XOR Checksum Validierung | Paket wird verarbeitet, kein Bitfehler |
| **ST-ANA-01** | TS-03 | Analog-Protokoll (DC) | M0_AMP / M1_AMP | DC Vorwärts (DCC0=+15V, DCC1=GND) | $V(M0) \approx U_+$, $V(M1) \approx 0\,\text{V}$ |
| **ST-ANA-02** | TS-03 | Analog-Protokoll (DC) | M0_AMP / M1_AMP | DC Rückwärts (DCC0=GND, DCC1=+15V) | $V(M0) \approx 0\,\text{V}$, $V(M1) \approx U_+$ |
| **ST-ANA-03** | TS-03 | Analog-Protokoll (AC) | M0_AMP / M1_AMP | AC Analogmodus (50 Hz, 16V AC) | $V_{\text{eff}}(M0/M1) \approx 12\dots15\,\text{V}$ |
| **ST-ACK-01** | TS-04 | Decoder -> Zentrale (ACK) | DCC0 / DCC1 | Basic ACK Stromimpuls | $I_{\text{ACK}} \ge 60\,\text{mA}$, $t_{\text{ACK}} = 6\,\text{ms} \pm 1\,\text{ms}$ |
| **ST-ACK-02** | TS-04 | Decoder -> Zentrale (ACK) | Messwiderstand | CV-Leseauftrag Acknowledge | Spannungsimpuls am Shunt-Widerstand |
| **ST-RC-01** | TS-05 | Decoder -> Zentrale (RailCom) | DCC0 / DCC1 | RailCom Cutout Erzeugung | Austastlücke $t_{\text{cutout}} = 488\,\mu\text{s} \pm 10\,\mu\text{s}$ |
| **ST-RC-02** | TS-05 | Decoder -> Zentrale (RailCom) | DCC0 / DCC1 | RailCom Datensignal Channel 1 & 2 | Datenübertragung während Cutout aktiv |
| **ST-MOT-01** | TS-06 | Ein-/Ausgänge Motor | M0_AMP / M1_AMP | Vorwärtsfahrt Fahrstufe 14 | $V(M0) > V(M1)$, PWM Duty Cycle ~50% |
| **ST-MOT-02** | TS-06 | Ein-/Ausgänge Motor | M0_AMP / M1_AMP | Rückwärtsfahrt Fahrstufe 14 | $V(M1) > V(M0)$, PWM Duty Cycle ~50% |
| **ST-MOT-03** | TS-06 | Ein-/Ausgänge Motor | M0_AMP / M1_AMP | Motor Stop (Fahrstufe 0) | $V(M0) = 0\,\text{V}$, $V(M1) = 0\,\text{V}$, Diff = 0V |
| **ST-FUNC-01** | TS-07 | Ein-/Ausgänge Funktion | F0_AMP | F0 Einschalten (FL / Aux 0) | F0_AMP schaltet nach GND ($V < 0.5\,\text{V}$) |
| **ST-FUNC-02** | TS-07 | Ein-/Ausgänge Funktion | F0_AMP | F0 Ausschalten | F0_AMP hochohmig / $V \approx U_+$ via Pullup |
| **ST-FUNC-03** | TS-07 | Ein-/Ausgänge Funktion | F1_AMP | F1 Einschalten (Aux 1) | F1_AMP gibt Spannung aus ($V \approx U_+$) |
| **ST-CTRL-01**| TS-08 | Fahrtkontrolle | M0_AMP / M1_AMP | Dynamische Fahrstufenänderung (0–128) | Kontinuierliche PWM-Anpassung |
| **ST-FLT-01** | TS-09 | Hardware-Fehler | def_fault_a | Emergency Trip bei Low-Signal | DCC-Gleisausgänge sofort $0\,\text{V}$ |
| **ST-FLT-02** | TS-09 | Hardware-Fehler | def_fault_a | Reset & Recovery Routine | Ausgänge werden nach Freigabe reaktiviert |

---

## 3. Detaillierte Statische Testfallspezifikationen

### 3.1 Kategorie 1: Stromversorgung & Brückengleichrichter (PWR / BR) [TS-01]

#### ST-PWR-01: Nennspannungsausgabe U+ am Brückengleichrichter
* **Testfall-ID:** ST-PWR-01
* **Referenz-Testschritt:** TS-01
* **Testgegenstand / Messpunkt:** `U+` (Pin 27 / D12), `GND`
* **Voraussetzungen / Testaufbau:** Tester mit Spannungsversorgung verbunden; DCC0 und DCC1 mit Rechtecksignal $\pm 16\,\text{V}_{\text{peak}}$ beaufschlagt.
* **Eingangssignal:** $U_{\text{DCC}} = 16.0\,\text{V}$ (AC/Digital Rechteck, 10 kHz).
* **Messverfahren:** Spannungsmessung via ADC an Pin `U+_DIV` (Voltage Divider 1:10 / Factor 4.30) und Kontrollmessung mit Digitalmultimeter (DMM).
* **Erwartetes Ergebnis:** Die gleichgerichtete DC-Spannung $U_+$ beträgt nominal:
  $$U_+ = U_{\text{DCC}} - 2 \cdot V_{\text{Diode}} \approx 16.0\,\text{V} - 2 \cdot 0.7\,\text{V} = 14.6\,\text{V}$$
* **Toleranz / Akzeptanzkriterium:** $13.8\,\text{V} \le U_+ \le 15.4\,\text{V}$ ($\pm 5\%$).

#### ST-PWR-02: Referenzpotenzialprüfung System-GND
* **Testfall-ID:** ST-PWR-02
* **Referenz-Testschritt:** TS-01
* **Testgegenstand / Messpunkt:** `GND` (Bezugspotenzial relativ zu U+)
* **Voraussetzungen / Testaufbau:** Masseanschluss der Testplatine mit der Versorgungsquelle verbunden.
* **Eingangssignal:** Inaktive / Aktive Speisung an DCC0/DCC1.
* **Messverfahren:** Spannungsmessung DMM zwischen Tester-System-GND und Decoder-Massepunkt.
* **Erwartetes Ergebnis:** Potenzialdifferenz ist minimal ($0.0\,\text{V}$).
* **Toleranz / Akzeptanzkriterium:** $V_{\text{GND}} \le 50\,\text{mV}$.

#### ST-PWR-03: Unterspannungs-Grenzprüfung (Under-Voltage Limit)
* **Testfall-ID:** ST-PWR-03
* **Referenz-Testschritt:** TS-01
* **Testgegenstand / Messpunkt:** `U+`, `VIN` (Pin 25 / D10)
* **Voraussetzungen / Testaufbau:** Regelbares Labornetzgerät an DCC0/DCC1.
* **Eingangssignal:** Minimal zugelassene Eingangsspannung $U_{\text{DCC}} = 7.0\,\text{V}$ DC.
* **Messverfahren:** Kontinuierliche ADC-Erfassung an `PIN_VIN` und `PIN_U_PLUS`.
* **Erwartetes Ergebnis:** Der Decoder bleibt betriebsbereit; $U_+$ liegt bei ca. $5.6\,\text{V}$.
* **Toleranz / Akzeptanzkriterium:** $U_+ \ge 5.0\,\text{V}$, kein ungeplanter Reset der Logikschaltung.

#### ST-PWR-04: Überspannungs-Grenzprüfung (Over-Voltage Limit)
* **Testfall-ID:** ST-PWR-04
* **Referenz-Testschritt:** TS-01
* **Testgegenstand / Messpunkt:** `U+`, `VIN` (Pin 25 / D10)
* **Voraussetzungen / Testaufbau:** Labornetzgerät mit Strombegrenzung (max. 1.0 A).
* **Eingangssignal:** Maximal zugelassene Eingangsspannung $U_{\text{DCC}} = 30.0\,\text{V}$ DC.
* **Messverfahren:** Spannungsmessung an U+; Überwachung des Ruhestroms.
* **Erwartetes Ergebnis:** $U_+$ steigt proportional auf ca. $28.6\,\text{V}$; keine unzulässige Erwärmung oder Bauteilschädigung.
* **Toleranz / Akzeptanzkriterium:** $U_+ \le 29.0\,\text{V}$, Stromaufnahme im Leerlauf $< 50\,\text{mA}$.

#### ST-PWR-05: Genauigkeitsprüfung der analogen Spannungsteiler (1:10 / Factor 4.30)
* **Testfall-ID:** ST-PWR-05
* **Referenz-Testschritt:** TS-01
* **Testgegenstand / Messpunkt:** `A0` (`FUNC0_DIV`), `A1` (`MOTOR0_DIV`), `A2` (`MOTOR1_DIV`), `A3` (`FUNC1_DIV`)
* **Voraussetzungen / Testaufbau:** Kalibrierte Gleichspannung $U_{\text{TEST}} = 10.00\,\text{V}$ an den Divider-Eingängen anlegen.
* **Eingangssignal:** Statische DC-Spannung $10.00\,\text{V}$.
* **Messverfahren:** ADC-Wert am ATmega / MicroController auslesen.
* **Erwartetes Ergebnis:** $V_{\text{ADC}} = \frac{10.00\,\text{V}}{4.30} \approx 2.325\,\text{V}$ (entspricht ADC-Wert $\approx 476$ bei 10-Bit $5\,\text{V}$-Referenz).
* **Toleranz / Akzeptanzkriterium:** Abweichung $\le \pm 2\%$.

---

### 3.2 Kategorie 2: Digitale Protokolle Zentrale -> Decoder (DCC / MM / SX) [TS-02]

#### ST-DCC-01: Statischer Signalpegel am DCC H-Brückenausgang
* **Testfall-ID:** ST-DCC-01
* **Referenz-Testschritt:** TS-02
* **Testgegenstand / Messpunkt:** `DCC0.HIGH` (Pin 17), `DCC0.LOW` (Pin 19), `DCC1.HIGH` (Pin 21), `DCC1.LOW` (Pin 23)
* **Voraussetzungen / Testaufbau:** H-Brücken-Ansteuerung im statischen Testmodus Phase A bzw. Phase B.
* **Eingangssignal:** Statische Pin-Setzungen via Software.
* **Messverfahren:** Oszilloskop / DMM an Den H-Brückengates und Gleisausgängen DCC0/DCC1.
* **Erwartetes Ergebnis:**
  - Phase A: `DCC0` = High-Side aktiv ($V \ge 12\,\text{V}$), `DCC1` = Low-Side aktiv ($V \le 0.5\,\text{V}$).
  - Phase B: `DCC0` = Low-Side aktiv ($V \le 0.5\,\text{V}$), `DCC1` = High-Side aktiv ($V \ge 12\,\text{V}$).
* **Toleranz / Akzeptanzkriterium:** $V_{\text{High}} \ge 11.5\,\text{V}$, $V_{\text{Low}} \le 0.5\,\text{V}$.

#### ST-DCC-02: NMRA DCC Bit '1' Timing-Validierung
* **Testfall-ID:** ST-DCC-02
* **Referenz-Testschritt:** TS-02
* **Testgegenstand / Messpunkt:** `DCC0`, `DCC1`
* **Voraussetzungen / Testaufbau:** DCC Generator sendet kontinuierlich Logisch '1' Bits.
* **Eingangssignal:** DCC Bit '1' Datenstrom.
* **Messverfahren:** Oszilloskop mit Timing-Messung (Flanke-zu-Flanke).
* **Erwartetes Ergebnis:**
  - Halbperiodendauer: $t_{\text{half}} = 58\,\mu\text{s}$.
  - Gesamtbitdauer: $t_{\text{bit}} = 116\,\mu\text{s}$.
* **Toleranz / Akzeptanzkriterium:** NMRA S-9.1 Konformität ($55\,\mu\text{s} \le t_{\text{half}} \le 61\,\mu\text{s}$).

#### ST-DCC-03: NMRA DCC Bit '0' Timing-Validierung
* **Testfall-ID:** ST-DCC-03
* **Referenz-Testschritt:** TS-02
* **Testgegenstand / Messpunkt:** `DCC0`, `DCC1`
* **Voraussetzungen / Testaufbau:** DCC Generator sendet Logisch '0' Bits.
* **Eingangssignal:** DCC Bit '0' Datenstrom.
* **Messverfahren:** Oszilloskop Timing-Messung.
* **Erwartetes Ergebnis:**
  - Halbperiodendauer: $t_{\text{half}} = 100\,\mu\text{s}$.
  - Gesamtbitdauer: $t_{\text{bit}} = 200\,\mu\text{s}$.
* **Toleranz / Akzeptanzkriterium:** NMRA S-9.1 Konformität ($95\,\mu\text{s} \le t_{\text{half}} \le 105\,\mu\text{s}$).

#### ST-DCC-04: NMRA Präambel-Erkennung
* **Testfall-ID:** ST-DCC-04
* **Referenz-Testschritt:** TS-02
* **Testgegenstand / Messpunkt:** `DCC0`, `DCC1`
* **Voraussetzungen / Testaufbau:** Generierung von NMRA DCC Standardpaketen.
* **Eingangssignal:** Paketfolge mit variierender Präambellänge.
* **Messverfahren:** Logikanalysator / Software-Dekodierung.
* **Erwartetes Ergebnis:** Decoder synchonisiert fehlerfrei ab 14 aufeinanderfolgenden '1'-Bits (Preamble).
* **Toleranz / Akzeptanzkriterium:** $14 \dots 16$ Bits Präambel werden korrekt erkannt.

#### ST-DCC-05: Checksummen- & Paketvalidierung (XOR Checksum)
* **Testfall-ID:** ST-DCC-05
* **Referenz-Testschritt:** TS-02
* **Testgegenstand / Messpunkt:** Internes Protokollmodul / Telemetrie
* **Voraussetzungen / Testaufbau:** Übertragung gültiger sowie korrumpierter DCC-Pakete (z.B. Adresse `0x03`, Speed-Data `0x4E`).
* **Eingangssignal:**
  - Paket 1: `[0x03, 0x4E, 0x4D]` (Gültiges Checksummen-XOR: $0x03 \oplus 0x4E = 0x4D$).
  - Paket 2: `[0x03, 0x4E, 0x00]` (Ungültige Checksumme).
* **Messverfahren:** Serielle Telemetrieausgabe des Teststands / Decoder-Reaktion.
* **Erwartetes Ergebnis:** Paket 1 wird ausgeführt; Paket 2 wird verworfen.
* **Toleranz / Akzeptanzkriterium:** 100% Erkennung von Bitfehlern in der Checksumme.

---

### 3.3 Kategorie 3: Analoge Betriebsprotokolle Zentrale -> Decoder (AC / DC) [TS-03]

#### ST-ANA-01: Gleichspannung DC Vorwärtsbetrieb
* **Testfall-ID:** ST-ANA-01
* **Referenz-Testschritt:** TS-03
* **Testgegenstand / Messpunkt:** `DCC0`, `DCC1`, `M0_AMP`, `M1_AMP`
* **Voraussetzungen / Testaufbau:** Gleichspannung an Gleiseingänge anlegen.
* **Eingangssignal:** $V(\text{DCC0}) = +15.0\,\text{V}$, $V(\text{DCC1}) = 0.0\,\text{V}$ (DC).
* **Messverfahren:** ADC-Messung via Spannungsteiler an `M0_AMP` und `M1_AMP`.
* **Erwartetes Ergebnis:** Decoder erkennt DC Analog Vorwärts; `M0_AMP` durchgeschaltet ($V \approx U_+$), `M1_AMP` nach GND.
* **Toleranz / Akzeptanzkriterium:** $V(M0\_AMP) \ge 13.5\,\text{V}$, $V(M1\_AMP) \le 0.5\,\text{V}$.

#### ST-ANA-02: Gleichspannung DC Rückwärtsbetrieb
* **Testfall-ID:** ST-ANA-02
* **Referenz-Testschritt:** TS-03
* **Testgegenstand / Messpunkt:** `DCC0`, `DCC1`, `M0_AMP`, `M1_AMP`
* **Voraussetzungen / Testaufbau:** Gleichspannung umgepolt anlegen.
* **Eingangssignal:** $V(\text{DCC0}) = 0.0\,\text{V}$, $V(\text{DCC1}) = +15.0\,\text{V}$ (DC).
* **Messverfahren:** ADC-Messung via Spannungsteiler an `M0_AMP` und `M1_AMP`.
* **Erwartetes Ergebnis:** Decoder erkennt DC Analog Rückwärts; `M1_AMP` durchgeschaltet ($V \approx U_+$), `M0_AMP` nach GND.
* **Toleranz / Akzeptanzkriterium:** $V(M1\_AMP) \ge 13.5\,\text{V}$, $V(M0\_AMP) \le 0.5\,\text{V}$.

#### ST-ANA-03: Wechselspannung AC Analogbetrieb (Märklin AC Standard)
* **Testfall-ID:** ST-ANA-03
* **Referenz-Testschritt:** TS-03
* **Testgegenstand / Messpunkt:** `DCC0`, `DCC1`, `M0_AMP`, `M1_AMP`
* **Voraussetzungen / Testaufbau:** Sinus-Wechselspannung über Transformator anlegen.
* **Eingangssignal:** $16.0\,\text{V}_{\text{eff}}$ AC, $50\,\text{Hz}$.
* **Messverfahren:** True-RMS Spannungsmessung an Motor- und Funktionsausgängen.
* **Erwartetes Ergebnis:** Decoder schaltet in den AC-Analogmodus; Ausgänge werden geregelt angesteuert.
* **Toleranz / Akzeptanzkriterium:** Stabil betriebsfähig im Bereich $12.0\,\text{V}_{\text{eff}} \dots 18.0\,\text{V}_{\text{eff}}$.

---

### 3.4 Kategorie 4: Rückmeldung Decoder -> Zentrale (DCC-Acknowledge) [TS-04]

#### ST-ACK-01: Acknowledge Stromimpuls-Parameter
* **Testfall-ID:** ST-ACK-01
* **Referenz-Testschritt:** TS-04
* **Testgegenstand / Messpunkt:** Gleisstrom / Strommess-Shunt am Testaufbau
* **Voraussetzungen / Testaufbau:** Tester sendet CV-Schreib- oder Leseauftrag (Service Mode / Direct Mode).
* **Eingangssignal:** NMRA Service Mode Programmierbefehl (z.B. CV1 lesen).
* **Messverfahren:** Strommessung via Shunt-Widerstand und Speicheroszilloskop.
* **Erwartetes Ergebnis:** Der Decoder generiert durch kurzzeitiges Einschalten der Motorlast einen definierten Stromimpuls.
  - Impulsstrom: $I_{\text{ACK}} \ge 60\,\text{mA}$ über dem Grundstrom.
  - Impulsdauer: $t_{\text{ACK}} = 6.0\,\text{ms} \pm 1.0\,\text{ms}$.
* **Toleranz / Akzeptanzkriterium:** $I_{\text{ACK}} \ge 60\,\text{mA}$, $t_{\text{ACK}} = 5.0 \dots 7.0\,\text{ms}$ gemäss NMRA S-9.2.3.

#### ST-ACK-02: Spannungseinbruchsmessung während CV-Lesen
* **Testfall-ID:** ST-ACK-02
* **Referenz-Testschritt:** TS-04
* **Testgegenstand / Messpunkt:** `U+`, `VIN`
* **Voraussetzungen / Testaufbau:** Testaufbau im Programmiermodus.
* **Eingangssignal:** CV-Leseauftrag.
* **Messverfahren:** Abtastung der Versorgungsspannung $U_+$ während des ACK-Impulses.
* **Erwartetes Ergebnis:** Spannungsabfall an $U_+$ bleibt im zulässigen Bereich ($< 1.0\,\text{V}$).
* **Toleranz / Akzeptanzkriterium:** Kein Unterspannungs-Reset des Mikrocontrollers während des ACK-Impulses.

---

### 3.5 Kategorie 5: Rückmeldung Decoder -> Zentrale (RailCom) [TS-05]

#### ST-RC-01: RailCom Cutout Erzeugung (Austastlücke)
* **Testfall-ID:** ST-RC-01
* **Referenz-Testschritt:** TS-05
* **Testgegenstand / Messpunkt:** `DCC0`, `DCC1`
* **Voraussetzungen / Testaufbau:** DCC-Signal generator mit aktivierter RailCom-Funktionalität.
* **Eingangssignal:** DCC-Paket mit unmittelbar folgendem RailCom-Cutout.
* **Messverfahren:** Oszilloskop-Triggering auf das Ende des DCC-Paket-Stopbits.
* **Erwartetes Ergebnis:**
  - H-Brücke schaltet in High-Impedance / Kurzschluss-Zustand für $t_{\text{cutout}}$.
  - Cutout-Dauer: $t_{\text{cutout}} = 488\,\mu\text{s}$.
* **Toleranz / Akzeptanzkriterium:** $460\,\mu\text{s} \le t_{\text{cutout}} \le 500\,\mu\text{s}$ gemäss NMRA S-9.2.2.

#### ST-RC-02: Signalpegel während RailCom Channel 1 & Channel 2
* **Testfall-ID:** ST-RC-02
* **Referenz-Testschritt:** TS-05
* **Testgegenstand / Messpunkt:** `DCC0`, `DCC1`
* **Voraussetzungen / Testaufbau:** Decoder mit aktiviertem RailCom-Transmitter (CV29 Bit 3 = 1).
* **Eingangssignal:** DCC-Paket mit RailCom Cutout.
* **Messverfahren:** Differenzspannungsmessung an DCC0/DCC1 während Ch1 und Ch2.
* **Erwartetes Ergebnis:** Decoder sendet UART-Byte-Strom (250 kBaud) durch Strommodulation im Cutout.
* **Toleranz / Akzeptanzkriterium:** Signalpegel und Bit-Timing innerhalb der RailCom-Spezifikation.

---

### 3.6 Kategorie 6: Ein-/Ausgänge Motorausgänge (M0_AMP / M1_AMP) [TS-06]

#### ST-MOT-01: Motorausgang Vorwärtsfahrt (Fahrstufe 14)
* **Testfall-ID:** ST-MOT-01
* **Referenz-Testschritt:** TS-06
* **Testgegenstand / Messpunkt:** `M0_AMP` (Pin 10 / A1), `M1_AMP` (Pin 11 / A2)
* **Voraussetzungen / Testaufbau:** DCC Befehl "Address 3, Speed Forward 14" aktiv.
* **Eingangssignal:** DCC Fahrbefehl Vorwärts Step 14.
* **Messverfahren:** ADC-Abtastung an `MOTOR0_DIV` und `MOTOR1_DIV` (16 Samples Mittelung).
* **Erwartetes Ergebnis:**
  - `M0_AMP`: PWM-Spannung mit Tastverhältnis $\approx 50\% \cdot U_+$ ($\approx 7.3\,\text{V}$).
  - `M1_AMP`: Durchgeschaltet nach GND ($\approx 0.0\,\text{V}$).
  - Differenzspannung: $V_{\text{diff}} = |V(M0) - V(M1)| \approx 7.3\,\text{V}$.
* **Toleranz / Akzeptanzkriterium:** $6.5\,\text{V} \le V_{\text{diff}} \le 8.2\,\text{V}$.

#### ST-MOT-02: Motorausgang Rückwärtsfahrt (Fahrstufe 14)
* **Testfall-ID:** ST-MOT-02
* **Referenz-Testschritt:** TS-06
* **Testgegenstand / Messpunkt:** `M0_AMP`, `M1_AMP`
* **Voraussetzungen / Testaufbau:** DCC Befehl "Address 3, Speed Reverse 14" aktiv.
* **Eingangssignal:** DCC Fahrbefehl Rückwärts Step 14.
* **Messverfahren:** ADC-Abtastung an `MOTOR0_DIV` und `MOTOR1_DIV`.
* **Erwartetes Ergebnis:**
  - `M0_AMP`: Durchgeschaltet nach GND ($\approx 0.0\,\text{V}$).
  - `M1_AMP`: PWM-Spannung mit Tastverhältnis $\approx 50\% \cdot U_+$ ($\approx 7.3\,\text{V}$).
  - Differenzspannung: $V_{\text{diff}} \approx 7.3\,\text{V}$.
* **Toleranz / Akzeptanzkriterium:** $6.5\,\text{V} \le V_{\text{diff}} \le 8.2\,\text{V}$.

#### ST-MOT-03: Motorausgang Neutralstellung / Stillstand (Fahrstufe 0)
* **Testfall-ID:** ST-MOT-03
* **Referenz-Testschritt:** TS-06
* **Testgegenstand / Messpunkt:** `M0_AMP`, `M1_AMP`
* **Voraussetzungen / Testaufbau:** DCC Befehl "Address 3, Motor Stop" aktiv.
* **Eingangssignal:** DCC Fahrbefehl Speed 0.
* **Messverfahren:** ADC-Abtastung an `MOTOR0_DIV` und `MOTOR1_DIV`.
* **Erwartetes Ergebnis:**
  - $V(M0\_AMP) = 0.0\,\text{V}$.
  - $V(M1\_AMP) = 0.0\,\text{V}$.
  - Differenzspannung $V_{\text{diff}} = 0.0\,\text{V}$.
* **Toleranz / Akzeptanzkriterium:** $V_{\text{diff}} \le 0.2\,\text{V}$.

---

### 3.7 Kategorie 7: Ein-/Ausgänge Funktionsausgänge (F0_AMP / F1_AMP) [TS-07]

#### ST-FUNC-01: Funktionsausgang F0 (FL) Einschalten
* **Testfall-ID:** ST-FUNC-01
* **Referenz-Testschritt:** TS-07
* **Testgegenstand / Messpunkt:** `F0_AMP` (Pin 9 / A0)
* **Voraussetzungen / Testaufbau:** Pull-Up Widerstand nach U+ vorhanden.
* **Eingangssignal:** DCC Befehl "Address 3, Function F0 ON".
* **Messverfahren:** ADC-Abtastung an `FUNC0_DIV`.
* **Erwartetes Ergebnis:** F0-Transistor schaltet aktiv nach GND (Open-Drain Low-Side).
* **Toleranz / Akzeptanzkriterium:** $V(F0\_AMP) \le 0.5\,\text{V}$.

#### ST-FUNC-02: Funktionsausgang F0 (FL) Ausschalten
* **Testfall-ID:** ST-FUNC-02
* **Referenz-Testschritt:** TS-07
* **Testgegenstand / Messpunkt:** `F0_AMP` (Pin 9 / A0)
* **Voraussetzungen / Testaufbau:** Pull-Up Widerstand nach U+ an `F0_AMP`.
* **Eingangssignal:** DCC Befehl "Address 3, Function F0 OFF".
* **Messverfahren:** ADC-Abtastung an `FUNC0_DIV`.
* **Erwartetes Ergebnis:** F0-Transistor wird hochohmig; Spannung wird über Pull-Up auf U+ gezogen.
* **Toleranz / Akzeptanzkriterium:** $V(F0\_AMP) \ge U_+ - 0.5\,\text{V}$.

#### ST-FUNC-03: Funktionsausgang F1 (FR) Einschalten
* **Testfall-ID:** ST-FUNC-03
* **Referenz-Testschritt:** TS-07
* **Testgegenstand / Messpunkt:** `F1_AMP` (Pin 12 / A3)
* **Voraussetzungen / Testaufbau:** Lastwiderstand gegen GND.
* **Eingangssignal:** DCC Befehl "Address 3, Function F1 ON".
* **Messverfahren:** ADC-Abtastung an `FUNC1_DIV`.
* **Erwartetes Ergebnis:** F1-Ausgang gibt High-Side Versorgungsspannung aus ($V \approx U_+$).
* **Toleranz / Akzeptanzkriterium:** $V(F1\_AMP) \ge U_+ - 1.0\,\text{V}$.

---

### 3.8 Kategorie 8: Fahrtkontrolle & Motorensteuerung [TS-08]

#### ST-CTRL-01: Dynamischer Fahrstufen-Sweep (128 Fahrstufen Modus)
* **Testfall-ID:** ST-CTRL-01
* **Referenz-Testschritt:** TS-08
* **Testgegenstand / Messpunkt:** `M0_AMP`, `M1_AMP`
* **Voraussetzungen / Testaufbau:** Automatisierte Sequenzierung der Fahrstufen von 0 bis 126.
* **Eingangssignal:** Stufenweise Erhöhung des DCC Speed-Bytes.
* **Messverfahren:** Kontinuierliche ADC-Erfassung der Motorspannungen.
* **Erwartetes Ergebnis:** Proportional linearer Anstieg der Effektiv- / PWM-Mittelwertspannung an den Motorausgängen.
* **Toleranz / Akzeptanzkriterium:** Monotoner Anstieg ohne Spannungssprünge oder Einbrüche.

#### ST-CTRL-02: Richtungswechsel-Verzögerung (Direction Reversal)
* **Testfall-ID:** ST-CTRL-02
* **Referenz-Testschritt:** TS-08
* **Testgegenstand / Messpunkt:** `M0_AMP`, `M1_AMP`
* **Voraussetzungen / Testaufbau:** Decoder in Vorwärtsfahrt bei Fahrstufe 14.
* **Eingangssignal:** Abrupptes Senden eines Rückwärtsfahrt-Befehls.
* **Messverfahren:** Oszilloskop-Aufzeichnung der Umpolung.
* **Erwartetes Ergebnis:** Dead-Time / Bremsrampe verhindert Brückenkurzschluss; geordnete Umpolung der PWM-Phasen.
* **Toleranz / Akzeptanzkriterium:** Dead-Time $\ge 2\,\mu\text{s}$, kein Überstromimpuls.

---

### 3.9 Kategorie 9: Hardware-Fehlerschutz & Safety Shutdown (`def_fault_a`)

#### ST-FLT-01: Not-Abschaltung bei Hardware-Fehler (`def_fault_a` = LOW)
* **Testfall-ID:** ST-FLT-01
* **Referenz-Testschritt:** Hardware Fault Protection
* **Testgegenstand / Messpunkt:** `def_fault_a` (Pin 13 / A4 / SDA), DCC-Treiberstufen
* **Voraussetzungen / Testaufbau:** Normaler DCC Sendebetrieb aktiv (`dccOutputEnabled = true`).
* **Eingangssignal:** Pin `def_fault_a` extern auf GND ziehen ($0.0\,\text{V}$).
* **Messverfahren:** Abtastung der Signale `DCC0.HIGH`, `DCC0.LOW`, `DCC1.HIGH`, `DCC1.LOW`.
* **Erwartetes Ergebnis:**
  - Sofortige Abschaltung aller H-Brücken-Ansteuersignale (alle Pins LOW).
  - Telemetrie-Meldung: `[EMERGENCY TRIP] Hardware Fault Detected...`.
  - Gleisspannung entfällt ($0.0\,\text{V}$).
* **Toleranz / Akzeptanzkriterium:** Reaktionszeit $< 100\,\mu\text{s}$.

#### ST-FLT-02: Fault-Clear und System-Reaktivierung
* **Testfall-ID:** ST-FLT-02
* **Referenz-Testschritt:** Hardware Fault Recovery
* **Testgegenstand / Messpunkt:** `def_fault_a`, Serial CLI Interface
* **Voraussetzungen / Testaufbau:** System befindet sich im Trip-Zustand (`ST-FLT-01`).
* **Eingangssignal:**
  1. Freigabe der Fehlerleitung (`def_fault_a` = HIGH / Pull-Up).
  2. Eingabe des CLI-Befehls `'c'` (Clear Fault).
* **Messverfahren:** Beobachtung des Telemetrie-Status und Wiederaufnahme der DCC-Generierung.
* **Erwartetes Ergebnis:** Normaler DCC-Betrieb wird wieder aufgenommen.
* **Toleranz / Akzeptanzkriterium:** `systemFaultDetected` wechselt auf `false`, H-Brückenausgänge werden reaktiviert.

---

## 4. Testdurchführung und Abnahmekriterien

1. **Testumgebung & Kalibrierung:**
   - Der Tester muss vor Durchführen der Testfälle an eine kalibrierte Spannungsquelle ($15.0\,\text{V} \pm 0.1\,\text{V}$) angeschlossen werden.
   - Die ADC-Referenzspannung ist auf $5.00\,\text{V}$ zu überprüfen.
2. **Dokumentation:**
   - Jedes Testergebnis ist in ein digitales Prüfprotokoll einzutragen.
   - Bei Abweichungen außerhalb der festgelegten Toleranzen gilt der Testfall als **FAIL**.
3. **Sicherheit:**
   - Vor jedem Testschritt ist sicherzustellen, dass die Strombegrenzung am Netzgerät greift, um Beschädigungen des Prüflings (DUT) zu vermeiden.
