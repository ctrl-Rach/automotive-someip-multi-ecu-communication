# Automotive SOME/IP Multi-ECU Communication

## Project Overview

This project demonstrates communication between multiple Electronic Control Units (ECUs) using the SOME/IP protocol.

SOME/IP stands for Scalable Service-Oriented Middleware over IP. It is used in automotive systems to allow different ECUs to communicate with each other.

The project is implemented using Python and the SomeIPY library.

## Project Objectives

- Understand SOME/IP communication.
- Implement service discovery between ECUs.
- Perform request and response communication.
- Implement event-based communication.
- Monitor and analyse SOME/IP packets using Wireshark.

## ECUs and Services

This project contains two main services:

### 1. Vehicle Speed Service

Service ID: `0x1234`

This service provides vehicle speed and vehicle state information.

**Methods:**
- GetSpeed (`0x0001`) – Gets the current vehicle speed.
- GetVehicleState (`0x0002`) – Gets the vehicle state.

**Events:**
- SpeedChanged (`0x8001`) – Sends updates when vehicle speed changes.
- OverspeedWarning (`0x8002`) – Sends a warning when the speed exceeds the defined limit.

### 2. Climate Service

Service ID: `0x2234`

This service provides cabin temperature information and allows the target temperature to be changed.

**Methods:**
- GetCabinTemperature (`0x0001`) – Gets the current cabin temperature.
- SetTargetTemperature (`0x0002`) – Sets the desired cabin temperature.

**Event:**
- CabinTemperatureChanged (`0x8001`) – Sends updates when cabin temperature changes.

## ECU Applications

The project includes the following applications:

- **Vehicle Speed Service:** Provides vehicle speed and vehicle state information.
- **Instrument Cluster:** Receives vehicle speed information and subscribes to speed-related events.
- **Climate Service:** Provides cabin temperature information and handles temperature requests.
- **Central Display:** Communicates with both Vehicle Speed and Climate services.

## Technologies Used

- Python 3.12
- SomeIPY 2.1.2
- SOME/IP Protocol
- SOME/IP Service Discovery
- Wireshark
- Ubuntu Linux
- VirtualBox

## Project Structure

```text
someip-python-assignment/
│
├── src/
│   ├── vehicle_speed_interface.py
│   ├── vehicle_speed_service.py
│   ├── cluster_client.py
│   ├── climate_interface.py
│   ├── climate_service.py
│   └── central_display.py
│
├── config/
│   └── someipyd.json
│
├── captures/
│   └── assignment2-multi-ecu.pcapng
│
├── images/
│
├── README.md
└── requirements.txt
```

## Installation and Setup

1. Install Python 3.12.
2. Install the required SomeIPY library.
3. Open the project directory.
4. Create and activate a Python virtual environment.
5. Install the required dependencies.

Example:

```bash
pip install someipy==2.1.2
```

## Running the Project

Start the SOME/IP daemon first:

```bash
someipyd --config config/someipyd.json
```

Then run the ECU applications in separate terminal windows:

**Vehicle Speed Service**
```bash
python src/vehicle_speed_service.py
```

**Climate Service**
```bash
python src/climate_service.py
```

**Instrument Cluster**
```bash
python src/cluster_client.py
```

**Central Display**
```bash
python src/central_display.py
```

## Wireshark Packet Analysis

Wireshark was used to capture and analyse SOME/IP communication.

The packet capture includes:
- SOME/IP Service Discovery announcements.
- Vehicle Speed service requests and responses.
- Climate service requests and responses.
- Communication between the ECU applications.

The capture file is available in the `captures` folder.

## Conclusion

This project helped in understanding automotive communication using the SOME/IP protocol. It demonstrates service discovery, method communication, event notifications and communication between multiple ECUs.

It also provides practical experience in analysing automotive network traffic using Wireshark.
