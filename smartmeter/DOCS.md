# SmartmeterHA

Diese App liest verschlüsselte VKW-Smartmeter-Telegramme eines Zählers aus und veröffentlicht die Messwerte über MQTT-Discovery für Home Assistant.

## Voraussetzungen

- Home Assistant mit aktivierter MQTT-Integration
- Offizielle Mosquitto-Broker-App installiert und gestartet
- Unterstützter serieller USB-Adapter am Host
- Hexadezimaler Kundenschnittstellen-Schlüssel des Zählerbetreibers

## Konfiguration

Die Einstellungen der App im Tab Konfiguration sind in der Regel die folgenden:

- `key`: Erforderlicher hexadezimaler Leseschlüssel. Wird als Passwort-Option gespeichert.
- `comport`: Serielle Schnittstelle der App, am besten ein stabiler Pfad unter `/dev/serial/by-id/...`.
- `device_name`: Präfix für die MQTT-Topics und Name des Home-Assistant-Geräts. Bei einer Migration sollte der bisherige Wert beibehalten werden.
- `log_level`: `0` für Fehler, `1` für Betriebsprotokolle, `2` für Telegrammdaten und dekodierte Werte.

Die MQTT-Verbindungsdaten werden automatisch aus dem MQTT-Dienst von Home Assistant übernommen. Es müssen keine zusätzlichen Zugangsdaten in der App hinterlegt werden.

## Verhalten der Home-Assistant-Entitäten

Der Reader veröffentlicht MQTT-Discovery-Konfigurationen und Status-Topics mit dem aktuellen Gerätenamen als Topic-Präfix. Nach einer `online`-Nachricht auf `homeassistant/status` werden die Discovery-Daten erneut veröffentlicht.

Wenn `device_name` geändert wird, erstellt Home Assistant ein neues Gerät und neue Entitäten. Der bisherige Name sollte deshalb beibehalten werden, um verwaiste Einträge und doppelte Geräte zu vermeiden.

## Fehlerbehebung

- Prüfe, ob die konfigurierte Schnittstelle unter `/dev/serial/by-id/` vorhanden ist.
- Vergewissere dich, dass der Leseschlüssel exakt mit dem vom Zählerbetreiber angegebenen Schlüssel übereinstimmt.
- Wenn keine MQTT-Verbindung aufgebaut wird, überprüfe die MQTT-Integration und stelle sicher, dass der Mosquitto-Broker gestartet ist.
- Das App-Protokoll zeigt den gewählten seriellen Port und den MQTT-Verbindungsstatus an.

## Hinweis

Pro App-Installation wird ein Zähler ausgelesen. Für mehrere Zähler werden mehrere Instanzen mit unterschiedlichen seriellen Schnittstellen eingerichtet.
