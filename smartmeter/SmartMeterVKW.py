from os import system, name
import sys
from time import sleep
import binascii
import datetime
import logging
import re
import time
import serial
from Cryptodome.Cipher import AES
import paho.mqtt.client as mqtt
import os

from HADiscovery import clearLegacyDiscoveryMessages, sendDiscoveryMessage, state_topic

# Environment Variable setzen, damit der Fehler nicht auf der Console Kommt
os.environ["TERM"] = "xterm"

TRACE_LEVEL = logging.DEBUG - 1
logging.addLevelName(TRACE_LEVEL, "TRACE")

LOG_LEVELS = {
    "ERROR": logging.ERROR,
    "WARNING": logging.WARNING,
    "INFO": logging.INFO,
    "DEBUG": logging.DEBUG,
    "TRACE": TRACE_LEVEL,
}

logLevelName = os.getenv("LOG_LEVEL", "INFO").strip().upper()
if logLevelName not in LOG_LEVELS:
    print(
        "Invalid LOG_LEVEL {!r}. Expected one of: {}".format(
            logLevelName, ", ".join(LOG_LEVELS)
        ),
        file=sys.stderr,
    )
    sys.exit(2)

logger = logging.getLogger("smartmeter")
logger.setLevel(LOG_LEVELS[logLevelName])
logger.propagate = False
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(
    logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s")
)
logger.addHandler(handler)

deviceName = os.getenv("DEVICE_NAME", "SmartMeterVKW")
logger.info("Device name: %s", deviceName)
instanceId = os.getenv("INSTANCE_ID", "smartmeter-1")
if re.fullmatch(r"[a-z0-9_-]+", instanceId) is None:
    logger.error(
        "Invalid INSTANCE_ID %r; use only lowercase letters, numbers, '-' or '_'",
        instanceId,
    )
    sys.exit(2)
logger.info("Instance ID: %s", instanceId)

mqttBroker = os.getenv("MQTT_BROKER", "localhost")
mqttuser = os.getenv("MQTT_USER", None)
mqttpasswort = os.getenv("MQTT_PASSWORD", None)
mqttport = int(os.getenv("MQTT_PORT", 1883))
logger.info("MQTT broker: %s", mqttBroker)
logger.info("MQTT user: %s", mqttuser)
logger.info("MQTT password: %s", "[is set]" if mqttpasswort is not None else "None")
logger.info("MQTT port: %s", mqttport)
# Comport Config/Init
comport = os.getenv("COMPORT", "/dev/ttyUSB0")
logger.info("Serial port: %s", comport)

key_value = os.getenv("KEY")
if key_value is None:
    logger.error("No meter key provided")
    sys.exit()
logger.info("Meter key is present")
logger.debug("Meter key: %s", key_value)
try:
    key = binascii.unhexlify(key_value)
except binascii.Error as err:
    logger.error("Meter key is not valid hexadecimal: %s", err)
    sys.exit(2)


def clear():
    if logger.isEnabledFor(logging.DEBUG):
        if name == "nt":
            _ = system("cls")

        else:
            _ = system("clear")


def mqttPublish(topic, payload):
    topics = [state_topic(instanceId, topic), f"{deviceName}/{topic}"]
    for publishTopic in dict.fromkeys(topics):
        response = client.publish(publishTopic, payload, 1)
        if not response.is_published():
            logger.warning("MQTT message could not be published: %s", publishTopic)


client = mqtt.Client(f"smartmeter-{instanceId}")
statusTopic = state_topic(instanceId, "status")
legacyStatusTopic = f"{deviceName}/status"
client.will_set(statusTopic, "offline", qos=1, retain=True)
try:
    client.username_pw_set(mqttuser, mqttpasswort)
    client.connect(mqttBroker, mqttport)
    client.publish(statusTopic, "online", qos=1, retain=True)
    client.publish(legacyStatusTopic, "online", qos=1, retain=True)
    logger.info("Connected to Broker")
