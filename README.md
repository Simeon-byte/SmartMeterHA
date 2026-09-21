# SmartmeterHA – Home-Assistant-App

Diese App liest verschlüsselte VKW-Smartmeter-Telegramme eines Kaifa MA309M H4LAT1 aus und veröffentlicht die Messwerte über MQTT-Discovery in Home Assistant.

Die Anwendung ist pro Installation auf genau einen Zähler ausgelegt. Für zwei Zähler musst du die App daher zweimal mit unterschiedlichen seriellen Schnittstellen und unterschiedlichen `instance_id`-Werten einrichten.

## Voraussetzungen

Bevor du loslegst, solltest du Folgendes vorbereitet haben:

- Home Assistant OS oder Home Assistant Supervised
- Die offizielle Mosquitto-Broker-App
- Die MQTT-Integration von Home Assistant, korrekt für diesen Broker eingerichtet
- Ein unterstützter USB-Seriell-/MBus-Adapter am Home-Assistant-Host
- Den hexadezimalen Kundenschnittstellen-Schlüssel des Zählerbetreibers

## Installation in Home Assistant

1. Öffne in Home Assistant unter Einstellungen > Geräte & Dienste > Apps > App-Repositorys die Repository-Verwaltung.
2. Füge `https://github.com/Simeon-byte/SmartMeterHA` als Git-Repository hinzu.
3. Wechsle in den Bereich Apps und installiere SmartmeterHA.
4. Starte die App und öffne die Konfiguration.
5. Trage die nötigen Werte ein:
   - `key`: Leseschlüssel des Zählers
   - `comport`: serielle Schnittstelle, am besten ein stabiler Pfad unter `/dev/serial/by-id/...`
   - `instance_id`: unveränderlicher technischer Schlüssel, zum Beispiel `meter-01`
   - `device_name`: Name für das Gerät und das MQTT-Topic-Präfix
   - `log_level`: `error`, `warning`, `info`, `debug` oder `trace`
6. Speichere die Einstellungen und starte die App erneut.
7. Prüfe die App-Logs, damit die Verbindung zum Zähler und zum MQTT-Broker korrekt aufgebaut wird.

> Die App nutzt den MQTT-Dienst von Home Assistant. Zusätzliche Zugangsdaten für den Broker müssen nicht separat in SmartmeterHA hinterlegt werden.

## Konfiguration

| Option        | Beschreibung                                                                                                                                                        |
| ------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `key`         | Erforderlicher hexadezimaler Leseschlüssel. Wird als Passwort-Option gespeichert.                                                                                   |
| `comport`     | Serielle Schnittstelle. Wenn möglich, einen stabilen Pfad unter `/dev/serial/by-id/...` verwenden.                                                                  |
| `instance_id` | Unveränderlicher technischer Schlüssel für MQTT-Topics, Discovery und `unique_id`. Pro Zählerinstanz eindeutig; nur Kleinbuchstaben, Zahlen, `_` und `-` verwenden. |
| `device_name` | Sichtbarer Name des Home-Assistant-Geräts. Er ist nicht Bestandteil der technischen Identität.                                                                      |
| `log_level`   | `error` für Fehler, `warning` für Warnungen, `info` für Betriebsstatus, `debug` für detaillierte Diagnose und `trace` für rohe Telegramme.                          |

Die gewählte Stufe und alle schwerwiegenderen Meldungen werden angezeigt. Bei `debug` wird der Zähler-Schlüssel zur Fehlersuche im Klartext geloggt. Das MQTT-Passwort wird niemals geloggt. `trace` sollte nur vorübergehend verwendet werden, da dabei vollständige Telegramme in den App-Logs erscheinen.

Ein stabiler Pfad wie `/dev/serial/by-id/...` ist besser als `/dev/ttyUSB0`, weil die Schnittstelle sich sonst nach einem Neustart ändern kann.

## Hinweise zur Einrichtung

- Wenn du nur einen Zähler hast, reicht eine Installation aus.
- Für zwei oder mehr Zähler installierst du die App mehrfach mit jeweils eigener serieller Schnittstelle und eigener `instance_id`.

## MQTT-Entitäten

Der Reader veröffentlicht die kanonischen Topics unter `smartmeter/<instance_id>/...`. Die Discovery-Konfigurationen verwenden diese Topics und stabile IDs wie `smartmeter_<instance_id>_WirkenergieP`. Unter `smartmeter/<instance_id>/status` wird nach erfolgreicher MQTT-Verbindung retained `online` veröffentlicht. Der MQTT Last Will veröffentlicht bei einem unerwarteten Verbindungsabbruch retained `offline`.

Während der Übergangsphase werden die Messwerte zusätzlich unter den bisherigen `<device_name>/<feld>`-Topics veröffentlicht, damit bestehende MQTT-Automationen weiter funktionieren. Diese Legacy-Topics werden in einer späteren Major-Version entfernt.

Alle Messwertsensoren verwenden dieses Topic als Availability-Topic. Home Assistant zeigt die Sensoren daher automatisch als nicht verfügbar an, wenn der Reader die MQTT-Verbindung verliert.

Nach einem Start, nach jedem erfolgreichen MQTT-Reconnect und nach einer `online`-Nachricht auf `homeassistant/status` werden die Discovery-Daten erneut gesendet.

Eine Änderung von `device_name` ändert die technische Identität nicht. `instance_id` darf nach der ersten Einrichtung dagegen nicht mehr geändert werden. `Zeit` und `Cosemlogdevname` werden weiterhin als technische MQTT-Daten veröffentlicht, aber bewusst nicht als Home-Assistant-Entitäten entdeckt.

Vor der Migration sollten Home-Assistant-Konfiguration, Entity-Registry, Dashboards und Automationen gesichert werden. Durch die neuen technischen IDs werden neue Entitäten angelegt; Dashboards und Automationen müssen einmalig auf diese Entity-IDs umgestellt werden.

## Unterstützte Hardware

- Kaifa MA309M H4LAT1 Smartmeter aus dem VKW-Gebiet Vorarlberg
- USB-Seriell-/MBus-Adapter, der die Kundenschnittstelle als UART-Gerät bereitstellt

Andere Zähler wurden nicht getestet.

## Fehlerbehebung

- Prüfe, ob die konfigurierte Schnittstelle unter `/dev/serial/by-id/` wirklich vorhanden ist.
- Stelle sicher, dass der Leseschlüssel exakt zum Schlüssel des Zählerbetreibers passt.
- Wenn keine MQTT-Verbindung aufgebaut wird, prüfe, ob die MQTT-Integration in Home Assistant eingerichtet ist und der Mosquitto-Broker läuft.
- Im Log der App kannst du die gewählte Schnittstelle und den Verbindungsstatus sehen.

## Danksagung

Der Reader basiert auf der Arbeit von [greenMikeEU](https://github.com/greenMikeEU) und der Anleitung von [Michael Reitbauer](https://www.michaelreitbauer.at/kaifa-ma309-auslesen-smart-meter-evn/).
