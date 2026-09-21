# SmartmeterHA Home-Assistant-App

Home-Assistant-App zum Auslesen verschluesselter VKW-Smartmeter-Telegramme eines Kaifa MA309M H4LAT1 und zum Bereitstellen der Messwerte ueber die MQTT-Discovery.

Die Anwendung ist fuer einen Zaehler pro App-Installation ausgelegt. Fuer zwei Zaehler wird die App zweimal mit unterschiedlichen seriellen Schnittstellen installiert.

## Voraussetzungen

- Home Assistant OS oder Home Assistant Supervised
- Die offizielle Mosquitto-Broker-App
- Die MQTT-Integration von Home Assistant, eingerichtet fuer diesen Broker
- Ein unterstuetzter USB-Seriell-Adapter am Home-Assistant-Host
- Der hexadezimale Kundenschnittstellen-Schluessel des Zaehlerbetreibers

## Installation

1. Dieses Git-Repository unter **Einstellungen > Apps > App-Repository** hinzufuegen.
2. Die **SmartmeterHA**-App installieren.
3. Serielle Schnittstelle, Leseschluessel, Geraetename und Log-Level konfigurieren.
4. Die App starten und die App-Protokolle pruefen.

Die App verwendet den MQTT-Dienst von Home Assistant. MQTT-Broker-Zugangsdaten muessen nicht zusaetzlich in SmartmeterHA hinterlegt werden.

## Konfiguration

| Option | Beschreibung |
| --- | --- |
| `key` | Erforderlicher hexadezimaler Leseschluessel. Wird als Passwort-Option gespeichert. |
| `comport` | Serielle Schnittstelle. Wenn moeglich einen stabilen Pfad unter `/dev/serial/by-id/...` verwenden. |
| `device_name` | Praefix fuer MQTT-Topics und Name des Home-Assistant-Geraets. Bei einer Migration den bisherigen Wert beibehalten. |
| `log_level` | `0` fuer Fehler, `1` fuer Betriebsprotokolle, `2` fuer Telegrammdaten und dekodierte Werte. |

Die App stellt die UART-Geraete des Hosts ueber das Hardware-Mapping von Home Assistant bereit. `/dev/ttyUSB0` ist der Standardwert fuer einfache Installationen. Ein stabiler by-id-Pfad wird bevorzugt.

## MQTT-Entitaeten

Der bestehende Reader veroeffentlicht dieselben MQTT-Topics und Discovery-Kennungen wie die urspruengliche Container-Installation. Discovery-Nachrichten werden beim Start der App und erneut nach einer `online`-Nachricht auf `homeassistant/status` gesendet.

Wenn `device_name` geaendert wird, erstellt Home Assistant ein neues Geraet und neue Entitaeten. Den bisherigen Namen beibehalten, damit Eintraege in der Entitaeten-Registry erhalten bleiben.

## Unterstuetzte Hardware

- Kaifa MA309M H4LAT1 Smartmeter aus dem VKW-Gebiet Vorarlberg
- USB-Seriell-/MBus-Adapter, der die Kundenschnittstelle als UART-Geraet bereitstellt

Andere Zaehler wurden nicht getestet.

## Entwicklung

Der Quellcode der App liegt unter `smartmeter/`. Die Reader-Module werden in der ersten Packaging-Phase bewusst unveraendert aus der urspruenglichen Container-Implementierung uebernommen.

Build- und Laufzeit-Tests sollten auf einer Home-Assistant-OS- oder Supervised-Testinstallation mit echtem Adapter und Zaehler durchgefuehrt werden. Das lokale Repository simuliert keine verschluesselten Zaehlertelegramme.

## Danksagung

Der Reader basiert auf der Arbeit von [greenMikeEU](https://github.com/greenMikeEU) und der Anleitung von [Michael Reitbauer](https://www.michaelreitbauer.at/kaifa-ma309-auslesen-smart-meter-evn/).
