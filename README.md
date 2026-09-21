# SmartmeterHA Home Assistant App

Home Assistant app for reading encrypted VKW smart meter telegrams from a Kaifa MA309M H4LAT1 customer interface and exposing the measurements through MQTT discovery.

The reader is designed for one meter per app installation. Install the app twice when two serial meters need to be read.

## Requirements

- Home Assistant OS or Supervised
- The official Mosquitto Broker app
- The Home Assistant MQTT integration configured for Mosquitto
- A supported serial USB adapter connected to the Home Assistant host
- The hexadecimal customer-interface key from the meter operator

## Installation

1. Add this Git repository to **Settings > Apps > App repository**.
2. Install the **SmartmeterHA** app.
3. Configure the serial device, reader key, device name, and log level.
4. Start the app and inspect its logs.

The app uses the Home Assistant MQTT service. MQTT broker credentials are not duplicated in the SmartmeterHA configuration.

## Configuration

| Option | Description |
| --- | --- |
| `key` | Required hexadecimal reader key. Stored as a password option. |
| `comport` | Serial device. Prefer a stable `/dev/serial/by-id/...` path. |
| `device_name` | MQTT topic prefix and Home Assistant device name. Keep the old value when migrating. |
| `log_level` | `0` for errors, `1` for operational logs, `2` for telegram data and decoded values. |

The app exposes host UART devices through Home Assistant's app hardware mapping. The default `/dev/ttyUSB0` is provided for simple installations, but a stable by-id path is preferred when available.

## MQTT entities

The existing reader publishes the same MQTT topics and discovery identifiers as the original container deployment. Home Assistant discovery messages are sent when the app starts and again after an `online` message on `homeassistant/status`.

Changing `device_name` creates a new device and a new set of entities. Keep the existing name to preserve entity registry entries.

## Supported hardware

- Kaifa MA309M H4LAT1 smart meter used by VKW Vorarlberg
- USB serial/MBus adapter exposing the meter interface as a UART device

Other meters are not tested.

## Development

The app source is under `smartmeter/`. The reader modules are intentionally copied unchanged from the original container implementation in the first packaging phase.

Build and runtime validation should be performed on a Home Assistant OS or Supervised test installation with a real serial adapter and meter. The local repository does not emulate encrypted meter telegrams.

## Credits

The reader is based on the work by [greenMikeEU](https://github.com/greenMikeEU) and the guide by [Michael Reitbauer](https://www.michaelreitbauer.at/kaifa-ma309-auslesen-smart-meter-evn/).
