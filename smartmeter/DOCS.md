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
- `log_level`: `error`, `warning`, `info`, `debug` oder `trace`.

Die gewählte Stufe und alle schwerwiegenderen Meldungen werden angezeigt. `error` protokolliert nur Fehler, `warning` zusätzlich Warnungen, `info` den normalen Betriebsstatus, `debug` detaillierte Diagnose inklusive des Zähler-Schlüssels im Klartext und `trace` zusätzlich vollständige Telegramme. Das MQTT-Passwort wird unabhängig vom Log-Level niemals geloggt. `debug` und `trace` sollten nur vorübergehend zur Fehlersuche aktiviert werden.

Die MQTT-Verbindungsdaten werden automatisch aus dem MQTT-Dienst von Home Assistant übernommen. Es müssen keine zusätzlichen Zugangsdaten in der App hinterlegt werden.

## Verhalten der Home-Assistant-Entitäten

Der Reader veröffentlicht MQTT-Discovery-Konfigurationen und Status-Topics mit dem aktuellen Gerätenamen als Topic-Präfix. Das Status-Topic `<device_name>/status` meldet nach erfolgreicher MQTT-Verbindung retained `online`. Der konfigurierte MQTT Last Will meldet bei einem unerwarteten Verbindungsabbruch retained `offline`.

Alle Messwertsensoren referenzieren dieses Topic als `availability_topic` mit `online` als verfügbarem und `offline` als nicht verfügbarem Payload. Home Assistant kann dadurch die Verfügbarkeit der Entitäten automatisch darstellen.

Nach einer `online`-Nachricht auf `homeassistant/status` werden die Discovery-Daten erneut veröffentlicht.

Wenn `device_name` geändert wird, erstellt Home Assistant ein neues Gerät und neue Entitäten. Der bisherige Name sollte deshalb beibehalten werden, um verwaiste Einträge und doppelte Geräte zu vermeiden.

## Fehlerbehebung

- Prüfe, ob die konfigurierte Schnittstelle unter `/dev/serial/by-id/` vorhanden ist.
- Vergewissere dich, dass der Leseschlüssel exakt mit dem vom Zählerbetreiber angegebenen Schlüssel übereinstimmt.
- Wenn keine MQTT-Verbindung aufgebaut wird, überprüfe die MQTT-Integration und stelle sicher, dass der Mosquitto-Broker gestartet ist.
- Das App-Protokoll zeigt den gewählten seriellen Port und den MQTT-Verbindungsstatus an.

## Hinweis

Pro App-Installation wird ein Zähler ausgelesen. Für mehrere Zähler werden mehrere Instanzen mit unterschiedlichen seriellen Schnittstellen eingerichtet.
