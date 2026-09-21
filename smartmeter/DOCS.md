# SmartmeterHA

Diese App liest verschluesselte VKW-Smartmeter-Telegramme von einem Zaehler aus und veroeffentlicht MQTT-Discovery-Entitaeten fuer Home Assistant.

## Voraussetzungen

- Home Assistant OS oder Supervised mit der offiziellen Mosquitto-Broker-App
- Die MQTT-Integration von Home Assistant
- Ein unterstuetzter serieller USB-Adapter am Host
- Der hexadezimale Kundenschnittstellen-Schluessel des Zaehlerbetreibers

Pro App-Installation wird ein Zaehler gelesen. Fuer zwei Zaehler die App zweimal mit unterschiedlichen seriellen Schnittstellen installieren.

## Konfiguration

Die App im Tab **Konfiguration** einrichten:

- `key`: Erforderlicher hexadezimaler Leseschluessel. Wird als Passwort-Option gespeichert.
- `comport`: Serielle Schnittstelle der App, normalerweise ein stabiler Pfad unter `/dev/serial/by-id/...`.
- `device_name`: Praefix fuer MQTT-Topics und Name des Home-Assistant-Geraets. Bei einer Migration den bisherigen Wert beibehalten.
- `log_level`: `0` fuer Fehler, `1` fuer Betriebsprotokolle oder `2` fuer Telegrammdaten und dekodierte Werte.

Die App bezieht die MQTT-Verbindungsdaten aus dem MQTT-Dienst von Home Assistant. Vor dem Start von SmartmeterHA die offizielle Mosquitto-Broker-App installieren und konfigurieren.

## Home-Assistant-Entitaeten

Der Reader veroeffentlicht MQTT-Discovery-Konfigurationen und Status-Topics mit dem bisherigen Geraetenamen als Topic-Praefix. Discovery wird nach einer `online`-Nachricht auf `homeassistant/status` erneut veroeffentlicht.

Eine Aenderung von `device_name` erstellt einen neuen Satz Home-Assistant-Entitaeten. Den bisherigen Namen beibehalten, um verwaiste Entitaeten und doppelte Geraete zu vermeiden.

## Fehlerbehebung

Das App-Protokoll zeigt die ausgewaehlte serielle Schnittstelle und den MQTT-Verbindungsstatus. Pruefen, ob das konfigurierte Geraet unter `/dev/serial/by-id/` vorhanden ist und ob der Leseschluessel exakt dem vom Zaehlerbetreiber bereitgestellten hexadezimalen Schluessel entspricht.

Wenn keine MQTT-Verbindung hergestellt werden kann, pruefen, ob die MQTT-Integration eingerichtet und die Mosquitto-Broker-App gestartet ist.
