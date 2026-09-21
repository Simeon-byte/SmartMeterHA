import json


def sendDiscoveryMessage(client, deviceName):
    device = {
        "name": deviceName,
        "identifiers": [deviceName],
        "model": "MA309MH4LAT1",
    }
    topics = [
        {
            "topic": f"homeassistant/sensor/{deviceName}/Zaehlernummer/config",
            "payload": {
                "name": "Zaehlernummer",
                "state_topic": f"{deviceName}/Zaehlernummer",
                "value_template": "{{ value }}",
                "unique_id": f"{deviceName}/Zaehlernummer",
                "device": device,
            },
        },
        {
            "topic": f"homeassistant/sensor/{deviceName}/SpannungL1/config",
            "payload": {
                "name": "SpannungL1",
                "state_topic": f"{deviceName}/SpannungL1",
                "value_template": "{{ value }}",
                "device_class": "voltage",
                "unit_of_measurement": "V",
                "unique_id": f"{deviceName}/SpannungL1",
                "device": device,
            },
        },
        {
            "topic": f"homeassistant/sensor/{deviceName}/SpannungL2/config",
            "payload": {
                "name": "SpannungL2",
                "state_topic": f"{deviceName}/SpannungL2",
                "value_template": "{{ value }}",
                "device_class": "voltage",
                "unit_of_measurement": "V",
                "unique_id": f"{deviceName}/SpannungL2",
                "device": device,
            },
        },
        {
            "topic": f"homeassistant/sensor/{deviceName}/SpannungL3/config",
            "payload": {
                "name": "SpannungL3",
                "state_topic": f"{deviceName}/SpannungL3",
                "value_template": "{{ value }}",
                "device_class": "voltage",
                "unit_of_measurement": "V",
                "unique_id": f"{deviceName}/SpannungL3",
                "device": device,
            },
        },
        {
            "topic": f"homeassistant/sensor/{deviceName}/StromL1/config",
            "payload": {
                "name": "StromL1",
                "state_topic": f"{deviceName}/StromL1",
                "value_template": "{{ value }}",
                "device_class": "current",
                "unit_of_measurement": "A",
                "unique_id": f"{deviceName}/StromL1",
                "device": device,
            },
        },
        {
            "topic": f"homeassistant/sensor/{deviceName}/StromL2/config",
            "payload": {
                "name": "StromL2",
                "state_topic": f"{deviceName}/StromL2",
                "value_template": "{{ value }}",
                "device_class": "current",
                "unit_of_measurement": "A",
                "unique_id": f"{deviceName}/StromL2",
                "device": device,
            },
        },
        {
            "topic": f"homeassistant/sensor/{deviceName}/StromL3/config",
            "payload": {
                "name": "StromL3",
                "state_topic": f"{deviceName}/StromL3",
                "value_template": "{{ value }}",
                "device_class": "current",
                "unit_of_measurement": "A",
                "unique_id": f"{deviceName}/StromL3",
                "device": device,
            },
        },
        {
            "topic": f"homeassistant/sensor/{deviceName}/MomentanleistungP/config",
            "payload": {
                "name": "MomentanleistungP",
                "state_topic": f"{deviceName}/MomentanleistungP",
                "value_template": "{{ value }}",
                "device_class": "power",
                "unit_of_measurement": "W",
                "unique_id": f"{deviceName}/MomentanleistungP",
                "device": device,
            },
        },
        {
            "topic": f"homeassistant/sensor/{deviceName}/MomentanleistungN/config",
            "payload": {
                "name": "MomentanleistungN",
                "state_topic": f"{deviceName}/MomentanleistungN",
                "value_template": "{{ value }}",
                "device_class": "power",
                "unit_of_measurement": "W",
                "unique_id": f"{deviceName}/MomentanleistungN",
                "device": device,
            },
        },
        {
            "topic": f"homeassistant/sensor/{deviceName}/WirkenergieP/config",
            "payload": {
                "name": "WirkenergieP",
                "state_topic": f"{deviceName}/WirkenergieP",
                "state_class": "total_increasing",
                "value_template": "{{ value }}",
                "device_class": "energy",
                "unit_of_measurement": "kWh",
                "unique_id": f"{deviceName}/WirkenergieP",
                "device": device,
            },
        },
        {
            "topic": f"homeassistant/sensor/{deviceName}/WirkenergieN/config",
            "payload": {
                "name": "WirkenergieN",
                "state_topic": f"{deviceName}/WirkenergieN",
                "state_class": "total_increasing",
                "value_template": "{{ value }}",
                "device_class": "energy",
                "unit_of_measurement": "kWh",
                "unique_id": f"{deviceName}/WirkenergieN",
                "device": device,
            },
        },
        {
            "topic": f"homeassistant/sensor/{deviceName}/BlindleistungP/config",
            "payload": {
                "name": "BlindleistungP",
                "state_topic": f"{deviceName}/BlindleistungP",
                "value_template": "{{ value }}",
                "device_class": "power",
                "unit_of_measurement": "W",
                "unique_id": f"{deviceName}/BlindleistungP",
                "device": device,
            },
        },
        {
            "topic": f"homeassistant/sensor/{deviceName}/BlindleistungN/config",
            "payload": {
                "name": "BlindleistungN",
                "state_topic": f"{deviceName}/BlindleistungN",
                "value_template": "{{ value }}",
                "device_class": "power",
                "unit_of_measurement": "W",
                "unique_id": f"{deviceName}/BlindleistungN",
                "device": device,
            },
        },
    ]
    for topic in topics:
        client.publish(topic["topic"], json.dumps(topic["payload"]), qos=1)
