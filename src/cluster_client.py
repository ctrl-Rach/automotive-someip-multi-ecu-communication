"""
Virtual Instrument Cluster ECU – Assignment 2

Consumes VehicleSpeedService.
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

from vehicle_speed_interface import (
    CONSUMER_PORT,
    GET_SPEED_METHOD_ID,
    GET_VEHICLE_STATE_METHOD_ID,
    INSTANCE_ID,
    INTERFACE_IP,
    SERVICE_ID,
    SPEED_CHANGED_EVENT_ID,
    OVERSPEED_WARNING_EVENT_ID,
    SpeedPayload,
    VehicleStatePayload,
    speed_eventgroup,
    overspeed_eventgroup,
    vehicle_speed_service,
)


# Receive speed and overspeed events

def event_callback(event_id, event_payload):

    try:

        if event_id == SPEED_CHANGED_EVENT_ID:

            message = SpeedPayload().deserialize(event_payload)

            print("\nSpeedChanged notification received")
            print(f"Vehicle speed: {message.speed_kmph.value} km/h")

        elif event_id == OVERSPEED_WARNING_EVENT_ID:

            message = SpeedPayload().deserialize(event_payload)

            print("\n!!! OVERSPEED WARNING !!!")
            print(f"Current speed: {message.speed_kmph.value} km/h")

    except Exception as error:
        print(f"Event decoding error: {error}")


# Request vehicle speed

async def call_get_speed(client_instance):

    while True:

        try:

            result = await client_instance.call_method(
                GET_SPEED_METHOD_ID,
                b"",
            )

            if result.message_type == MessageType.RESPONSE:

                if result.return_code == ReturnCode.E_OK:

                    message = SpeedPayload().deserialize(result.payload)

                    print(
                        f"\nGetSpeed: "
                        f"{message.speed_kmph.value} km/h"
                    )

        except Exception as error:
            print(f"GetSpeed failed: {error}")

        await asyncio.sleep(5)


# Request vehicle state

async def call_get_vehicle_state(client_instance):

    while True:

        try:

            result = await client_instance.call_method(
                GET_VEHICLE_STATE_METHOD_ID,
                b"",
            )

            if result.message_type == MessageType.RESPONSE:

                if result.return_code == ReturnCode.E_OK:

                    message = VehicleStatePayload().deserialize(
                        result.payload
                    )

                    if message.vehicle_state.value == 0:
                        print("\nGetVehicleState: STOPPED")
                    else:
                        print("\nGetVehicleState: MOVING")

        except Exception as error:
            print(f"GetVehicleState failed: {error}")

        await asyncio.sleep(5)


# Main function

async def main():

    set_someipy_log_level(logging.INFO)

    print("=" * 50)
    print("Virtual Instrument Cluster ECU")
    print("VehicleSpeedService Consumer")
    print("=" * 50)

    daemon = await connect_to_someipy_daemon()

    print("Connected to someipy daemon")

    client_instance = ClientServiceInstance(
        daemon=daemon,
        service=vehicle_speed_service,
        instance_id=INSTANCE_ID,
        endpoint_ip=INTERFACE_IP,
        endpoint_port=CONSUMER_PORT,
    )

    client_instance.register_callback(event_callback)

    print("Searching for VehicleSpeedService...")

    while not await client_instance.is_available():
        await asyncio.sleep(1)

    print("VehicleSpeedService AVAILABLE")

    # Subscribe to SpeedChanged

    client_instance.subscribe_eventgroup(
        speed_eventgroup,
        5,
    )

    print("Subscribed to SpeedChanged")

    # Subscribe to OverspeedWarning

    client_instance.subscribe_eventgroup(
        overspeed_eventgroup,
        5,
    )

    print("Subscribed to OverspeedWarning")

    speed_task = asyncio.create_task(
        call_get_speed(client_instance)
    )

    state_task = asyncio.create_task(
        call_get_vehicle_state(client_instance)
    )

    try:
        await asyncio.Future()

    finally:

        speed_task.cancel()
        state_task.cancel()

        await daemon.disconnect_from_daemon()


if __name__ == "__main__":

    try:
        asyncio.run(main())

    except KeyboardInterrupt:
        print("\nInstrument Cluster stopped")
