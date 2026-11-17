"""
Virtual Climate ECU – Assignment 2

Provides:
1. GetCabinTemperature method
2. SetTargetTemperature method
3. CabinTemperatureChanged event
"""

import asyncio
import logging
from typing import Tuple

from someipy import (
    MessageType,
    Method,
    MethodResult,
    ReturnCode,
    ServerServiceInstance,
    ServiceBuilder,
    TransportLayerProtocol,
    connect_to_someipy_daemon,
)

from someipy.someipy_logging import set_someipy_log_level

from climate_interface import (
    CLIMATE_SERVICE_ID,
    CLIMATE_INSTANCE_ID,
    CLIMATE_MAJOR_VERSION,
    CLIMATE_IP,
    CLIMATE_PROVIDER_PORT,
    GET_CABIN_TEMPERATURE_METHOD_ID,
    SET_TARGET_TEMPERATURE_METHOD_ID,
    CABIN_TEMPERATURE_CHANGED_EVENT_ID,
    CLIMATE_EVENTGROUP_ID,
    TemperaturePayload,
    TargetTemperaturePayload,
    TemperatureStatusPayload,
    climate_eventgroup,
)


# Initial temperatures (in tenths of degree Celsius)

current_temperature = 240
target_temperature = 240


# METHOD 1: GetCabinTemperature

async def get_temperature_handler(
    input_data: bytes,
    client_address: Tuple[str, int],
) -> MethodResult:

    print("\nGetCabinTemperature request received")

    print(
        f"Current cabin temperature: "
        f"{current_temperature / 10:.1f} °C"
    )

    response_payload = TemperaturePayload(
        current_temperature
    ).serialize()

    result = MethodResult()
    result.message_type = MessageType.RESPONSE
    result.return_code = ReturnCode.E_OK
    result.payload = response_payload

    print("Temperature response sent")

    return result


# METHOD 2: SetTargetTemperature

async def set_temperature_handler(
    input_data: bytes,
    client_address: Tuple[str, int],
) -> MethodResult:

    global target_temperature

    request = TargetTemperaturePayload().deserialize(
        input_data
    )

    requested_temperature = (
        request.target_temperature.value
    )

    print("\nSetTargetTemperature request received")

    print(
        f"Requested temperature: "
        f"{requested_temperature / 10:.1f} °C"
    )

    if 160 <= requested_temperature <= 300:

        target_temperature = requested_temperature
        status = 0

        print("Temperature ACCEPTED")

    else:

        status = 1

        print("INVALID TEMPERATURE")

    response_payload = TemperatureStatusPayload(
        status
    ).serialize()

    result = MethodResult()
    result.message_type = MessageType.RESPONSE
    result.return_code = ReturnCode.E_OK
    result.payload = response_payload

    print(f"Status: {status}")

    return result


# BUILD CLIMATE SERVICE

def build_climate_service():

    get_temperature_method = Method(
        id=GET_CABIN_TEMPERATURE_METHOD_ID,
        protocol=TransportLayerProtocol.UDP,
        method_handler=get_temperature_handler,
    )

    set_temperature_method = Method(
        id=SET_TARGET_TEMPERATURE_METHOD_ID,
        protocol=TransportLayerProtocol.UDP,
        method_handler=set_temperature_handler,
    )

    return (
        ServiceBuilder()
        .with_service_id(CLIMATE_SERVICE_ID)
        .with_major_version(CLIMATE_MAJOR_VERSION)
        .with_method(get_temperature_method)
        .with_method(set_temperature_method)
        .with_eventgroup(climate_eventgroup)
        .build()
    )


# SIMULATE CABIN TEMPERATURE

async def simulate_temperature(
    service_instance: ServerServiceInstance,
):

    global current_temperature

    while True:

        current_temperature += 5

        if current_temperature > 300:
            current_temperature = 240

        event_payload = TemperaturePayload(
            current_temperature
        ).serialize()

        print()
        print(
            f"Cabin temperature changed: "
            f"{current_temperature / 10:.1f} °C"
        )

        service_instance.send_event(
            CLIMATE_EVENTGROUP_ID,
            CABIN_TEMPERATURE_CHANGED_EVENT_ID,
            event_payload,
        )

        print("CabinTemperatureChanged event sent")

        await asyncio.sleep(3)


# MAIN FUNCTION

async def main():

    set_someipy_log_level(logging.INFO)

    print("=" * 60)
    print("Virtual Climate ECU")
    print("ClimateService Provider")
    print("=" * 60)

    print(f"Service ID: 0x{CLIMATE_SERVICE_ID:04X}")
    print(f"Instance ID: 0x{CLIMATE_INSTANCE_ID:04X}")
    print(f"GetCabinTemperature: 0x{GET_CABIN_TEMPERATURE_METHOD_ID:04X}")
    print(f"SetTargetTemperature: 0x{SET_TARGET_TEMPERATURE_METHOD_ID:04X}")
    print(f"Temperature Event: 0x{CABIN_TEMPERATURE_CHANGED_EVENT_ID:04X}")

    print("=" * 60)

    print("Connecting to someipy daemon...")

    daemon = await connect_to_someipy_daemon()

    print("Connected to someipy daemon")

    provider_service = build_climate_service()

    provider_instance = ServerServiceInstance(
        daemon=daemon,
        service=provider_service,
        instance_id=CLIMATE_INSTANCE_ID,
        endpoint_ip=CLIMATE_IP,
        endpoint_port=CLIMATE_PROVIDER_PORT,
        ttl=5,
        cyclic_offer_delay_ms=2000,
    )

    print("Offering ClimateService...")

    await provider_instance.start_offer()

    print("ClimateService is being offered")

    temperature_task = asyncio.create_task(
        simulate_temperature(provider_instance)
    )

    try:

        await asyncio.Future()

    finally:

        temperature_task.cancel()

        try:
            await temperature_task
        except asyncio.CancelledError:
            pass

        await provider_instance.stop_offer()

        await daemon.disconnect_from_daemon()


if __name__ == "__main__":

    try:
        asyncio.run(main())

    except KeyboardInterrupt:
        print("\nClimate ECU stopped")
