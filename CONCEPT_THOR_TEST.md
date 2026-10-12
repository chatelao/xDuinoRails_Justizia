Testprotokoll ThorTestaufbau	2Aussenschnittstelle des Decoders	2Innenmesspunkte des Decoders	3Testprotokoll	4Stromversorgung	4BR - Brückengleichreichter (Bridge Rectifier)	4PWR - Stromversorgung (Voltage supply)	4Protokolle Zentrale zu Decoder	5Digitale Protokolle Zentrale zu Decoder (DCC/MM/SX)	5Analoge Protokolle Zentrale zu Decoder (AC/DC)	5Protokolle Decoder zu Zentrale	6Digitale Protokolle Decoder zu Zentrale	6DCC-Acknowledge	6Railcom	6Ein-/Ausgänge Decoder zu Funktionen	7Motor	7Funktionsausgänge	7Fahrtkontrolle des Decoder	8Highlevel Befehle decodieren	8Motorensteuerung anwenden	8TestaufbauAussenschnittstelle des Decoders
Messpunkt | Expected mode | Ansteuerung | Messverfahren
-- | -- | -- | --
DCC0 | Input 0-30V | Via externe H-Brücke |
DCC1 | Input 0-30V | Via externe H-Brücke |
U+ | Output 0-30V |   | ADC via Spannungsteiler 1:10
GND | 0V (relativ zu U+) |   | ADC via Spannungsteiler 1:10
M0_AMP | Output 0-30V |   | ADC via Spannungsteiler 1:10
M1_AMP | Output 0-30V |   | ADC via Spannungsteiler 1:10
F0_AMP | Output GND oder Open-Drain |   | ADC via Spannungsteiler 1:10
F1_AMP | Output 0-30V |   | ADC via Spannungsteiler 1:10

## Testschritte / Test Steps

Schritt-ID | Bereich / Kategorie | Testbeschreibung | Erwartetes Ergebnis | Messverfahren / Prüfmethode
-- | -- | -- | -- | --
TS-01 | Stromversorgung (BR / PWR) | Eingangsspannung an DCC0/DCC1 anlegen | U+ führt geregelte DC-Spannung (~0-30V), GND als Referenz | ADC Messung an U+ und GND (Spannungsteiler 1:10)
TS-02 | Protokolle Zentrale -> Decoder (DCC/MM/SX) | Digitale Befehlspakete über DCC-H-Brücke senden | Decoder empfängt und antwortet korrekt ohne Bitfehler | Oszilloskop / Logikanalysator an DCC0/DCC1
TS-03 | Protokolle Zentrale -> Decoder (AC/DC Analog) | Analoges Wechsel- oder Gleichspannungssignal anlegen | Decoder erkennt Analogmodus und schaltet Ausgänge frei | ADC Messung an Motor- und Funktionsausgängen
TS-04 | Protokolle Decoder -> Zentrale (DCC-Acknowledge) | Programmierbefehl / CV-Leseauftrag senden | Decoder generiert Acknowledge-Stromimpuls (>60mA) | Strom- / Spannungsmessung am Testaufbau
TS-05 | Protokolle Decoder -> Zentrale (Railcom) | DCC Signal mit Railcom-Cutout senden | Decoder sendet Railcom-Datenpakete während der Lücke | Oszilloskop an DCC0/DCC1 während Railcom-Cutout
TS-06 | Ein-/Ausgänge (Motor M0_AMP / M1_AMP) | Fahrtbefehl Vorwärts/Rückwärts senden | PWM-Spannung an M0_AMP und M1_AMP entsprechend der Fahrstufe | ADC via Spannungsteiler 1:10 an M0_AMP / M1_AMP
TS-07 | Ein-/Ausgänge (Funktionsausgänge F0 / F1) | Licht- / Funktionsbefehl F0/F1 einschalten | F0_AMP / F1_AMP schalten nach GND bzw. geben Spannung aus | ADC via Spannungsteiler 1:10 an F0_AMP / F1_AMP
TS-08 | Fahrtkontrolle | Highlevel-Befehle (Geschwindigkeit/Richtung) ändern | Motorensteuerung passt PWM-Austeuerung dynamisch an | Kontinuierliche ADC-Erfassung der Motorspannungen
