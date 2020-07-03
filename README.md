# Domoticz-MitsubishiHpMQTT-Plugin
Mitsubishi Air Conditionner Domoticz plugin interfacing Swicago MQTT ESP

<img src="https://github.com/Masurov/Domoticz-MitsubishiHpMQTT-Plugin/blob/master/devices.png"/>

## Key Features

* Creates devices for managing for AC in Domoticz :
  * On/Off switch for the unit
  * Mode selector switch
  * Fan speed selector switch
  * Vertical vane selector switch
  * Wide vane selector switch
  * Temperature sensor giving the internal temperature
  * Temperature setpoint to set the desired temperature
* Devices have state pictures

## Prerequisites 

* MQTT broker running
* Hardware interface with the AC [Swicago Heatpump MQTT program](https://github.com/SwiCago/HeatPump/tree/master/examples/mitsubishi_heatpump_mqtt_esp8266_esp32) setup to use your MQTT broker

/!\ beware, Gysmo38's Mitsubishi2MQTT implementation won't work because it's specific to HomeAssistant.
 
## Installation

Tested on Python version 3.7 & Domoticz version 4.10717

To install:

* Go in your Domoticz directory, open the plugins directory.
* Navigate to the directory using a command line
* Run: ```git clone https://github.com/Masurov/Domoticz-MitsubishiHpMQTT-Plugin.git```
* Restart Domoticz.

In the web UI, navigate to the Hardware page. In the hardware dropdown there will be an entry called "Mitsubishi Heatpump MQTT interface Plugin".

## Updating

To update:
* Go in your Domoticz directory using a command line and open the plugins directory then the Domoticz-ParadoxPrt3-Plugin directory.
* Run: ```git pull```
* Restart Domoticz.

## Configuration

| Field | Information|
| ----- | ---------- |
| MQTT Server address | IP of your MQTT broker |
| Port | Port of your MQTT broker |
| Heatpump MQTT topic | MQTT topic the ESP has been programmed with (heatpump by default) |
| Debug | When true the logging level will be much higher to aid with troubleshooting |

## Change log

| Version | Information|
| ----- | ---------- |
| 1.1 | Fixes wrong selector levels with python version under 3.7 |
| 1.0 | Initial upload version |
