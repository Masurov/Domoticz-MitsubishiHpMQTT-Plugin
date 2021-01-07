#           Mitsubishi Heatpump MQTT interface Plugin
#
#           Author:     Masure, 2019
#
#
#   Plugin parameter definition below will be parsed during startup and copied into Manifest.xml, this will then drive the user interface in the Hardware web page

"""
<plugin key="MitsubishiHpMqtt" name="Mitsubishi Heatpump MQTT interface Plugin" author="Masure" version="1.2" externallink="">
    <params>
        <param field="Address" label="MQTT Server address" width="300px" required="true" default="127.0.0.1"/>
        <param field="Port" label="Port" width="300px" required="true" default="1883"/>
        <param field="Username" label="MQTT login" width="300px" default=""/>
        <param field="Password" label="MQTT password" width="300px" default="" password="true" />
        <param field="Mode5" label="Heatpump MQTT topic" width="300px" required="true" default="heatpump"/>
        
        <param field="Mode6" label="Debug" width="75px">
            <options>
                <option label="Extra verbose: (Framework logs 2+4+8+16+64 + MQTT dump)" value="Verbose+"/>
                <option label="Verbose: (Framework logs 2+4+8+16+64 + MQTT dump)" value="Verbose"/>
                <option label="Normal: (Framework logs 2+4+8)" value="Debug"/>
                <option label="None" value="Normal"  default="true" />
            </options>
        </param>
    </params>
</plugin>
"""

import bijection
import Domoticz
import json
from mqttclient import MqttClient
from devicemappings.switchdevice import SwitchDeviceMapping
from devicemappings.selectordevice import SelectorDeviceMapping
from devicemappings.temperaturedevice import TemperatureDeviceMapping
from devicemappings.setpointdevice import SetpointDeviceMapping