except Exception as err:
    logger.error(
        "MQTT broker is not reachable or credentials are invalid: %s", err
    )


# Send HomeAssistant discovery message
clearLegacyDiscoveryMessages(client, deviceName)
sendDiscoveryMessage(client, deviceName, instanceId)


# on Message Callback
def on_message(client, userdata, msg):
    logger.debug("Received `%s` from `%s` topic", msg.payload.decode(), msg.topic)

    if msg.topic == "homeassistant/status":
        if msg.payload.decode() == "online":
            logger.info(
                "Received online status from Homeassistant - Re-sending Discovery Message"
            )
            sendDiscoveryMessage(client, deviceName, instanceId)


def on_connect(client, userdata, flags, rc):
    if rc != 0:
        logger.warning("MQTT connection failed with result code: %s", rc)
        return
    client.publish(statusTopic, "online", qos=1, retain=True)
    client.publish(legacyStatusTopic, "online", qos=1, retain=True)
    client.subscribe("homeassistant/status")
    sendDiscoveryMessage(client, deviceName, instanceId)
    logger.info("MQTT connection established; status and discovery refreshed")


FIRST_RECONNECT_DELAY = 1
RECONNECT_RATE = 2
MAX_RECONNECT_COUNT = 12
MAX_RECONNECT_DELAY = 60


def on_disconnect(client, userdata, rc):
    logger.warning("Disconnected with result code: %s", rc)
    reconnect_count, reconnect_delay = 0, FIRST_RECONNECT_DELAY
    while reconnect_count < MAX_RECONNECT_COUNT:
        logger.debug("Reconnecting in %s seconds...", reconnect_delay)
        time.sleep(reconnect_delay)

        try:
            client.reconnect()
            logger.info("Reconnected successfully!")
            return
        except Exception as err:
            logger.warning("%s. Reconnect failed. Retrying...", err)

        reconnect_delay *= RECONNECT_RATE
        reconnect_delay = min(reconnect_delay, MAX_RECONNECT_DELAY)
        reconnect_count += 1
    logger.error("Reconnect failed after %s attempts. Exiting...", reconnect_count)
    sys.exit(1)


# Subscribe to Homeassistant Status Topic (online/offline)
client.subscribe("homeassistant/status")

# Set Callbacks
client.on_connect = on_connect
client.on_message = on_message
client.on_disconnect = on_disconnect


def recv(serial):
    while True:
        data = serial.read_all()
        if data == "":
            logger.debug("Waiting for serial data")
            continue
        else:
            # log ("\n...lausche auf Schnittstelle", 2)
            break
    return data


