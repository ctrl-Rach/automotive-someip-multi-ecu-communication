"""
Central Display ECU – Assignment 2

Consumes:
1. VehicleSpeedService
2. ClimateService
"""

import asyncio
import logging

from someipy import (
    ClientServiceInstance,
    MessageType,
    ReturnCode,
    connect_to_someipy_daemon,
)

from someipy.someipy_logging import set_someipy_log_level

# Vehicle service imports

from vehicle_speed_interface import (
    SERVICE_ID,
    INSTANCE_ID,
    INTERFACE_IP,
    GET_SPEED_METHOD_ID,
    GET_VEHICLE_STATE_METHOD_ID,
    SPEED_CHANGED_EVENT_ID,
    OVERSPEED_WARNING_EVENT_ID,
    SpeedPayload,
    VehicleStatePayload,
    speed_eventgroup,
    overspeed_eventgroup,
    vehicle_speed_service,
)

# Climate service imports

from climate_interface import (
    CLIMATE_INSTANCE_ID,
    CLIMATE_IP,
    CLIMATE_CONSUMER_PORT,
    GET_CABIN_TEMPERATURE_METHOD_ID,
    SET_TARGET_TEMPERATURE_METHOD_ID,
    CABIN_TEMPERATURE_CHANGED_EVENT_ID,
    TemperaturePayload,
    TargetTemperaturePayload,
    TemperatureStatusPayload,
    climate_eventgroup,
    climate_service,
)


# VEHICLE EVENT CALLBACK

def vehicle_event_callback(event_id, event_payload):

    try:

        message = SpeedPayload().deserialize(event_payload)

        if event_id == SPEED_CHANGED_EVENT_ID:

            print(
                f"\n[DISPLAY] Vehicle Speed: "
                f"{message.speed_kmph.value} km/h"
            )

        elif event_id == OVERSPEED_WARNING_EVENT_ID:

            print(
                f"\n[DISPLAY] !!! OVERSPEED WARNING !!! "
                f"{message.speed_kmph.value} km/h"
            )

    except Exception as error:
        print(f"Vehicle event error: {error}")


# CLIMATE EVENT CALLBACK

def climate_event_callback(event_id, event_payload):

    try:

        if event_id == CABIN_TEMPERATURE_CHANGED_EVENT_ID:

            message = TemperaturePayload().deserialize(
                event_payload
            )

            print(
                f"\n[DISPLAY] Cabin Temperature: "
                f"{message.temperature.value / 10:.1f} °C"
            )

    except Exception as error:
        print(f"Climate event error: {error}")


# VEHICLE SPEED REQUEST

async def get_vehicle_speed(vehicle_client):

    while True:

        try:

            result = await vehicle_client.call_method(
                GET_SPEED_METHOD_ID,
                b"",
            )

            if (
                result.message_type == MessageType.RESPONSE
                and result.return_code == ReturnCode.E_OK
            ):

                message = SpeedPayload().deserialize(
                    result.payload
                )

                print(
                    f"\n[DISPLAY] Current Speed: "
                    f"{message.speed_kmph.value} km/h"
                )

        except Exception as error:
            print(f"Speed request error: {error}")

        await asyncio.sleep(5)


# VEHICLE STATE REQUEST

async def get_vehicle_state(vehicle_client):

    while True:

        try:

            result = await vehicle_client.call_method(
                GET_VEHICLE_STATE_METHOD_ID,
                b"",
            )

            if (
                result.message_type == MessageType.RESPONSE
                and result.return_code == ReturnCode.E_OK
            ):

                message = VehicleStatePayload().deserialize(
                    result.payload
                )

                state = (
                    "STOPPED"
                    if message.vehicle_state.value == 0
                    else "MOVING"
                )

                print(f"\n[DISPLAY] Vehicle State: {state}")

        except Exception as error:
            print(f"Vehicle state error: {error}")

        await asyncio.sleep(5)


# CABIN TEMPERATURE REQUEST

