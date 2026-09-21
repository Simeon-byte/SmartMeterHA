# SmartmeterHA – Home-Assistant-App

Diese App liest verschlüsselte VKW-Smartmeter-Telegramme eines Kaifa MA309M H4LAT1 aus und veröffentlicht die Messwerte über MQTT-Discovery in Home Assistant.

Die Anwendung ist pro Installation auf genau einen Zähler ausgelegt. Für zwei Zähler musst du die App daher zweimal mit unterschiedlichen seriellen Schnittstellen einrichten.

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
   - `device_name`: Name für das Gerät und das MQTT-Topic-Präfix
   - `log_level`: `0` = Fehler, `1` = Betriebsprotokoll, `2` = Telegrammdaten und dekodierte Werte
6. Speichere die Einstellungen und starte die App erneut.
7. Prüfe die App-Logs, damit die Verbindung zum Zähler und zum MQTT-Broker korrekt aufgebaut wird.

> Die App nutzt den MQTT-Dienst von Home Assistant. Zusätzliche Zugangsdaten für den Broker müssen nicht separat in SmartmeterHA hinterlegt werden.

## Konfiguration

| Option        | Beschreibung                                                                                                                 |
| ------------- | ---------------------------------------------------------------------------------------------------------------------------- |
| `key`         | Erforderlicher hexadezimaler Leseschlüssel. Wird als Passwort-Option gespeichert.                                            |
| `comport`     | Serielle Schnittstelle. Wenn möglich, einen stabilen Pfad unter `/dev/serial/by-id/...` verwenden.                           |
| `device_name` | Präfix für MQTT-Topics und Name des Home-Assistant-Geräts. Bei einer Migration sollte der bisherige Wert beibehalten werden. |
| `log_level`   | `0` für Fehler, `1` für Betriebsprotokolle, `2` für Telegrammdaten und dekodierte Werte.                                     |

Ein stabiler Pfad wie `/dev/serial/by-id/...` ist besser als `/dev/ttyUSB0`, weil die Schnittstelle sich sonst nach einem Neustart ändern kann.

## Hinweise zur Einrichtung

- Wenn du nur einen Zähler hast, reicht eine Installation aus.
- Für zwei oder mehr Zähler installierst du die App mehrfach mit jeweils eigener serieller Schnittstelle.

## MQTT-Entitäten

Der Reader veröffentlicht automatisch die Discovery-Konfigurationen und Status-Topics für Home Assistant. Nach einem Start der App und nach einer `online`-Nachricht auf `homeassistant/status` werden die Discovery-Daten erneut gesendet.

Wenn `device_name` geändert wird, legt Home Assistant ein neues Gerät und neue Entitäten an. Der bisherige Name sollte deshalb erhalten bleiben, damit verwaiste Einträge und doppelte Geräte vermieden werden.

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
