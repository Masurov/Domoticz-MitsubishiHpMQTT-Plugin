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
* Hardware interface with the AC setup to use your MQTT broker
  * **/!\ beware**, Gysmo38's Mitsubishi2MQTT implementation won't work because it's specific to HomeAssistant.
  * Refer to [Swicago's Heatpump readme](https://github.com/SwiCago/HeatPump) to setup the hardware
  * Configure, compile and upload his [Swicago Heatpump MQTT program](https://github.com/SwiCago/HeatPump/tree/master/examples/mitsubishi_heatpump_mqtt_esp8266_esp32)
    * Edit mitsubishi_heatpump_mqtt_esp8266_esp32.h to setup wifi, mqtt connection
    * Edit mitsubishi_heatpump_mqtt_esp8266_esp32.ino to add  
      ```C
      // connect to the heatpump. Callbacks first so that the hpPacketDebug callback is available for connect()
      hp.setSettingsChangedCallback(hpSettingsChanged);
      hp.setStatusChangedCallback(hpStatusChanged);
      hp.setPacketCallback(hpPacketDebug);
      // vvv theses lines should be added to prevent unsync if you use remote
      hp.enableAutoUpdate();
      hp.enableExternalUpdate();
      ```
    * Compile and upload the program
 
## Plugin Installation

Tested on Python version 3.7 & Domoticz version 4.10717

To install:

* Go in your Domoticz directory, open the plugins directory.
* Navigate to the directory using a command line
* Run: ```git clone https://github.com/Masurov/Domoticz-MitsubishiHpMQTT-Plugin.git```
* Restart Domoticz.

In the web UI, navigate to the Hardware page. In the hardware dropdown there will be an entry called "Mitsubishi Heatpump MQTT interface Plugin".

## Updating

To update:
* Go in your Domoticz directory using a command line and open the plugins directory then the Domoticz-MitsubishiHpMQTT-Plugin directory.
* Run: ```git pull```
* Restart Domoticz.

## Configuration

| Field | Information|
| ----- | ---------- |
| MQTT Server address | IP of your MQTT broker |
| Port | Port of your MQTT broker |
| Login | MQTT broker login (if needed) |
| Password | MQTT broker password (if needed) |
| Heatpump MQTT topic | MQTT topic the ESP has been programmed with (heatpump by default) |
| Debug | When true the logging level will be much higher to aid with troubleshooting |

## Change log

| Version | Information|
| ----- | ---------- |
| 1.2 | Added login and password parameters for MQTT broker connection |
| 1.1 | Fixes wrong selector levels with python version under 3.7 |
| 1.0 | Initial upload version |