async def get_cabin_temperature(climate_client):

    while True:

        try:

            result = await climate_client.call_method(
                GET_CABIN_TEMPERATURE_METHOD_ID,
                b"",
            )

            if (
                result.message_type == MessageType.RESPONSE
                and result.return_code == ReturnCode.E_OK
            ):

                message = TemperaturePayload().deserialize(
                    result.payload
                )

                print(
                    f"\n[DISPLAY] Cabin Temperature: "
                    f"{message.temperature.value / 10:.1f} °C"
                )

        except Exception as error:
            print(f"Temperature request error: {error}")

        await asyncio.sleep(5)


# SET TARGET TEMPERATURE

async def set_target_temperature(climate_client):

    await asyncio.sleep(3)

    try:

        # Request 25.0 degree Celsius

        requested_temperature = 250

        payload = TargetTemperaturePayload(
            requested_temperature
        ).serialize()

        result = await climate_client.call_method(
            SET_TARGET_TEMPERATURE_METHOD_ID,
            payload,
        )

        if (
            result.message_type == MessageType.RESPONSE
            and result.return_code == ReturnCode.E_OK
        ):

            message = TemperatureStatusPayload().deserialize(
                result.payload
            )

            if message.status.value == 0:

                print(
                    "\n[DISPLAY] Target temperature "
                    "25.0 °C ACCEPTED"
                )

            else:

                print(
                    "\n[DISPLAY] Target temperature "
                    "REJECTED"
                )

    except Exception as error:
        print(f"Set temperature error: {error}")


# MAIN FUNCTION

async def main():

    set_someipy_log_level(logging.INFO)

    print("=" * 60)
    print("CENTRAL DISPLAY ECU")
    print("VehicleSpeedService + ClimateService")
    print("=" * 60)

    daemon = await connect_to_someipy_daemon()

    print("Connected to someipy daemon")

    # Create Vehicle Service Client

    vehicle_client = ClientServiceInstance(
        daemon=daemon,
        service=vehicle_speed_service,
        instance_id=INSTANCE_ID,
        endpoint_ip=INTERFACE_IP,
        endpoint_port=3004,
    )

    vehicle_client.register_callback(
        vehicle_event_callback
    )

    # Create Climate Service Client

    climate_client = ClientServiceInstance(
        daemon=daemon,
        service=climate_service,
        instance_id=CLIMATE_INSTANCE_ID,
        endpoint_ip=CLIMATE_IP,
        endpoint_port=CLIMATE_CONSUMER_PORT,
    )

    climate_client.register_callback(
        climate_event_callback
    )

    print("Searching for VehicleSpeedService...")

    while not await vehicle_client.is_available():
        await asyncio.sleep(1)

    print("VehicleSpeedService AVAILABLE")

    print("Searching for ClimateService...")

    while not await climate_client.is_available():
        await asyncio.sleep(1)

    print("ClimateService AVAILABLE")

    # Subscribe to vehicle events

    vehicle_client.subscribe_eventgroup(
        speed_eventgroup,
        5,
    )

    vehicle_client.subscribe_eventgroup(
        overspeed_eventgroup,
        5,
    )

    # Subscribe to climate event

    climate_client.subscribe_eventgroup(
        climate_eventgroup,
        5,
    )

    print("Subscribed to all event groups")

    # Start all operations

    tasks = [
        asyncio.create_task(get_vehicle_speed(vehicle_client)),
        asyncio.create_task(get_vehicle_state(vehicle_client)),
        asyncio.create_task(get_cabin_temperature(climate_client)),
        asyncio.create_task(set_target_temperature(climate_client)),
    ]

    try:

        await asyncio.Future()

    finally:

        for task in tasks:
            task.cancel()

        await asyncio.gather(
            *tasks,
            return_exceptions=True,
        )

        await daemon.disconnect_from_daemon()


if __name__ == "__main__":

    try:
        asyncio.run(main())

    except KeyboardInterrupt:
        print("\nCentral Display stopped")
