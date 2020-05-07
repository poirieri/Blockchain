# Blockchain implementation for IoT

This project implements simple blockchain over MQTT communication and can be used on multiple IoT devices.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

### Prerequisites
In order to run this project you need to download Mosquitto broker implementation: https://mosquitto.org/ and run mosquitto.exe
MongoDB Compass with Server installed
Python 3.8

##Run project

```
main.exe trust_value isMiner
```
At least one device has to be Miner.

In order to run miner device
```
main.py 1  
```
In order to run non-miner device (not-trusted yet)
```
main.py 0
```

### Packages:
* paho-mqtt	1.5.0	1.5.0
* pip	19.0.3	20.1
* pymongo	3.10.1	3.10.1
* rsa	4.0	4.0

## Run command
```
main.py trust_value isMiner
```
In order to run miner device
```
main.py 1 
```
In order to run non-miner device (not-trusted yet)
```
main.py 1
```

## Versioning

V0.1

## Authors

* **Izabela Poirier** - *Initial work* 

