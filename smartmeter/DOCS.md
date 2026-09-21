# SmartmeterHA

This app reads encrypted VKW smart meter telegrams from one serial meter and publishes MQTT discovery entities for Home Assistant.

## Requirements

- Home Assistant OS or Supervised with the official Mosquitto Broker app
- The Home Assistant MQTT integration configured for that broker
- A supported serial USB adapter connected to the host
- The meter key as a hexadecimal string

Install one app instance per meter. To read two meters, install this app twice with different serial devices and device names.

## Configuration

Configure the app from its **Configuration** tab:

- `key`: Required hexadecimal reader key. It is stored as a password option.
- `comport`: Serial device exposed to the app, normally a stable `/dev/serial/by-id/...` path.
- `device_name`: Prefix used for MQTT topics and the Home Assistant device name. Keep the existing value when migrating to preserve entities.
- `log_level`: `0` for errors only, `1` for operational logs, or `2` for telegram data and decoded values.

The app obtains MQTT connection details from the Home Assistant MQTT service. Install and configure the official Mosquitto Broker app before starting SmartmeterHA.

## Home Assistant entities

The reader publishes MQTT discovery configuration and state topics using the existing device-name topic prefix. Discovery is sent again when Home Assistant publishes `online` on `homeassistant/status`.

Changing `device_name` creates a new set of Home Assistant entities. Keep the old name to avoid orphaned entities during migration.

## Troubleshooting

Check the app log for the selected serial device and MQTT connection status. Confirm that the configured device exists under `/dev/serial/by-id/` and that the reader key is the exact hexadecimal key supplied by the meter operator.

If the app cannot connect to MQTT, verify that the MQTT integration is configured and that the Mosquitto Broker app is running.
