import json


DISCOVERY_PREFIX = "homeassistant"
TOPIC_PREFIX = "smartmeter"
ORIGIN = {
    "name": "SmartmeterHA",
    "support_url": "https://github.com/Simeon-byte/SmartMeterHA",
}

SENSORS = (
    {
        "key": "Zaehlernummer",
        "name": "Zahlernummer",
        "entity_category": "diagnostic",
    },
    {
        "key": "SpannungL1",
        "name": "Spannung L1",
        "device_class": "voltage",
        "state_class": "measurement",
        "unit_of_measurement": "V",
    },
    {
        "key": "SpannungL2",
        "name": "Spannung L2",
        "device_class": "voltage",
        "state_class": "measurement",
        "unit_of_measurement": "V",
    },
    {
        "key": "SpannungL3",
        "name": "Spannung L3",
        "device_class": "voltage",
        "state_class": "measurement",
        "unit_of_measurement": "V",
    },
    {
        "key": "StromL1",
        "name": "Strom L1",
        "device_class": "current",
        "state_class": "measurement",
        "unit_of_measurement": "A",
    },
    {
        "key": "StromL2",
        "name": "Strom L2",
        "device_class": "current",
        "state_class": "measurement",
        "unit_of_measurement": "A",
    },
    {
        "key": "StromL3",
        "name": "Strom L3",
        "device_class": "current",
        "state_class": "measurement",
        "unit_of_measurement": "A",
    },
    {
        "key": "MomentanleistungP",
        "name": "Momentanleistung P",
        "device_class": "power",
        "state_class": "measurement",
        "unit_of_measurement": "W",
    },
    {
        "key": "MomentanleistungN",
        "name": "Momentanleistung N",
        "device_class": "power",
        "state_class": "measurement",
        "unit_of_measurement": "W",
    },
    {
        "key": "WirkenergieP",
        "name": "Wirkenergie P",
        "device_class": "energy",
        "state_class": "total_increasing",
        "unit_of_measurement": "kWh",
    },
    {
        "key": "WirkenergieN",
        "name": "Wirkenergie N",
        "device_class": "energy",
        "state_class": "total_increasing",
        "unit_of_measurement": "kWh",
    },
    {
        "key": "BlindleistungP",
        "name": "Blindleistung P",
        "device_class": "power",
        "unit_of_measurement": "W",
    },
    {
        "key": "BlindleistungN",
        "name": "Blindleistung N",
        "device_class": "power",
        "unit_of_measurement": "W",
    },
)


def state_topic(instance_id, key):
    return f"{TOPIC_PREFIX}/{instance_id}/{key}"


def discovery_topic(instance_id, key):
    return f"{DISCOVERY_PREFIX}/sensor/{instance_id}/{key}/config"


def build_discovery_messages(device_name, instance_id, software_version=None):
    device = {
        "name": device_name,
        "identifiers": [f"smartmeter:{instance_id}"],
        "manufacturer": "Kaifa",
        "model": "MA309MH4LAT1",
    }
    if software_version:
        device["sw_version"] = software_version

    messages = []
    for sensor in SENSORS:
        key = sensor["key"]
        payload = {
            "name": sensor["name"],
            "state_topic": state_topic(instance_id, key),
            "unique_id": f"smartmeter_{instance_id}_{key}",
            "device": device,
            "availability_topic": state_topic(instance_id, "status"),
            "payload_available": "online",
            "payload_not_available": "offline",
            "origin": ORIGIN,
        }
        payload.update(
            {
                field: sensor[field]
                for field in (
                    "device_class",
                    "entity_category",
                    "state_class",
                    "unit_of_measurement",
                )
                if field in sensor
            }
        )
        messages.append((discovery_topic(instance_id, key), payload))
    return messages


def sendDiscoveryMessage(client, device_name, instance_id, software_version=None):
    for topic, payload in build_discovery_messages(
        device_name, instance_id, software_version
    ):
        client.publish(topic, json.dumps(payload), qos=1)


def clearLegacyDiscoveryMessages(client, device_name):
    for sensor in SENSORS:
        topic = f"{DISCOVERY_PREFIX}/sensor/{device_name}/{sensor['key']}/config"
        client.publish(topic, "", qos=1, retain=True)