if __name__ == "__main__":
    serial = serial.Serial(
        port=comport,
        baudrate=2400,
        parity=serial.PARITY_EVEN,
        stopbits=serial.STOPBITS_ONE,
        bytesize=serial.EIGHTBITS,
    )
    client.loop_start()
    # Header Startbytes vom Vorarlberger Smartmeter
    headerstart = "68fafa68"

    logger.info("Starting SmartMeter with log level %s", logLevelName)
    while True:

        sleep(5)

        data = recv(serial)
        doit = 0
        if (data != b"") & (len(data) >= 355):
            startbytes = data[0:4].hex()

            if startbytes == headerstart:
                doit = 1
                # log ("Laenge von data = ", len(data))
            else:
                # syncronisierung nötig
                clear()
                logger.warning("Serial data is out of sync; resynchronizing")
                # log ("Laenge von data = ", len(data))
                serial.flushInput()
                sleep(0.5)

        if doit == 1:
            clear()
            logger.log(TRACE_LEVEL, "data: " + data.hex())
            msglen1 = int(hex(data[1]), 16)  # 1. FA --- 250 Byte
            # log ("msg1: ", msglen1)

            header1 = 27
            header2 = 9

            splitinfo = data[6]  # wenn hier 00, dann gibts noch eine Nachricht

            systitle = data[11:19]  # hier steht der SysTitle --- 8 Bytes
            # log ("systitle:", systitle.hex() )

            ic = data[23:27]  # hier steht der SysTitle --- 4 Bytes
            iv = systitle + ic  # iv ist 12 Bytes
            # log ("iv= ", iv.hex() , "Länge: ", len(iv))

            # log ("\nmsg1:")
            msg1 = data[header1 : (6 + msglen1 - 2)]
            # log (msg1.hex())
            # log ("Länge: ",len(msg1))

            # log ("\nmsg2:")
            msglen2 = int(hex(data[msglen1 + 7]), 16)  # 1. FA --- 38 Byte
            # log ("msglen2: ", msglen2)
            # log (hex(data[msglen1+7]))

            msg2 = data[msglen1 + 6 + header2 : (msglen1 + 5 + 5 + msglen2)]
            cyphertext = msg1 + msg2

            cyphertext_bytes = binascii.unhexlify(cyphertext.hex())
            cipher = AES.new(key, AES.MODE_GCM, nonce=iv)
            decrypted = cipher.decrypt(cyphertext_bytes)

            # OBIS Code Werte aus decrypted.hex auslesen
            databin = decrypted.hex()
            ueberschrift = (
                "\n\t\t*** KUNDENSCHNITTSTELLE ***\n\nOBIS Code\tBezeichnung\t\t\t Wert"
            )
            logger.debug(ueberschrift)

            obis_len = 12

            # Datum Uhrzeit lesen
            # 0000010000ff
            obis_zeitstempel = "0000010000ff"
            obis_zeitstempel_offset = 4
            obis_zeitlaenge = 24
            obis_zeitstempel_pos = databin.find(obis_zeitstempel)
            if obis_zeitstempel_pos > 1:
                obis_datum_zeit = databin[
                    obis_len
                    + obis_zeitstempel_pos
                    + obis_zeitstempel_offset : obis_len
                    + obis_zeitstempel_pos
                    + obis_zeitstempel_offset
                    + obis_zeitlaenge
                ]
                jahr = int(obis_datum_zeit[:4], 16)
                monat = int(obis_datum_zeit[4:6], 16)
                tag = int(obis_datum_zeit[6:8], 16)
                stunde = int(obis_datum_zeit[10:12], 16)
                minute = int(obis_datum_zeit[12:14], 16)
                sekunde = int(obis_datum_zeit[14:16], 16)

                obis_datum_zeit = datetime.datetime(
                    jahr, monat, tag, stunde, minute, sekunde
                )
                # datum_zeit = "0.0.1.0.0.255\tDatum Zeit:\t\t\t "+obis_datum_zeit.strftime("%d.%m.%Y %H:%M:%S")
                datum_zeit = obis_datum_zeit.strftime("%d.%m.%Y %H:%M:%S")

                logger.debug(datum_zeit)
                mqttPublish("Zeit", obis_datum_zeit.strftime("%Y-%m-%d %H:%M:%S"))

            else:
                # obis fehler
                datum_zeit = "\n*** kann OBIS Code nicht finden ===> key Fehler? ***\n"
                logger.warning(datum_zeit)

            # Zählernummer des Netzbetreibers
            # 0000600100ff
            obis_zaehlernummer = "0000600100ff"
            obis_zaehlernummer_pos = databin.find(obis_zaehlernummer)
            if obis_zaehlernummer_pos > 1:
                obis_zaehlernummer_anzzeichen = 2 * int(
                    databin[
                        obis_zaehlernummer_pos
                        + obis_len
                        + 2 : obis_zaehlernummer_pos
                        + obis_len
                        + 4
                    ],
                    16,
                )
                obis_zaehlernummer = databin[
                    obis_zaehlernummer_pos
                    + obis_len
                    + 4 : obis_zaehlernummer_pos
                    + obis_len
                    + 4
                    + obis_zaehlernummer_anzzeichen
                ]
                bytes_object = bytes.fromhex(obis_zaehlernummer)
                zaehlernummer = (
                    "0.0.96.1.0.255\tZaehlernummer:\t\t\t "
                    + bytes_object.decode("ASCII")
                )
                zaehlernummerfilename = bytes_object.decode("ASCII")
                logger.debug(zaehlernummer)
                mqttPublish("Zaehlernummer", bytes_object.decode("ASCII"))

            # COSEM Logical Device Name
            # 00002a0000ff
            obis_cosemlogdevname = "00002a0000ff"
            obis_cosemlogdevname_pos = databin.find(obis_cosemlogdevname)
            if obis_cosemlogdevname_pos > 1:
                obis_cosemlogdevname_anzzeichen = 2 * int(
                    databin[
                        obis_cosemlogdevname_pos
                        + obis_len
                        + 2 : obis_cosemlogdevname_pos
                        + obis_len
                        + 4
                    ],
                    16,
                )
                obis_cosemlogdevname = databin[
                    obis_cosemlogdevname_pos
                    + obis_len
                    + 4 : obis_cosemlogdevname_pos
                    + obis_len
                    + 4
                    + obis_cosemlogdevname_anzzeichen
                ]
                bytes_object = bytes.fromhex(obis_cosemlogdevname)
                cosemlogdevname = (
                    "0.0.42.0.0.255\tCOSEM logical device name:\t "
                    + bytes_object.decode("ASCII")
                )

                logger.debug(cosemlogdevname)
                mqttPublish("Cosemlogdevname", bytes_object.decode("ASCII"))

            # Spannung L1 (V)
            # 0100200700ff
            obis_spannungl1 = "0100200700ff"
            obis_spannungl1_pos = databin.find(obis_spannungl1)
            if obis_spannungl1_pos > 1:
                obis_spannungl1_anzzeichen = 4
                obis_spannungl1 = databin[
                    obis_spannungl1_pos
                    + obis_len
                    + 2 : obis_spannungl1_pos
                    + obis_len
                    + 2
                    + obis_spannungl1_anzzeichen
                ]
                spannungl1 = "1.0.32.7.0.255\tSpannung L1 (V):\t\t " + str(
                    int(obis_spannungl1, 16) / 10
                )

                logger.debug(spannungl1)
                mqttPublish("SpannungL1", int(obis_spannungl1, 16) / 10)

            # Spannung L2 (V)
            # 0100340700FF
            obis_spannungl2 = "0100340700ff"
            obis_spannungl2_pos = databin.find(obis_spannungl2)
            if obis_spannungl2_pos > 1:
                obis_spannungl2_anzzeichen = 4
                obis_spannungl2 = databin[
                    obis_spannungl2_pos
                    + obis_len
                    + 2 : obis_spannungl2_pos
                    + obis_len
                    + 2
                    + obis_spannungl2_anzzeichen
                ]
                spannungl2 = "1.0.52.7.0.255\tSpannung L2 (V):\t\t " + str(
                    int(obis_spannungl2, 16) / 10
                )

                logger.debug(spannungl2)
                mqttPublish("SpannungL2", int(obis_spannungl2, 16) / 10)

            # Spannung L3 (V)
            # 0100480700ff
            obis_spannungl3 = "0100480700ff"
            obis_spannungl3_pos = databin.find(obis_spannungl3)
            if obis_spannungl3_pos > 1:
                obis_spannungl3_anzzeichen = 4
                obis_spannungl3 = databin[
                    obis_spannungl3_pos
                    + obis_len
                    + 2 : obis_spannungl3_pos
                    + obis_len
                    + 2
                    + obis_spannungl3_anzzeichen
                ]
                spannungl3 = "1.0.72.7.0.255\tSpannung L3 (V):\t\t " + str(
                    int(obis_spannungl3, 16) / 10
                )

                logger.debug(spannungl3)
                mqttPublish("SpannungL3", int(obis_spannungl3, 16) / 10)

            # Strom L1 (A)
            # 01001f0700ff
            obis_stroml1 = "01001f0700ff"
            obis_stroml1_pos = databin.find(obis_stroml1)
            if obis_stroml1_pos > 1:
                obis_stroml1_anzzeichen = 4
                obis_stroml1 = databin[
                    obis_stroml1_pos
                    + obis_len
                    + 2 : obis_stroml1_pos
                    + obis_len
                    + 2
                    + obis_stroml1_anzzeichen
                ]
                stroml1 = "1.0.31.7.0.255\tStrom L1 (A):\t\t\t " + str(
                    int(obis_stroml1, 16) / 100
                )

                logger.debug(stroml1)
                mqttPublish("StromL1", int(obis_stroml1, 16) / 100)

            # Strom L2 (A)
            # 0100330700ff
            obis_stroml2 = "0100330700ff"
            obis_stroml2_pos = databin.find(obis_stroml2)
            if obis_stroml2_pos > 1:
                obis_stroml2_anzzeichen = 4
                obis_stroml2 = databin[
                    obis_stroml2_pos
                    + obis_len
                    + 2 : obis_stroml2_pos
                    + obis_len
                    + 2
                    + obis_stroml2_anzzeichen
                ]
                stroml2 = "1.0.51.7.0.255\tStrom L2 (A):\t\t\t " + str(
                    int(obis_stroml2, 16) / 100
                )

                logger.debug(stroml2)
                mqttPublish("StromL2", int(obis_stroml2, 16) / 100)

            # Strom L3 (A)
            # 0100470700ff
            obis_stroml3 = "0100470700ff"
            obis_stroml3_pos = databin.find(obis_stroml3)
            if obis_stroml3_pos > 1:
                obis_stroml3_anzzeichen = 4
                obis_stroml3 = databin[
                    obis_stroml3_pos
                    + obis_len
                    + 2 : obis_stroml3_pos
                    + obis_len
                    + 2
                    + obis_stroml3_anzzeichen
                ]
                stroml3 = "1.0.71.7.0.255\tStrom L3 (A):\t\t\t " + str(
                    int(obis_stroml3, 16) / 100
                )

                logger.debug(stroml3)
                mqttPublish("StromL3", int(obis_stroml3, 16) / 100)

            # Wirkleistung Bezug +P (W)
            # 0100010700ff
            obis_wirkleistungbezug = "0100010700ff"
            obis_wirkleistungbezug_pos = databin.find(obis_wirkleistungbezug)
            if obis_wirkleistungbezug_pos > 1:
                obis_wirkleistungbezug_anzzeichen = 8
                obis_wirkleistungbezug = databin[
                    obis_wirkleistungbezug_pos
                    + obis_len
                    + 2 : obis_wirkleistungbezug_pos
                    + obis_len
                    + 2
                    + obis_wirkleistungbezug_anzzeichen
                ]
                wirkleistungbezug = "1.0.1.7.0.255\tWirkleistung Bezug [kW]:\t " + str(
                    int(obis_wirkleistungbezug, 16) / 1000
                )

                logger.debug(wirkleistungbezug)
                mqttPublish(
                    "MomentanleistungP",
                    int(obis_wirkleistungbezug, 16),
                )

            # Wirkleistung Lieferung -P (W)
            # 0100020700ff
            obis_wirkleistunglieferung = "0100020700ff"
            obis_wirkleistunglieferung_pos = databin.find(obis_wirkleistunglieferung)
            if obis_wirkleistunglieferung_pos > 1:
                obis_wirkleistunglieferung_anzzeichen = 8
                obis_wirkleistunglieferung = databin[
                    obis_wirkleistunglieferung_pos
                    + obis_len
                    + 2 : obis_wirkleistunglieferung_pos
                    + obis_len
                    + 2
                    + obis_wirkleistunglieferung_anzzeichen
                ]
                wirkleistunglieferung = (
                    "1.0.2.7.0.255\tWirkleistung Lieferung [kW]:\t "
                    + str(int(obis_wirkleistunglieferung, 16) / 1000)
                )

                logger.debug(wirkleistunglieferung)
                mqttPublish(
                    "MomentanleistungN",
                    int(obis_wirkleistunglieferung, 16),
                )

            # Wirkenergie Bezug +A (Wh)
            # 0100010800ff
            obis_wirkenergiebezug = "0100010800ff"
            obis_wirkenergiebezug_pos = databin.find(obis_wirkenergiebezug)
            if obis_wirkenergiebezug_pos > 1:
                obis_wirkenergiebezug_anzzeichen = 8
                obis_wirkenergiebezug = databin[
                    obis_wirkenergiebezug_pos
                    + obis_len
                    + 2 : obis_wirkenergiebezug_pos
                    + obis_len
                    + 2
                    + obis_wirkenergiebezug_anzzeichen
                ]
                wirkenergiebezug = "1.0.1.8.0.255\tWirkenergie Bezug [kWh]:\t " + str(
                    int(obis_wirkenergiebezug, 16) / 1000
                )

                logger.debug(wirkenergiebezug)
                mqttPublish("WirkenergieP", int(obis_wirkenergiebezug, 16) / 1000)

            # Wirkenergie Lieferung -A (Wh)
            # 0100020800ff
            obis_wirkenergielieferung = "0100020800ff"
            obis_wirkenergielieferung_pos = databin.find(obis_wirkenergielieferung)
            if obis_wirkenergielieferung_pos > 1:
                obis_wirkenergielieferung_anzzeichen = 8
                obis_wirkenergielieferung = databin[
                    obis_wirkenergielieferung_pos
                    + obis_len
                    + 2 : obis_wirkenergielieferung_pos
                    + obis_len
                    + 2
                    + obis_wirkenergielieferung_anzzeichen
                ]
                wirkenergielieferung = (
                    "1.0.2.8.0.255\tWirkenergie Lieferung [kWh]:\t "
                    + str(int(obis_wirkenergielieferung, 16) / 1000)
                )

                logger.debug(wirkenergielieferung)
                mqttPublish("WirkenergieN", int(obis_wirkenergielieferung, 16) / 1000)

            # Blindleistung Bezug +R (Wh)
            # 0100030800ff
            obis_blindleistungbezug = "0100030800ff"
            obis_blindleistungbezug_pos = databin.find(obis_blindleistungbezug)
            if obis_blindleistungbezug_pos > 1:
                obis_blindleistungbezug_anzzeichen = 8
                obis_blindleistungbezug = databin[
                    obis_blindleistungbezug_pos
                    + obis_len
                    + 2 : obis_blindleistungbezug_pos
                    + obis_len
                    + 2
                    + obis_blindleistungbezug_anzzeichen
                ]
                blindleistungbezug = (
                    "1.0.3.8.0.255\tBlindleistung Bezug [kW]:\t "
                    + str(int(obis_blindleistungbezug, 16) / 1000)
                )

                logger.debug(blindleistungbezug)
                mqttPublish("BlindleistungP", int(obis_blindleistungbezug, 16) / 1000)

            # Blindleistung Lieferung -R (Wh)
            # 0100040800ff
            obis_blindleistunglieferung = "0100040800ff"
            obis_blindleistunglieferung_pos = databin.find(obis_blindleistunglieferung)
            if obis_blindleistunglieferung_pos > 1:
                obis_blindleistunglieferung_anzzeichen = 8
                obis_blindleistunglieferung = databin[
                    obis_blindleistunglieferung_pos
                    + obis_len
                    + 2 : obis_blindleistunglieferung_pos
                    + obis_len
                    + 2
                    + obis_blindleistunglieferung_anzzeichen
                ]
                blindleistunglieferung = (
                    "1.0.4.8.0.255\tBlindleistung Lieferung [kW]:\t "
                    + str(int(obis_blindleistunglieferung, 16) / 1000)
                )

                logger.debug(blindleistunglieferung)
                mqttPublish(
                    "BlindleistungN",
                    int(obis_blindleistunglieferung, 16) / 1000,
                )

serial.close()
