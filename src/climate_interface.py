"""
Climate Service Interface – Assignment 2
"""

from dataclasses import dataclass

from someipy import (
    Event,
    EventGroup,
    Method,
    ServiceBuilder,
    TransportLayerProtocol,
)

from someipy.serialization import SomeIpPayload, Sint16, Uint8


# Service details

CLIMATE_SERVICE_ID = 0x2234
CLIMATE_INSTANCE_ID = 0x0001
CLIMATE_MAJOR_VERSION = 1

CLIMATE_IP = "127.0.0.1"
CLIMATE_PROVIDER_PORT = 4000
CLIMATE_CONSUMER_PORT = 4002


# Method IDs

GET_CABIN_TEMPERATURE_METHOD_ID = 0x0001
SET_TARGET_TEMPERATURE_METHOD_ID = 0x0002


# Event IDs

CABIN_TEMPERATURE_CHANGED_EVENT_ID = 0x8001
CLIMATE_EVENTGROUP_ID = 0x0001


# Cabin temperature payload

@dataclass
class TemperaturePayload(SomeIpPayload):

    temperature: Sint16

    def __init__(self, temperature: int = 240):
        self.temperature = Sint16(temperature)


# Target temperature request payload

@dataclass
class TargetTemperaturePayload(SomeIpPayload):

    target_temperature: Sint16

    def __init__(self, target_temperature: int = 240):
        self.target_temperature = Sint16(target_temperature)


# Status response payload

@dataclass
class TemperatureStatusPayload(SomeIpPayload):

    status: Uint8

    def __init__(self, status: int = 0):
        self.status = Uint8(status)


# Define methods

get_cabin_temperature_method = Method(
    id=GET_CABIN_TEMPERATURE_METHOD_ID,
    protocol=TransportLayerProtocol.UDP,
)

set_target_temperature_method = Method(
    id=SET_TARGET_TEMPERATURE_METHOD_ID,
    protocol=TransportLayerProtocol.UDP,
)


# Define event

cabin_temperature_changed_event = Event(
    id=CABIN_TEMPERATURE_CHANGED_EVENT_ID,
    protocol=TransportLayerProtocol.UDP,
)


# Define event group

climate_eventgroup = EventGroup(
    id=CLIMATE_EVENTGROUP_ID,
    events=[cabin_temperature_changed_event],
)


# Build Climate Service

climate_service = (
    ServiceBuilder()
    .with_service_id(CLIMATE_SERVICE_ID)
    .with_major_version(CLIMATE_MAJOR_VERSION)
    .with_method(get_cabin_temperature_method)
    .with_method(set_target_temperature_method)
    .with_eventgroup(climate_eventgroup)
    .build()
)
