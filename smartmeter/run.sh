#!/usr/bin/with-contenv bashio

KEY="$(bashio::config 'key')"
if [ -z "${KEY}" ]; then
    bashio::exit.nok "The reader key is required"
fi

export KEY
export COMPORT="$(bashio::config 'comport')"
export DEVICE_NAME="$(bashio::config 'device_name')"
export LOG_LEVEL="$(bashio::config 'log_level')"

export MQTT_BROKER="$(bashio::services mqtt 'host')"
export MQTT_PORT="$(bashio::services mqtt 'port')"
export MQTT_USER="$(bashio::services mqtt 'username')"
export MQTT_PASSWORD="$(bashio::services mqtt 'password')"

bashio::log.info "Starting SmartmeterHA for ${COMPORT}"
exec python3 -u /SmartMeterVKW.py