class BasePlugin:
    mqttClient = None

    def __init__(self):
        self.mappedDevicesByUnit = {}
    
        self.HeatpumpTopic = None
        self.HeatpumpSetTopic = None
        self.RoomTempTopic = None
        self.HardwareID = None
        self.PluginKey = None
        return

    def onStart(self):

        try:
            Domoticz.Heartbeat(10)

            self.PluginKey = "MitsubishiHpMqtt"
            self.HardwareID = Parameters["HardwareID"]
            self.debugging = Parameters["Mode6"]
            if self.debugging == "Verbose":
                Domoticz.Debugging(2+4+8+16+64)
            if self.debugging == "Debug":
                Domoticz.Debugging(2)
            self.HeatpumpTopic = Parameters["Mode5"]
            self.HeatpumpSetTopic = self.HeatpumpTopic + "/set"
            self.RoomTempTopic = self.HeatpumpTopic + "/status"


            self.mappedDevicesByUnit = {}
            self.payloadKeyToDevice = bijection.Bijection()

            Domoticz.Debug("Mapping power")
            self.powerDeviceMapping = SwitchDeviceMapping(Devices, Images, self.PluginKey, self.HardwareID, "Power", "POW", "power", usedByDefault=True, switchType=0, dzValues = {0:"OFF", 1:"ON"})
            self.mappedDevicesByUnit[self.powerDeviceMapping.dzDevice.Unit] = self.powerDeviceMapping
            self.payloadKeyToDevice["power"] = self.powerDeviceMapping

            Domoticz.Debug("Mapping mode")
            self.modeDeviceMapping = SelectorDeviceMapping(Devices, Images, self.PluginKey, self.HardwareID, "Mode", "MODE", "mode", usedByDefault=True, dzLevelsCodes = [('Auto','AUTO'), ('Froid','COOL'), ('Déshum.','DRY'), ('Chaud','HEAT'), ('Ventil.','FAN')] , offHidden=True)
            self.mappedDevicesByUnit[self.modeDeviceMapping.dzDevice.Unit] = self.modeDeviceMapping
            self.payloadKeyToDevice["mode"] = self.modeDeviceMapping

            Domoticz.Debug("Mapping fan")
            self.fanDeviceMapping = SelectorDeviceMapping(Devices, Images, self.PluginKey, self.HardwareID, "Flux", "FAN", "fan", usedByDefault=True, dzLevelsCodes = [('Auto','AUTO'), ('Silence','QUIET'), ('1','1'), ('2','2'), ('3','3'), ('4','4')], offHidden=True)
            self.mappedDevicesByUnit[self.fanDeviceMapping.dzDevice.Unit] = self.fanDeviceMapping
            self.payloadKeyToDevice["fan"] = self.fanDeviceMapping

            Domoticz.Debug("Mapping vane")
            self.vVaneDeviceMapping = SelectorDeviceMapping(Devices, Images, self.PluginKey, self.HardwareID, "Inclinaison", "VVANE", "vane", usedByDefault=True, dzLevelsCodes = [('Auto','AUTO'), ('1','1'), ('2','2'), ('3','3'), ('4','4'), ('5','5'), ('Oscillant','SWING')], offHidden=True)
            self.mappedDevicesByUnit[self.vVaneDeviceMapping.dzDevice.Unit] = self.vVaneDeviceMapping
            self.payloadKeyToDevice["vane"] = self.vVaneDeviceMapping

            Domoticz.Debug("Mapping wvane")
            self.wVaneDeviceMapping = SelectorDeviceMapping(Devices, Images, self.PluginKey, self.HardwareID, "Direction", "WVANE", "wideVane", usedByDefault=True, dzLevelsCodes = [('<<','<<'), ('<','<'), ('V','|'), ('>','>'), ('>>','>>'), ('Oscillant','SWING')] , offHidden=True)
            self.mappedDevicesByUnit[self.wVaneDeviceMapping.dzDevice.Unit] = self.wVaneDeviceMapping
            self.payloadKeyToDevice["wideVane"] = self.wVaneDeviceMapping

            Domoticz.Debug("Mapping setpoint")
            self.setpointDeviceMapping = SetpointDeviceMapping(Devices, Images, self.PluginKey, self.HardwareID, "Thermostat", "TEMPSET", "temperature", usedByDefault=True)
            self.mappedDevicesByUnit[self.setpointDeviceMapping.dzDevice.Unit] = self.setpointDeviceMapping
            self.payloadKeyToDevice["temperature"] = self.setpointDeviceMapping

            Domoticz.Debug("Mapping temperature")
            self.temperatureDevicemapping = TemperatureDeviceMapping(Devices, Images, self.PluginKey, self.HardwareID, "T° Split", "TEMP", "roomTemperature", usedByDefault=True)
            self.mappedDevicesByUnit[self.temperatureDevicemapping.dzDevice.Unit] = self.temperatureDevicemapping


            self.mqttserveraddress = Parameters["Address"].strip()
            self.mqttserverport = Parameters["Port"].strip()
            clientIdPrefix = 'Domoticz_'+Parameters['Key']+'_'+str(Parameters['HardwareID'])
            self.mqttClient = MqttClient(self.mqttserveraddress, self.mqttserverport, clientIdPrefix, self.onMQTTConnected, self.onMQTTDisconnected, self.onMQTTPublish, None)
        except Exception as e:
            Domoticz.Error("MQTT client start error: "+str(e))
            self.mqttClient = None
    
    def onStop(self):
        Domoticz.Debug("onStop called")

    def onCommand(self, Unit, Command, Level, Color):  # react to commands arrived from Domoticz
        if self.mqttClient is None:
            return False
        Domoticz.Debug("Command: " + Command + " (" + str(Level) + ") Color:" + Color)
        try:
            Domoticz.Debug("    getting device for unit " + str(Unit))
            if (Unit in self.mappedDevicesByUnit):
                Domoticz.Debug("    found")
                Domoticz.Debug("    key : " + str(self.mappedDevicesByUnit[Unit].externalDeviceId))  
                Domoticz.Debug("    value : " + str(self.mappedDevicesByUnit[Unit].DzCommandToExt(Command, str(Level))))  
                payloaddic = { self.mappedDevicesByUnit[Unit].externalDeviceId : self.mappedDevicesByUnit[Unit].DzCommandToExt(Command, str(Level))} 
                Domoticz.Debug(str(payloaddic))

            if (not payloaddic is None):
                Domoticz.Debug("    publishing on " + self.HeatpumpSetTopic + " : " + str(json.dumps(payloaddic)))
                self.mqttClient.Publish(self.HeatpumpSetTopic, json.dumps(payloaddic))
        except Exception as e:
            Domoticz.Debug(str(e))
            return False
    
    def iif(self, boolValue, trueValue, falseValue):
        if (boolValue == True):
            return trueValue
        else:
            return falseValue
         
    def onConnect(self, Connection, Status, Description):
       if self.mqttClient is not None:
        self.mqttClient.onConnect(Connection, Status, Description)

    def onDisconnect(self, Connection):
       if self.mqttClient is not None:
        self.mqttClient.onDisconnect(Connection)

    def onMessage(self, Connection, Data):
       if self.mqttClient is not None:
        self.mqttClient.onMessage(Connection, Data)

    def onHeartbeat(self):
        # Domoticz.Debug("Heartbeating...")
        if self.mqttClient is not None:
            try:
                # Reconnect if connection has dropped
                if (self.mqttClient.mqttConn is None) or (not self.mqttClient.isConnected):
                    Domoticz.Debug("Reconnecting")
                    self.mqttClient.Open()
                else:
                    # Domoticz.Debug("Ping...")
                    self.mqttClient.Ping()
            except Exception as e:
                Domoticz.Error(str(e))

    def onMQTTConnected(self):
        if self.mqttClient is not None:
            self.mqttClient.Subscribe([self.HeatpumpTopic, self.RoomTempTopic])

    def onMQTTDisconnected(self):
        Domoticz.Debug("onMQTTDisconnected")


    def onMQTTPublish(self, topic, message): # process incoming MQTT statuses
        jsondic = json.loads(message.decode('utf8'))

        for mappedDevice in self.mappedDevicesByUnit.values():
            if (mappedDevice.externalDeviceId in jsondic):
                mappedDevice.UpdateDz(jsondic[mappedDevice.externalDeviceId])

        return 


global _plugin

_plugin = BasePlugin()

def onStart():
    global _plugin
    _plugin.onStart()

def onStop():
    global _plugin
    _plugin.onStop()

def onConnect(Connection, Status, Description):
    global _plugin
    _plugin.onConnect(Connection, Status, Description)

def onDisconnect(Connection):
    global _plugin
    _plugin.onDisconnect(Connection)

def onMessage(Connection, Data):
    global _plugin
    _plugin.onMessage(Connection, Data)

def onCommand(Unit, Command, Level, Color):
    global _plugin
    _plugin.onCommand(Unit, Command, Level, Color)

def onHeartbeat():
    global _plugin
    _plugin.onHeartbeat()