FROM ghcr.io/home-assistant/base:latest

ARG BUILD_VERSION=0.2.0
ARG BUILD_ARCH=amd64

LABEL \
    io.hass.version="${BUILD_VERSION}" \
    io.hass.type="app" \
    io.hass.arch="${BUILD_ARCH}"

COPY requirements.txt /

RUN apk add --no-cache \
    python3 \
    py3-pip \
    && python3 -m pip install --no-cache-dir --break-system-packages -r /requirements.txt

COPY run.sh /
COPY HADiscovery.py /
COPY SmartMeterVKW.py /

RUN chmod a+x /run.sh

CMD ["/run.sh"]
