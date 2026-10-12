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
