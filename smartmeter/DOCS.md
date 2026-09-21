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
- `instance_id`: Unveränderlicher technischer Schlüssel für diese Zählerinstanz. Er muss bei mehreren App-Instanzen eindeutig sein und darf nur Kleinbuchstaben, Zahlen, `_` und `-` enthalten.
- `device_name`: Sichtbarer Name des Home-Assistant-Geräts. Er ist nicht Bestandteil der technischen Identität.
- `log_level`: `error`, `warning`, `info`, `debug` oder `trace`.

Die gewählte Stufe und alle schwerwiegenderen Meldungen werden angezeigt. `error` protokolliert nur Fehler, `warning` zusätzlich Warnungen, `info` den normalen Betriebsstatus, `debug` detaillierte Diagnose inklusive des Zähler-Schlüssels im Klartext und `trace` zusätzlich vollständige Telegramme. Das MQTT-Passwort wird unabhängig vom Log-Level niemals geloggt. `debug` und `trace` sollten nur vorübergehend zur Fehlersuche aktiviert werden.

Die MQTT-Verbindungsdaten werden automatisch aus dem MQTT-Dienst von Home Assistant übernommen. Es müssen keine zusätzlichen Zugangsdaten in der App hinterlegt werden.

## Verhalten der Home-Assistant-Entitäten

Der Reader veröffentlicht MQTT-Discovery-Konfigurationen und Status-Topics mit `smartmeter/<instance_id>/` als technischem Topic-Präfix. Der Anzeigename des Geräts wird separat aus `device_name` gesetzt. Das Status-Topic `smartmeter/<instance_id>/status` meldet nach erfolgreicher MQTT-Verbindung retained `online`. Der konfigurierte MQTT Last Will meldet bei einem unerwarteten Verbindungsabbruch retained `offline`.

Alle Messwertsensoren referenzieren dieses Topic als `availability_topic` mit `online` als verfügbarem und `offline` als nicht verfügbarem Payload. Home Assistant kann dadurch die Verfügbarkeit der Entitäten automatisch darstellen.

Nach jedem erfolgreichen Reconnect und nach einer `online`-Nachricht auf `homeassistant/status` werden die Discovery-Daten erneut veröffentlicht.

Die `unique_id`-Werte basieren auf `instance_id` und dem stabilen Feldnamen. Änderungen an `device_name` erzeugen dadurch keine neuen technischen Entitäten. `instance_id` darf nach der ersten Einrichtung nicht geändert werden.

`Zeit` und `Cosemlogdevname` bleiben als technische MQTT-Daten verfügbar, werden aber nicht automatisch als Home-Assistant-Entitäten angelegt. Während der Migration werden Messwerte zusätzlich auf den bisherigen `<device_name>/<feld>`-Topics veröffentlicht.

## Fehlerbehebung

- Prüfe, ob die konfigurierte Schnittstelle unter `/dev/serial/by-id/` vorhanden ist.
- Vergewissere dich, dass der Leseschlüssel exakt mit dem vom Zählerbetreiber angegebenen Schlüssel übereinstimmt.
- Wenn keine MQTT-Verbindung aufgebaut wird, überprüfe die MQTT-Integration und stelle sicher, dass der Mosquitto-Broker gestartet ist.
- Verwende pro Add-on-Instanz eine eigene `instance_id` und ändere sie nach der Einrichtung nicht mehr.
- Das App-Protokoll zeigt den gewählten seriellen Port und den MQTT-Verbindungsstatus an.

## Hinweis

Pro App-Installation wird ein Zähler ausgelesen. Für mehrere Zähler werden mehrere Instanzen mit unterschiedlichen seriellen Schnittstellen und unterschiedlichen `instance_id`-Werten eingerichtet.
